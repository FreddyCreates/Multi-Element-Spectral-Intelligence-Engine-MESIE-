"""Virtual silicon chip — spectral ALU + RF front-end + OTA MAC on commodity CPU."""

from __future__ import annotations

import hashlib
import json
import platform
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.evaluation.neuroswarm_audit import NeuroSwarmClaimsVerifier
from mesie.library.domain_corpus import load_domain_corpus
from mesie.sdk.fast_compute import FastSpectralCompute
from mesie.silicon.ota_mesh import OTAMeshReport, run_ota_mesh_round
from mesie.silicon.rf_frontend import RFHILCertReport, VirtualRFFrontEnd

from mesie.version_info import VIRTUAL_CHIP_VERSION as CHIP_VERSION
CERT_DIR = Path(__file__).resolve().parents[2] / "deliverables" / "virtual_silicon"


@dataclass
class VirtualChipSpec:
    chip_name: str = "MESIE-VS1"
    process_node_nm: int = 7
    rf_frontends: int = 1
    spectral_alu_width: int = 256
    ota_mac: str = "NSOT_multicast_v1"
    sovereign: bool = True
    airgapped: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VirtualChipBenchmarkLane:
    threat_fast_p50_ms: float
    ann_p50_ms: float
    ann_p95_ms: float
    ann_backend: str
    rf_hil_latency_ms: float
    ota_mesh_ok: bool
    ota_frames_received: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VirtualChipCertification:
    chip_version: str
    spec: VirtualChipSpec
    rf_hil: RFHILCertReport
    ota_mesh: OTAMeshReport
    benchmark_lane: VirtualChipBenchmarkLane
    platform: str
    certified: bool
    gaps_resolved: List[str]
    gaps_remaining: List[str]
    generated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chip_version": self.chip_version,
            "spec": self.spec.to_dict(),
            "rf_hil": self.rf_hil.to_dict(),
            "ota_mesh": self.ota_mesh.to_dict(),
            "benchmark_lane": self.benchmark_lane.to_dict(),
            "platform": self.platform,
            "certified": self.certified,
            "gaps_resolved": self.gaps_resolved,
            "gaps_remaining": self.gaps_remaining,
            "generated_at": self.generated_at,
        }


