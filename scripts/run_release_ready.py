"""Release readiness gate — 0.3.4 / SDK 1.4.1."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.release.bootstrap import bootstrap
from mesie.release.readiness_check import export_report, run_release_check


def main() -> None:
    bootstrap(quiet=False)
    report = run_release_check()
    path = export_report()
    print("=== MESIE Release Readiness ===")
    print(f"Ready: {report.ready}")
    print(f"MESIE {report.mesie_version} | SDK {report.sdk_version}")
    for c in report.checks:
        mark = "PASS" if c["ok"] else "FAIL"
        print(f"  [{mark}] {c['name']}: {c.get('detail', '')[:80]}")
    print(f"Report: {path}")
    sys.exit(0 if report.ready else 1)


if __name__ == "__main__":
    main()