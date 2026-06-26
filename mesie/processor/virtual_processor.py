"""Virtual processor — MESIE compute primitives agents invoke (not chat)."""

from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from mesie.processor.accounting import LocalAccountingLedger

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = ROOT / "deliverables" / "processor" / "MESIE_Processor_Manifest.json"


@dataclass
class ProcessorResult:
    ok: bool
    operation: str
    output: Any
    latency_ms: float
    lrc: Dict[str, Any]
    measured_units: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "operation": self.operation,
            "output": self.output,
            "latency_ms": self.latency_ms,
            "lrc": self.lrc,
            "measured_units": self.measured_units,
        }


@dataclass
class VirtualProcessor:
    """MESIE virtual processor — embed/match/benchmark/exec without LLM talk."""

    ledger: LocalAccountingLedger = field(default_factory=LocalAccountingLedger)
    vault_root: Path = field(default_factory=lambda: ROOT / ".processor_vault")

    def __post_init__(self) -> None:
        self.ledger.bind(self.vault_root)
        self._fc = None
        self._chip = None

    def status(self) -> Dict[str, Any]:
        packet_dir = ROOT / "deliverables"
        packet_files = sum(1 for _ in packet_dir.rglob("*.json")) if packet_dir.is_dir() else 0
        packet_bytes = sum(p.stat().st_size for p in packet_dir.rglob("*.json")) if packet_dir.is_dir() else 0
        return {
            "product": "MESIE Virtual Processor",
            "processor_version": "1.1.0",
            "accounting": self.ledger.export_status(packet_files=packet_files, packet_bytes=packet_bytes),
            "vault": str(self.vault_root),
            "operations": [
                "embed", "match", "benchmark", "exec_tool", "virtual_chip", "list_chips", "robotics_pulse",
            ],
            "chip_skus": [sku.chip_id for sku in self._chip_skus()],
            "mcp_note": "Expose via HTTP :8750 or Loom runspace_exec; not a chat shell.",
        }

    def export_manifest(self, path: Optional[Path] = None) -> Path:
        import json

        from mesie.processor import PROCESSOR_VERSION
        from mesie.version_info import MESIE_VERSION

        out = Path(path) if path else DEFAULT_MANIFEST_PATH
        payload = {
            "product": "MESIE Virtual Processor",
            "version": PROCESSOR_VERSION,
            "mesie_version": MESIE_VERSION,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": self.status(),
            "sample": self.status(),
            "deploy_artifacts": {
                "port": 8750,
                "health_path": "/processor/status",
                "manifest_path": str(out),
            },
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return out

    def _finish(self, operation: str, t0: float, output: Any, *, measured: int, ok: bool = True) -> ProcessorResult:
        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        lrc = self.ledger.mint_cycle(operation, measured_units=measured, latency_ms=elapsed, payload=output)
        return ProcessorResult(ok=ok, operation=operation, output=output, latency_ms=elapsed, lrc=lrc.to_dict(), measured_units=measured)

    def embed(self, record_path: str) -> ProcessorResult:
        from mesie.io.loaders import load_record
        from mesie.sdk.fast_compute import FastSpectralCompute

        t0 = time.perf_counter()
        if Path(record_path).is_file():
            rec = load_record(record_path)
        else:
            from data import load_reference_record
            rec = load_reference_record(record_path)
        fc = FastSpectralCompute()
        vec = fc.embed_one(rec)
        return self._finish("embed", t0, {"dims": len(vec), "record_id": getattr(rec, "record_id", str(record_path))}, measured=len(vec))

    def match_pair(self, path_a: str, path_b: str) -> ProcessorResult:
        from mesie.matching.matcher import match_records
        from mesie.io.loaders import load_record

        t0 = time.perf_counter()
        a, b = load_record(path_a), load_record(path_b)
        result = match_records(a, b)
        out = {"score": result.composite_score, "a": a.record_id, "b": b.record_id}
        return self._finish("match", t0, out, measured=2)

    def benchmark(self, *, trials: int = 200) -> ProcessorResult:
        from mesie.evaluation.neuroswarm_audit import NeuroSwarmClaimsVerifier
        from mesie.silicon.virtual_chip import VirtualSiliconChip

        t0 = time.perf_counter()
        audit = NeuroSwarmClaimsVerifier(n_latency_trials=trials)
        threat = audit.benchmark_threat_response_fast_path()
        chip = VirtualSiliconChip()
        lane = chip.benchmark_lane()
        out = {
            "threat_p50_ms": threat.p50_ms,
            "ann_p50_ms": lane.ann_p50_ms,
            "ann_p95_ms": lane.ann_p95_ms,
            "ann_backend": lane.ann_backend,
            "ota_mesh_ok": lane.ota_mesh_ok,
            "trials": trials,
        }
        return self._finish("benchmark", t0, out, measured=trials + lane.ota_frames_received)

    def exec_tool(self, tool_id: str, *, timeout_s: int = 120) -> ProcessorResult:
        from mesie.tools.registry import tool_by_id

        t0 = time.perf_counter()
        tool = tool_by_id(tool_id)
        if not tool:
            return self._finish("exec_tool", t0, {"error": f"unknown tool: {tool_id}"}, measured=0, ok=False)
        cmd = tool.command
        if cmd.startswith("python "):
            args = [sys.executable] + cmd.split()[1:]
        else:
            args = cmd.split()
        r = subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout_s)
        out = {"tool_id": tool_id, "exit_code": r.returncode, "stdout_tail": (r.stdout or "")[-800:], "stderr_tail": (r.stderr or "")[-400:]}
        return self._finish("exec_tool", t0, out, measured=len(r.stdout or "") + len(r.stderr or ""), ok=r.returncode == 0)

    @staticmethod
    def _chip_skus():
        from mesie.silicon.chip_registry import list_chips

        return list_chips()

    def list_chips(self) -> ProcessorResult:
        from mesie.silicon.chip_registry import deploy_manifest

        t0 = time.perf_counter()
        out = deploy_manifest()
        return self._finish("list_chips", t0, out, measured=len(out.get("skus", [])))

    def virtual_chip_certify(self, *, chip_id: str = "MESIE-VS1") -> ProcessorResult:
        from mesie.silicon.virtual_chip import VirtualSiliconChip

        t0 = time.perf_counter()
        chip = VirtualSiliconChip.from_sku(chip_id)
        cert = chip.certify()
        out = cert.to_dict()
        out["chip_id"] = chip_id
        return self._finish("virtual_chip", t0, out, measured=cert.benchmark_lane.ota_frames_received + 100)

    def robotics_pulse(self) -> ProcessorResult:
        """One NeuroSwarm / robotics readiness pulse for satellite loop."""
        import numpy as np
        from mesie.evaluation.neuroswarm_audit import NeuroSwarmClaimsVerifier
        from mesie.robotics.multimodal_fusion import Modality, ModalityStream, MultiModalFusion

        t0 = time.perf_counter()
        fusion = MultiModalFusion()
        fusion.feed(ModalityStream(Modality.SPECTRAL, np.array([0.1, 0.3, 0.5, 0.7])))
        fusion.feed(ModalityStream(Modality.IMU, np.array([1.0, 0.8, 0.6])))
        fused = fusion.fuse()
        audit = NeuroSwarmClaimsVerifier(n_latency_trials=50)
        threat = audit.benchmark_threat_response_fast_path()
        out = {"fusion_dims": len(fused.vector), "threat_p50_ms": threat.p50_ms, "sovereign": True}
        return self._finish("robotics_pulse", t0, out, measured=len(fused.vector) + 50)
