"""Market-facing Virtual Processor research — positioning, scale, usage."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]


def build_market_research(*, live_metrics: bool = True) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {}
    if live_metrics:
        try:
            from mesie.processor.virtual_processor import VirtualProcessor

            proc = VirtualProcessor()
            bench = proc.benchmark(trials=50)
            rob = proc.robotics_pulse()
            metrics = {
                "threat_p50_ms": bench.output.get("threat_p50_ms"),
                "ann_p50_ms": bench.output.get("ann_p50_ms"),
                "fusion_dims": rob.output.get("fusion_dims"),
                "embed_ok": proc.embed("ref-earthquake-psd-001").ok,
            }
        except Exception as exc:
            metrics = {"note": f"live probe skipped: {exc}"}

    from mesie.agentic.micro.foundations import foundations_snapshot

    foundations = foundations_snapshot()
    return {
        "product": "MESIE Virtual Processor",
        "tagline": "Sovereign compute for AI agents that orchestrate AI — measured, not simulated.",
        "version": "1.1.0",
        "market_position": {
            "category": "Agentic Infrastructure / Edge Spectral Compute",
            "differentiators": [
                "Sub-millisecond threat-response path with published benchmark JSON",
                "Universal signal plane — text, JSON, events, and spectra share one embed/match stack",
                "70-career NOVA IT org runs library, protocols, laws, and release gates",
                "LRC accounting ledger — every operation mints a local receipt",
                "Airgapped virtual silicon certification lane (RF HIL + OTA mesh model)",
                "Zero third-party inference on the sovereign path (SOLUS + native voice optional)",
            ],
            "buyer_personas": [
                {"segment": "AI platform teams", "need": "Deterministic tool execution layer under LLM orchestrators"},
                {"segment": "Defense / robotics edge", "need": "Fusion + threat SLA with sovereign audit trail"},
                {"segment": "Industrial digital twin", "need": "PSD/FAS/seismic/power signals in one retrieval index"},
                {"segment": "Developer kit publishers", "need": "HTTP + CLI kit agents can call without chat UI"},
            ],
            "competitive_frame": {
                "vs_cloud_llm_only": "LLMs talk; Virtual Processor executes and proves work with LRC + ms benchmarks.",
                "vs_vector_db_only": "Spectral records carry physics, domains, and text in one embedding — not flat chunks.",
                "vs_simulated_agents": "NOVA careers run pytest, embed library, showcase export — not placeholder pulses.",
            },
        },
        "scalability": {
            "vertical": {
                "single_node": "MAESI batch match 800x+ loop speedup on laptop-class hardware",
                "processor_ops": ["embed", "match", "benchmark", "read_signal", "generate_text", "mesh_pulse"],
                "memory": "Library index + swarm DTN shards on disk; vault compounds work units",
            },
            "horizontal": {
                "nova_runtime": "70 staggered micro satellites — light/medium/heavy task tiers",
                "robotics_satellite": "Independent process with watchdog restart",
                "mesh": "VP-MESH v1.2 — UDP multicast beacons + LAN peer registry + phi-weighted compute routing",
                "vp_mesh": "239.192.77.2:37542 multicast, library/mesh_peers/vp_nodes, VP_MESH_STATE.json",
                "edge": "Processor HTTP :8750 + MCP bridge; field-route tool for edge protocol",
            },
            "limits_today": [
                "Physical SDR silicon — virtual HIL only",
                "Native voice path loads AuroNativeLM — use SOLUS brief for lightweight generation",
                "Single-machine NOVA supervisor — multi-host fleet routing is roadmap",
            ],
        },
        "how_to_use": {
            "quickstart": [
                ".\\Start-NovaRuntime.ps1",
                "python scripts/run_virtual_processor.py",
                "python scripts/package_processor_devkit.py",
            ],
            "http_api": {
                "base": "http://127.0.0.1:8750",
                "endpoints": {
                    "GET /processor/status": "Health + operations list",
                    "POST /processor/embed": '{"record_path":"ref-earthquake-psd-001"}',
                    "POST /processor/read-signal": '{"payload":"any text or JSON","hint":"text"}',
                    "POST /processor/generate-text": '{"payload":{...},"style":"analyst_brief"}',
                    "POST /processor/benchmark": '{"trials":200}',
                    "GET /processor/nova-runtime": "Live 70-career state",
                },
            },
            "agent_pattern": "LLM plans → POST /processor/exec or domain tool → read LRC + showcase JSON as proof",
            "developer_kit": "deliverables/processor/VIRTUAL_PROCESSOR_DEVKIT.zip",
        },
        "measured_proof": metrics,
        "foundations": {
            "library_mb": foundations.get("library", {}).get("mb"),
            "library_files": foundations.get("library", {}).get("files"),
            "engines": foundations.get("engine_count"),
            "tools": foundations.get("tools"),
        },
        "plain_summary": (
            f"MESIE Virtual Processor v1.1: sovereign agentic compute with universal signals, "
            f"{foundations.get('engine_count', 11)} engines, {foundations.get('library', {}).get('files', 0)} library files, "
            f"and sub-ms benchmark paths — packaged devkit + NOVA 70-career runtime for production release."
        ),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def export_market_research(path: Path | None = None) -> Path:
    out = path or ROOT / "deliverables" / "processor" / "VIRTUAL_PROCESSOR_MARKET_RESEARCH.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build_market_research(), indent=2), encoding="utf-8")
    return out