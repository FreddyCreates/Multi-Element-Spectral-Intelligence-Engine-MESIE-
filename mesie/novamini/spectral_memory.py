"""Spectral memory buffer for NOVAMINI — FFT signatures + cosine recall."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

PHI_INV = 0.6180339887498949


def text_to_spectrum(text: str, n: int = 64) -> np.ndarray:
    """Map text to a fixed spectral signature via char-code FFT."""
    sig = np.array([float(ord(c) % 97) for c in text[:n]], dtype=np.float64)
    if len(sig) < n:
        sig = np.pad(sig, (0, n - len(sig)))
    detrended = sig - np.linspace(sig[0], sig[-1], n)
    spectrum = np.abs(np.fft.rfft(detrended))
    norm = float(np.linalg.norm(spectrum)) + 1e-12
    return spectrum / norm


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


@dataclass
class MemoryTurn:
    user: str
    spoken: str
    role: str
    vector: List[float]
    ts: float
    salience: float = PHI_INV

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user": self.user,
            "spoken": self.spoken,
            "role": self.role,
            "vector": self.vector,
            "ts": self.ts,
            "salience": self.salience,
        }


@dataclass
class SpectralMemory:
    """Local vault-backed episodic memory for NOVAMINI conversations."""

    vault_dir: Path
    max_turns: int = 256
    _turns: List[MemoryTurn] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self._load()

    @property
    def ledger_path(self) -> Path:
        return self.vault_dir / "memory_ledger.jsonl"

    def _load(self) -> None:
        if not self.ledger_path.is_file():
            return
        for line in self.ledger_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                self._turns.append(
                    MemoryTurn(
                        user=row["user"],
                        spoken=row["spoken"],
                        role=row.get("role", "AURO"),
                        vector=row["vector"],
                        ts=row.get("ts", time.time()),
                        salience=row.get("salience", PHI_INV),
                    )
                )
            except (json.JSONDecodeError, KeyError):
                continue

    def store(self, user: str, spoken: str, role: str = "AURO") -> MemoryTurn:
        vec = text_to_spectrum(user + " " + spoken)
        turn = MemoryTurn(
            user=user,
            spoken=spoken,
            role=role,
            vector=vec.tolist(),
            ts=time.time(),
            salience=min(1.0, PHI_INV + len(user) / 500.0),
        )
        self._turns.append(turn)
        if len(self._turns) > self.max_turns:
            self._turns = self._turns[-self.max_turns :]
        with self.ledger_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(turn.to_dict(), ensure_ascii=False) + "\n")
        return turn

    def recall(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        if not self._turns:
            return []
        q = text_to_spectrum(query)
        scored = []
        for t in self._turns:
            v = np.array(t.vector, dtype=np.float64)
            sim = cosine_sim(q, v) * t.salience
            scored.append((sim, t))
        scored.sort(key=lambda x: -x[0])
        return [
            {
                "score": round(s, 4),
                "user": t.user[:120],
                "spoken": t.spoken[:200],
                "role": t.role,
            }
            for s, t in scored[:k]
            if s > 0.15
        ]

    def status(self) -> Dict[str, Any]:
        return {
            "turns": len(self._turns),
            "vault": str(self.vault_dir),
            "ledger": str(self.ledger_path),
        }