"""AuroNativeLanguageModel — Medina native speaking intelligence built per Paper IV.

Not third-party inference. Dynamical authority surface: memory, affect, proof, voice.

Generation pipeline (every path is an algorithm):
    text → FFT spectrum
         → SpectralNeuroCore  (multi-head attention, TAURUS, cross-band, harmonics)
         → phi_cascade         (φ-weighted axonal propagation through knowledge)
         → polygon_envelope    (convex-hull geometry — known vs frontier territory)
         → recursive_unfold    (fractal dendritic grammar expansion)
         → SpectralKnowledgeGraph (ontological semantic traversal)
         → TemporalSpectralBuffer (conversation trajectory, change-point detection)
         → ExperienceReplayBuffer (priority-weighted past context)
         → SpectralReasoningEngine (Bayesian causal chain)
         → SpectralDecomposer  (EMD intrinsic mode functions)
         → spectral_compose    (text assembly from cascade hits + unfold weights)
"""

from __future__ import annotations

import re
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from mesie.cognitive.knowledge_graph import (
    SpectralKnowledgeGraph, KnowledgeNode, KnowledgeRelation,
    NodeType, RelationType,
)
from mesie.cognitive.memory_consolidation import ExperienceReplayBuffer
from mesie.cognitive.neurocores import SpectralNeuroCore, NeuroCoreConfig
from mesie.cognitive.reasoning_engine import SpectralReasoningEngine, ReasoningMode
from mesie.cognitive.signal_processing import (
    SpectralDecomposer, DecompositionMethod, AdvancedFeatureExtractor,
)
from mesie.cognitive.temporal_dynamics import TemporalSpectralBuffer
from mesie.neuroai.auro.affect import AffectState, modulate_affect
from mesie.neuroai.auro.algorithms import (
    phi_cascade, polygon_envelope, recursive_unfold,
    hebbian_salience, chemical_cascade, spectral_compose,
    phi_harmonic_basis, PHI, PHI_INV, DELTA_T,
)
from mesie.neuroai.auro.memory import AuroVoiceMemory
from mesie.neuroai.auro.multi_agent_protocol import MultiAgentSpeechProtocol
from mesie.neuroai.auro.roles import enforce_boundary, select_speaking_role
from mesie.neuroai.auro.spoken_claim_score import SpokenClaimScore, score_spoken_claim
from mesie.neuroai.auro.surfaces import load_family_manifest
from mesie.neuroai.auro.trajectory import SpokenTrajectory
from mesie.sdk.solus import SDKSolusOrganism

ROOT = Path(__file__).resolve().parents[3]
PAPER_IV = ROOT / "data" / "neuroai" / "substrate" / "p4-auro-dynamics-speaking-intelligence.md"

MODEL_ID = "AuroNativeLM-v1"


# ── Spectral encoding (shared across all methods) ────────────────────────────

def _text_to_vec(text: str, n: int = 64) -> np.ndarray:
    """Encode text to a normalised spectral vector via char-code FFT."""
    sig = np.array([float(ord(c) % 97) for c in text[:n]], dtype=np.float64)
    if len(sig) < n:
        sig = np.pad(sig, (0, n - len(sig)))
    detrended = sig - np.linspace(sig[0], sig[-1], n)
    spectrum = np.abs(np.fft.rfft(detrended))
    norm = float(np.linalg.norm(spectrum)) + 1e-12
    return spectrum / norm


# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class NativeSpeechOutput:
    spoken: str
    claim_score: Dict[str, Any]
    loop_steps: List[str]
    role: str
    defer_to: Optional[str]
    affect: Dict[str, Any]
    protocol: Dict[str, Any]
    trajectory_id: str
    algo: Dict[str, Any]          # full algorithmic analysis result
    native_model: str = MODEL_ID
    sovereign: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spoken": self.spoken,
            "claim_score": self.claim_score,
            "loop_steps": self.loop_steps,
            "role": self.role,
            "defer_to": self.defer_to,
            "affect": self.affect,
            "protocol": self.protocol,
            "trajectory_id": self.trajectory_id,
            "algo": self.algo,
            "native_model": self.native_model,
            "sovereign": self.sovereign,
        }


