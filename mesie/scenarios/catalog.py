"""Load military and enterprise scenario catalogs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

SCENARIOS_DIR = Path(__file__).resolve().parents[2] / "data" / "scenarios"


def load_catalog(name: str) -> Dict[str, Any]:
    path = SCENARIOS_DIR / f"{name}.json"
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def military_scenarios() -> List[Dict[str, Any]]:
    return load_catalog("military_drone_scenarios")["scenarios"]


def enterprise_scenarios() -> List[Dict[str, Any]]:
    return load_catalog("enterprise_civilian_scenarios")["scenarios"]