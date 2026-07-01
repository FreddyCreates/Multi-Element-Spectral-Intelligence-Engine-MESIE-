#!/usr/bin/env python3
"""Generate official commercial paperwork, certifications, and test report."""

from __future__ import annotations

import argparse
import json
import sys

from mesie.processor.official_pack import build_official_dossier, package_official_bundle, run_commercial_tests


def main() -> int:
    parser = argparse.ArgumentParser(description="MESIE Virtual Processor official commercial pack")
    parser.add_argument("--quick", action="store_true", help="Faster commercial tests (fewer rounds)")
    parser.add_argument("--tests-only", action="store_true", help="Run commercial tests only")
    parser.add_argument("--bundle", action="store_true", help="Zip official bundle for distribution")
    parser.add_argument("--no-tests", action="store_true", help="Generate docs/certs without running tests")
    args = parser.parse_args()

    if args.tests_only:
        rep = run_commercial_tests(quick=args.quick)
        print(json.dumps(rep, indent=2))
        return 0 if rep.get("commercial_ready") else 1

    if args.bundle:
        path = package_official_bundle()
        print(json.dumps({"ok": True, "bundle": str(path)}, indent=2))
        return 0

    dossier = build_official_dossier(run_tests=not args.no_tests, quick=args.quick)
    print(json.dumps(dossier, indent=2))
    return 0 if dossier.get("commercial_ready") else 1


if __name__ == "__main__":
    raise SystemExit(main())