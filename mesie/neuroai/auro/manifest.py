"""Auro manifest — Alpha-family roles, packet ID, claim posture (Paper IV)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "data" / "neuroai" / "auro_manifest.json"
LEXICON_PATH = ROOT / "data" / "neuroai" / "auro_lexicon.json"

AURO_PACKET_ID = "NEUROAI-REPO-CERN-EXPANDED-20260601"
AURO_EDITION = "auro-native-v1"


@lru_cache(maxsize=1)
def load_auro_manifest() -> Dict[str, Any]:
    if MANIFEST_PATH.is_file():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {
        "packet_id": AURO_PACKET_ID,
        "blocked_claims": ["sentient", "conscious", "clinically validated"],
        "alpha_family": {},
    }


@lru_cache(maxsize=1)
def load_auro_lexicon() -> Dict[str, Any]:
    if LEXICON_PATH.is_file():
        return json.loads(LEXICON_PATH.read_text(encoding="utf-8"))
    return {"posture_phrases": {}, "prosody_markers": {}}