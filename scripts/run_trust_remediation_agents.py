"""Trust remediation auto-agents — audit, run harnesses, commit branch."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.agents.trust_remediation import TrustRemediationOrchestrator


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--branch", default="trust/production-readiness")
    args = parser.parse_args()

    report = TrustRemediationOrchestrator(branch=args.branch, dry_run=args.dry_run).run()
    print("=== Trust Remediation Agents ===")
    print(f"Branch: {report.branch}")
    print(f"Committed: {report.committed} ({report.commit_hash})")
    print(f"Production ready (harness): {report.production_ready}")
    for a in report.actions:
        print(f"  [{a['agent']}] {a['action']}: {'OK' if a['ok'] else 'FAIL'}")
    sys.exit(0 if report.production_ready else 1)


if __name__ == "__main__":
    main()