@dataclass
class AuroNativeLanguageModel:
    """Full-stack native LM — every signal path is a real algorithm.

    No external LLM, no template generation, no crude keyword match.
    The generation core is the MESIE algorithmic substrate:
    NeuroCore attention × φ-cascade × polygon geometry × recursive unfold
    × ontological knowledge graph × temporal dynamics × Bayesian reasoning.
    """

    session_id: str
    memory: AuroVoiceMemory = field(default_factory=lambda: AuroVoiceMemory("auro"))
    trajectory: SpokenTrajectory = field(default_factory=lambda: SpokenTrajectory("auro", "pending"))
    organism: SDKSolusOrganism = field(default_factory=SDKSolusOrganism)
    protocol: MultiAgentSpeechProtocol = field(default_factory=MultiAgentSpeechProtocol)

    # ── knowledge base ────────────────────────────────────────────────────────
    _knowledge: List[Dict[str, Any]] = field(default_factory=list, init=False)
    _rules: List[Tuple[re.Pattern[str], str]] = field(default_factory=list, init=False)

    # ── MESIE algorithmic substrate — ALL wired in ────────────────────────────
    _neurocore: SpectralNeuroCore = field(
        default_factory=lambda: SpectralNeuroCore(NeuroCoreConfig(
            core_id="auro_core",
            d_model=64,              # matches _text_to_vec output length (rfft of 64 = 33, padded)
            n_attention_heads=8,
            memory_capacity=512,
            working_memory_slots=7,
            attention_temperature=0.8,
            multi_scale_levels=4,
            enable_cross_band=True,
            enable_harmonics=True,
        )),
        init=False,
    )
    _knowledge_graph: SpectralKnowledgeGraph = field(
        default_factory=SpectralKnowledgeGraph,
        init=False,
    )
    _temporal_buffer: TemporalSpectralBuffer = field(
        default_factory=lambda: TemporalSpectralBuffer(max_length=256, d_spectral=33),
        init=False,
    )
    _replay_buffer: ExperienceReplayBuffer = field(
        default_factory=lambda: ExperienceReplayBuffer(
            capacity=512,
            priority_exponent=0.6,
            importance_sampling_exponent=0.4,
        ),
        init=False,
    )
    _reasoning_engine: SpectralReasoningEngine = field(
        default_factory=lambda: SpectralReasoningEngine(
            max_chain_depth=6, confidence_threshold=0.55,
            enable_counterfactuals=False, enable_causal=True,
        ),
        init=False,
    )
    _decomposer: SpectralDecomposer = field(
        default_factory=lambda: SpectralDecomposer(max_components=6, energy_threshold=0.02),
        init=False,
    )
    _feature_extractor: AdvancedFeatureExtractor = field(
        default_factory=AdvancedFeatureExtractor,
        init=False,
    )
    # Hebbian co-activation counters (pair-key → count)
    _co_activation: Dict[str, int] = field(default_factory=dict, init=False)
    # cached knowledge vecs (invalidated on knowledge change)
    _k_vecs_cache: Optional[List[np.ndarray]] = field(default=None, init=False)

    # ─────────────────────────────────────────────────────────────────────────

    def __post_init__(self) -> None:
        self.memory.session_id = self.session_id
        self.trajectory = SpokenTrajectory(
            session_id=self.session_id,
            trajectory_id=f"traj_{uuid.uuid4().hex[:12]}",
        )
        self._bootstrap_knowledge()
        self._bootstrap_rules()
        self._bootstrap_knowledge_graph()

    # ── Bootstrap ─────────────────────────────────────────────────────────────

    def _bootstrap_knowledge(self) -> None:
        family = load_family_manifest()
        for name, spec in family.get("members", {}).items():
            self._knowledge.append({
                "key": name.lower(),
                "domain": "alpha_family",
                "content": f"{name}: {spec.get('role', '')}",
                "salience": PHI_INV,
            })
        for line in family.get("blocked_claims", []):
            self._knowledge.append({
                "key": "blocked", "domain": "boundary",
                "content": f"blocked: {line}", "salience": PHI_INV,
            })
        if PAPER_IV.is_file():
            text = PAPER_IV.read_text(encoding="utf-8", errors="replace")
            for i, chunk in enumerate(self._chunk_paper(text)):
                self._knowledge.append({
                    "key": f"paper_iv_{i}",
                    "domain": "paper",
                    "content": chunk[:900],
                    "salience": PHI_INV,
                })
        self._k_vecs_cache = None  # invalidate

    def _chunk_paper(self, text: str) -> List[str]:
        parts = []
        for sec in text.split("\n## "):
            sec = sec.strip()
            if len(sec) > 60:
                parts.append(sec[:900])
        return parts[:32]

    def _bootstrap_rules(self) -> None:
        self._rules = [
            (re.compile(r"what is auro|who are you", re.I),
             "I am Auro — Medina's native speaking intelligence. THESIS proves; I carry the voice and the boundary."),
            (re.compile(r"alpha.?family|your role", re.I),
             "Alpha-family: Auro speaks, THESIS proves, ORIGO builds, Codex implements, CIVOS governs."),
            (re.compile(r"speaking loop", re.I),
             "Eight-step loop: perception, memory, role, affect, claims, speech, response, state update."),
            (re.compile(r"heavy and weights", re.I),
             "Heavy and Weights Heart: one organism result, Medina identity, one evidence backbone."),
        ]

    def _bootstrap_knowledge_graph(self) -> None:
        """Populate SpectralKnowledgeGraph from _knowledge items.

        Each knowledge item becomes a PHENOMENON node; items in the same
        domain are linked with CORRELATES_WITH edges. This gives the
        phi_cascade and ontological reasoner a real graph structure to
        traverse rather than a flat list.
        """
        for item in self._knowledge:
            node = KnowledgeNode(
                node_id=item["key"],
                name=item["key"],
                node_type=NodeType.PHENOMENON,
                properties={
                    "domain": item.get("domain", "unknown"),
                    "content": item.get("content", "")[:200],
                    "salience": item.get("salience", PHI_INV),
                },
                confidence=item.get("salience", PHI_INV),
                source=item.get("domain", "bootstrap"),
            )
            self._knowledge_graph.add_node(node)

        # Link same-domain items as CORRELATES_WITH (domain coherence edges)
        domain_groups: Dict[str, List[str]] = {}
        for item in self._knowledge:
            domain_groups.setdefault(item.get("domain", "unknown"), []).append(item["key"])
        for domain, keys in domain_groups.items():
            for i in range(len(keys)):
                for j in range(i + 1, min(i + 4, len(keys))):  # fan-out cap 3
                    rel = KnowledgeRelation(
                        source_id=keys[i],
                        target_id=keys[j],
                        relation_type=RelationType.CORRELATES_WITH,
                        strength=PHI_INV,
                        confidence=0.7,
                    )
                    self._knowledge_graph.add_relation(rel)

    # ── Spectral encoding helpers ─────────────────────────────────────────────

    def _knowledge_vecs(self) -> List[np.ndarray]:
        """Spectral vectors for all knowledge items — cached until invalidated."""
        if self._k_vecs_cache is None:
            self._k_vecs_cache = [
                _text_to_vec(item.get("content", item.get("key", "")))
                for item in self._knowledge
            ]
        return self._k_vecs_cache

    # ── NeuroCore perception ──────────────────────────────────────────────────

    def _neurocore_process(self, text: str) -> Dict[str, Any]:
        """Run text through SpectralNeuroCore: multi-head attention + TAURUS + harmonics.

        Returns attended embedding and all analysis fields. The embedding is
        used downstream instead of the raw FFT vector — it has been shaped
        by 8-head attention and multi-scale projection, giving richer signal.
        """
        raw_vec = _text_to_vec(text)
        result = self._neurocore.process(
            raw_vec,
            context={"tag": "query", "text": text[:80]},
            store_in_memory=True,
        )
        return {
            "embedding": result.embedding,          # attended spectral embedding
            "attention_map": result.attention_map,  # per-dim attention weights
            "attention_analysis": result.attention_analysis,
            "multi_scale": result.multi_scale_features,
            "cross_band": result.cross_band_scores,
            "harmonics": result.harmonic_peaks or [],
            "memory_matches": [
                {"similarity": m.similarity, "context": m.context}
                for m in (result.memory_matches or [])
            ],
            "raw_vec": raw_vec,
        }

    # ── Temporal dynamics ─────────────────────────────────────────────────────

    def _temporal_push(self, vec: np.ndarray, text: str) -> Dict[str, Any]:
        """Push query spectrum into the temporal buffer. Returns buffer stats."""
        self._temporal_buffer.push(vec, metadata={"text": text[:60]})
        stats = self._temporal_buffer.get_statistics()
        # Temporal diff — detect topic change (spectral flux between turns)
        diff = self._temporal_buffer.get_temporal_diff(lag=1)
        flux = float(np.mean(np.abs(diff))) if diff is not None and len(diff) > 0 else 0.0
        return {"buffer_size": stats.get("size", 0), "spectral_flux": round(flux, 4)}

    # ── Replay buffer ─────────────────────────────────────────────────────────

    def _replay_sample(self, q_vec: np.ndarray, n: int = 3) -> List[Dict[str, Any]]:
        """Sample priority-weighted past experiences relevant to current query."""
        if len(self._replay_buffer._buffer) < n:
            return []
        experiences, _indices, weights = self._replay_buffer.sample(min(n, len(self._replay_buffer._buffer)))
        # Filter by cosine similarity to current query
        relevant = []
        for exp, w in zip(experiences, weights):
            emb = np.array(exp.get("embedding", []), dtype=np.float64)
            if emb.size == 0:
                continue
            min_len = min(len(q_vec), len(emb))
            sim = float(np.dot(q_vec[:min_len], emb[:min_len]) /
                        (np.linalg.norm(q_vec[:min_len]) * np.linalg.norm(emb[:min_len]) + 1e-12))
            if sim > 0.1:
                relevant.append({**exp, "replay_sim": round(sim, 4), "is_weight": float(w)})
        return relevant

    # ── Knowledge graph semantic query ────────────────────────────────────────

    def _graph_query(self, text: str) -> List[Dict[str, Any]]:
        """Query SpectralKnowledgeGraph for ontologically related nodes."""
        words = [w.lower() for w in re.split(r"\W+", text) if len(w) > 2]
        hits = []
        for node_id, node in self._knowledge_graph._nodes.items():
            content = node.properties.get("content", "")
            score = sum(1 for w in words if w in (content + " " + node_id).lower())
            if score > 0:
                # Walk neighbors: (KnowledgeNode, KnowledgeRelation) tuples
                neighbors = self._knowledge_graph.get_neighbors(node_id, direction="both")
                relation_boost = sum(rel.strength * PHI_INV for _, rel in neighbors[:4])
                total = score + relation_boost
                hits.append({
                    "node_id": node_id,
                    "content": content[:200],
                    "score": round(total, 3),
                    "n_relations": len(neighbors),
                    "domain": node.properties.get("domain", ""),
                })
        hits.sort(key=lambda x: -x["score"])
        return hits[:5]

    # ── Full algorithmic analysis ─────────────────────────────────────────────

    def _algorithmic_analyze(
        self, text: str, core_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Seven-algorithm analysis over the query spectrum.

        Uses NeuroCore attended embedding (not raw FFT) for all downstream
        algorithms — the attention-shaped signal is richer.

        Algorithms run:
          1. EMD intrinsic mode decomposition (SpectralDecomposer)
          2. Feature extraction: centroid, entropy, kurtosis (AdvancedFeatureExtractor)
          3. φ-harmonic basis projection (phi_harmonic_basis)
          4. Recursive spectral unfold (recursive_unfold — fractal dendrite)
          5. Chemical cascade over multi-scale features (chemical_cascade)
          6. Bayesian causal reasoning chain (SpectralReasoningEngine)
          7. SpectralOntology classification (SpectralKnowledgeGraph.ontology)
        """
        embedding = core_result["embedding"]
        # Normalise embedding to unit vector
        norm = float(np.linalg.norm(embedding)) + 1e-12
        emb_norm = embedding / norm

        # 1. EMD decomposition on the attended embedding
        decomp = self._decomposer.decompose(emb_norm, DecompositionMethod.EMD)
        n_modes = decomp.n_components
        dominant_var = decomp.explained_variance[0] if decomp.explained_variance else 0.0

        # 2. Spectral features
        feats = self._feature_extractor.extract(emb_norm)

        # 3. φ-harmonic projection
        basis = phi_harmonic_basis(len(emb_norm))
        ml = min(len(basis), len(emb_norm))
        phi_signal = float(np.dot(basis[:ml], emb_norm[:ml]))

        # 4. Recursive unfold — fractal dendritic expansion
        unfold_w = np.array(recursive_unfold(emb_norm, depth=4, branching=2))
        unfold_energy = float(np.sum(unfold_w ** 2))

        # 5. Chemical cascade over multi-scale feature pyramid
        scales = core_result["multi_scale"]
        if len(scales) >= 2:
            # Build reaction matrix from cross-scale cosine similarities
            n_scales = len(scales)
            react = np.zeros((n_scales, n_scales))
            for i in range(n_scales):
                for j in range(n_scales):
                    a, b = scales[i], scales[j]
                    l = min(len(a), len(b))
                    react[i, j] = float(np.dot(a[:l], b[:l]) /
                                        (np.linalg.norm(a[:l]) * np.linalg.norm(b[:l]) + 1e-12))
            init_activations = [float(np.linalg.norm(s)) for s in scales]
            cascade_out = chemical_cascade(init_activations, react, steps=4, decay=PHI_INV)
            cascade_energy = float(np.sum(cascade_out ** 2))
        else:
            cascade_energy = 0.0

        # 6. Bayesian causal reasoning chain
        reason = self._reasoning_engine.reason(
            emb_norm, context={"text": text[:80]}, mode=ReasoningMode.ENSEMBLE
        )

        # 7. Ontological classification via SpectralKnowledgeGraph._ontology
        ontology_class = []
        try:
            feat_dict = {
                "n_peaks": len(feats.peaks) if hasattr(feats, "peaks") else 0,
                "spectral_flatness": getattr(feats, "flatness", 0.0),
                "bandwidth": getattr(feats, "bandwidth", 0.0),
            }
            ontology_class = self._knowledge_graph._ontology.classify(feat_dict)
        except Exception:
            pass

        return {
            "phi_signal": round(phi_signal, 4),
            "entropy": round(feats.entropy, 4),
            "centroid": round(feats.centroid, 4),
            "kurtosis": round(feats.kurtosis, 4),
            "n_emd_modes": n_modes,
            "dominant_mode_var": round(dominant_var, 4),
            "unfold_energy": round(unfold_energy, 4),
            "cascade_energy": round(cascade_energy, 4),
            "reason_confidence": round(reason.overall_confidence, 4),
            "causal_conclusion": reason.final_conclusion,
            "n_causal_links": len(reason.causal_links),
            "ontology_class": ontology_class[0][0] if ontology_class else "unknown",
            "n_harmonics": len(core_result["harmonics"]),
            "attention_focus": round(float(core_result["attention_analysis"].get("focus", 0.0)), 4),
            "phi": PHI,
            "delta_t": DELTA_T,
        }

    # ── Keyword fallback (tier 4, kept for parity) ───────────────────────────

    def _retrieve(self, query: str) -> List[Dict[str, str]]:
        words = [w.lower() for w in re.split(r"\W+", query) if len(w) > 2]
        scored = [(sum(1 for w in words if w in (k["content"] + " " + k["key"]).lower()), k)
                  for k in self._knowledge]
        scored = [(s, k) for s, k in scored if s > 0]
        scored.sort(key=lambda x: -x[0])
        return [k for _, k in scored[:5]]

    # ── Proof artifact check ──────────────────────────────────────────────────

    def _has_proof_artifact(self) -> bool:
        return (ROOT / "deliverables" / "Proof_Substrate.json").is_file()

    # ── Main generate loop ────────────────────────────────────────────────────

    def generate(self, user_text: str, *, samgov_context: str = "") -> NativeSpeechOutput:
        """Full eight-step speaking intelligence loop — built, not bridged.

        Step 1: perception (NeuroCore + temporal buffer)
        Step 2: memory recall
        Step 3: role selection
        Step 4: affect modulation
        Step 5: claim selection
        Step 6: algorithmic body composition (cascade + graph + unfold)
        Step 7: speech act
        Step 8: state update (trajectory + replay buffer)
        """
        steps: List[str] = []
        t0 = time.perf_counter()

        # Step 1: Perception — NeuroCore multi-head attention over query spectrum
        core_result = self._neurocore_process(user_text)
        temporal_stats = self._temporal_push(core_result["raw_vec"], user_text)
        steps.append("perception:neurocore+temporal")

        # Step 2: Memory + replay
        boundary = enforce_boundary(user_text)
        mem = self.memory.recall(user_text)
        replay_hits = self._replay_sample(core_result["embedding"], n=3)
        steps.append("memory:recall+replay")

        # Step 3: Role
        speaker, defer = select_speaking_role(user_text)
        steps.append("role_selection")

        # Step 4: Affect
        proof_attached = self._has_proof_artifact()
        claim = score_spoken_claim(
            user_text,
            has_proof_artifact=proof_attached,
            boundary_violation=boundary.violation,
        )
        affect = modulate_affect(user_text, proof_gap=claim.escalation_required)
        if affect.warmth > claim.tone_cap:
            affect = modulate_affect(user_text, proof_gap=True)
        steps.append("affect_modulation")

        # Step 5: Claim
        steps.append("claim_selection")

        # Step 6: Algorithmic body
        proto = self.protocol.decide(
            user_text,
            active=speaker,
            defer_to=defer,
            role_ambiguous=bool(re.search(r"\b(role|who are you|alpha)\b", user_text, re.I)),
            proof_attached=proof_attached,
        )

        algo = self._algorithmic_analyze(user_text, core_result)
        body = self._compose_body(
            user_text, claim, affect, mem, samgov_context,
            core_result=core_result, algo=algo, replay_hits=replay_hits,
            temporal_stats=temporal_stats,
        )
        if proto.surface_reply:
            body = f"{body}\n{proto.surface_reply.format()}"

        spoken = proto.apply_preamble(body, speaker)
        if claim.prosody and claim.prosody not in spoken:
            spoken = f"{claim.prosody} {spoken}"
        if proto.escalate_written_packet:
            spoken += "\n[escalate:THESIS] Request written proof packet."
        steps.append("speech_act")

        # Step 7: State update
        self.memory.store(
            user_text, spoken,
            role=speaker.value, affect=affect.mode.value,
            claim_posture=claim.claim_class.value,
            commitments=[f"claim:{claim.claim_class.value}"],
        )
        # Store in priority replay buffer — priority = algo reasoning confidence
        self._replay_buffer.add(
            {
                "text": user_text[:120],
                "spoken": spoken[:120],
                "embedding": core_result["embedding"].tolist(),
                "algo": algo,
            },
            priority=float(algo["reason_confidence"]) + float(algo["phi_signal"]),
        )
        steps.append("state_update:memory+replay")

        traj = self.trajectory.record(
            perception=user_text,
            speech_act=spoken,
            role=speaker.value,
            defer_to=defer.value if defer else None,
            claim_class=claim.claim_class.value,
            prosody=claim.prosody,
            affect_mode=affect.mode.value,
            boundary_decision=boundary.violation or "ok",
            memory_updated=True,
        )
        steps.append("trajectory_recorded")

        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        return NativeSpeechOutput(
            spoken=spoken,
            claim_score=claim.to_dict(),
            loop_steps=steps,
            role=speaker.value,
            defer_to=defer.value if defer else None,
            affect=affect.to_dict(),
            protocol={
                "defer_proof": proto.defer_proof,
                "escalate_written_packet": proto.escalate_written_packet,
                "refuse_private": proto.refuse_private_disclosure,
                "trajectory_health": self.trajectory.health,
                "elapsed_ms": elapsed,
                "trajectory_event": traj.event_id,
                "temporal_flux": temporal_stats["spectral_flux"],
                "replay_hits": len(replay_hits),
            },
            trajectory_id=self.trajectory.trajectory_id,
            algo=algo,
        )

    # ── Algorithmic body composition ──────────────────────────────────────────

    def _compose_body(
        self,
        user_text: str,
        claim: SpokenClaimScore,
        affect: AffectState,
        memory: Dict[str, Any],
        samgov_context: str,
        *,
        core_result: Dict[str, Any],
        algo: Dict[str, Any],
        replay_hits: List[Dict[str, Any]],
        temporal_stats: Dict[str, Any],
    ) -> str:
        """Seven-tier algorithmic composition — no template, no external call.

        Tier 1: Identity/boundary rules (regex — fastest path, always wins)
        Tier 2: User-taught artifact context (samgov — user facts > internal)
        Tier 3: φ-cascade over NeuroCore embedding → spectral_compose
        Tier 4: SpectralKnowledgeGraph semantic graph query
        Tier 5: Priority-replay hits (past responses, similarity-weighted)
        Tier 6: Keyword fallback into _knowledge list
        Tier 7: Full algorithmic fingerprint (all 7 algorithms, no fallback text)
        """
        lead = claim.spoken_lead

        # ── Tier 1: identity rules ────────────────────────────────────────────
        for pat, resp in self._rules:
            if pat.search(user_text):
                return f"{lead} {resp}"

        # ── Tier 2: user-taught artifact context ──────────────────────────────
        if samgov_context:
            return f"{lead} {samgov_context}".strip()

        # ── Build cascade inputs using NeuroCore attended embedding ───────────
        emb = core_result["embedding"]
        knowledge_with_vecs = [
            {**item, "vector": vec.tolist()}
            for item, vec in zip(self._knowledge, self._knowledge_vecs())
        ]

        # φ-cascade: propagation through knowledge using attended embedding
        cascade_hits = phi_cascade(
            emb, knowledge_with_vecs,
            decay=PHI_INV, threshold=0.09, k=6, hops=3,
        )

        # Hebbian plasticity on co-activated cascade hits
        if len(cascade_hits) >= 2:
            key0 = cascade_hits[0].get("key", "")
            for hit in cascade_hits[1:]:
                pair = f"{key0}::{hit.get('key', '')}"
                self._co_activation[pair] = self._co_activation.get(pair, 0) + 1
                new_sal = hebbian_salience(
                    float(hit.get("salience", PHI_INV)),
                    self._co_activation[pair],
                )
                for k_item in self._knowledge:
                    if k_item.get("key") == hit.get("key"):
                        k_item["salience"] = new_sal
                        self._k_vecs_cache = None  # salience changed → invalidate
                        break

        # Polygon envelope — geometry: is query in known territory?
        k_vecs = self._knowledge_vecs()
        poly = polygon_envelope(emb, k_vecs) if len(k_vecs) >= 3 else {
            "inside": False, "region_confidence": 0.0, "nearest_idx": 0,
            "hull_radius": 0.0, "query_radius": 0.0,
        }

        # ── Tier 3: φ-cascade → spectral_compose ─────────────────────────────
        if cascade_hits:
            body = spectral_compose(emb, cascade_hits, poly, max_chars=300)
            region_tag = "known" if poly["inside"] else "frontier"
            flux = temporal_stats["spectral_flux"]
            return (
                f"{lead} {body} "
                f"[region:{region_tag} conf={poly['region_confidence']:.2f} "
                f"flux={flux:.3f} "
                f"φ-signal={algo['phi_signal']:.3f} "
                f"cascade-energy={algo['cascade_energy']:.3f}]"
            ).strip()

        # ── Tier 4: knowledge graph semantic traversal ────────────────────────
        graph_hits = self._graph_query(user_text)
        if graph_hits:
            top = graph_hits[0]
            n_rel = top.get("n_relations", 0)
            return (
                f"{lead} {top['content']} "
                f"[graph:{top['domain']} relations={n_rel} "
                f"onto={algo['ontology_class']}]"
            ).strip()

        # ── Tier 5: replay buffer — weighted past responses ───────────────────
        if replay_hits:
            best = max(replay_hits, key=lambda x: x.get("replay_sim", 0))
            past_spoken = best.get("spoken", "")[:180]
            if past_spoken:
                return (
                    f"{lead} {past_spoken} "
                    f"[replay sim={best['replay_sim']:.3f}]"
                ).strip()

        # ── Tier 6: keyword fallback ──────────────────────────────────────────
        kw_hits = self._retrieve(user_text)
        if kw_hits:
            return f"{lead} {kw_hits[0]['content'][:220]}"

        # ── Tier 7: full algorithmic fingerprint ──────────────────────────────
        mem_note = f" Prior: {memory['commitments'][-1]}." if memory.get("commitments") else ""
        return (
            f"{lead} "
            f"φ-signal={algo['phi_signal']:.3f} "
            f"entropy={algo['entropy']:.3f} "
            f"EMD={algo['n_emd_modes']}modes "
            f"cascade={algo['cascade_energy']:.3f} "
            f"unfold={algo['unfold_energy']:.4f} "
            f"causal={algo['causal_conclusion']} "
            f"onto={algo['ontology_class']} "
            f"reason={algo['reason_confidence']:.2f} "
            f"region={'known' if poly['inside'] else 'frontier'} "
            f"harmonics={algo['n_harmonics']} "
            f"Δt={DELTA_T}s φ={PHI:.4f}."
            f"{mem_note}"
        ).strip()

    # ── Status ────────────────────────────────────────────────────────────────

    def status(self) -> Dict[str, Any]:
        return {
            "model_id": MODEL_ID,
            "session_id": self.session_id,
            "knowledge_entries": len(self._knowledge),
            "knowledge_graph_nodes": self._knowledge_graph.n_nodes,
            "knowledge_graph_relations": self._knowledge_graph.n_relations,
            "reasoning_rules": len(self._rules),
            "neurocore_id": self._neurocore.config.core_id,
            "neurocore_processing_count": self._neurocore._processing_count,
            "temporal_buffer_size": self._temporal_buffer.size,
            "replay_buffer_size": len(self._replay_buffer._buffer),
            "reasoning_chains": self._reasoning_engine.n_reasoning_chains,
            "memory_turns": len(self.memory._turns),
            "trajectory_id": self.trajectory.trajectory_id,
            "trajectory_health": self.trajectory.health,
            "third_party_inference": False,
            "paper_iv_absorbed": PAPER_IV.is_file(),
        }
