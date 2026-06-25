#!/usr/bin/env python3
"""Package and deploy MESIE services — dry-run by default."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    from mesie.deploy.packager import package_all, package_service
    from mesie.deploy.registry import DEPLOY_TARGETS, SERVICE_REGISTRY
    from mesie.deploy.router import deploy_service

    parser = argparse.ArgumentParser(description="MESIE service packaging and deploy")
    parser.add_argument("--all", action="store_true", help="Package all services")
    parser.add_argument("--service", metavar="ID", help="Package one service")
    parser.add_argument("--deploy", metavar="ID", help="Deploy a packaged service")
    parser.add_argument("--target", default="local-http", choices=DEPLOY_TARGETS, help="Deploy target")
    parser.add_argument("--apply", action="store_true", help="Execute deploy (default is dry-run)")
    parser.add_argument("--list", action="store_true", help="List packagable services")
    args = parser.parse_args()

    if args.list:
        print(json.dumps({sid: svc.to_dict() for sid, svc in SERVICE_REGISTRY.items()}, indent=2))
        return 0

    if args.all:
        bundles = package_all()
        print(json.dumps({"ok": True, "bundles": [str(p) for p in bundles]}, indent=2))
        return 0

    if args.service:
        path = package_service(args.service)
        print(json.dumps({"ok": True, "bundle": str(path)}, indent=2))
        return 0

    if args.deploy:
        result = deploy_service(args.deploy, args.target, dry_run=not args.apply)
        print(json.dumps(result.to_dict(), indent=2))
        return 0 if result.dry_run or result.applied else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
