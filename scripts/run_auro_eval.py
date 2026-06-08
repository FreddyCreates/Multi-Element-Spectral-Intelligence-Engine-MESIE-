"""Auro evaluation program — Paper IV voice-memory, role-coherence, boundary speech."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.neuroai.auro.eval import AuroEvalSuite


def main() -> None:
    suite = AuroEvalSuite()
    report = suite.run()
    path = suite.export(report)
    print("=== Auro Native Speaking Intelligence — Eval ===")
    print(f"Edition: {report.edition} | Packet: {report.packet_id}")
    print(f"Passed: {report.passed}/{len(report.cases)}")
    for c in report.cases:
        mark = "PASS" if c.passed else "FAIL"
        print(f"  [{mark}] {c.eval_id}: {c.detail}")
    print(f"Report: {path}")
    sys.exit(0 if report.ok else 1)


if __name__ == "__main__":
    main()