"""Is This True? — honest Grok/X-style verification response."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.verification.is_this_true import IsThisTrueEngine


def main() -> None:
    path = IsThisTrueEngine().export()
    print("=== Is This True? ===")
    print(f"Verdict: partially_true_software_substrate")
    print(f"Report: {path}")
    print("See deliverables/Is_This_True_Response.md for full honest answer.")
    sys.exit(0)


if __name__ == "__main__":
    main()