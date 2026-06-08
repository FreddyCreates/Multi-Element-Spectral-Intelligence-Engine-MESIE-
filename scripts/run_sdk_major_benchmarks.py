"""SDK v1.4 major third-party benchmark suite + integration smoke."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.evaluation.external_benchmarks import ExternalBenchmarkPack
from mesie.evaluation.major_benchmarks import MajorBenchmarkHarness
from mesie.evaluation.neuroswarm_audit import NeuroSwarmClaimsVerifier
from mesie.sdk import MAESIClient, __sdk_version__
from data import load_reference_record


def _md(report: dict) -> str:
    lines = [
        f"# MAESI SDK Major Third-Party Benchmarks",
        "",
        f"**SDK:** {report['sdk_version']} | **MESIE:** {report['mesie_version']}",
        f"**Verdict:** `{report['major']['verdict']}`",
        f"**Win rate:** {report['major']['win_rate']}% ({report['major']['wins']}/{len(report['major']['rows'])})",
        "",
        "## Third-party comparison table",
        "",
        "| Category | Benchmark | Reference ms | MESIE ms | Wins |",
        "|----------|-----------|--------------|----------|------|",
    ]
    for r in report["major"]["rows"]:
        w = "yes" if r["mesie_wins"] else "no"
        lines.append(f"| {r['category']} | {r['benchmark']} | {r['reference_ms']} | {r['mesie_ms']:.4f} | {w} |")

    lines.extend([
        "",
        "## Assessment",
        "",
        report["major"]["assessment"],
        "",
        "## SDK integration",
        "",
        f"- SwarmSDK: {report['sdk_smoke']['swarm_version']}",
        f"- Corpus: {report['sdk_smoke']['corpus_size']} records",
        f"- Routing: {'OK' if report['sdk_smoke']['routing_ok'] else 'FAIL'}",
        "",
        "## Gaps",
        "",
    ])
    for g in report["major"]["gaps"]:
        lines.append(f"- {g}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=300)
    parser.add_argument("--agents", type=int, default=10000)
    args = parser.parse_args()

    t0 = time.perf_counter()
    client = MAESIClient()
    ew = load_reference_record("defense_ew_spectrum_reference")

    swarm_status = client.swarm.status().to_dict()
    mission = client.swarm_mission(ew, preset_id="ew", n_agents=500, jam_ground=True)
    major = MajorBenchmarkHarness(n_trials=args.trials, corpus_size=args.agents).run()
    external = ExternalBenchmarkPack(n_trials=args.trials).run()
    audit = NeuroSwarmClaimsVerifier(n_latency_trials=min(500, args.trials)).run_audit()

    payload = {
        "suite": "sdk_major_benchmarks",
        "sdk_version": __sdk_version__,
        "mesie_version": __import__("mesie").__version__,
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "sdk_smoke": {
            "swarm_version": swarm_status["version"],
            "corpus_size": swarm_status["corpus_size"],
            "routing_ok": swarm_status["routing_ok"],
            "mission_ok": mission.ok,
            "mission_ms": mission.coordination_ms,
        },
        "major": major.to_dict(),
        "external": external.to_dict(),
        "audit_overall": audit.overall_verdict,
    }

    out_json = ROOT / "deliverables" / "MAESI_SDK_Major_Benchmarks.json"
    out_md = ROOT / "deliverables" / "MAESI_SDK_Major_Benchmarks.md"
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    out_md.write_text(_md(payload), encoding="utf-8")

    print(f"=== MAESI SDK {__sdk_version__} Major Benchmarks ===")
    print(f"Verdict: {major.verdict}")
    print(f"Wins: {major.wins}/{len(major.rows)} ({major.win_rate}%)")
    print(f"Threat p50: {major.latency_summary['threat_fast_p50']}ms")
    print(f"Swarm 10K: {major.latency_summary['swarm_10k_ms_per_agent']} ms/agent")
    print(f"Mission ok: {mission.ok}")
    print(f"Report: {out_json}")
    sys.exit(0)


if __name__ == "__main__":
    main()