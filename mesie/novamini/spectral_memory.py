"""Spectral memory buffer for NOVAMINI — FFT signatures + cosine recall + Hebbian plasticity
+ temporal dynamics (TemporalSpectralBuffer) + priority replay (ExperienceReplayBuffer)."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from mesie.cognitive.memory_consolidation import ExperienceReplayBuffer
from mesie.cognitive.temporal_dynamics import TemporalSpectralBuffer
from mesie.neuroai.auro.algorithms import hebbian_salience

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


def chunk_text(text: str, chunk_chars: int = 400, overlap: int = 60) -> List[str]:
    """Split artifact text into overlapping chunks for spectral indexing."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_chars:
        return [text]
    chunks: List[str] = []
    start = 0
    step = max(1, chunk_chars - overlap)
    while start < len(text):
        chunks.append(text[start : start + chunk_chars])
        start += step
    return chunks


@dataclass
class ArtifactChunk:
    """One spectrally-indexed slice of a whole artifact (file, doc, pasted text)."""

    artifact_id: str
    artifact_name: str
    chunk_index: int
    text: str
    vector: List[float]
    ts: float
    salience: float = PHI_INV

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_name": self.artifact_name,
            "chunk_index": self.chunk_index,
            "text": self.text,
            "vector": self.vector,
            "ts": self.ts,
            "salience": self.salience,
        }


