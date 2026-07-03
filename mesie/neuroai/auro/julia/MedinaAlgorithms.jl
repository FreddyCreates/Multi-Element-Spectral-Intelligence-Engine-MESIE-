"""
MedinaAlgorithms.jl — Medina native algorithmic generation suite in Julia.

Maximum-performance implementations of all 7 Medina algorithms:
  phi_harmonic_basis  — Schumann-anchored φ-spaced frequency basis (FFTW-backed)
  text_to_spectrum    — char-code FFT spectral encoding (native FFTW)
  phi_cascade         — φ-weighted axonal cascade, BLAS matrix-vector products
  polygon_envelope    — φ-harmonic convex-hull geometry (LinearAlgebra)
  recursive_unfold    — fractal dendritic grammar, @inbounds @simd inner loops
  hebbian_salience    — LTP synaptic plasticity (scalar, zero allocation)
  chemical_cascade    — enzyme ODE, BLAS-backed matrix ops, pre-allocated buffers
  batch_analyze       — all algorithms in one call, no subprocess round-trips

Laws: PHI = 1.618…, PHI_INV = 0.618…, SCHUMANN = 7.83 Hz, DELTA_T = 0.873 s
"""

module MedinaAlgorithms

using LinearAlgebra
using FFTW

export phi_harmonic_basis, text_to_spectrum, phi_cascade, polygon_envelope,
       recursive_unfold, hebbian_salience, chemical_cascade, batch_analyze

# ── Constants ──────────────────────────────────────────────────────────────────
const PHI      = 1.618033988749895
const PHI_INV  = 0.6180339887498949
const SCHUMANN = 7.83
const DELTA_T  = 0.873

# ── 1. φ-harmonic frequency basis ─────────────────────────────────────────────
"""
    phi_harmonic_basis(n::Int=64) -> Vector{Float64}

Geometric series of frequencies anchored at Schumann resonance (7.83 Hz),
each frequency = previous × φ⁻¹. Pre-allocated, zero-copy return.
"""
function phi_harmonic_basis(n::Int=64)::Vector{Float64}
    freqs = Vector{Float64}(undef, n)
    @inbounds freqs[1] = SCHUMANN / 100.0
    @inbounds for i in 2:n
        freqs[i] = freqs[i-1] * PHI_INV
    end
    nrm = norm(freqs)
    nrm < 1e-12 && return freqs
    freqs ./= nrm
    return freqs
end

# ── 2. Text → spectral vector (char-code FFT) ─────────────────────────────────
"""
    text_to_spectrum(text::String, n::Int=64) -> Vector{Float64}

Map text to a normalised spectral signature via char-code rfft.
Uses FFTW under the hood — orders of magnitude faster than numpy.
Output length = n÷2 + 1 (rfft output).
"""
function text_to_spectrum(text::String, n::Int=64)::Vector{Float64}
    chars = collect(codeunits(text))
    sig = Vector{Float64}(undef, n)
    m = min(length(chars), n)
    @inbounds for i in 1:m
        sig[i] = Float64(Int(chars[i]) % 97)
    end
    @inbounds for i in (m+1):n
        sig[i] = 0.0
    end
    # Linear detrend
    slope = (sig[n] - sig[1]) / max(1, n - 1)
    @inbounds for i in 1:n
        sig[i] -= sig[1] + slope * (i - 1)
    end
    spec = abs.(rfft(sig))
    nrm = norm(spec)
    nrm < 1e-12 && return spec
    spec ./= nrm
    return spec
end

# ── Helper: cosine similarity (zero-allocation, BLAS dot) ─────────────────────
@inline function _cosine(a::AbstractVector{Float64}, b::AbstractVector{Float64})::Float64
    n = min(length(a), length(b))
    d = dot(view(a, 1:n), view(b, 1:n))
    na = norm(view(a, 1:n))
    nb = norm(view(b, 1:n))
    return d / (na * nb + 1e-12)
end

