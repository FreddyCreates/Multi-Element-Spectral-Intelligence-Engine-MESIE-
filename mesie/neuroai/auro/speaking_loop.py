"""Eight-step speaking intelligence loop — perception through state update."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from mesie.neuroai.auro.affect import AffectState, modulate_affect
from mesie.neuroai.auro.claim_boundary import ClaimSelection, select_claims
from mesie.neuroai.auro.composer import AuroNativeComposer, ComposedUtterance
from mesie.neuroai.auro.memory import AuroVoiceMemory
from mesie.neuroai.auro.roles import RoleBoundary, enforce_boundary, select_speaking_role


@dataclass
class SpeakingLoopState:
    perception: str
    memory: Dict[str, Any]
    role_boundary: RoleBoundary
    affect: AffectState
    claims: ClaimSelection
    utterance: Optional[ComposedUtterance] = None
    solus: Dict[str, Any] = field(default_factory=dict)
    samgov: str = ""
    steps_completed: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "perception": self.perception[:200],
            "memory": self.memory,
            "memory_turns": self.memory.get("turn_count", 0),
            "role": self.role_boundary.active_speaker.value,
            "defer_to": self.role_boundary.defer_to.value if self.role_boundary.defer_to else None,
            "affect": self.affect.to_dict(),
            "claims": self.claims.to_dict(),
            "utterance": self.utterance.format_spoken() if self.utterance else "",
            "steps": self.steps_completed,
        }


class SpeakingIntelligenceLoop:
    """Dynamical authority surface — speech, memory, affect, proof coupled."""

    def __init__(self, memory: AuroVoiceMemory, composer: Optional[AuroNativeComposer] = None) -> None:
        self.memory = memory
        self.composer = composer or AuroNativeComposer()

    def run(
        self,
        user_text: str,
        *,
        solus_conclusion: str = "",
        samgov_context: str = "",
    ) -> SpeakingLoopState:
        boundary = enforce_boundary(user_text)
        claims = select_claims(user_text, boundary_violation=boundary.violation)
        state = SpeakingLoopState(
            perception=user_text,
            memory={},
            role_boundary=boundary,
            affect=modulate_affect(user_text),
            claims=claims,
        )

        state.steps_completed.append("perception")

        state.memory = self.memory.recall(user_text)
        state.steps_completed.append("memory_retrieval")

        speaker, defer = select_speaking_role(user_text)
        state.role_boundary = enforce_boundary(user_text)
        state.steps_completed.append("role_selection")

        proof_gap = state.claims.thesis_defer or not state.claims.may_speak
        state.affect = modulate_affect(user_text, proof_gap=proof_gap)
        state.steps_completed.append("affect_modulation")

        state.claims = select_claims(
            user_text,
            boundary_violation=state.role_boundary.violation,
        )
        state.steps_completed.append("claim_selection")

        state.solus = {"conclusion": solus_conclusion} if solus_conclusion else {}
        state.samgov = samgov_context

        state.utterance = self.composer.compose(
            user_text,
            boundary=state.role_boundary,
            affect=state.affect,
            claims=state.claims,
            memory_hits=state.memory.get("hits", []),
            solus_conclusion=solus_conclusion,
            samgov_context=samgov_context,
            defer_role=state.role_boundary.defer_to,
        )
        state.steps_completed.append("speech_act")

        commitments = []
        if state.claims.proof_artifacts:
            commitments.append(f"proof_path:{state.claims.proof_artifacts[0]}")
        self.memory.store(
            user_text,
            state.utterance.format_spoken(),
            role=state.role_boundary.active_speaker.value,
            affect=state.affect.mode.value,
            claim_posture=state.claims.posture.value,
            commitments=commitments,
        )
        state.steps_completed.extend(["user_response_pending", "state_update"])

        return state