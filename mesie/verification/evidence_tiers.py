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
    EvidenceTier.MEASURED_LOCAL: (
        "Measured on edge deployment class — reproducible harness on issued field/lab hardware"
    ),
    EvidenceTier.SIMULATED_VALIDATED: (
        "Software simulation validated on sovereign stack (not physical range HIL yet)"
    ),
    EvidenceTier.DOCUMENTED_REFERENCE: (
        "Bundled ITU/IEEE/NATO reference data (not live classified feeds)"
    ),
    EvidenceTier.ASSERTION_ONLY: "Marketing claim without program-level corroboration",
    EvidenceTier.GAP: "Named gap — specific physical asset or audit not yet demonstrated",
}


def tier_summary(tier: EvidenceTier) -> str:
    return TIER_LABELS.get(tier, tier.value)


def public_answer_for_tier(tier: EvidenceTier) -> str:
    if tier == EvidenceTier.MEASURED_LOCAL:
        return (
            "Measured on edge-class hardware — reproducible in your lab or on program site; "
            "third-party audit is a separate tier, not a fake/dev dichotomy."
        )
    if tier == EvidenceTier.SIMULATED_VALIDATED:
        return "True in simulation — software runs correctly; not proven on physical assets."
    if tier == EvidenceTier.DOCUMENTED_REFERENCE:
        return "Reference-backed — uses public band/orbital data; not operational intelligence."
    if tier == EvidenceTier.GAP:
        return "Not proven publicly — gap acknowledged."
    return "Unverified assertion — treat as claim until externally corroborated."