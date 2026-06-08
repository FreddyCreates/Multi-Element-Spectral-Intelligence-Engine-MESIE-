"""MAESI SDK client — unified fast API over MESIE + knowledge libraries."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from mesie.embeddings.fingerprint import SpectralFingerprintPipeline
from mesie.io.loaders import RecordInput, load_record
from mesie.sdk.fast_compute import FastSpectralCompute, SpeedBenchmark
from mesie.sdk.physical_laws import get_fundamental_laws
from mesie.sdk.chemical_elements import get_periodic_table
from mesie.sdk.biological_systems import get_biological_systems
from mesie.sdk.technical_library import TechnicalConcept, get_technical_library, get_technical_matrix
from mesie.sdk.research_knowledge import ResearchEntry, get_research_catalog, search_research, get_research_matrix


@dataclass
class KnowledgeStats:
    physical_laws: int
    chemical_elements: int
    biological_systems: int
    technical_concepts: int
    research_entries: int


@dataclass
class MAESIQueryResult:
    record_id: str
    neighbors: List[Dict[str, Any]]
    research_hits: List[str]
    technical_hits: List[str]
    elapsed_ms: float


@dataclass
class MAESIRunReport:
    version: str
    knowledge: KnowledgeStats
    speed: Optional[SpeedBenchmark]
    fingerprint_hits: List[Dict[str, Any]] = field(default_factory=list)
    neuroaix_available: bool = False
    solus_organism: Optional[Dict[str, Any]] = None
    plain_summary: str = ""


class MAESIClient:
    """One entry point: knowledge + fast compute + optional fingerprint / NeuroAIX."""

    def __init__(
        self,
        *,
        fast: bool = True,
        use_fingerprint: bool = True,
        use_solus_caretakers: bool = True,
        use_solus_math_layer: bool = True,
    ) -> None:
        self.fast_compute = FastSpectralCompute() if fast else None
        self.fingerprint = SpectralFingerprintPipeline() if use_fingerprint else None
        self._indexed = False
        self.organism = None
        self.math_layer = None
        self._native_ai = None
        self._field_access = None
        self._swarm = None
        self._terminal = None
        if use_solus_caretakers or use_solus_math_layer:
            from mesie.sdk.solus import SDKSolusOrganism, SolusMathLayer

            self.organism = SDKSolusOrganism()
            if use_solus_math_layer:
                self.math_layer = SolusMathLayer(organism=self.organism)
        self._law_matrix = np.stack([l.to_embedding() for l in get_fundamental_laws()])
        self._tech_matrix = get_technical_matrix()
        self._research_matrix = get_research_matrix()
        self._technical = get_technical_library()
        self._research = get_research_catalog()

    @property
    def version(self) -> str:
        from mesie.sdk import __sdk_version__

        return __sdk_version__

    @property
    def native_ai(self):
        """Fused native local AI — stream + generate deliverables inside SDK."""
        if self._native_ai is None:
            from mesie.sdk.native_ai import NativeLocalAIEngine

            self._native_ai = NativeLocalAIEngine()
            if self.organism is not None:
                self._native_ai.organism = self.organism
            self._native_ai._maesi = self
            self._native_ai._indexed = self._indexed
        return self._native_ai

    def stream_native_ai(self, records: Sequence[RecordInput], **kwargs):
        """Stream native AI generation events; writes deliverables by default."""
        return self.native_ai.stream_generate(records, **kwargs)

    def generate_native_deliverable(self, records: Sequence[RecordInput], **kwargs):
        """Generate full native AI deliverable bundle (JSON + MD + stream log)."""
        return self.native_ai.generate(records, **kwargs)

    @property
    def field_access(self):
        """Airgapped field access — world computer via real frequencies, no WiFi/third-party."""
        if self._field_access is None:
            from mesie.sovereign.field_access import get_field_access_engine

            self._field_access = get_field_access_engine()
        return self._field_access

    def bridge_to_field(self, record: RecordInput):
        """Align a spectrum with the physical field — sovereign access without internet."""
        return self.field_access.bridge(record)

    def route_field(self, source: str, destination: str, *, policy: str = "shortest"):
        """Route through the sovereign field mesh — aliases like ground, world, leo0, geo."""
        return self.field_access.route(source, destination, policy=policy)

    @property
    def terminal(self):
        """Full terminal session — PowerShell-first on Windows edge deploys."""
        if self._terminal is None:
            from mesie.sdk.terminal import default_session

            self._terminal = default_session()
        return self._terminal

    def run_tool(self, tool_id: str, extra: str = "") -> int:
        """Run a native registry tool through the SDK terminal layer."""
        return self.terminal.run_tool(tool_id, extra)

    def open_terminal(self, *, command: str | None = None) -> int | None:
        """Open interactive OS terminal (PowerShell window on Windows)."""
        return self.terminal.open_interactive(command=command)

    @property
    def swarm(self):
        """Drone swarm intelligence — missions, coordination, formation, mesh."""
        if self._swarm is None:
            from mesie.sdk.swarm_client import SwarmSDK

            self._swarm = SwarmSDK()
        return self._swarm

    def swarm_mission(self, record: RecordInput, *, preset_id: str = "ew", n_agents: int = 1000, jam_ground: bool = False):
        """Execute full swarm mission preset (strike/isr/ew/swarm_forge)."""
        return self.swarm.mission_plan(record, preset_id=preset_id, n_agents=n_agents, jam_ground=jam_ground)

    def swarm_coordinate(self, record: RecordInput, *, n_agents: int = 1000, jam_ground: bool = False):
        """Decentralized swarm coordination at scale."""
        return self.swarm.coordinate(record, n_agents=n_agents, jam_ground=jam_ground)

    def rf_ingest(self, *, simulated: bool = True):
        """Live RF adapter — Schumann-band spectral ingest → field bridge."""
        return self.swarm.rf_ingest(simulated=simulated)

    def knowledge_stats(self) -> KnowledgeStats:
        return KnowledgeStats(
            physical_laws=len(get_fundamental_laws()),
            chemical_elements=len(get_periodic_table()),
            biological_systems=len(get_biological_systems()),
            technical_concepts=len(self._technical),
            research_entries=len(self._research),
        )

    def index_corpus(self, records: Sequence[RecordInput]) -> int:
        if self.fast_compute:
            n = self.fast_compute.build_index(records)
        if self.fingerprint:
            self.fingerprint.index_records(records)
        self._indexed = True
        return n if self.fast_compute else len(records)

    def _project_hits(self, embedding: np.ndarray, matrix: np.ndarray, labels: List[str], top_k: int = 3) -> List[str]:
        d = min(embedding.shape[0], matrix.shape[1])
        sims = matrix[:, :d] @ embedding[:d]
        idx = np.argsort(-sims)[:top_k]
        return [labels[i] for i in idx]

    def query(self, record: RecordInput, top_k: int = 5) -> MAESIQueryResult:
        t0 = time.perf_counter()
        rec = load_record(record)
        emb = self.fast_compute.embed_one(rec) if self.fast_compute else np.zeros(17)
        neighbors = []
        if self.fast_compute and self.fast_compute._matrix is not None:
            for rid, sim in self.fast_compute.cosine_search(rec, top_k=top_k):
                neighbors.append({"record_id": rid, "similarity": round(sim, 4)})
        tech = self._project_hits(emb, self._tech_matrix, [t.name for t in self._technical])
        research = search_research(rec.record_id.replace("_", " "), top_k=3)
        if not research:
            research = self._project_hits(
                emb,
                self._research_matrix,
                [r.title for r in self._research],
            )
            research = [str(x) for x in research]
        else:
            research = [r.title for r in research]
        return MAESIQueryResult(
            record_id=rec.record_id,
            neighbors=neighbors,
            research_hits=research,
            technical_hits=tech,
            elapsed_ms=(time.perf_counter() - t0) * 1000,
        )

    def run_full(
        self,
        records: Sequence[RecordInput],
        *,
        benchmark: bool = True,
    ) -> MAESIRunReport:
        stats = self.knowledge_stats()
        self.index_corpus(records)
        speed = None
        if benchmark and self.fast_compute and len(records) >= 2:
            speed = FastSpectralCompute.benchmark_match(records, n_repeat=300)

        fp_hits = []
        if self.fingerprint and records:
            hits = self.fingerprint.query(records[0], top_k=3)
            fp_hits = [{"id": h.item_id, "sim": round(h.similarity, 4)} for h in hits]

        neuro = False
        try:
            from mesie.sdk.neuroaix_engine import MAESIObservationEncoder

            enc = MAESIObservationEncoder(embedding_dim=64)
            obs = enc.encode(np.random.randn(32))
            neuro = obs.spectral_embedding is not None
        except Exception:
            neuro = False

        if self.math_layer and records:
            first = load_record(records[0])
            comp = first.components[0]
            self.math_layer.reason_spectral_cycle(
                comp.frequency.tolist(),
                comp.amplitude.tolist(),
                cycle_context={"record_id": first.record_id, "phase": "maesi_run_full"},
            )

        q = self.query(records[0]) if records else None
        plain = (
            f"MAESI SDK v{self.version}: {stats.technical_concepts} technical + "
            f"{stats.research_entries} research entries loaded. "
        )
        if speed:
            plain += f"Batch match {speed.speedup_ratio}x faster than loop ({speed.batch_match_ms} ms vs {speed.loop_match_ms} ms). "
        if q:
            plain += f"Query {q.record_id} in {q.elapsed_ms:.1f} ms; top neighbor {q.neighbors[0] if q.neighbors else 'n/a'}."

        solus_report = None
        if self.organism:
            solus_stats = {
                "physical_laws": stats.physical_laws,
                "chemical_elements": stats.chemical_elements,
                "technical_concepts": stats.technical_concepts,
                "research_entries": stats.research_entries,
                "speedup_ratio": speed.speedup_ratio if speed else 1.0,
            }
            solus_report = self.organism.tend_sdk(solus_stats)
            plain += f" SOLUS caretakers: {solus_report['sdk_health']}."

        return MAESIRunReport(
            version=self.version,
            knowledge=stats,
            speed=speed,
            fingerprint_hits=fp_hits,
            neuroaix_available=neuro,
            solus_organism=solus_report,
            plain_summary=plain,
        )