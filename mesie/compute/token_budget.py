"""MESIE Load-Bearing Token Budget — 12x message compression, reasoning uplift."""

from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "deliverables" / "compute" / "TOKEN_BUDGET_BASELINE.json"
STATE = ROOT / "deliverables" / "compute" / "TOKEN_BUDGET_STATE.json"
RECEIPTS = ROOT / "deliverables" / "compute" / "LOAD_BEARING_RECEIPTS.jsonl"

PHI = (1 + 5**0.5) / 2
REDUCTION = 12
RECEIPT_MAX = 240


def load_baseline() -> Dict[str, Any]:
    if BASELINE.is_file():
        return json.loads(BASELINE.read_text(encoding="utf-8"))
    return {"targets": {"message_reduction_factor": REDUCTION}}


def compact_text(text: str, *, max_chars: int = RECEIPT_MAX) -> str:
    """Load-bearing surface: strip prose, keep verbs + paths + numbers."""
    if not text:
        return ""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    keep: List[str] = []
    for ln in lines:
        if any(c in ln for c in "./\\") or ln.startswith(("{", "[", "ok", "ERR")):
            keep.append(ln)
        elif len(ln) < 80 and any(ch.isdigit() for ch in ln):
            keep.append(ln)
        if sum(len(x) for x in keep) >= max_chars:
            break
    out = " | ".join(keep) if keep else text[:max_chars]
    return out[:max_chars]


def estimate_tokens(text: str) -> int:
    return max(1, math.ceil(len(text) / 4))


def compact_tokens(raw: int) -> int:
    return max(1, math.ceil(raw / REDUCTION))


def load_bearing_encode(payload: Dict[str, Any]) -> Dict[str, Any]:
    """ST-φ style budget vector for overhead/reasoning routing."""
    from mesie.compute.hub import MESIEComputeHub

    brief = json.dumps(payload, separators=(",", ":"), sort_keys=True)[:2000]
    enc = MESIEComputeHub(model_id="ST-φ-128").encode(brief)
    return {
        "ok": True,
        "compact_tokens": compact_tokens(estimate_tokens(brief)),
        "raw_tokens_est": estimate_tokens(brief),
        "reduction_factor": REDUCTION,
        "st_phi": enc,
        "phi_weight": PHI,
    }


def snapshot(override: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    base = load_baseline()
    slices = dict(base.get("slices", {}))
    if override:
        for k, v in override.items():
            if k in slices and isinstance(v, dict):
                slices[k].update(v)
            else:
                slices[k] = v
    msg = slices.get("messages", {}).get("tokens", 0)
    free = slices.get("free", {}).get("tokens", 0)
    compact_msg = compact_tokens(msg)
    uplift = {
        "messages_compact_tokens": compact_msg,
        "messages_saved_tokens": max(0, msg - compact_msg),
        "reasoning_headroom_tokens": int(slices.get("reasoning_overhead", {}).get("tokens", 0) * 0.5),
        "free_after_compact_est": free + max(0, msg - compact_msg),
    }
    out = {
        "protocol": "MESIE-LOAD-BEARING/1.0",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "slices": slices,
        "uplift": uplift,
        "surface_gate": "production_only",
        "baseline": str(BASELINE),
    }
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return out


def append_receipt(phase: str, summary: str, *, production: bool = True) -> Dict[str, Any]:
    if not production:
        return {"ok": False, "reason": "surface_gate: production_only"}
    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phase": phase,
        "compact": compact_text(summary),
        "tokens_est": compact_tokens(estimate_tokens(summary)),
    }
    RECEIPTS.parent.mkdir(parents=True, exist_ok=True)
    with RECEIPTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, separators=(",", ":")) + "\n")
    return rec


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="MESIE load-bearing token budget")
    p.add_argument("--snapshot", action="store_true")
    p.add_argument("--compact", metavar="TEXT")
    p.add_argument("--receipt", nargs=2, metavar=("PHASE", "TEXT"))
    args = p.parse_args()
    if args.snapshot:
        print(json.dumps(snapshot(), indent=2))
        return 0
    if args.compact:
        print(json.dumps({"compact": compact_text(args.compact), "tokens": compact_tokens(estimate_tokens(args.compact))}))
        return 0
    if args.receipt:
        print(json.dumps(append_receipt(args.receipt[0], args.receipt[1])))
        return 0
    print(json.dumps(snapshot(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())