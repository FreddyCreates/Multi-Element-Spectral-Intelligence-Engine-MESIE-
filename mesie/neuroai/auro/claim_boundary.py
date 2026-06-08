"""Claim selection — proof posture, THESIS deferral, public-safe speech."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from mesie.neuroai.auro.manifest import load_auro_manifest


class ClaimPosture(str, Enum):
    C3_HYPOTHESIS = "C3_hypothesis"
    C4_STRATEGIC = "C4_strategic"
    BLOCKED = "blocked"
    DEFER_THESIS = "defer_thesis"
    SAMGOV_CONTRACTOR = "samgov_contractor"
    ROLE_GUARD = "role_guard"


PRIVATE_MARKERS = re.compile(
    r"\b(classified|cui|fouo|internal only|not for release|private key|secret)\b",
    re.I,
)
PROOF_REQUEST = re.compile(
    r"\b(prove|evidence|substrate|readiness|audit|measured|tier)\b",
    re.I,
)
SAMGOV_REQUEST = re.compile(r"\b(sam\.gov|gsa|contractor|opportunit|proposal|naics)\b", re.I)


@dataclass
class ClaimSelection:
    posture: ClaimPosture
    may_speak: bool
    thesis_defer: bool
    abstract_private: bool
    honest_limit: str
    proof_artifacts: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "posture": self.posture.value,
            "may_speak": self.may_speak,
            "thesis_defer": self.thesis_defer,
            "abstract_private": self.abstract_private,
            "honest_limit": self.honest_limit,
            "proof_artifacts": self.proof_artifacts,
        }


def select_claims(user_text: str, *, boundary_violation: Optional[str] = None) -> ClaimSelection:
    manifest = load_auro_manifest()
    blocked = manifest.get("blocked_claims", [])
    low = user_text.lower()

    if boundary_violation:
        return ClaimSelection(
            posture=ClaimPosture.BLOCKED,
            may_speak=False,
            thesis_defer=True,
            abstract_private=False,
            honest_limit="Blocked claim — Auro research surface only.",
            proof_artifacts=[],
        )

    for term in blocked:
        t = term.replace("_", " ")
        if t in low or term in low:
            return ClaimSelection(
                posture=ClaimPosture.BLOCKED,
                may_speak=False,
                thesis_defer=True,
                abstract_private=False,
                honest_limit=f"Blocked: {term}",
                proof_artifacts=[],
            )

    abstract = bool(PRIVATE_MARKERS.search(user_text))
    if PROOF_REQUEST.search(user_text):
        return ClaimSelection(
            posture=ClaimPosture.DEFER_THESIS,
            may_speak=True,
            thesis_defer=True,
            abstract_private=abstract,
            honest_limit="Software evidence tiers — not DoD accreditation.",
            proof_artifacts=[
                "deliverables/Proof_Substrate.json",
                "deliverables/neuroswarmai_com/evidence_manifest.json",
            ],
        )

    if SAMGOV_REQUEST.search(user_text):
        return ClaimSelection(
            posture=ClaimPosture.SAMGOV_CONTRACTOR,
            may_speak=True,
            thesis_defer=False,
            abstract_private=abstract,
            honest_limit="Bundled SAM refs — SAM_API_KEY for live pull.",
            proof_artifacts=["deliverables/MESIE_SamGov_Contractor_Edition.json"],
        )

    if re.search(r"\b(you are|who are you|your role|alpha.?family|auro|medina)\b", low):
        return ClaimSelection(
            posture=ClaimPosture.ROLE_GUARD,
            may_speak=True,
            thesis_defer=False,
            abstract_private=False,
            honest_limit="Alpha-family role separation enforced.",
            proof_artifacts=[],
        )

    return ClaimSelection(
        posture=ClaimPosture.C4_STRATEGIC,
        may_speak=True,
        thesis_defer=False,
        abstract_private=abstract,
        honest_limit="partially_true_software_substrate",
        proof_artifacts=[],
    )