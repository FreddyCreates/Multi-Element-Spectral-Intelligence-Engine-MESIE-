"""Evidence tiers — what we can honestly claim vs Grok/X critique."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict


class EvidenceTier(str, Enum):
    MEASURED_LOCAL = "measured_local"
    SIMULATED_VALIDATED = "simulated_validated"
    DOCUMENTED_REFERENCE = "documented_reference"
    ASSERTION_ONLY = "assertion_only"
    GAP = "gap"


TIER_LABELS = {
    EvidenceTier.MEASURED_LOCAL: "Measured on this machine (reproducible harness)",
    EvidenceTier.SIMULATED_VALIDATED: "Software simulation validated (not physical HIL)",
    EvidenceTier.DOCUMENTED_REFERENCE: "Bundled ITU/IEEE/NATO reference data (not live classified)",
    EvidenceTier.ASSERTION_ONLY: "Marketing claim without independent corroboration",
    EvidenceTier.GAP: "Known gap — not proven",
}


def tier_summary(tier: EvidenceTier) -> str:
    return TIER_LABELS.get(tier, tier.value)


def public_answer_for_tier(tier: EvidenceTier) -> str:
    if tier == EvidenceTier.MEASURED_LOCAL:
        return "Partially true — locally measured and reproducible; not independently audited."
    if tier == EvidenceTier.SIMULATED_VALIDATED:
        return "True in simulation — software runs correctly; not proven on physical assets."
    if tier == EvidenceTier.DOCUMENTED_REFERENCE:
        return "Reference-backed — uses public band/orbital data; not operational intelligence."
    if tier == EvidenceTier.GAP:
        return "Not proven publicly — gap acknowledged."
    return "Unverified assertion — treat as claim until externally corroborated."