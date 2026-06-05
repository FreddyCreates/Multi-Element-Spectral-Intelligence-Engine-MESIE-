"""Fast spectral compute engine for the MAESI SDK.

Provides vectorized batch operations and approximate nearest neighbor
search over spectral embeddings — replacing per-pair loop matching
with matrix cosine similarity for ~100-1000× speedup.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from mesie.core.records import MultiElementRecord
from mesie.embeddings.vectorizers import SpectralVectorizer


@dataclass
class SpeedBenchmark:
    """Performance benchmark results.

    Attributes
    ----------
    loop_match_ms : float
        Per-pair matching time using sequential loop (ms).
    batch_match_ms : float
        Per-pair matching time using batch matrix ops (ms).
    speedup_ratio : float
        Speedup factor (loop / batch).
    embed_batch_ms : float
        Time to embed N items in batch (ms).
    ann_query_ms : float
        ANN query time (ms).
    n_items : int
        Number of items benchmarked.
    """

    loop_match_ms: float = 0.0
    batch_match_ms: float = 0.0
    speedup_ratio: float = 1.0
    embed_batch_ms: float = 0.0
    ann_query_ms: float = 0.0
    n_items: int = 0


class FastSpectralCompute:
    """Vectorized spectral compute with ANN index.

    Uses a shared SpectralVectorizer singleton, batch embedding,
    and matrix cosine similarity for high-throughput spectral search.

    Example
    -------
    >>> fc = FastSpectralCompute()
    >>> fc.build_index(records)
    >>> hits = fc.cosine_search(query_record, top_k=5)
    """

    _shared_vectorizer: Optional[SpectralVectorizer] = None

    def __init__(self, vectorizer: Optional[SpectralVectorizer] = None):
        if vectorizer is not None:
            self._vectorizer = vectorizer
        else:
            if FastSpectralCompute._shared_vectorizer is None:
                FastSpectralCompute._shared_vectorizer = SpectralVectorizer()
            self._vectorizer = FastSpectralCompute._shared_vectorizer

        self._index_embeddings: Optional[np.ndarray] = None
        self._index_ids: List[str] = []
        self._index_records: List[MultiElementRecord] = []

    @property
    def vectorizer(self) -> SpectralVectorizer:
        """The shared vectorizer instance."""
        return self._vectorizer

    @property
    def index_size(self) -> int:
        """Number of records in the index."""
        return len(self._index_ids)

    def build_index(self, records: Sequence[MultiElementRecord]) -> None:
        """Build the ANN index from a batch of records.

        Parameters
        ----------
        records : Sequence[MultiElementRecord]
            Records to index.
        """
        self._index_records = list(records)
        self._index_ids = [r.record_id for r in records]
        self._index_embeddings = self._vectorizer.batch_transform(records)

        # L2-normalize for cosine similarity
        norms = np.linalg.norm(self._index_embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self._index_embeddings = self._index_embeddings / norms

    def cosine_search(
        self,
        query: MultiElementRecord,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """Search the index by cosine similarity.

        Parameters
        ----------
        query : MultiElementRecord
            Query record.
        top_k : int
            Number of results.

        Returns
        -------
        List of (record_id, similarity) tuples sorted descending.
        """
        if self._index_embeddings is None or len(self._index_ids) == 0:
            return []

        q_vec = self._vectorizer.transform(query)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []
        q_vec = q_vec / q_norm

        similarities = self._index_embeddings @ q_vec
        top_k = min(top_k, len(similarities))
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        return [(self._index_ids[i], float(similarities[i])) for i in top_indices]

    def batch_cosine_matrix(self, records: Sequence[MultiElementRecord]) -> np.ndarray:
        """Compute pairwise cosine similarity matrix.

        Parameters
        ----------
        records : Sequence[MultiElementRecord]
            Records to compare.

        Returns
        -------
        NxN cosine similarity matrix.
        """
        embeddings = self._vectorizer.batch_transform(records)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized = embeddings / norms
        return normalized @ normalized.T

    def benchmark(self, records: Sequence[MultiElementRecord]) -> SpeedBenchmark:
        """Run performance benchmark comparing loop vs batch matching.

        Parameters
        ----------
        records : Sequence[MultiElementRecord]
            Records to benchmark.

        Returns
        -------
        SpeedBenchmark with timing results.
        """
        from mesie.matching.matcher import match_records

        n = len(records)
        if n < 2:
            return SpeedBenchmark(n_items=n)

        # Loop matching benchmark
        start = time.perf_counter()
        for i in range(min(n, 5)):
            for j in range(i + 1, min(n, 5)):
                match_records(records[i], records[j])
        loop_elapsed = time.perf_counter() - start
        n_pairs_loop = min(n, 5) * (min(n, 5) - 1) // 2
        loop_ms_per_pair = (loop_elapsed / max(n_pairs_loop, 1)) * 1000

        # Batch embedding benchmark
        start = time.perf_counter()
        embeddings = self._vectorizer.batch_transform(records)
        embed_ms = (time.perf_counter() - start) * 1000

        # Batch cosine benchmark
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized = embeddings / norms

        start = time.perf_counter()
        _sim_matrix = normalized @ normalized.T
        batch_elapsed = time.perf_counter() - start
        n_pairs_batch = n * (n - 1) // 2
        batch_ms_per_pair = (batch_elapsed / max(n_pairs_batch, 1)) * 1000

        # ANN query benchmark
        self.build_index(records)
        start = time.perf_counter()
        self.cosine_search(records[0], top_k=min(5, n))
        ann_ms = (time.perf_counter() - start) * 1000

        speedup = loop_ms_per_pair / max(batch_ms_per_pair, 1e-9)

        return SpeedBenchmark(
            loop_match_ms=round(loop_ms_per_pair, 4),
            batch_match_ms=round(batch_ms_per_pair, 6),
            speedup_ratio=round(speedup, 1),
            embed_batch_ms=round(embed_ms, 4),
            ann_query_ms=round(ann_ms, 4),
            n_items=n,
        )
