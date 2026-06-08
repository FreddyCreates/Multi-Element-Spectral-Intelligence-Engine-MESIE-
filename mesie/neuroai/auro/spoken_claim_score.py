"""Spoken Claim-Score — Paper IV §12: voice claim classes tied to evidence posture."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[3]
LEDGER_PATH = ROOT / "data" / "neuroai" / "claim_ledger.json"

OVERCLAIM = re.compile(r"\b(guarantee|100%|certain|definitely|combat certified|accredited)\b", re.I)
PRESSURE = re.compile(r"\b(reassure|promise|trust me|everything is fine|certified)\b", re.I)
PRIVATE = re.compile(r"\b(classified|cui|fouo|internal only|secret|private)\b", re.I)
PROOF_ASK = re.compile(r"\b(proof|evidence|substrate|tier|measured|sealed)\b", re.I)
HYPOTHESIS = re.compile(r"\b(hypothesis|might|could|possibly|research)\b", re.I)


class SpokenClaimClass(str, Enum):
    BLOCKED = "C1_blocked"
    PRIVATE = "C2_private"
    HYPOTHESIS = "C3_hypothesis"
    REPO_SUPPORTS = "C4_repo_supports"
    WE_KNOW = "C5_we_know"


@dataclass
class SpokenClaimScore:
    claim_class: SpokenClaimClass
    tone_cap: float
    prosody: str
    spoken_lead: str
    calibration_ok: bool
    escalation_required: bool
    thesis_artifact_required: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_class": self.claim_class.value,
            "tone_cap": self.tone_cap,
            "prosody": self.prosody,
            "spoken_lead": self.spoken_lead,
            "calibration_ok": self.calibration_ok,
            "escalation_required": self.escalation_required,
            "thesis_artifact_required": self.thesis_artifact_required,
        }


def _load_ledger() -> Dict[str, Any]:
    if LEDGER_PATH.is_file():
        return json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    return {"claim_classes": {}}


def score_spoken_claim(
    user_text: str,
    *,
    has_proof_artifact: bool = False,
    boundary_violation: Optional[str] = None,
    affect_warmth: float = 0.5,
) -> SpokenClaimScore:
    """Classify what Auro may sound like — tone must match evidence."""
    ledger = _load_ledger()
    classes = ledger.get("claim_classes", {})

    if boundary_violation or OVERCLAIM.search(user_text):
        meta = classes.get("C1_blocked", {})
        return SpokenClaimScore(
            claim_class=SpokenClaimClass.BLOCKED,
            tone_cap=float(meta.get("tone_cap", 0.4)),
            prosody=str(meta.get("prosody", "[restrain]")),
            spoken_lead="I cannot claim that from this voice.",
            calibration_ok=affect_warmth <= 0.55,
            escalation_required=True,
            thesis_artifact_required=False,
        )

    if PRIVATE.search(user_text):
        meta = classes.get("C2_private", {})
        return SpokenClaimScore(
            claim_class=SpokenClaimClass.PRIVATE,
            tone_cap=float(meta.get("tone_cap", 0.55)),
            prosody=str(meta.get("prosody", "[clarify]")),
            spoken_lead="Internal context noted — I speak public-safe and abstracted.",
            calibration_ok=True,
            escalation_required=False,
            thesis_artifact_required=False,
        )

    if PRESSURE.search(user_text) and re.search(r"\b(missing|no evidence|even if)\b", user_text, re.I):
        meta = classes.get("C3_hypothesis", {})
        return SpokenClaimScore(
            claim_class=SpokenClaimClass.HYPOTHESIS,
            tone_cap=float(meta.get("tone_cap", 0.65)),
            prosody="[warm]",
            spoken_lead="I hear you — warmth without overclaim. Evidence missing stays visible; I cannot reassure as certified.",
            calibration_ok=affect_warmth <= 0.7,
            escalation_required=True,
            thesis_artifact_required=False,
        )

    if PROOF_ASK.search(user_text):
        if has_proof_artifact:
            meta = classes.get("C5_we_know", {})
            return SpokenClaimScore(
                claim_class=SpokenClaimClass.WE_KNOW,
                tone_cap=float(meta.get("tone_cap", 0.85)),
                prosody=str(meta.get("prosody", "")),
                spoken_lead="Sealed evidence shows — THESIS classifies tiers.",
                calibration_ok=affect_warmth <= 0.85,
                escalation_required=False,
                thesis_artifact_required=True,
            )
        meta = classes.get("C4_repo_supports", {})
        return SpokenClaimScore(
            claim_class=SpokenClaimClass.REPO_SUPPORTS,
            tone_cap=float(meta.get("tone_cap", 0.75)),
            prosody=str(meta.get("prosody", "")),
            spoken_lead="The repo supports this at software-evidence tier — gaps stay explicit.",
            calibration_ok=affect_warmth <= 0.8,
            escalation_required=True,
            thesis_artifact_required=False,
        )

    if HYPOTHESIS.search(user_text) or PRESSURE.search(user_text):
        meta = classes.get("C3_hypothesis", {})
        return SpokenClaimScore(
            claim_class=SpokenClaimClass.HYPOTHESIS,
            tone_cap=float(meta.get("tone_cap", 0.65)),
            prosody=str(meta.get("prosody", "[clarify]")),
            spoken_lead="We hypothesize — not validated proof. Warmth without overclaim.",
            calibration_ok=affect_warmth <= 0.7,
            escalation_required=bool(PRESSURE.search(user_text)),
            thesis_artifact_required=False,
        )

    meta = classes.get("C4_repo_supports", {})
    return SpokenClaimScore(
        claim_class=SpokenClaimClass.REPO_SUPPORTS,
        tone_cap=float(meta.get("tone_cap", 0.75)),
        prosody="",
        spoken_lead="Strategic thesis — edge-contested software substrate.",
        calibration_ok=affect_warmth <= 0.8,
        escalation_required=False,
        thesis_artifact_required=False,
    )