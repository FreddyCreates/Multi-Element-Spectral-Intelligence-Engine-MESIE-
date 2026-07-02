"""Haskell adapter — runghc health + φ-kernel spectral fallback."""

from __future__ import annotations

import json
import math
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from mesie.polyglot.adapters.base import PolyglotAdapter
from mesie.polyglot.adapters.rust_adapter import _fallback_match, _fallback_validate
from mesie.polyglot.contract import AISVectorMessage, PolyglotAction, RuntimeId

ROOT = Path(__file__).resolve().parents[3]
HEALTH_HS = ROOT / "bindings" / "haskell" / "health.hs"
PHI = 0.6180339887498948


def _phi_fingerprint(record: dict) -> dict:
    """Spectral φ-kernel fingerprint — mirrors depth Haskell Batch00."""
    comps = record.get("components") or []
    if not comps:
        return {"fingerprint": [], "score": 0.0}
    c = comps[0]
    freq = [float(x) for x in (c.get("frequency") or [])[:64]]
    amp = [float(x) for x in (c.get("amplitude") or [])[:64]]
    n = min(len(freq), len(amp), 64)
    if n == 0:
        return {"fingerprint": [], "score": 0.0}
    weighted = []
    for i in range(n):
        decay = PHI ** (i * 0.1 / max(n, 1))
        weighted.append(amp[i] * decay)
    dot = sum(w * math.cos(f * PHI) for f, w in zip(freq[:n], weighted))
    norm = math.sqrt(sum(w * w for w in weighted) + 1e-12)
    score = max(0.0, min(1.0, (dot / norm + 1.0) * 0.5))
    fp = [round(score * math.cos(i * PHI), 6) for i in range(8)]
    return {"fingerprint": fp, "score": round(score, 6), "runtime": "haskell-phi"}


class HaskellAdapter(PolyglotAdapter):
    runtime = RuntimeId.HASKELL

    def available(self) -> bool:
        if shutil.which("runghc") is None or not HEALTH_HS.is_file():
            return False
        try:
            proc = subprocess.run(
                ["runghc", str(HEALTH_HS)],
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )
            data = json.loads(proc.stdout)
            return data.get("status") == "ok"
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            return False

    def _handle(self, message: AISVectorMessage) -> Tuple[dict, Optional[List[float]]]:
        if message.action == PolyglotAction.HEALTH:
            if self.available():
                proc = subprocess.run(
                    ["runghc", str(HEALTH_HS)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=True,
                )
                return json.loads(proc.stdout), None
            return {"status": "ok", "mode": "fallback"}, None

        if message.action == PolyglotAction.FINGERPRINT:
            out = _phi_fingerprint(message.record or {})
            return out, out.get("fingerprint")

        if message.action == PolyglotAction.VALIDATE:
            return _fallback_validate(message.record or {}), None
        if message.action == PolyglotAction.MATCH:
            return _fallback_match(message.record_a or message.record or {}, message.record_b or {}), None
        if message.action == PolyglotAction.EMBED:
            from mesie.polyglot.adapters.python_adapter import PythonAdapter

            return PythonAdapter()._handle(message)

        raise ValueError(f"haskell unsupported action: {message.action}")
