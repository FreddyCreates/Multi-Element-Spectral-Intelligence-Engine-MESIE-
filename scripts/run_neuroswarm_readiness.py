"""NeuroSwarmAI.com readiness push — harness + evidence pack + gap plan."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.verification.readiness import ReadinessOrchestrator


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-harness", action="store_true")
    parser.add_argument("--push", action="store_true", help="git push trust/production-readiness")
    args = parser.parse_args()

    report = ReadinessOrchestrator().run(run_harness=not args.skip_harness)

    print("=== NeuroSwarmAI.com Readiness ===")
    print(f"Site: {report.site_url}")
    print(f"Level: {report.readiness_level}")
    print(f"Production ready (software): {report.production_ready}")
    print(f"Gaps open: {report.gaps_open} | P0 tasks ready: {report.gaps_closed_software}")
    print(f"Harness: {'PASS' if report.harness_pass else 'FAIL'}")
    print(f"Evidence: deliverables/neuroswarmai_com/evidence_manifest.json")

    if args.push:
        for cmd in [
            ["git", "add", "deliverables/neuroswarmai_com", "deliverables/NeuroSwarmAI_Readiness_Report.json",
             "mesie/verification/readiness.py", "scripts/run_neuroswarm_readiness.py"],
            ["git", "commit", "-m", "readiness: NeuroSwarmAI.com evidence pack + gap closure plan"],
            ["git", "push", "-u", "origin", "trust/production-readiness"],
        ]:
            r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
            if r.returncode != 0 and "commit" in cmd:
                print(f"commit note: {r.stderr or r.stdout}")
            elif r.returncode != 0:
                print(f"push failed: {r.stderr or r.stdout}")
                sys.exit(1)
        print("Pushed: origin/trust/production-readiness")

    sys.exit(0 if report.production_ready else 1)


if __name__ == "__main__":
    main()