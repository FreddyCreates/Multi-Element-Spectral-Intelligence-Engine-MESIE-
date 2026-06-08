"""Interior data center — sovereign corpus vault inside the org (not public cloud).

Gathers every bundled reference, benchmark, library, scenario, and knowledge shard
already in the MESIE tree. Feeds edge appliances and cluster-edge nodes.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.production.deployment_doctrine import DeploymentClass
from mesie.version_info import INTERIOR_DC_VERSION

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
DELIVERABLES = ROOT / "deliverables"
LIBRARY = ROOT / "library"


@dataclass
class CorpusShard:
    shard_id: str
    lane: str
    path: str
    bytes: int
    record_count: int
    domains: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class InteriorDataCenterReport:
    dc_version: str
    deployment_class: str
    sovereign: bool
    airgapped: bool
    third_party_cloud: bool
    total_bytes: int
    total_shards: int
    total_records: int
    shards: List[CorpusShard]
    ingest_lanes: List[str]
    knowledge: Dict[str, int]
    evidence_vault: List[Dict[str, Any]]
    feeds: Dict[str, str]
    generated_at: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["shards"] = [s.to_dict() for s in self.shards]
        return d


class InteriorDataCenter:
    """Sovereign interior DC — catalog and serve bundled + org evidence data."""

    INGEST_LANES = [
        "bundled_references",
        "bundled_benchmarks",
        "spectral_libraries",
        "scenario_packs",
        "mission_worlds",
        "csv_field_ingest",
        "udp_rf_frames",
        "evidence_deliverables",
        "sdk_knowledge_catalog",
    ]

    EVIDENCE_ARTIFACTS = [
        "Proof_Substrate.json",
        "MAESI_SDK_Major_Benchmarks.json",
        "MESIE_Production_Tiers_Report.json",
        "MESIE_Scenario_Simulation_Report.json",
        "NeuroSwarmAI_Audit_Evidence.json",
        "neuroswarmai_com/evidence_manifest.json",
    ]

    def __init__(self, *, dc_id: str = "interior-dc-001") -> None:
        self.dc_id = dc_id

    def _count_json_records(self, path: Path) -> int:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return 0
        if isinstance(data, list):
            return len(data)
        if isinstance(data, dict):
            for key in ("scenarios", "presets", "entries", "claims", "rows", "ticks"):
                if isinstance(data.get(key), list):
                    return len(data[key])
            if "components" in data:
                return len(data["components"])
        return 1

    def _shard(
        self,
        shard_id: str,
        lane: str,
        path: Path,
        *,
        domains: Optional[List[str]] = None,
    ) -> Optional[CorpusShard]:
        if not path.is_file():
            return None
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        return CorpusShard(
            shard_id=shard_id,
            lane=lane,
            path=rel,
            bytes=path.stat().st_size,
            record_count=self._count_json_records(path),
            domains=domains or [],
        )

    def _gather_reference_shards(self) -> List[CorpusShard]:
        from data import list_references

        shards: List[CorpusShard] = []
        for name in sorted(list_references()):
            p = DATA / "reference" / f"{name}.json"
            shards.append(
                self._shard(f"ref-{name}", "bundled_references", p, domains=["reference"])
            )
        return [s for s in shards if s]

    def _gather_benchmark_shards(self) -> List[CorpusShard]:
        from data import list_benchmarks

        shards: List[CorpusShard] = []
        for name in sorted(list_benchmarks()):
            p = DATA / "benchmarks" / f"{name}.json"
            shards.append(
                self._shard(f"bench-{name}", "bundled_benchmarks", p, domains=["benchmark"])
            )
        return [s for s in shards if s]

    def _gather_library_shards(self) -> List[CorpusShard]:
        from data import list_library
        from mesie.library.domain_corpus import DOMAIN_MAP

        lib_domains = {n: d for d, names in DOMAIN_MAP.items() for n in names if d == "libraries"}
        shards: List[CorpusShard] = []
        for name in sorted(list_library()):
            p = DATA / "spectral_library" / f"{name}.json"
            shards.append(
                self._shard(
                    f"lib-{name}",
                    "spectral_libraries",
                    p,
                    domains=["library", lib_domains.get(name, "spectral")],
                )
            )
        return [s for s in shards if s]

    def _gather_scenario_shards(self) -> List[CorpusShard]:
        scen_dir = DATA / "scenarios"
        shards: List[CorpusShard] = []
        if scen_dir.is_dir():
            for p in sorted(scen_dir.glob("*.json")):
                domain = "military" if "military" in p.stem else "enterprise"
                shards.append(
                    self._shard(f"scen-{p.stem}", "scenario_packs", p, domains=[domain])
                )
        return [s for s in shards if s]

    def _gather_mission_world_shards(self) -> List[CorpusShard]:
        worlds_data = DATA / "worlds"
        worlds_lib = LIBRARY / "mission_worlds"
        shards: List[CorpusShard] = []
        for base in (worlds_data, worlds_lib):
            if not base.is_dir():
                continue
            for p in sorted(base.rglob("*.json")):
                shards.append(
                    self._shard(f"world-{p.stem}", "mission_worlds", p, domains=["theater"])
                )
        return [s for s in shards if s]

    def _gather_sample_shards(self) -> List[CorpusShard]:
        samples = DATA / "samples"
        shards: List[CorpusShard] = []
        if samples.is_dir():
            for p in sorted(samples.iterdir()):
                if p.is_file():
                    shards.append(
                        CorpusShard(
                            shard_id=f"sample-{p.stem}",
                            lane="csv_field_ingest",
                            path=str(p.relative_to(ROOT)).replace("\\", "/"),
                            bytes=p.stat().st_size,
                            record_count=1,
                            domains=["field_ingest"],
                        )
                    )
        return shards

    def _knowledge_stats(self) -> Dict[str, int]:
        from mesie.sdk import MAESIClient

        client = MAESIClient()
        k = client.knowledge_stats()
        return {
            "physical_laws": k.physical_laws,
            "chemical_elements": k.chemical_elements,
            "biological_systems": k.biological_systems,
            "technical_concepts": k.technical_concepts,
            "research_entries": k.research_entries,
        }

    def _evidence_vault(self) -> List[Dict[str, Any]]:
        vault: List[Dict[str, Any]] = []
        for rel in self.EVIDENCE_ARTIFACTS:
            p = DELIVERABLES / rel
            if p.is_file():
                vault.append({
                    "artifact": rel,
                    "bytes": p.stat().st_size,
                    "lane": "evidence_deliverables",
                })
        return vault

    def catalog(self) -> InteriorDataCenterReport:
        shards: List[CorpusShard] = []
        shards.extend(self._gather_reference_shards())
        shards.extend(self._gather_benchmark_shards())
        shards.extend(self._gather_library_shards())
        shards.extend(self._gather_scenario_shards())
        shards.extend(self._gather_mission_world_shards())
        shards.extend(self._gather_sample_shards())

        knowledge = self._knowledge_stats()
        evidence = self._evidence_vault()
        total_bytes = sum(s.bytes for s in shards) + sum(e["bytes"] for e in evidence)

        return InteriorDataCenterReport(
            dc_version=INTERIOR_DC_VERSION,
            deployment_class=DeploymentClass.INTERIOR_DATACENTER.value,
            sovereign=True,
            airgapped=True,
            third_party_cloud=False,
            total_bytes=total_bytes,
            total_shards=len(shards),
            total_records=sum(s.record_count for s in shards),
            shards=shards,
            ingest_lanes=list(self.INGEST_LANES),
            knowledge=knowledge,
            evidence_vault=evidence,
            feeds={
                "edge_contested_appliance": "tier1_manifest + domain_corpus slice",
                "cluster_edge": "corpus fingerprint + OTA mesh metadata",
                "industry_contractor": "scenario_packs + proof_substrate export",
                "builder_lab": "full shard catalog + REPL examples",
            },
            generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    def export(self, path: Optional[Path] = None) -> Path:
        report = self.catalog()
        out = path or DELIVERABLES / "MESIE_Interior_DataCenter_Manifest.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")

        md = DELIVERABLES / "MESIE_Interior_DataCenter_Narrative.md"
        md.write_text(self._narrative(report), encoding="utf-8")
        return out

    def _narrative(self, report: InteriorDataCenterReport) -> str:
        lines = [
            "# MESIE Interior Data Center",
            "",
            "Sovereign corpus vault **inside your organization** — not public cloud.",
            "",
            f"**DC version:** {report.dc_version} | **Shards:** {report.total_shards} | "
            f"**Records:** {report.total_records} | **Bytes:** {report.total_bytes:,}",
            "",
            "## What this is",
            "",
            "Your interior DC gathers references, benchmarks, spectral libraries, scenarios,",
            "mission worlds, SDK knowledge, and evidence deliverables already in the MESIE tree.",
            "Edge operators and cluster-edge nodes pull from here — airgapped, sovereign.",
            "",
            "## Feeds",
            "",
        ]
        for k, v in report.feeds.items():
            lines.append(f"- **{k}:** {v}")
        lines.extend(["", "## Knowledge catalog", ""])
        for k, v in report.knowledge.items():
            lines.append(f"- {k}: {v}")
        lines.extend(["", "## Ingest lanes", "", ", ".join(report.ingest_lanes), ""])
        return "\n".join(lines)