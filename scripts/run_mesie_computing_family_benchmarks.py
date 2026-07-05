#!/usr/bin/env python3
"""MESIE COMPUTING FAMILY — full official benchmark + protocol suite tied to whole system."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "deliverables" / "compute" / "MESIE_COMPUTING_FAMILY_RELEASE.json"
PYTHON = sys.executable


def _run(label: str, args: List[str], timeout: int = 600) -> Dict[str, Any]:
    t0 = time.perf_counter()
    try:
        r = subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout, check=False)
        elapsed = round(time.perf_counter() - t0, 2)
        parsed = None
        if r.stdout.strip():
            try:
                parsed = json.loads(r.stdout)
            except json.JSONDecodeError:
                parsed = {"raw_tail": r.stdout[-2000:]}
        return {
            "label": label,
            "ok": r.returncode == 0,
            "exit_code": r.returncode,
            "elapsed_s": elapsed,
            "result": parsed,
            "stderr_tail": (r.stderr or "")[-500:] if r.returncode != 0 else "",
        }
    except Exception as exc:
        return {"label": label, "ok": False, "error": str(exc), "elapsed_s": round(time.perf_counter() - t0, 2)}


def _intel_protocol_benchmark() -> Dict[str, Any]:
    from data import load_reference_record
    from mesie.ai.intelligence_protocols import IntelligenceConfig, IntelligenceLevel, IntelligenceProtocol
    import numpy as np

    t0 = time.perf_counter()
    proto = IntelligenceProtocol(IntelligenceConfig(level=IntelligenceLevel.AUTONOMOUS))
    from mesie.io.loaders import load_record

    rec = load_record(load_reference_record("ref-earthquake-psd-001"))
    comp = rec.components[0] if rec.components else None
    amp = np.array((comp.amplitude if comp else [0.1, 0.2, 0.3]), dtype=float)
    result = proto.reason(amp)
    return {
        "ok": True,
        "protocol": "MESIE-INTELLIGENCE-PROTOCOL/1.0",
        "level": IntelligenceLevel.AUTONOMOUS.value,
        "conclusion": result.conclusion,
        "confidence": result.confidence,
        "elapsed_s": round(time.perf_counter() - t0, 3),
    }


def _triple_protocol_status() -> Dict[str, Any]:
    from mesie.cloud.triple_protocol import build_triple_manifest, triple_flow_status

    t0 = time.perf_counter()
    manifest = build_triple_manifest()
    flow = triple_flow_status()
    return {
        "ok": True,
        "protocol": manifest.get("protocol"),
        "layers": len(manifest.get("layers", [])),
        "flow_healthy": (flow.get("P2_mcp_colony") or {}).get("compute_healthy"),
        "flow": flow,
        "elapsed_s": round(time.perf_counter() - t0, 3),
    }


def _economic_monte_carlo(trials: int) -> Dict[str, Any]:
    t0 = time.perf_counter()
    from scripts.monte_carlo_enterprise_benchmark import MonteCarloEnterpriseRunner

    report = MonteCarloEnterpriseRunner().run_all(n_trials=trials)
    summary = {
        "protocol": "MESIE-ENTERPRISE-MONTE-CARLO/1.0",
        "use_cases": len(report.get("use_cases") or []),
        "overall_success_rate": report.get("overall_success_rate"),
        "enterprise_grade": report.get("enterprise_grade"),
        "cases": report.get("use_cases"),
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "ok": True,
    }
    path = ROOT / "deliverables" / "enterprise" / "MONTE_CARLO_FAMILY_BENCHMARK.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def run_family_benchmarks(*, trials: int = 200, mc_trials: int = 100, skip_squads: bool = False) -> Dict[str, Any]:
    t0 = time.perf_counter()
    phases: List[Dict[str, Any]] = []

    print("[family] Phase 1 — Live metrics + 8 Virtual Products", flush=True)
    from mesie.compute.live_metrics import collect_live_metrics

    live = collect_live_metrics()
    phases.append({"phase": "live_metrics", "ok": True, "result": live})

    print("[family] Phase 2 — MESIE COMPUTE Hub benchmark", flush=True)
    from mesie.compute.hub import MESIEComputeHub

    hub_bench = MESIEComputeHub().full_benchmark(trials=trials)
    phases.append({"phase": "compute_hub", "ok": True, "result": hub_bench})

    print("[family] Phase 3 — Processor official benchmarks", flush=True)
    phases.append(_run("processor_benchmarks", [PYTHON, "scripts/run_processor_benchmarks.py"], timeout=180))

    print("[family] Phase 4 — SDK major industry benchmarks (MLPerf-class, vector DB, LLM, swarm)", flush=True)
    phases.append(
        _run(
            "sdk_major_benchmarks",
            [PYTHON, "scripts/run_sdk_major_benchmarks.py", "--trials", str(trials), "--agents", "10000"],
            timeout=600,
        )
    )

    print("[family] Phase 5 — Economic protocols (Monte Carlo enterprise)", flush=True)
    try:
        phases.append({"phase": "economic_monte_carlo", **_economic_monte_carlo(mc_trials)})
    except Exception as exc:
        phases.append({"phase": "economic_monte_carlo", "ok": False, "error": str(exc)})

    print("[family] Phase 6 — Intelligence protocols", flush=True)
    try:
        phases.append({"phase": "intelligence_protocols", **_intel_protocol_benchmark()})
    except Exception as exc:
        phases.append({"phase": "intelligence_protocols", "ok": False, "error": str(exc)})

    print("[family] Phase 7 — Triple protocol (Loom + MCP + Bridge)", flush=True)
    try:
        phases.append({"phase": "triple_protocol", **_triple_protocol_status()})
    except Exception as exc:
        phases.append({"phase": "triple_protocol", "ok": False, "error": str(exc)})

    if not skip_squads:
        print("[family] Phase 8 — Tri-Agent Squads (--all)", flush=True)
        phases.append(_run("tri_agent_squads", [PYTHON, "-m", "mesie.compute.tri_agent_squads", "--all"], timeout=900))

    from mesie.compute.virtual_products import load_products
    from mesie.compute.tri_agent_squads import list_squads

    products = [p.to_dict() for p in load_products()]
    squads = list_squads()

    st = hub_bench.get("st_phi") or {}
    fast_ann = hub_bench.get("fast_ann") or {}
    vp = hub_bench.get("virtual_processor") or {}

    major_path = ROOT / "deliverables" / "MAESI_SDK_Major_Benchmarks.json"
    if major_path.is_file():
        sdk_payload = json.loads(major_path.read_text(encoding="utf-8"))
        major = sdk_payload.get("major") or {}
    else:
        major = {}

    latency_table = {
        "fast_ann_p50_ms": fast_ann.get("p50_ms"),
        "vp_ann_p50_ms": (vp.get("ann") or {}).get("p50_ms") if isinstance(vp.get("ann"), dict) else vp.get("ann_p50_ms"),
        "st_phi_128_encode_p50_ms": st.get("encode_p50_ms"),
        "st_phi_256_encode_p50_ms": st.get("encode_p50_ms"),
        "nova_threat_p50_ms": (major.get("latency_summary") or {}).get("threat_fast_p50"),
        "enterprise_fast_p50_ms": (major.get("latency_summary") or {}).get("enterprise_fast_p50"),
        "mesie_ann_p50_ms": (major.get("latency_summary") or {}).get("mesie_ann_p50"),
        "swarm_10k_ms_per_agent": (major.get("latency_summary") or {}).get("swarm_10k_ms_per_agent"),
    }

    release = {
        "title": "MESIE COMPUTING FAMILY",
        "protocol": "MESIE-COMPUTING-FAMILY-RELEASE/1.0",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "virtual_products": products,
        "tri_agent_squads": squads,
        "latency_table_ms": latency_table,
        "industry_benchmarks": {
            "verdict": major.get("verdict"),
            "win_rate": major.get("win_rate"),
            "wins": major.get("wins"),
            "row_count": len(major.get("rows") or []),
        },
        "phases": phases,
        "system_ties": {
            "processor": "http://127.0.0.1:8750",
            "universal_mcp": "http://127.0.0.1:8765",
            "career_hub": "http://127.0.0.1:8767",
            "sovereign_os": "http://127.0.0.1:8770",
            "depth_catalog": "GET /processor/depth",
            "native_dsl_catalog": "GET /processor/dsl",
            "triple_protocol": "deliverables/cloudcolony/TRIPLE_PROTOCOL_MANIFEST.json",
            "native_release": "deliverables/research/papers/NATIVE_RELEASE_MANIFEST.json",
        },
        "all_phases_ok": all(p.get("ok", True) for p in phases),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(release, indent=2) + "\n", encoding="utf-8")
    return release


def _print_dashboard(release: Dict[str, Any]) -> None:
    print("\n" + "=" * 72)
    print("  MESIE COMPUTING FAMILY — LIVE BENCHMARK DASHBOARD")
    print("=" * 72)

    print("\n## 8 Virtual Products (live stats)")
    print(f"{'SKU':<22} {'Invocations':>12} {'p50 ms':>10} {'Health':>8}")
    print("-" * 56)
    for p in release.get("virtual_products") or []:
        print(
            f"{p.get('sku',''):<22} {p.get('invocations',0):>12} "
            f"{p.get('p50_ms',0):>10.4f} {'OK' if p.get('healthy') else 'DOWN':>8}"
        )

    print("\n## Tri-Agent Squads (3 × 3 agents)")
    print(f"{'Squad':<16} {'Agents':<40} {'Mission'}")
    print("-" * 72)
    squad_agents = {
        "ops-triad": "health, benchmark, bridge",
        "quality-triad": "pytest, commercial pack, metrics",
        "intel-triad": "embed, match, scientific text",
        "research-triad": "metamaterial, domain suite, release pack",
    }
    for s in release.get("tri_agent_squads") or []:
        sid = s.get("squad_id", "")
        agents = squad_agents.get(sid, ", ".join(a.get("role", "") for a in s.get("agents", [])))
        print(f"{s.get('name',''):<16} {agents:<40} {s.get('mission','')}")

    print("\n## Live Latency Table (ms)")
    lt = release.get("latency_table_ms") or {}
    for k, v in lt.items():
        if v is not None:
            print(f"  {k}: {v}")

    ind = release.get("industry_benchmarks") or {}
    if ind.get("verdict"):
        print(f"\n## Industry Benchmarks: {ind.get('wins')}/{ind.get('row_count')} wins "
              f"({ind.get('win_rate')}%) — verdict: {ind.get('verdict')}")

    print(f"\nManifest: {OUT}")
    print(f"All phases OK: {release.get('all_phases_ok')}")
    print("=" * 72 + "\n")


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="MESIE COMPUTING FAMILY full benchmarks")
    parser.add_argument("--trials", type=int, default=200)
    parser.add_argument("--mc-trials", type=int, default=100)
    parser.add_argument("--skip-squads", action="store_true")
    args = parser.parse_args()

    release = run_family_benchmarks(trials=args.trials, mc_trials=args.mc_trials, skip_squads=args.skip_squads)
    _print_dashboard(release)
    return 0 if release.get("all_phases_ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())