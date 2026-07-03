"""Reality Engine stack — front · middle intelligence · back compute."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from mesie.design.languages import CANONICAL_LANGUAGES


@dataclass(frozen=True)
class RealityLayer:
    layer_id: str
    title: str
    responsibility: str
    surfaces: tuple[str, ...]


FRONT_LAYER = RealityLayer(
    "front",
    "Front Reality Surfaces",
    "HTML/CSS/JS/3D/XR — 100+ paradigm stacks as live intelligence agents",
    (
        "websites/reality-engine/index.html",
        "websites/enterprise-4k/index.html",
        "websites/computing-family/index.html",
        "templates/surfaces/",
    ),
)

MIDDLE_LAYER = RealityLayer(
    "middle",
    "Middle Intelligence",
    "ST-φ encode, SOLUS formal stack, design orchestrator, federation envelopes",
    (
        "mesie/design/orchestrator.py",
        "mesie/design/reality_engine.py",
        "mesie/compute/hub.py",
        "mesie/enterprise/federation/orchestrator.py",
    ),
)

BACK_LAYER = RealityLayer(
    "back",
    "Back Compute & Proof",
    "Virtual processor :8750, polyglot suite, depth pillars, receipt chain",
    (
        "mesie/processor/server.py",
        "mesie/polyglot/suite.py",
        "mesie/depth/envelope_router.py",
        "mesie/enterprise/receipt_chain.py",
    ),
)


def reality_stack_manifest() -> Dict[str, Any]:
    return {
        "protocol": "MESIE-REALITY-STACK/1.0",
        "layers": [
            {
                "layer_id": FRONT_LAYER.layer_id,
                "title": FRONT_LAYER.title,
                "responsibility": FRONT_LAYER.responsibility,
                "surfaces": list(FRONT_LAYER.surfaces),
            },
            {
                "layer_id": MIDDLE_LAYER.layer_id,
                "title": MIDDLE_LAYER.title,
                "responsibility": MIDDLE_LAYER.responsibility,
                "surfaces": list(MIDDLE_LAYER.surfaces),
            },
            {
                "layer_id": BACK_LAYER.layer_id,
                "title": BACK_LAYER.title,
                "responsibility": BACK_LAYER.responsibility,
                "surfaces": list(BACK_LAYER.surfaces),
            },
        ],
        "flow": "brief → middle encode → core agents (20 langs) → back invoke → receipt → front render",
        "language_count_per_core": 20,
        "canonical_languages": [lang.language_id for lang in CANONICAL_LANGUAGES],
    }
