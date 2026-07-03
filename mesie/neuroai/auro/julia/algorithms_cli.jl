#!/usr/bin/env julia
# Medina Algorithms CLI — JSON stdin → JSON stdout dispatch.
# Called by algorithms_jl.py via subprocess.run (same pattern as MESIEPolyglot/cli.jl).
#
# Supported actions:
#   health          → { ok: true }
#   text_to_spectrum  → { vector: [...] }
#   phi_harmonic_basis → { vector: [...] }
#   phi_cascade       → { indices: [...], scores: [...] }
#   polygon_envelope  → { inside, region_confidence, ... }
#   recursive_unfold  → { weights: [...] }
#   hebbian_salience  → { salience: float }
#   chemical_cascade  → { activations: [...] }
#   batch_analyze     → full algorithm result dict (preferred — one round-trip)

include(joinpath(@__DIR__, "MedinaAlgorithms.jl"))
using .MedinaAlgorithms
using JSON

function dispatch(req::Dict)
    action = get(req, "action", "health")

    if action == "health"
        return Dict("ok" => true, "runtime" => "julia", "module" => "MedinaAlgorithms")

    elseif action == "text_to_spectrum"
        text = get(req, "text", "")
        n    = get(req, "n", 64)
        v    = text_to_spectrum(text, n)
        return Dict("ok" => true, "vector" => v)

    elseif action == "phi_harmonic_basis"
        n = get(req, "n", 64)
        v = phi_harmonic_basis(n)
        return Dict("ok" => true, "vector" => v)

    elseif action == "phi_cascade"
        q_vec  = Float64.(get(req, "query_vec", Float64[]))
        k_data = get(req, "knowledge_vecs", Any[])
        k_vecs = [Float64.(v) for v in k_data]
        sals   = Float64.(get(req, "saliences", fill(0.618, length(k_vecs))))
        decay  = Float64(get(req, "decay", 0.6180339887498949))
        thr    = Float64(get(req, "threshold", 0.12))
        k      = Int(get(req, "k", 5))
        hops   = Int(get(req, "hops", 3))
        idx, scores = phi_cascade(q_vec, k_vecs, sals;
                                  decay=decay, threshold=thr, k=k, hops=hops)
        return Dict("ok" => true, "indices" => idx, "scores" => scores)

    elseif action == "polygon_envelope"
        q_vec  = Float64.(get(req, "query_vec", Float64[]))
        k_data = get(req, "knowledge_vecs", Any[])
        k_vecs = [Float64.(v) for v in k_data]
        poly   = polygon_envelope(q_vec, k_vecs)
        return Dict(
            "ok"               => true,
            "inside"           => poly.inside,
            "region_confidence"=> poly.region_confidence,
            "nearest_idx"      => poly.nearest_idx,
            "hull_radius"      => poly.hull_radius,
            "query_radius"     => poly.query_radius,
        )

    elseif action == "recursive_unfold"
        seed     = Float64.(get(req, "seed", Float64[]))
        depth    = Int(get(req, "depth", 3))
        branching= Int(get(req, "branching", 2))
        w        = recursive_unfold(seed; depth=depth, branching=branching)
        return Dict("ok" => true, "weights" => w)

    elseif action == "hebbian_salience"
        base  = Float64(get(req, "base_salience", 0.618))
        count = Int(get(req, "co_activation_count", 1))
        rate  = Float64(get(req, "rate", 0.6180339887498949 * 0.08))
        ceil_ = Float64(get(req, "ceiling", 1.0))
        s     = hebbian_salience(base, count; rate=rate, ceiling=ceil_)
        return Dict("ok" => true, "salience" => s)

    elseif action == "chemical_cascade"
        acts  = Float64.(get(req, "activations", Float64[]))
        R_raw = get(req, "reaction_matrix", Any[])
        R     = Matrix{Float64}(hcat([Float64.(row) for row in R_raw]...)')
        steps = Int(get(req, "steps", 4))
        decay = Float64(get(req, "decay", 0.6180339887498949))
        out   = chemical_cascade(acts, R; steps=steps, decay=decay)
        return Dict("ok" => true, "activations" => out)

    elseif action == "batch_analyze"
        text     = get(req, "text", "")
        k_texts  = String.(get(req, "knowledge_texts", String[]))
        sals     = Float64.(get(req, "saliences", Float64[]))
        result   = batch_analyze(text, k_texts, sals)
        result["ok"] = true
        return result

    else
        return Dict("ok" => false, "error" => "unsupported action: $action")
    end
end

input = read(stdin, String)
req   = JSON.parse(input)
out   = dispatch(req)
println(JSON.json(out))