# ── 3. φ-cascade — axonal signal propagation ─────────────────────────────────
"""
    phi_cascade(query_vec, knowledge_vecs, saliences;
                decay=PHI_INV, threshold=0.12, k=5, hops=3) -> Vector{Int}

φ-cascade propagation over knowledge_vecs.
Returns indices (1-based) of top-k activated items above threshold.
Uses BLAS matrix-vector product for cascade hops.

Algorithm:  A(t+1) = A(t) + hop_factor × S × A(t)
            where S is the pairwise cosine similarity matrix (computed once)
            hop_factor = decay^hop
"""
function phi_cascade(
    query_vec    :: Vector{Float64},
    knowledge_vecs :: Vector{Vector{Float64}},
    saliences    :: Vector{Float64};
    decay        :: Float64 = PHI_INV,
    threshold    :: Float64 = 0.12,
    k            :: Int     = 5,
    hops         :: Int     = 3,
)::Tuple{Vector{Int}, Vector{Float64}}
    n = length(knowledge_vecs)
    n == 0 && return Int[], Float64[]

    # Tier-0: direct cosine similarity to query
    activations = Vector{Float64}(undef, n)
    @inbounds for i in 1:n
        activations[i] = _cosine(query_vec, knowledge_vecs[i])
    end

    # Pairwise similarity matrix — symmetric, built once (O(n²) — n always small)
    S = Matrix{Float64}(undef, n, n)
    @inbounds for i in 1:n
        S[i, i] = 1.0
        for j in (i+1):n
            s = _cosine(knowledge_vecs[i], knowledge_vecs[j])
            S[i, j] = s
            S[j, i] = s
        end
    end

    # Cascade hops — BLAS gemv for propagation
    prop = Vector{Float64}(undef, n)
    @inbounds for hop in 1:(hops-1)
        hop_factor = decay ^ hop
        mul!(prop, S, activations)          # prop = S * activations (BLAS)
        @simd for i in 1:n
            activations[i] += hop_factor * prop[i]
        end
    end

    # Weight by salience (biotech: receptor density)
    @inbounds @simd for i in 1:n
        activations[i] *= saliences[i]
    end

    # Rank and filter
    order = sortperm(activations, rev=true)
    top_idx  = Int[]
    top_scor = Float64[]
    for i in order
        activations[i] > threshold || break
        push!(top_idx, i)
        push!(top_scor, activations[i])
        length(top_idx) >= k && break
    end
    return top_idx, top_scor
end

# ── 4. Polygon envelope — φ-harmonic convex-hull geometry ────────────────────
"""
    polygon_envelope(query_vec, knowledge_vecs) -> NamedTuple

Project all vectors onto 2D φ-harmonic basis (golden-angle spiral coordinates).
Compute convex hull of knowledge cloud via mean-radius heuristic.
Determine whether query is inside (known) or outside (frontier).

Returns: (inside, region_confidence, nearest_idx, hull_radius, query_radius)
"""
function polygon_envelope(
    query_vec      :: Vector{Float64},
    knowledge_vecs :: Vector{Vector{Float64}},
)
    n_items = length(knowledge_vecs)
    if n_items < 3
        return (inside=false, region_confidence=0.0, nearest_idx=1,
                hull_radius=0.0, query_radius=0.0)
    end

    dim = length(query_vec)
    basis1 = phi_harmonic_basis(dim)

    # Second basis: golden-angle shift in harmonic space
    shift = mod(round(Int, dim * PHI_INV), dim) + 1
    basis2 = circshift(basis1, shift)

    # Project all knowledge vectors
    pts = Matrix{Float64}(undef, n_items, 2)
    @inbounds for i in 1:n_items
        v = knowledge_vecs[i]
        m = min(length(v), dim)
        pts[i, 1] = dot(view(basis1, 1:m), view(v, 1:m))
        pts[i, 2] = dot(view(basis2, 1:m), view(v, 1:m))
    end

    # Project query
    qm = min(length(query_vec), dim)
    qx = dot(view(basis1, 1:qm), view(query_vec, 1:qm))
    qy = dot(view(basis2, 1:qm), view(query_vec, 1:qm))

    # Centroid
    cx = mean(view(pts, :, 1))
    cy = mean(view(pts, :, 2))

    # Hull radius = mean distance of knowledge points from centroid
    hull_radius = mean(sqrt((pts[i, 1] - cx)^2 + (pts[i, 2] - cy)^2) for i in 1:n_items)

    # Query radius
    q_radius = sqrt((qx - cx)^2 + (qy - cy)^2)

    # Nearest knowledge point
    nearest_idx = 1
    nearest_dist = Inf
    @inbounds for i in 1:n_items
        d = sqrt((pts[i, 1] - qx)^2 + (pts[i, 2] - qy)^2)
        if d < nearest_dist
            nearest_dist = d
            nearest_idx = i
        end
    end

    inside = q_radius <= hull_radius * 1.15
    region_confidence = clamp(1.0 - q_radius / (hull_radius + 1e-12), 0.0, 1.0)

    return (
        inside             = inside,
        region_confidence  = round(region_confidence, digits=4),
        nearest_idx        = nearest_idx,
        hull_radius        = round(hull_radius, digits=4),
        query_radius       = round(q_radius, digits=4),
    )
