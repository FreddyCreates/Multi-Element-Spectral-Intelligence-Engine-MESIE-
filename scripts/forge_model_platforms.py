#!/usr/bin/env python3
"""Forge model platform manifests — registry, bridge, unified catalog."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables" / "platform"


def main() -> int:
    from mesie.platform.model_catalog import build_unified_model_catalog
    from mesie.platform.mvp_bridge import bridge_manifest
    from mesie.platform.registry import platform_manifest

    OUT.mkdir(parents=True, exist_ok=True)

    catalog = build_unified_model_catalog()
    platform = platform_manifest()
    bridge = bridge_manifest()

    (OUT / "UNIFIED_MODEL_CATALOG.json").write_text(
        json.dumps(catalog, indent=2) + "\n", encoding="utf-8"
    )
    (OUT / "PLATFORM_REGISTRY.json").write_text(
        json.dumps(platform, indent=2) + "\n", encoding="utf-8"
    )
    (OUT / "MVP_PROTOCOL_BRIDGE.json").write_text(
        json.dumps(bridge, indent=2) + "\n", encoding="utf-8"
    )
    (OUT / "PLATFORM_MANIFEST.json").write_text(
        json.dumps(
            {
                "catalog": catalog,
                "platform": platform,
                "bridge": bridge,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "ok": True,
        "models": catalog["model_count"],
        "services": platform["service_count"],
        "out": str(OUT),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    raise SystemExit(main())