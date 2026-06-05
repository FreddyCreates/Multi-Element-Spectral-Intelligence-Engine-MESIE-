"""MAESI Client — Unified client over MESIE + knowledge libraries + fast compute.

Provides a single entry point for running the full MAESI SDK pipeline:
knowledge inventory, spectral matching, fingerprinting, benchmarking,
and NeuroAIX cognitive integration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from mesie.core.records import MultiElementRecord
from mesie.sdk.fast_compute import FastSpectralCompute, SpeedBenchmark
from mesie.sdk.technical_library import get_technical_library
from mesie.sdk.research_knowledge import get_research_catalog
from mesie.sdk.physical_laws import get_fundamental_laws
from mesie.sdk.chemical_elements import get_periodic_table
from mesie.sdk.biological_systems import get_biological_systems


@dataclass
class KnowledgeStats:
    """Knowledge library size statistics."""

    physical_laws: int = 0
    chemical_elements: int = 0
    biological_systems: int = 0
    technical_concepts: int = 0
    research_entries: int = 0


@dataclass
class MAESIQueryResult:
    """Result from a single MAESI query."""

    record_id: str
    matches: List[tuple] = field(default_factory=list)
    fingerprint_hit: bool = False
    confidence: float = 0.0


@dataclass
class MAESIRunReport:
    """Full MAESI SDK run report."""

    version: str = "1.1.0"
    knowledge: KnowledgeStats = field(default_factory=KnowledgeStats)
    speed: Optional[SpeedBenchmark] = None
    fingerprint_hits: int = 0
    neuroaix_available: bool = False
    plain_summary: str = ""


class MAESIClient:
    """Unified MAESI SDK client.

    Integrates:
    - Knowledge libraries (physical, chemical, biological, technical, research)
    - Fast vectorized compute (batch embed + matrix cosine)
    - Fingerprint pipeline (spectral identity hashing)
    - NeuroAIX cognitive encoder (optional)

    Parameters
    ----------
    fast : bool
        Use FastSpectralCompute for batch operations (default True).
    use_fingerprint : bool
        Enable spectral fingerprinting pipeline (default False).
    """

    def __init__(self, fast: bool = True, use_fingerprint: bool = False):
        self.fast = fast
        self.use_fingerprint = use_fingerprint
        self._compute = FastSpectralCompute() if fast else None
        self._neuroaix_available = False

        # Check NeuroAIX availability
        try:
            from mesie.sdk.neuroaix_engine import MAESIObservationEncoder
            self._encoder = MAESIObservationEncoder(embedding_dim=64)
            self._neuroaix_available = True
        except Exception:
            self._encoder = None

    @property
    def neuroaix_available(self) -> bool:
        """Whether NeuroAIX cognitive encoder is available."""
        return self._neuroaix_available

    def get_knowledge_stats(self) -> KnowledgeStats:
        """Get current knowledge library statistics."""
        return KnowledgeStats(
            physical_laws=len(get_fundamental_laws()),
            chemical_elements=len(get_periodic_table()),
            biological_systems=len(get_biological_systems()),
            technical_concepts=len(get_technical_library()),
            research_entries=len(get_research_catalog()),
        )

    def query(self, record: MultiElementRecord, top_k: int = 5) -> MAESIQueryResult:
        """Query the SDK with a single spectral record.

        Parameters
        ----------
        record : MultiElementRecord
            Input spectral record.
        top_k : int
            Number of similar matches to return.

        Returns
        -------
        MAESIQueryResult with matches and metadata.
        """
        matches = []
        fingerprint_hit = False

        if self._compute and self._compute.index_size > 0:
            matches = self._compute.cosine_search(record, top_k=top_k)
            if matches and matches[0][1] > 0.95:
                fingerprint_hit = True

        confidence = matches[0][1] if matches else 0.0

        return MAESIQueryResult(
            record_id=record.record_id,
            matches=matches,
            fingerprint_hit=fingerprint_hit,
            confidence=confidence,
        )

    def run_full(
        self,
        records: Sequence[MultiElementRecord],
        benchmark: bool = False,
    ) -> MAESIRunReport:
        """Run the full MAESI SDK pipeline.

        Parameters
        ----------
        records : Sequence[MultiElementRecord]
            Input spectral records.
        benchmark : bool
            Whether to run performance benchmarks.

        Returns
        -------
        MAESIRunReport with complete results.
        """
        knowledge = self.get_knowledge_stats()

        # Build index
        speed = None
        fingerprint_hits = 0

        if self._compute and len(records) > 0:
            self._compute.build_index(records)

            # Query each record for fingerprint matches
            if self.use_fingerprint:
                for rec in records:
                    result = self.query(rec, top_k=1)
                    if result.fingerprint_hit:
                        fingerprint_hits += 1

            # Benchmark
            if benchmark:
                speed = self._compute.benchmark(records)

        # Summary
        total_knowledge = (
            knowledge.physical_laws
            + knowledge.chemical_elements
            + knowledge.biological_systems
            + knowledge.technical_concepts
            + knowledge.research_entries
        )
        summary_parts = [
            f"MAESI SDK v1.1.0 | {total_knowledge} knowledge entries loaded",
            f"({knowledge.physical_laws} laws, {knowledge.chemical_elements} elements, "
            f"{knowledge.biological_systems} bio, {knowledge.technical_concepts} technical, "
            f"{knowledge.research_entries} research)",
        ]
        if speed:
            summary_parts.append(
                f"Speed: {speed.speedup_ratio}x batch vs loop | "
                f"ANN query {speed.ann_query_ms} ms"
            )
        summary_parts.append(
            f"NeuroAIX: {'available' if self._neuroaix_available else 'not loaded'}"
        )

        return MAESIRunReport(
            version="1.1.0",
            knowledge=knowledge,
            speed=speed,
            fingerprint_hits=fingerprint_hits,
            neuroaix_available=self._neuroaix_available,
            plain_summary=" | ".join(summary_parts),
        )