end

# ── 5. Recursive unfold — fractal dendritic grammar ──────────────────────────
"""
    recursive_unfold(seed::Vector{Float64}; depth::Int=3, branching::Int=2) -> Vector{Float64}

Fractal dendritic expansion at Julia speed.
Each spectral component spawns `branching` children at φ-scaled spiral indices.
Decays by φ⁻¹ per level. @inbounds @simd hot path, minimal allocation.
"""
function recursive_unfold(
    seed      :: Vector{Float64};
    depth     :: Int = 3,
    branching :: Int = 2,
)::Vector{Float64}
    n = length(seed)
    weights = copy(seed)

    function _recurse!(result::Vector{Float64}, parent::Vector{Float64},
                       level::Int, scale::Float64)
        level == 0 || scale < 1e-7 && return
        child = zeros(Float64, n)
        @inbounds for i in 1:n
            parent[i] > 1e-10 || continue
            for b in 1:branching
                child_i = mod(round(Int, (i-1) * PHI * b), n) + 1
                child[child_i] += parent[i] * scale * PHI_INV
            end
        end
        _recurse!(child, child, level - 1, scale * PHI_INV)
        @inbounds @simd for i in 1:n
            result[i] += child[i]
        end
    end

    _recurse!(weights, copy(seed), depth, 1.0)
    nrm = norm(weights)
    nrm < 1e-12 && return weights
    weights ./= nrm
    return weights
end

# ── 6. Hebbian LTP — synaptic plasticity ─────────────────────────────────────
"""
    hebbian_salience(base::Float64, co_activation_count::Int;
                     rate::Float64=PHI_INV*0.08, ceiling::Float64=1.0) -> Float64

Neurons that fire together, wire together.
Logarithmic growth bounded at ceiling — no runaway potentiation.
Zero allocation: pure scalar arithmetic.
"""
@inline function hebbian_salience(
    base                :: Float64,
    co_activation_count :: Int;
    rate    :: Float64 = PHI_INV * 0.08,
    ceiling :: Float64 = 1.0,
)::Float64
    return min(ceiling, base + rate * log1p(Float64(co_activation_count)))
end

# ── 7. Chemical cascade — enzyme reaction-network ODE ────────────────────────
"""
    chemical_cascade(activations, reaction_matrix;
                     steps::Int=4, decay::Float64=PHI_INV) -> Vector{Float64}

Discretised enzyme kinetics:  A(t+1) = decay × A(t) + (1-decay) × R × A(t)
Normalised each step — conserves activation, no blow-up.
Pre-allocated buffer, BLAS gemv for matrix-vector product.
"""
function chemical_cascade(
    activations     :: Vector{Float64},
    reaction_matrix :: Matrix{Float64};
    steps :: Int    = 4,
    decay :: Float64 = PHI_INV,
)::Vector{Float64}
    a    = copy(activations)
    tmp  = similar(a)
    a1d  = 1.0 - decay
    for _ in 1:steps
        mul!(tmp, reaction_matrix, a)       # BLAS: tmp = R * a
        @inbounds @simd for i in eachindex(a)
            a[i] = decay * a[i] + a1d * tmp[i]
        end
        nrm = norm(a)
        nrm < 1e-12 && break
        a ./= nrm
    end
    return a
