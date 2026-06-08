"""Sam.gov / GSA contractor edition export."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.enterprise.samgov_suite import SamGovSuite


def main() -> None:
    path = SamGovSuite().export()
    rep = SamGovSuite().build_report()
    print("=== MESIE Sam.gov Contractor Edition ===")
    print(f"Edition: {rep.edition}")
    print(f"Workflows: {len(rep.workflows)}")
    print(f"Opportunity refs: {len(rep.opportunity_refs)}")
    print(f"Report: {path}")
    sys.exit(0)


if __name__ == "__main__":
    main()