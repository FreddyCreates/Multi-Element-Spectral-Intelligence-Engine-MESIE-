#!/usr/bin/env python3
"""Run NOVA showcase — benchmark workflow proof for public release."""

from __future__ import annotations

import argparse
import json
import sys

from mesie.agentic.micro.showcase import run_showcase


def main() -> int:
    parser = argparse.ArgumentParser(description="NOVA showcase benchmark")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--no-export", action="store_true")
    args = parser.parse_args()

    rep = run_showcase(export=not args.no_export, quick=args.quick)
    print(json.dumps(rep, indent=2))
    return 0 if rep.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())