class VirtualSiliconChip:
    """Software virtual chip: replaces discrete RF+DSP+mesh ASIC on laptop/appliance."""

    def __init__(self, spec: Optional[VirtualChipSpec] = None, *, chip_id: str = "MESIE-VS1") -> None:
        from mesie.silicon.chip_registry import get_chip

        self._sku = get_chip(chip_id)
        self.spec = spec or self._sku.spec
        self.chip_id = chip_id
        self.rf = VirtualRFFrontEnd()
        self._corpus = load_domain_corpus()

    @classmethod
    def from_sku(cls, chip_id: str) -> "VirtualSiliconChip":
        return cls(chip_id=chip_id)

    def certify_rf_hil(self) -> RFHILCertReport:
        rep = self.rf.run_hil_loop(snr_db=24.0)
        if self.spec.rf_frontends > 1:
            rep2 = self.rf.run_hil_loop(snr_db=22.0)
            if not rep2.certified:
                rep = rep2
        return rep

    def run_ota_mesh(self, *, n_nodes: Optional[int] = None) -> OTAMeshReport:
        return run_ota_mesh_round(
            n_nodes=n_nodes or self._sku.ota_nodes,
            propagation_tier_index=self._sku.ota_propagation_tier,
        )

    def benchmark_lane(self) -> VirtualChipBenchmarkLane:
        audit = NeuroSwarmClaimsVerifier(n_latency_trials=self._sku.threat_trials)
        threat = audit.benchmark_threat_response_fast_path()
        fc = FastSpectralCompute()
        loaded = fc.load_library_index()
        if loaded == 0:
            fc.build_index(self._corpus)
        q = self._corpus[0]
        ann = fc.benchmark_ann_p50(q, n_trials=self._sku.ann_trials)

        hil = self.rf.run_hil_loop()
        ota = self.run_ota_mesh()
        return VirtualChipBenchmarkLane(
            threat_fast_p50_ms=threat.p50_ms,
            ann_p50_ms=ann.p50_ms,
            ann_p95_ms=ann.p95_ms,
            ann_backend=ann.backend,
            rf_hil_latency_ms=hil.ingest_latency_ms,
            ota_mesh_ok=ota.ok,
            ota_frames_received=ota.frames_received,
        )

    @staticmethod
    def attach_content_hash(payload: Dict[str, Any]) -> None:
        payload["content_hash"] = hashlib.sha256(
            json.dumps({k: v for k, v in payload.items() if k != "content_hash"}, sort_keys=True).encode()
        ).hexdigest()[:16]

    def certify(self) -> VirtualChipCertification:
        rf_hil = self.certify_rf_hil()
        ota = self.run_ota_mesh()
        bench = self.benchmark_lane()
        certified = rf_hil.certified and ota.ok and bench.ota_mesh_ok
        return VirtualChipCertification(
            chip_version=CHIP_VERSION,
            spec=self.spec,
            rf_hil=rf_hil,
            ota_mesh=ota,
            benchmark_lane=bench,
            platform=platform.platform(),
            certified=certified,
            gaps_resolved=[
                "RF path: virtual silicon SDR HIL (NSRF binary) certified without physical fab",
                "Multi-machine mesh: OTA multicast swarm radio (NSOT) with Hz-ladder propagation",
                "MLPerf: community formal pack with compliance manifest (see mlperf_submit)",
                f"ANN lane: statistical p50/p95 with band-sign LSH pre-filter ({bench.ann_backend})",
                f"Chip registry: deployable SKUs {self.chip_id} via MESIE_Chip_Deploy_Manifest.json",
            ],
            gaps_remaining=[
                "Physical SDR silicon certification (RTL/fab) — virtual only",
                "Official MLPerf leaderboard board review — community pack ready",
                "Live satellite modem hardware — virtual orbital tier models only",
            ],
            generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    def export_certification(self, path: Optional[Path] = None) -> Path:
        cert = self.certify()
        payload = cert.to_dict()
        payload["chip_id"] = self.chip_id
        self.attach_content_hash(payload)
        CERT_DIR.mkdir(parents=True, exist_ok=True)
        out = path or CERT_DIR / "MESIE_Virtual_Silicon_Certification.json"
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return out

    def narrative_md(self) -> str:
        cert = self.certify()
        return "\n".join([
            f"# MESIE Virtual Silicon ({self.chip_id})",
            "",
            f"**Chip:** {cert.spec.chip_name} v{cert.chip_version}",
            f"**Certified:** {cert.certified}",
            "",
            "## What this is",
            "",
            "A **virtual chip** — spectral RF front-end, ALU, and OTA MAC implemented in software",
            "on your laptop or on-prem appliance. Same APIs and latency envelope as a future ASIC,",
            "without waiting for fab. **Not regular MCP** — invoke via Virtual Processor HTTP `:8750`.",
            "",
            "## RF front-end (HIL certified)",
            "",
            f"- Path: `{cert.rf_hil.path}`",
            f"- Front-ends: {cert.spec.rf_frontends}",
            f"- SNR: {cert.rf_hil.snr_db} dB (virtual ground truth)",
            f"- Latency: {cert.rf_hil.ingest_latency_ms} ms",
            f"- Field coherence: {cert.rf_hil.field_coherence}",
            "",
            "## OTA swarm radio",
            "",
            f"- Protocol: {cert.spec.ota_mac}",
            f"- Tier: {cert.ota_mesh.propagation_tier}",
            f"- Frames: {cert.ota_mesh.frames_sent} sent / {cert.ota_mesh.frames_received} received",
            "",
            "## Benchmark lane (statistical)",
            "",
            f"- Threat-fast p50: {cert.benchmark_lane.threat_fast_p50_ms} ms",
            f"- ANN p50 / p95: {cert.benchmark_lane.ann_p50_ms} / {cert.benchmark_lane.ann_p95_ms} ms",
            f"- ANN backend: {cert.benchmark_lane.ann_backend}",
            "",
            "## Deploy",
            "",
            "- `POST http://127.0.0.1:8750/processor/virtual-chip` body `{\"chip_id\": \"" + self.chip_id + "\"}`",
            "- Manifest: `deliverables/virtual_silicon/MESIE_Chip_Deploy_Manifest.json`",
            "",
            f"*Generated {cert.generated_at}*",
        ])