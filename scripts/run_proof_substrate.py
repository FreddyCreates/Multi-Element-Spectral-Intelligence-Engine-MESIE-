"""Build and optionally verify the MESIE proof substrate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.verification.proof_substrate import DELIVERABLES, ProofSubstrateEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="MESIE proof substrate — sealed evidence graph")
    parser.add_argument("--verify", action="store_true", help="Verify seal on existing Proof_Substrate.json")
    args = parser.parse_args()

    engine = ProofSubstrateEngine()

    if args.verify:
        path = DELIVERABLES / "Proof_Substrate.json"
        if not path.is_file():
            print(f"Missing {path}")
            sys.exit(1)
        payload = json.loads(path.read_text(encoding="utf-8"))
        ok = engine.verify_seal(payload)
        print(f"=== Proof Substrate Verify ===")
        print(f"Seal valid: {ok}")
        print(f"Verdict: {payload.get('verdict')}")
        sys.exit(0 if ok else 1)

    path = engine.export()
    report = engine.build()
    present = sum(1 for a in report.artifact_index.values() if a.present)
    print("=== MESIE Proof Substrate ===")
    print(f"Verdict: {report.verdict}")
    print(f"Seal: {report.seal_digest[:24]}…")
    print(f"Claims: {len(report.claims)} | Artifacts present: {present}/{len(report.artifact_index)}")
    print(f"Gaps open: {report.gaps_open}")
    print(f"Report: {path}")
    print("Site copy: deliverables/neuroswarmai_com/proof_substrate.json")
    sys.exit(0)


if __name__ == "__main__":
    main()