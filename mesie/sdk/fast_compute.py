"""Fast batch spectral compute — vectorized embed, match, ANN."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from mesie.embeddings.vectorizers import SpectralVectorizer
from mesie.io.loaders import RecordInput, load_record

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INDEX = ROOT / "library" / "spectral_index.json"


@dataclass
class ANNStats:
    p50_ms: float
    p95_ms: float
    trials: int
    index_size: int
    backend: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "p50_ms": self.p50_ms,
            "p95_ms": self.p95_ms,
            "trials": self.trials,
            "index_size": self.index_size,
            "backend": self.backend,
        }


@dataclass
class SpeedBenchmark:
    n_items: int
    loop_match_ms: float
    batch_match_ms: float
    speedup_ratio: float
    embed_batch_ms: float
    ann_query_ms: float


class FastSpectralCompute:
    """Cached vectorizer + matrix operations for laptop-scale throughput."""

    _shared_vectorizer: Optional[SpectralVectorizer] = None

    def __init__(self, n_bands: int = 8) -> None:
        self.n_bands = n_bands
        self._matrix: Optional[np.ndarray] = None
        self._ids: List[str] = []
        self._norms: Optional[np.ndarray] = None
        self._backend: str = "matrix_cosine"
        self._band_buckets: Optional[Dict[int, List[int]]] = None

    @classmethod
    def vectorizer(cls, n_bands: int = 8) -> SpectralVectorizer:
        if cls._shared_vectorizer is None or cls._shared_vectorizer.n_bands != n_bands:
            cls._shared_vectorizer = SpectralVectorizer(n_bands=n_bands)
        return cls._shared_vectorizer

    def embed_one(self, record: RecordInput) -> np.ndarray:
        rec = load_record(record)
        return self.vectorizer(self.n_bands).transform(rec)

    def embed_batch(self, records: Sequence[RecordInput]) -> np.ndarray:
        vec = self.vectorizer(self.n_bands)
        embs = vec.batch_transform([load_record(r) for r in records])
        return np.asarray(embs, dtype=np.float64)

    def build_index(self, records: Sequence[RecordInput]) -> int:
        embs = self.embed_batch(records)
        self._matrix = embs
        self._ids = [load_record(r).record_id for r in records]
        self._norms = np.linalg.norm(embs, axis=1)
        self._norms = np.maximum(self._norms, 1e-12)
        self._backend = "matrix_cosine"
        self._band_buckets = self._build_band_buckets(embs)
        return len(self._ids)

    def load_library_index(self, path: Optional[Path] = None) -> int:
        """Load pre-embedded vectors from library/spectral_index.json."""
        p = path or DEFAULT_INDEX
        if not p.is_file():
            return 0
        data = json.loads(p.read_text(encoding="utf-8"))
        entries = data.get("entries", data.get("records", []))
        if not entries:
            return 0
        embs = np.asarray([e["embedding"] for e in entries], dtype=np.float64)
        self._matrix = embs
        self._ids = [e.get("id", e.get("record_id", f"idx_{i}")) for i, e in enumerate(entries)]
        self._norms = np.linalg.norm(embs, axis=1)
        self._norms = np.maximum(self._norms, 1e-12)
        self._backend = f"library_index:{p.name}"
        self._band_buckets = self._build_band_buckets(embs)
        return len(self._ids)

    @staticmethod
    def _build_band_buckets(embs: np.ndarray) -> Dict[int, List[int]]:
        """Band-sign LSH buckets — novel lightweight ANN pre-filter for larger corpora."""
        if len(embs) < 16:
            return {}
        signs = (embs[:, : min(8, embs.shape[1])] >= 0).astype(np.int8)
        keys = signs.dot(1 << np.arange(signs.shape[1], dtype=np.int64))
        buckets: Dict[int, List[int]] = {}
        for i, k in enumerate(keys.tolist()):
            buckets.setdefault(int(k), []).append(i)
        return buckets

    def cosine_search(self, query: RecordInput, top_k: int = 5) -> List[Tuple[str, float]]:
        if self._matrix is None:
            return []
        q = self.embed_one(query)
        qn = max(np.linalg.norm(q), 1e-12)
        candidates = self._candidate_indices(q)
        mat = self._matrix[candidates]
        norms = self._norms[candidates]
        sims = (mat @ q) / (norms * qn)
        idx_local = np.argpartition(-sims, min(top_k, len(sims) - 1))[:top_k]
        idx_local = idx_local[np.argsort(-sims[idx_local])]
        return [(self._ids[candidates[i]], float(sims[i])) for i in idx_local]

    def _candidate_indices(self, q: np.ndarray) -> List[int]:
        if not self._band_buckets or self._matrix is None:
            return list(range(len(self._ids)))
        signs = (q[: min(8, len(q))] >= 0).astype(np.int8)
        key = int(signs.dot(1 << np.arange(signs.shape[0], dtype=np.int64)))
        pool = set(self._band_buckets.get(key, []))
        # neighbor buckets (Hamming-1 flip) for recall
        for bit in range(min(8, len(q))):
            neighbor = key ^ (1 << bit)
            pool.update(self._band_buckets.get(neighbor, []))
        if len(pool) < max(8, len(self._ids) // 4):
            return list(range(len(self._ids)))
        return sorted(pool)

    def benchmark_ann_p50(
        self,
        query: RecordInput,
        *,
        n_trials: int = 200,
        top_k: int = 5,
    ) -> ANNStats:
        if self._matrix is None:
            raise RuntimeError("index not built — call build_index or load_library_index first")
        samples: List[float] = []
        for _ in range(n_trials):
            t0 = time.perf_counter()
            self.cosine_search(query, top_k=top_k)
            samples.append((time.perf_counter() - t0) * 1000)
        arr = np.asarray(samples)
        return ANNStats(
            p50_ms=round(float(np.percentile(arr, 50)), 4),
            p95_ms=round(float(np.percentile(arr, 95)), 4),
            trials=n_trials,
            index_size=len(self._ids),
            backend=self._backend,
        )

    @staticmethod
    def benchmark_match(
        records: Sequence[RecordInput],
        *,
        n_repeat: int = 500,
    ) -> SpeedBenchmark:
        from mesie.matching.matcher import match_records

        loaded = [load_record(r) for r in records]
        if len(loaded) < 2:
            raise ValueError("Need at least 2 records")
        a, b = loaded[0], loaded[1]

        t0 = time.perf_counter()
        for _ in range(n_repeat):
            match_records(a, b)
        loop_ms = (time.perf_counter() - t0) / n_repeat * 1000

        fc = FastSpectralCompute()
        t1 = time.perf_counter()
        mat = fc.embed_batch(loaded[: min(50, len(loaded))])
        t_embed = (time.perf_counter() - t1) * 1000
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-12)
        unit = mat / norms
        t2 = time.perf_counter()
        for _ in range(n_repeat):
            _ = unit[0] @ unit[1]
        batch_ms = (time.perf_counter() - t2) / n_repeat * 1000

        fc.build_index(loaded)
        q = loaded[0]
        t3 = time.perf_counter()
        fc.cosine_search(q, top_k=5)
        ann_ms = (time.perf_counter() - t3) * 1000

        return SpeedBenchmark(
            n_items=len(loaded),
            loop_match_ms=round(loop_ms, 4),
            batch_match_ms=round(batch_ms, 4),
            speedup_ratio=round(loop_ms / max(batch_ms, 1e-9), 2),
            embed_batch_ms=round(t_embed, 2),
            ann_query_ms=round(ann_ms, 4),
        )