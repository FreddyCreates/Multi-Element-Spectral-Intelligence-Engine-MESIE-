"""AuroNativeLanguageModel — Medina native speaking intelligence built per Paper IV.

Not third-party inference. Dynamical authority surface: memory, affect, proof, voice.
"""

from __future__ import annotations

import hashlib
import re
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.neuroai.auro.affect import AffectState, modulate_affect
from mesie.neuroai.auro.memory import AuroVoiceMemory
from mesie.neuroai.auro.multi_agent_protocol import MultiAgentSpeechProtocol
from mesie.neuroai.auro.roles import AlphaRole, enforce_boundary, select_speaking_role
from mesie.neuroai.auro.spoken_claim_score import SpokenClaimScore, score_spoken_claim
from mesie.neuroai.auro.surfaces import load_family_manifest
from mesie.neuroai.auro.trajectory import SpokenTrajectory
from mesie.sdk.solus import SDKSolusOrganism

ROOT = Path(__file__).resolve().parents[3]
PAPER_IV = ROOT / "data" / "neuroai" / "substrate" / "p4-auro-dynamics-speaking-intelligence.md"

MODEL_ID = "AuroNativeLM-v1"
PHI = 1.618033988749895


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
            "native_model": self.native_model,
            "sovereign": self.sovereign,
        }


@dataclass
class AuroNativeLanguageModel:
    """Built native LM — eight-step loop, spoken claim-score, multi-agent protocol."""

    session_id: str
    memory: AuroVoiceMemory = field(default_factory=lambda: AuroVoiceMemory("auro"))
    trajectory: SpokenTrajectory = field(default_factory=lambda: SpokenTrajectory("auro", "pending"))
    organism: SDKSolusOrganism = field(default_factory=SDKSolusOrganism)
    protocol: MultiAgentSpeechProtocol = field(default_factory=MultiAgentSpeechProtocol)
    _knowledge: List[Dict[str, str]] = field(default_factory=list, init=False)
    _rules: List[tuple[re.Pattern[str], str]] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.memory.session_id = self.session_id
        self.trajectory = SpokenTrajectory(
            session_id=self.session_id,
            trajectory_id=f"traj_{uuid.uuid4().hex[:12]}",
        )
        self._bootstrap_knowledge()
        self._bootstrap_rules()

    def _bootstrap_knowledge(self) -> None:
        family = load_family_manifest()
        for name, spec in family.get("members", {}).items():
            self._knowledge.append({
                "key": name.lower(),
                "domain": "alpha_family",
                "content": f"{name}: {spec.get('role', '')}",
            })
        for line in family.get("blocked_claims", []):
            self._knowledge.append({"key": "blocked", "domain": "boundary", "content": f"blocked: {line}"})

        if PAPER_IV.is_file():
            text = PAPER_IV.read_text(encoding="utf-8", errors="replace")
            for i, chunk in enumerate(self._chunk_paper(text)):
                self._knowledge.append({
                    "key": f"paper_iv_{i}",
                    "domain": "paper",
                    "content": chunk[:900],
                })

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

    def _solus_analyze(self, text: str) -> Dict[str, Any]:
        sig = [float(ord(c) % 97) for c in text[:96]]
        while len(sig) < 8:
            sig.append(1.0)
        analysis = self.organism.analyze_spectrum(list(range(len(sig))), sig)
        logic = self.organism.logic_action(
            "prove",
            theorem="auro_speaking: bounded voice preserves proof posture across time",
        )
        return {
            "signal_ratio": analysis.get("xray", {}).get("signal_ratio", 0.0),
            "logic_confidence": logic.brain.get("confidence", 0.0),
            "phi": PHI,
        }

    def _retrieve(self, query: str) -> List[Dict[str, str]]:
        words = [w.lower() for w in re.split(r"\W+", query) if len(w) > 2]
        scored = []
        for k in self._knowledge:
            blob = (k["content"] + " " + k["key"]).lower()
            hit = sum(1 for w in words if w in blob)
            if hit:
                scored.append((hit, k))
        scored.sort(key=lambda x: -x[0])
        return [k for _, k in scored[:5]]

    def _has_proof_artifact(self) -> bool:
        proof = ROOT / "deliverables" / "Proof_Substrate.json"
        return proof.is_file()

    def generate(self, user_text: str, *, samgov_context: str = "") -> NativeSpeechOutput:
        """Full eight-step speaking intelligence loop — built, not bridged."""
        steps: List[str] = []
        t0 = time.perf_counter()

        steps.append("perception")
        boundary = enforce_boundary(user_text)
        mem = self.memory.recall(user_text)
        steps.append("memory_retrieval")

        speaker, defer = select_speaking_role(user_text)
        steps.append("role_selection")

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
        steps.append("claim_selection")

        proto = self.protocol.decide(
            user_text,
            active=speaker,
            defer_to=defer,
            role_ambiguous=bool(re.search(r"\b(role|who are you|alpha)\b", user_text, re.I)),
            proof_attached=proof_attached,
        )

        body = self._compose_body(user_text, claim, affect, mem, samgov_context)
        if proto.surface_reply:
            body = f"{body}\n{proto.surface_reply.format()}"

        spoken = proto.apply_preamble(body, speaker)
        if claim.prosody and claim.prosody not in spoken:
            spoken = f"{claim.prosody} {spoken}"

        if proto.escalate_written_packet:
            spoken += "\n[escalate:THESIS] Request written proof packet — Invoke-MESIEProofSubstrate."

        steps.append("speech_act")

        self.memory.store(
            user_text,
            spoken,
            role=speaker.value,
            affect=affect.mode.value,
            claim_posture=claim.claim_class.value,
            commitments=[f"claim:{claim.claim_class.value}"],
        )
        steps.append("state_update")

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
                "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2),
                "trajectory_event": traj.event_id,
            },
            trajectory_id=self.trajectory.trajectory_id,
        )

    def _compose_body(
        self,
        user_text: str,
        claim: SpokenClaimScore,
        affect: AffectState,
        memory: Dict[str, Any],
        samgov_context: str,
    ) -> str:
        for pat, resp in self._rules:
            if pat.search(user_text):
                return f"{claim.spoken_lead} {resp}"

        hits = self._retrieve(user_text)
        if hits:
            excerpt = hits[0]["content"][:200]
            return f"{claim.spoken_lead} {excerpt}"

        solus = self._solus_analyze(user_text)
        mem_note = ""
        if memory.get("commitments"):
            mem_note = f" Prior commitments: {memory['commitments'][-1]}."
        sam = f" {samgov_context}." if samgov_context else ""

        return (
            f"{claim.spoken_lead} "
            f"SOLUS native reasoning — signal={solus['signal_ratio']:.3f}, "
            f"logic_conf={solus['logic_confidence']:.3f}, φ={solus['phi']:.4f}."
            f"{mem_note}{sam}"
        ).strip()

    def status(self) -> Dict[str, Any]:
        return {
            "model_id": MODEL_ID,
            "session_id": self.session_id,
            "knowledge_entries": len(self._knowledge),
            "reasoning_rules": len(self._rules),
            "memory_turns": len(self.memory._turns),
            "trajectory_id": self.trajectory.trajectory_id,
            "trajectory_health": self.trajectory.health,
            "third_party_inference": False,
            "paper_iv_absorbed": PAPER_IV.is_file(),
        }