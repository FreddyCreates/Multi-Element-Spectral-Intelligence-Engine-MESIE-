"""MESIE Pro Update suite — domains, field I/O, hive mesh, external benchmarks."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data import list_references, load_reference_record
from mesie.enterprise import EnterpriseAICopilot
from mesie.enterprise.fast_cycle import FastEnterpriseCycle
from mesie.evaluation.external_benchmarks import ExternalBenchmarkPack
from mesie.field_io import CSVSpectralIngest, UDPSpectralFrameParser
from mesie.library.domain_corpus import domain_catalog, load_domain_corpus
from mesie.sovereign.anchor_calibration import calibrate_field_anchors
from mesie.sovereign.sovereign_mesh import SovereignMesh


def _write_sample_csv(path: Path) -> None:
    ref = load_reference_record("earthquake_psd_reference")
    c = ref.components[0]
    lines = ["frequency,amplitude"]
    for f, a in zip(c.frequency[:64], c.amplitude[:64]):
        lines.append(f"{f},{a}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _render_md(payload: dict) -> str:
    pos = payload["positioning"]
    lat = pos["latency_posture"]
    lines = [
        "# MESIE Pro Update — Specialized General Expansion",
        "",
        f"**Version:** {payload['version']}",
        f"**Overall:** `{payload['overall']}`",
        f"**Runtime:** {payload['elapsed_s']}s",
        "",
        "## Positioning vs general LLM",
        "",
        "| Dimension | General LLM | MESIE / SOLUS |",
        "|-----------|-------------|---------------|",
        f"| Reasoning breadth | {pos['reasoning_breadth']['general_llm']} | {pos['reasoning_breadth']['mesie_solus']} |",
        f"| Tool ecosystem | {pos['tool_ecosystem']['general_llm']} | {pos['tool_ecosystem']['mesie']} |",
        "",
        "## Latency posture",
        "",
        f"- Threat-fast p50: **{lat['threat_fast_p50_ms']} ms** (sub-ms: {lat['threat_fast_sub_ms']})",
        f"- Enterprise-fast p50: **{lat['enterprise_fast_p50_ms']} ms** (sub-ms: {lat['enterprise_fast_sub_ms']})",
        "",
        "## External comparisons",
        "",
        "| System | Metric | Baseline ms | MESIE ms | Wins |",
        "|--------|--------|-------------|----------|------|",
    ]
    for c in payload["external"]["comparisons"]:
        win = "yes" if c["mesie_wins"] else "no"
        lines.append(f"| {c['system']} | {c['metric']} | {c['value_ms']} | {c['mesie_value_ms']} | {win} |")

    lines.extend(["", "## Pro update checks", ""])
    for chk in payload["checks"]:
        lines.append(f"- [{'PASS' if chk['ok'] else 'FAIL'}] **{chk['name']}** — {chk['detail']}")

    lines.extend(["", "## Gaps named plainly", ""])
    for g in payload["gaps_named"]:
        lines.append(f"- {g}")

    lines.extend(["", "## Tier 1 / Tier 2 ready", ""])
    for t in payload["tier1_ready"]:
        lines.append(f"- **T1:** {t}")
    for t in payload["tier2_ready"]:
        lines.append(f"- **T2:** {t}")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=200)
    args = parser.parse_args()

    t0 = time.perf_counter()
    checks: list[tuple[str, bool, str]] = []

    catalog = domain_catalog()
    corpus = load_domain_corpus()
    checks.append(("Domain corpus", len(corpus) >= 12, f"{len(corpus)} records, {len(catalog['domains'])} domains"))

    sample_csv = ROOT / "data" / "samples" / "spectral_ingest_sample.csv"
    _write_sample_csv(sample_csv)
    rec, csv_rep = CSVSpectralIngest().ingest(sample_csv)
    checks.append(("CSV field ingest", csv_rep.ok, f"{csv_rep.points} points"))

    udp = UDPSpectralFrameParser()
    frame = udp.encode_json(rec, seq=1)
    rec2, udp_rep = udp.parse(frame)
    checks.append(("UDP frame parse", udp_rep.ok, f"{udp_rep.format} {udp_rep.points} pts"))

    cal = calibrate_field_anchors()
    checks.append(("Anchor calibration", cal.ok, f"{cal.calibrated} anchors, drift={cal.mean_drift_pct}%"))

    mesh = SovereignMesh()
    bundle = mesh.export_bundle()
    checks.append(("Mesh export", bool(bundle.bundle_hash), f"peer={bundle.peer_id}"))

    copilot = EnterpriseAICopilot()
    tools = copilot.sovereign_tools()
    checks.append(("Copilot tools", len(tools) >= 20, f"{len(tools)} tools"))

    fast = copilot.invoke_tool("mesie_fast_enterprise_cycle", {"record": corpus[0], "candidate": corpus[1]})
    checks.append(
        ("Fast enterprise cycle",
         fast.get("sla_ok", False) or fast.get("latency_ms", 999) < 10,
         f"{fast.get('latency_ms')}ms"),
    )

    hive = copilot.invoke_tool("mesie_swarm_hive_coordinate", {"record": corpus[0], "n_agents": 1000})
    checks.append(("Hive mind 1K", hive.get("ok", False), f"{hive.get('ms_per_agent')} ms/agent"))

    external = ExternalBenchmarkPack(n_trials=args.trials).run()
    checks.append(("External benchmark", external.overall == "mesie_competitive", external.overall))

    fast_cycle = FastEnterpriseCycle()
    fast_cycle.index_corpus(corpus)
    ent = fast_cycle.run(corpus[0], candidate=corpus[1])

    payload = {
        "version": "pro-1.0.0",
        "company": "NeuroSwarmAI",
        "references": len(list_references()),
        "corpus_size": len(corpus),
        "copilot_tools": len(tools),
        "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in checks],
        "passed": sum(1 for _, ok, _ in checks if ok),
        "total": len(checks),
        "positioning": external.positioning,
        "gaps_named": external.gaps_named,
        "tier1_ready": external.tier1_ready,
        "tier2_ready": external.tier2_ready,
        "external": external.to_dict(),
        "calibration": cal.to_dict(),
        "mesh_bundle_hash": bundle.bundle_hash,
        "fast_enterprise": ent.to_dict(),
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "overall": "pro_update_ready" if all(ok for _, ok, _ in checks) else "pro_update_partial",
    }

    out_json = ROOT / "deliverables" / "MESIE_Pro_Update_Report.json"
    out_md = ROOT / "deliverables" / "MESIE_Pro_Update_Report.md"
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    out_md.write_text(_render_md(payload), encoding="utf-8")

    passed = payload["passed"]
    print(f"=== MESIE Pro Update ===\n{passed}/{len(checks)} checks | {payload['overall']}")
    print(f"Corpus: {len(corpus)} | Tools: {len(tools)} | Threat p50: {external.positioning['latency_posture']['threat_fast_p50_ms']}ms")
    print(f"Enterprise-fast p50: {external.positioning['latency_posture']['enterprise_fast_p50_ms']}ms")
    print(f"JSON: {out_json}")
    print(f"MD:   {out_md}")
    sys.exit(0 if passed == len(checks) else 1)


if __name__ == "__main__":
    main()