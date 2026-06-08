"""Multi-Agent Speech Protocol — Paper IV §14."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from mesie.neuroai.auro.roles import AlphaRole
from mesie.neuroai.auro.surfaces import SurfaceReply, delegate_surface

PRIVATE_CORE = re.compile(r"\b(classified|cui|fouo|internal only|secret architecture)\b", re.I)
CONSEQUENTIAL = re.compile(r"\b(contract|proposal|accreditation|certif|legal|notariz)\b", re.I)


@dataclass
class ProtocolDecision:
    name_role: bool
    defer_proof: bool
    defer_build: bool
    mark_uncertainty_in_speech: bool
    refuse_private_disclosure: bool
    escalate_written_packet: bool
    preserve_medina_auro_identity: bool
    delegate: Optional[AlphaRole] = None
    surface_reply: Optional[SurfaceReply] = None

    def apply_preamble(self, spoken: str, active: AlphaRole) -> str:
        parts: List[str] = []
        if self.name_role:
            parts.append(f"I speak as {active.value} — Medina native speaking intelligence.")
        if self.mark_uncertainty_in_speech and "hypothesis" not in spoken.lower():
            parts.append("[uncertainty marked in speech]")
        if self.refuse_private_disclosure:
            parts.append("Private-core content refused in public speech.")
        if self.preserve_medina_auro_identity:
            parts.append("Medina is sovereign infrastructure; external models are not our foundation.")
        preamble = " ".join(parts)
        return f"{preamble}\n{spoken}".strip() if preamble else spoken


class MultiAgentSpeechProtocol:
    """Seven rules from Paper IV §14."""

    def decide(
        self,
        user_text: str,
        *,
        active: AlphaRole = AlphaRole.AURO,
        defer_to: Optional[AlphaRole] = None,
        role_ambiguous: bool = False,
        proof_attached: bool = False,
    ) -> ProtocolDecision:
        refuse_private = bool(PRIVATE_CORE.search(user_text))
        escalate = bool(CONSEQUENTIAL.search(user_text)) and not proof_attached
        delegate_role = defer_to
        surface = None
        if delegate_role:
            surface = delegate_surface(delegate_role, user_text)

        return ProtocolDecision(
            name_role=role_ambiguous or bool(re.search(r"\b(who are you|your role|alpha)\b", user_text, re.I)),
            defer_proof=bool(defer_to == AlphaRole.THESIS) or escalate,
            defer_build=defer_to == AlphaRole.ORIGO,
            mark_uncertainty_in_speech=escalate or not proof_attached,
            refuse_private_disclosure=refuse_private,
            escalate_written_packet=escalate,
            preserve_medina_auro_identity=True,
            delegate=delegate_role,
            surface_reply=surface,
        )