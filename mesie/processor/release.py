"""Virtual Processor production release + developer kit."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class ProcessorReleaseReport:
    ready: bool
    processor_version: str = "1.0.0"
    checks: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ready": self.ready,
            "processor_version": self.processor_version,
            "checks": self.checks,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }


def run_processor_release(*, export: bool = True) -> ProcessorReleaseReport:
    from mesie.processor.virtual_processor import VirtualProcessor

    checks: List[Dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": ok, "detail": detail[:400]})

    proc = VirtualProcessor()
    st = proc.status()
    add("status", bool(st.get("product")), str(st.get("operations")))

    rob = proc.robotics_pulse()
    add("robotics_pulse", rob.ok, f"threat_p50={rob.output.get('threat_p50_ms')}")

    emb = proc.embed("ref-earthquake-psd-001")
    add("embed", emb.ok, f"dims={emb.output.get('dims')}")

    bench = proc.benchmark(trials=100)
    add("benchmark", bench.ok, f"p50={bench.output.get('threat_p50_ms')}")

    mesh = proc.mesh_pulse()
    add("mesh_pulse", mesh.ok, f"peers={mesh.output.get('peers_seen')} ota={mesh.output.get('ota_frames_received')}")

    acct = proc.ledger.export_status()
    add("accounting_lrc", bool(acct.get("cycle_count", 0) >= 0), str(acct.get("lrc_id", ""))[:16])

    ready = all(c["ok"] for c in checks)
    report = ProcessorReleaseReport(ready=ready, checks=checks)

    if export:
        out = ROOT / "deliverables" / "processor" / "VIRTUAL_PROCESSOR_RELEASE.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")

    return report


def export_devkit() -> Path:
    """AI-for-AI developer kit manifest — Virtual Processor + NOVA runtime."""
    from mesie.agentic.micro.foundations import foundations_snapshot
    from mesie.processor.stack_architecture import stack_architecture_snapshot
    from mesie.tools.registry import TOOLS

    kit = {
        "product": "MESIE Virtual Processor Developer Kit",
        "version": "1.1.0",
        "for": "AI agents orchestrating AI — Python executes, LLMs talk",
        "endpoints": {
            "processor_http": "http://127.0.0.1:8750/processor/status",
            "operations": [
                "POST /processor/embed",
                "POST /processor/match",
                "POST /processor/read-signal",
                "POST /processor/generate-text",
                "POST /processor/benchmark",
                "POST /processor/robotics-pulse",
                "GET /processor/mesh",
                "POST /processor/mesh/pulse",
                "POST /processor/mesh/soak",
                "POST /processor/exec",
                "GET /processor/nova-runtime",
                "GET /processor/architecture",
                "GET /processor/market-research",
            ],
        },
        "cli": {
            "nova_runtime": "python scripts/run_nova_runtime.py",
            "showcase": "python scripts/run_nova_showcase.py",
            "processor_server": "python scripts/run_virtual_processor.py",
            "package_devkit": "python scripts/package_processor_devkit.py",
        },
        "careers": "mesie/agentic/micro/career.py — 70 IT + domain micro agents",
        "signal_plane": {
            "doctrine": "Everything is a signal",
            "modalities": ["text", "json", "state", "event", "numeric", "spectral", "file"],
            "modules": ["mesie.signals.universal_reader", "mesie.signals.text_emitter"],
        },
        "architecture": stack_architecture_snapshot(),
        "foundations": foundations_snapshot(),
        "tools_sample": [{"id": t.id, "name": t.name} for t in TOOLS[:25]],
        "start": ".\\Start-NovaRuntime.ps1",
        "official": {
            "dossier": "deliverables/processor/official/VIRTUAL_PROCESSOR_OFFICIAL_DOSSIER.json",
            "bundle": "deliverables/processor/VIRTUAL_PROCESSOR_OFFICIAL_BUNDLE.zip",
            "command": "python scripts/run_official_commercial_pack.py --bundle",
        },
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    out = ROOT / "deliverables" / "processor" / "VIRTUAL_PROCESSOR_DEVKIT.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(kit, indent=2), encoding="utf-8")
    return out


def export_stack_architecture() -> Path:
    from mesie.processor.stack_architecture import stack_architecture_snapshot

    out = ROOT / "deliverables" / "processor" / "MESIE_STACK_ARCHITECTURE.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(stack_architecture_snapshot(), indent=2), encoding="utf-8")
    return out


def package_devkit_zip() -> Path:
    """Zip devkit manifest, research, architecture, showcase, and quickstart."""
    import zipfile

    from mesie.processor.market_research import export_market_research

    export_devkit()
    export_stack_architecture()
    export_market_research()

    quickstart = ROOT / "deliverables" / "processor" / "QUICKSTART.txt"
    quickstart.write_text(
        "MESIE Virtual Processor Developer Kit — Quickstart\n"
        "==================================================\n\n"
        "ONE COMMAND (recommended):\n"
        "   .\\Deploy-MESIE.ps1\n\n"
        "Or step by step:\n"
        "1. Start never-stop runtime:\n"
        "   .\\Start-NovaRuntime.ps1\n\n"
        "2. Start HTTP processor:\n"
        "   python -m mesie.processor --serve\n\n"
        "3. Read any signal (text, JSON, event, file path):\n"
        "   POST http://127.0.0.1:8750/processor/read-signal\n"
        '   {"payload":"your text or object","hint":"text"}\n\n'
        "4. Generate analyst text from any signal:\n"
        "   POST http://127.0.0.1:8750/processor/generate-text\n"
        '   {"payload":"sensor alert JSON","style":"executive"}\n\n'
        "5. Proof for market:\n"
        "   deliverables/nova/NOVA_SHOWCASE.json\n"
        "   deliverables/processor/VIRTUAL_PROCESSOR_MARKET_RESEARCH.json\n\n"
        "Doctrine: Everything is a signal — spectra, text, state, physics, domains.\n",
        encoding="utf-8",
    )

    zip_path = ROOT / "deliverables" / "processor" / "VIRTUAL_PROCESSOR_DEVKIT.zip"
    include = [
        "deliverables/processor/VIRTUAL_PROCESSOR_DEVKIT.json",
        "deliverables/processor/VIRTUAL_PROCESSOR_RELEASE.json",
        "deliverables/processor/VIRTUAL_PROCESSOR_MARKET_RESEARCH.json",
        "deliverables/processor/MESIE_STACK_ARCHITECTURE.json",
        "deliverables/processor/QUICKSTART.txt",
        "deliverables/nova/NOVA_SHOWCASE.json",
        "Deploy-MESIE.ps1",
        "Start-NovaRuntime.ps1",
        "scripts/run_nova_runtime.py",
        "scripts/run_virtual_processor.py",
        "scripts/run_processor_release.py",
        "scripts/package_processor_devkit.py",
        "scripts/run_vp_mesh.py",
        "scripts/run_official_commercial_pack.py",
    ]
    official_dir = ROOT / "deliverables" / "processor" / "official"
    if official_dir.is_dir():
        for p in official_dir.rglob("*"):
            if p.is_file():
                rel = p.relative_to(ROOT).as_posix()
                if rel not in include:
                    include.append(rel)
    official_zip = ROOT / "deliverables" / "processor" / "VIRTUAL_PROCESSOR_OFFICIAL_BUNDLE.zip"
    if official_zip.is_file():
        include.append("deliverables/processor/VIRTUAL_PROCESSOR_OFFICIAL_BUNDLE.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in include:
            src = ROOT / rel
            if src.is_file():
                zf.write(src, rel.replace("\\", "/"))
    return zip_path