end

# ── batch_analyze — all algorithms in one call ────────────────────────────────
"""
    batch_analyze(text::String, knowledge_texts::Vector{String},
                  saliences::Vector{Float64}) -> Dict

Run the full Medina algorithmic pipeline over a query text and knowledge base.
One Julia call replaces 7 subprocess round-trips.

Returns a Dict with all algorithm results for JSON serialisation.
"""
function batch_analyze(
    text            :: String,
    knowledge_texts :: Vector{String},
    saliences       :: Vector{Float64},
)::Dict{String, Any}
    n_k = length(knowledge_texts)
    if isempty(saliences)
        saliences = fill(PHI_INV, n_k)
    end

    # Spectral encoding — query + all knowledge
    q_vec   = text_to_spectrum(text)
    k_vecs  = [text_to_spectrum(t) for t in knowledge_texts]

    # φ-harmonic basis projection
    basis   = phi_harmonic_basis(length(q_vec))
    m       = min(length(basis), length(q_vec))
    phi_sig = dot(view(basis, 1:m), view(q_vec, 1:m))

    # φ-cascade
    cascade_idx, cascade_scores = phi_cascade(q_vec, k_vecs, saliences)

    # Polygon envelope
    poly = polygon_envelope(q_vec, k_vecs)

    # Recursive unfold
    unfold_w = recursive_unfold(q_vec; depth=4, branching=2)
    unfold_energy = sum(x^2 for x in unfold_w)

    # Chemical cascade over multi-scale feature pyramid (3 bands)
    dim = length(q_vec)
    band_size = max(1, dim ÷ 3)
    bands = [q_vec[((b-1)*band_size+1):min(b*band_size, dim)] for b in 1:3]
    n_bands = length(bands)
    react = Matrix{Float64}(undef, n_bands, n_bands)
    for i in 1:n_bands, j in 1:n_bands
        react[i, j] = _cosine(bands[i], bands[j])
    end
    init_act = [norm(b) for b in bands]
    cascade_out = chemical_cascade(init_act, react; steps=4, decay=PHI_INV)
    cascade_energy = sum(x^2 for x in cascade_out)

    # Spectral entropy (Shannon, over q_vec as probability dist)
    p = q_vec ./ (sum(q_vec) + 1e-12)
    entropy = -sum(x * log2(x + 1e-14) for x in p)

    # Spectral centroid
    freqs = Float64.(1:length(q_vec))
    centroid = dot(freqs, p)

    # Hebbian salience update for top cascade pair
    top_salience = if length(cascade_idx) >= 2
        hebbian_salience(saliences[cascade_idx[1]], length(cascade_idx))
    else
        isempty(saliences) ? PHI_INV : saliences[1]
    end

    return Dict{String, Any}(
        "phi_signal"       => round(phi_sig, digits=4),
        "entropy"          => round(entropy, digits=4),
        "centroid"         => round(centroid, digits=4),
        "unfold_energy"    => round(unfold_energy, digits=4),
        "cascade_energy"   => round(cascade_energy, digits=4),
        "n_cascade_hits"   => length(cascade_idx),
        "cascade_idx"      => cascade_idx,
        "cascade_scores"   => round.(cascade_scores, digits=4),
        "poly_inside"      => poly.inside,
        "poly_confidence"  => poly.region_confidence,
        "poly_hull_radius" => poly.hull_radius,
        "poly_query_radius"=> poly.query_radius,
        "poly_nearest_idx" => poly.nearest_idx,
        "top_salience"     => round(top_salience, digits=4),
        "phi"              => PHI,
        "phi_inv"          => PHI_INV,
        "schumann"         => SCHUMANN,
        "delta_t"          => DELTA_T,
        "runtime"          => "julia",
        "n_knowledge"      => n_k,
    )
end

end  # module MedinaAlgorithms