@dataclass
class SpectralMemory:
    """Local vault-backed episodic memory for NOVAMINI conversations + ingested artifacts.

    Algorithmic substrate:
        - text_to_spectrum: char-code FFT → cosine recall
        - Hebbian LTP: salience grows with co-activation
        - TemporalSpectralBuffer: sliding-window trajectory of conversation spectra
        - ExperienceReplayBuffer: priority-weighted past experience replay
    """

    vault_dir: Path
    max_turns: int = 256
    max_artifact_chunks: int = 4096
    _turns: List[MemoryTurn] = field(default_factory=list, init=False)
    _artifact_chunks: List[ArtifactChunk] = field(default_factory=list, init=False)
    _artifacts: Dict[str, Dict[str, Any]] = field(default_factory=dict, init=False)
    _temporal: TemporalSpectralBuffer = field(init=False)
    _replay: ExperienceReplayBuffer = field(init=False)

    def __post_init__(self) -> None:
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        # d_spectral=33 matches rfft output of 64-sample FFT
        self._temporal = TemporalSpectralBuffer(max_length=512, d_spectral=33)
        self._replay = ExperienceReplayBuffer(
            capacity=1024,
            priority_exponent=0.6,
            importance_sampling_exponent=0.4,
        )
        self._load()
        self._load_artifacts()

    @property
    def ledger_path(self) -> Path:
        return self.vault_dir / "memory_ledger.jsonl"

    @property
    def artifact_ledger_path(self) -> Path:
        return self.vault_dir / "artifact_ledger.jsonl"

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

    def _load_artifacts(self) -> None:
        if not self.artifact_ledger_path.is_file():
            return
        for line in self.artifact_ledger_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                chunk = ArtifactChunk(
                    artifact_id=row["artifact_id"],
                    artifact_name=row["artifact_name"],
                    chunk_index=row["chunk_index"],
                    text=row["text"],
                    vector=row["vector"],
                    ts=row.get("ts", time.time()),
                    salience=row.get("salience", PHI_INV),
                )
                self._artifact_chunks.append(chunk)
                self._artifacts.setdefault(
                    chunk.artifact_id,
                    {"artifact_id": chunk.artifact_id, "name": chunk.artifact_name, "chunks": 0},
                )["chunks"] += 1
            except (json.JSONDecodeError, KeyError):
                continue

    def store(self, user: str, spoken: str, role: str = "AURO", **kwargs: Any) -> MemoryTurn:
        vec = text_to_spectrum(user + " " + spoken)
        ts = time.time()
        salience = min(1.0, PHI_INV + len(user) / 500.0)
        turn = MemoryTurn(
            user=user,
            spoken=spoken,
            role=role,
            vector=vec.tolist(),
            ts=ts,
            salience=salience,
        )
        self._turns.append(turn)
        if len(self._turns) > self.max_turns:
            self._turns = self._turns[-self.max_turns :]
        with self.ledger_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(turn.to_dict(), ensure_ascii=False) + "\n")

        # Push spectrum into temporal trajectory buffer
        self._temporal.push(vec, timestamp=ts, metadata={"role": role, "text": user[:60]})

        # Store in priority replay — higher salience → higher priority
        self._replay.add(
            {"user": user[:120], "spoken": spoken[:120], "vector": vec.tolist(),
             "role": role, "ts": ts, **{k: v for k, v in kwargs.items() if k != "vector"}},
            priority=salience,
        )
        return turn

    def recall(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Cosine recall over turn history, enriched with replay-buffer diversity.

        Returns up to k turns from the primary ledger ranked by salience-weighted
        cosine similarity, with temporal flux appended as metadata.
        """
        q = text_to_spectrum(query)
        results: List[Dict[str, Any]] = []

        if self._turns:
            scored = []
            for t in self._turns:
                v = np.array(t.vector, dtype=np.float64)
                sim = cosine_sim(q, v) * t.salience
                scored.append((sim, t))
            scored.sort(key=lambda x: -x[0])
            results = [
                {
                    "score": round(s, 4),
                    "user": t.user[:120],
                    "spoken": t.spoken[:200],
                    "role": t.role,
                    "source": "ledger",
                }
                for s, t in scored[:k]
                if s > 0.15
            ]

        # Temporal flux — how much the spectral trajectory changed last step
        diff = self._temporal.get_temporal_diff(lag=1)
        flux = round(float(np.mean(np.abs(diff))), 4) if diff is not None and len(diff) > 0 else 0.0

        # Replay diversity: sample 1 priority-weighted past experience not already in results
        if len(self._replay._buffer) >= 2:
            try:
                past, _idx, _w = self._replay.sample(1)
                if past:
                    p = past[0]
                    p_vec = np.array(p.get("vector", []), dtype=np.float64)
                    if p_vec.size > 0:
                        sim = cosine_sim(q, p_vec)
                        if sim > 0.1:
                            results.append({
                                "score": round(sim, 4),
                                "user": p.get("user", "")[:120],
                                "spoken": p.get("spoken", "")[:200],
                                "role": p.get("role", "AURO"),
                                "source": "replay",
                            })
            except Exception:
                pass

        return [{"temporal_flux": flux, **r} for r in results]

    # ── Artifact ingestion — whole documents, not just chat turns ──────────

    def ingest_artifact(self, name: str, text: str, artifact_id: Optional[str] = None,
                         chunk_chars: int = 400, overlap: int = 60) -> Dict[str, Any]:
        """Chunk an artifact (file/doc/pasted text) and spectrally index every chunk
        so chat() can recall and reason off pieces of it, not just past turns."""
        aid = artifact_id or f"art-{abs(hash((name, len(text)))) % (10**12):012x}"
        chunks = chunk_text(text, chunk_chars=chunk_chars, overlap=overlap)
        if not chunks:
            return {"ok": False, "reason": "EMPTY_ARTIFACT", "artifact_id": aid, "name": name}

        now = time.time()
        written = 0
        with self.artifact_ledger_path.open("a", encoding="utf-8") as f:
            for i, chunk in enumerate(chunks):
                vec = text_to_spectrum(chunk)
                ac = ArtifactChunk(
                    artifact_id=aid, artifact_name=name, chunk_index=i,
                    text=chunk, vector=vec.tolist(), ts=now,
                    salience=min(1.0, PHI_INV + len(chunk) / 1000.0),
                )
                self._artifact_chunks.append(ac)
                f.write(json.dumps(ac.to_dict(), ensure_ascii=False) + "\n")
                written += 1
        self._artifacts[aid] = {"artifact_id": aid, "name": name, "chunks": written}
        if len(self._artifact_chunks) > self.max_artifact_chunks:
            self._artifact_chunks = self._artifact_chunks[-self.max_artifact_chunks :]
        return {"ok": True, "artifact_id": aid, "name": name, "chunks_indexed": written}

    def recall_artifacts(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Spectral cosine recall over ingested artifact chunks.

        Applies Hebbian LTP after recall: chunks that are recalled together
        have their salience strengthened (biotech: long-term potentiation).
        """
        if not self._artifact_chunks:
            return []
        q = text_to_spectrum(query)
        scored = []
        for c in self._artifact_chunks:
            v = np.array(c.vector, dtype=np.float64)
            sim = cosine_sim(q, v) * c.salience
            scored.append((sim, c))
        scored.sort(key=lambda x: -x[0])
        top = [(s, c) for s, c in scored[:k] if s > 0.15]

        # Hebbian plasticity: strengthen salience of co-recalled chunks
        if len(top) >= 2:
            for _s, chunk in top:
                chunk.salience = hebbian_salience(
                    chunk.salience,
                    co_activation_count=len(top),
                )

        return [
            {
                "score": round(s, 4),
                "artifact_id": c.artifact_id,
                "artifact_name": c.artifact_name,
                "chunk_index": c.chunk_index,
                "text": c.text[:300],
            }
            for s, c in top
        ]

    def recall_all(self, query: str, k_turns: int = 2, k_artifacts: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """Combined recall across conversation history and ingested artifacts."""
        return {
            "turns": self.recall(query, k=k_turns),
            "artifacts": self.recall_artifacts(query, k=k_artifacts),
        }

    def artifacts(self) -> List[Dict[str, Any]]:
        return list(self._artifacts.values())

    def status(self) -> Dict[str, Any]:
        return {
            "turns": len(self._turns),
            "vault": str(self.vault_dir),
            "ledger": str(self.ledger_path),
            "artifacts": len(self._artifacts),
            "artifact_chunks": len(self._artifact_chunks),
            "artifact_ledger": str(self.artifact_ledger_path),
            "temporal_buffer_size": self._temporal.size,
            "replay_buffer_size": len(self._replay._buffer),
        }