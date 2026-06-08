"""Full scenario simulation — military drone + enterprise civilian, real data backed."""

from __future__ import annotations

import json
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.scenarios.simulator import ScenarioSimulator
from mesie.sdk import __sdk_version__


def _md(payload: dict) -> str:
    mil = payload["military"]
    ent = payload["enterprise"]
    lines = [
        "# MESIE Scenario Simulation — Military Drone + Enterprise Civilian",
        "",
        f"**SDK:** {payload['sdk_version']}",
        f"**Platform:** {payload['platform']}",
        f"**Military:** {mil['passed']}/{mil['total']} PASS",
        f"**Enterprise:** {ent['passed']}/{ent['total']} PASS",
        "",
        "## Data provenance",
        "",
        "All scenarios use **bundled real reference data** — not synthetic placeholders:",
        "",
        "- **Military:** ITU/NATO RF bands, GPS/Starlink/Iridium satellite filings, EW swept spectrum, jamming profiles, Schumann resonances",
        "- **Enterprise:** Per-industry benchmark slices (v2), power grid harmonics, vibration, seismic, EEG, IEEE/ITU EM bands",
        "",
        "## Military drone scenarios",
        "",
        "| ID | Doctrine | Pass | ms/agent | Data sources |",
        "|----|----------|------|----------|--------------|",
    ]
    for r in mil["runs"]:
        ms = r["metrics"].get("ms_per_agent", "—")
        nsrc = len(r["data_sources"])
        lines.append(f"| {r['scenario_id']} | {r['doctrine']} | {'PASS' if r['ok'] else 'FAIL'} | {ms} | {nsrc} |")

    lines.extend([
        "",
        "## Enterprise civilian scenarios",
        "",
        "| ID | Industry | Pass | enterprise_fast ms | Benchmark slice |",
        "|----|----------|------|-------------------|-----------------|",
    ])
    for r in ent["runs"]:
        ms = r["metrics"].get("enterprise_fast_ms", "—")
        bench = r["metrics"].get("enterprise_benchmark_sample", "—")
        lines.append(f"| {r['scenario_id']} | {r['doctrine']} | {'PASS' if r['ok'] else 'FAIL'} | {ms} | {bench} |")

    lines.extend([
        "",
        "## Cross-domain thesis",
        "",
        "The **same virtual silicon stack** runs military drone swarms (EW/strike/ISR) and enterprise ",
        "civilian fleets (factory/energy/healthcare/telecom). Military paths stress jam failover and ",
        "10K coordination; enterprise paths stress SLA, anomaly separation, and sovereign vault workflows.",
        "",
        "## Reproducibility",
        "",
        "```bash",
        "python scripts/run_scenario_simulation_suite.py",
        "```",
        "",
        f"*Elapsed {payload['elapsed_s']}s | All pass: {payload['all_pass']}*",
    ])
    return "\n".join(lines)


def main() -> None:
    import mesie

    t0 = time.perf_counter()
    sim = ScenarioSimulator()
    result = sim.run_all()
    payload = {
        "suite": "scenario_simulation",
        "sdk_version": __sdk_version__,
        "mesie_version": mesie.__version__,
        "platform": platform.platform(),
        "elapsed_s": round(time.perf_counter() - t0, 2),
        **result,
    }

    out_json = ROOT / "deliverables" / "MESIE_Scenario_Simulation_Report.json"
    out_md = ROOT / "deliverables" / "MESIE_Scenario_Simulation_Report.md"
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    out_md.write_text(_md(payload), encoding="utf-8")

    print("=== MESIE Scenario Simulation ===")
    print(f"Military: {result['military']['passed']}/{result['military']['total']}")
    print(f"Enterprise: {result['enterprise']['passed']}/{result['enterprise']['total']}")
    print(f"All pass: {result['all_pass']}")
    print(f"Report: {out_json}")
    sys.exit(0 if result["all_pass"] else 1)


if __name__ == "__main__":
    main()