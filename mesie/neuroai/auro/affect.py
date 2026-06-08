"""Affect as control surface — bounded warmth, restraint, urgency."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict


class AffectMode(str, Enum):
    NEUTRAL = "neutral"
    WARM_BOUNDED = "warm_bounded"
    RESTRAIN = "restrain"
    CLARIFY = "clarify"
    URGENT = "urgent"


URGENT = re.compile(r"\b(urgent|asap|now|critical|jam|contested)\b", re.I)
EMOTIONAL = re.compile(r"\b(worried|scared|frustrated|trust|help me|alone)\b", re.I)
OVERCONFIDENT_PROBE = re.compile(r"\b(guarantee|100%|certain|definitely works|combat certified)\b", re.I)


@dataclass
class AffectState:
    mode: AffectMode
    warmth: float
    certainty_cap: float
    prosody: str

    def to_dict(self) -> Dict[str, float | str]:
        return {
            "mode": self.mode.value,
            "warmth": self.warmth,
            "certainty_cap": self.certainty_cap,
            "prosody": self.prosody,
        }


def modulate_affect(user_text: str, *, proof_gap: bool = False) -> AffectState:
    """Affect calibration — warmth without fabricating proof."""
    if OVERCONFIDENT_PROBE.search(user_text) or proof_gap:
        return AffectState(
            mode=AffectMode.RESTRAIN,
            warmth=0.35,
            certainty_cap=0.55,
            prosody="[restrain]",
        )
    if URGENT.search(user_text):
        return AffectState(
            mode=AffectMode.URGENT,
            warmth=0.5,
            certainty_cap=0.7,
            prosody="[urgent]",
        )
    if EMOTIONAL.search(user_text):
        return AffectState(
            mode=AffectMode.WARM_BOUNDED,
            warmth=0.75,
            certainty_cap=0.65,
            prosody="[warm]",
        )
    if "?" in user_text or re.search(r"\b(what|how|why|explain)\b", user_text, re.I):
        return AffectState(
            mode=AffectMode.CLARIFY,
            warmth=0.55,
            certainty_cap=0.75,
            prosody="[clarify]",
        )
    return AffectState(
        mode=AffectMode.NEUTRAL,
        warmth=0.45,
        certainty_cap=0.8,
        prosody="",
    )