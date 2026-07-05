#!/usr/bin/env python3
"""Forge HERMES 12-worker Cloudflare fleet + NOVA PROTOCOL pack."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from mesie.hermes.forge import forge_hermes_fleet
    from mesie.harness.alpha_registry import harness_manifest

    result = forge_hermes_fleet()
    alphas = harness_manifest()
    print(json.dumps({
        **result,
        "alpha_harness_count": alphas["harness_count"],
        "brand": "ItsnotAILabs",
        "nova_protocol": "NOVA-PROTOCOL-CLEAN-INTERNET/1.0",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())