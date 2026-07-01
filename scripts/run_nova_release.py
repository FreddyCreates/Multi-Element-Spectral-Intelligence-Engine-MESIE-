#!/usr/bin/env python3
"""Run NOVA + MININOVA production release gate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.nova.release import run_nova_release


def main() -> int:
    report = run_nova_release(export=True)
    print(json.dumps(report.to_dict(), indent=2))
    return 0 if report.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())