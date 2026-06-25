#!/usr/bin/env python3
"""Medina Surface — agents call this FIRST. Catalog + invoke Medina systems."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.surface.catalog import build_catalog
from mesie.surface.dispatcher import SurfaceDispatcher


def main() -> int:
    parser = argparse.ArgumentParser(description="Medina Surface — agent entrypoint")
    parser.add_argument("--status", action="store_true", help="Full inventory + proof")
    parser.add_argument("--export", action="store_true", help="Write MEDINA_SURFACE_MANIFEST.json")
    parser.add_argument("--serve", action="store_true", help="HTTP server :8760")
    sub = parser.add_subparsers(dest="cmd")
    inv = sub.add_parser("invoke")
    inv.add_argument("--system", required=True)
    inv.add_argument("--action", required=True)
    inv.add_argument("args", nargs="*")
    args = parser.parse_args()

    if args.serve:
        import uvicorn
        uvicorn.run("mesie.surface.server:app", host="127.0.0.1", port=8760, reload=False)
        return 0

    if args.cmd == "invoke":
        r = SurfaceDispatcher().invoke(args.system, args.action, extra_args=args.args or None)
        print(json.dumps(r.to_dict(), indent=2))
        return 0 if r.ok else 1

    cat = build_catalog(export=args.export or args.status or True)
    print(json.dumps(cat.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())