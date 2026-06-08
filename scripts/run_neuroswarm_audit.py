"""NeuroSwarmAI audit evidence pack — maps external critique → measured SDK benchmarks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.evaluation.neuroswarm_audit import NeuroSwarmClaimsVerifier


def _render_md(report: dict) -> str:
    lines = [
        f"# NeuroSwarmAI Audit Evidence Pack",
        "",
        f"**Company:** [{report['company']}]({report['company_url']})",
        f"**Stack:** {report['product_stack']}",
        f"**Audit version:** {report['audit_version']}",
        f"**Overall verdict:** `{report['overall_verdict']}`",
        f"**Runtime:** {report['elapsed_s']}s",
        "",
        "## Hardware & test conditions",
        "",
        f"- Platform: {report['hardware_profile']['platform']}",
        f"- Processor: {report['hardware_profile']['processor']}",
        f"- Trials: {report['test_conditions']['n_latency_trials']}",
        f"- Payload points: {report['test_conditions']['payload_points_typical']}",
        f"- Airgapped: {report['test_conditions']['airgapped']}",
        f"- Third-party APIs: {report['test_conditions']['third_party_apis']}",
        "",
        "## Latency summary (ms)",
        "",
        "| Path | p50 | p95 | p99 |",
        "|------|-----|-----|-----|",
    ]
    lat = report["latency"]
    for key, label in [
        ("match_records", "Spectral match"),
        ("cosine_ann", "Cosine ANN"),
        ("fingerprint_query", "Fingerprint query"),
        ("threat_fast_path", "Threat-fast (sensor→decision)"),
        ("enterprise_full_octopus", "Enterprise-full (Octopus)"),
    ]:
        if key in ("threat_fast_path", "enterprise_full_octopus"):
            s = lat[key]
        else:
            s = lat["spectral_ops"][key]
        lines.append(f"| {label} | {s['p50_ms']} | {s['p95_ms']} | {s['p99_ms']} |")

    lines.extend([
        "",
        "## Critique → evidence mapping",
        "",
        "| ID | Critique | Verdict | Measured highlight |",
        "|----|----------|---------|-------------------|",
    ])
    for f in report["findings"]:
        measured = f.get("measured", {})
        highlight = ""
        if "match_p50_ms" in measured:
            highlight = f"match p50={measured['match_p50_ms']}ms"
        elif "p50_ms" in measured:
            highlight = f"p50={measured['p50_ms']}ms"
        elif "airgapped" in measured:
            highlight = f"airgapped={measured['airgapped']}"
        elif "audit_version" in measured:
            highlight = f"harness v{measured['audit_version']}"
        else:
            highlight = "see JSON"
        lines.append(f"| {f['finding_id']} | {f['critique_topic']} | `{f['verdict']}` | {highlight} |")

    lines.extend([
        "",
        "## Audit responses",
        "",
    ])
    for f in report["findings"]:
        lines.extend([
            f"### {f['finding_id']}: {f['critique_topic']}",
            "",
            f"**Verdict:** `{f['verdict']}`",
            "",
            f["audit_response"],
            "",
        ])
        if f.get("remediation"):
            lines.append(f"*Remediation:* {f['remediation']}")
            lines.append("")

    lines.extend([
        "## Play next",
        "",
    ])
    for item in report["play_next"]:
        lines.append(f"- {item}")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="NeuroSwarmAI claims audit verifier")
    parser.add_argument("--trials", type=int, default=1000, help="Latency trial count")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    verifier = NeuroSwarmClaimsVerifier(n_latency_trials=args.trials, seed=args.seed)
    report = verifier.run_audit()
    payload = report.to_dict()

    out_json = ROOT / "deliverables" / "NeuroSwarmAI_Audit_Evidence.json"
    out_md = ROOT / "deliverables" / "NeuroSwarmAI_Audit_Evidence.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    out_md.write_text(_render_md(payload), encoding="utf-8")

    supported = sum(1 for f in payload["findings"] if f["verdict"] in {"supported", "remediated"})
    partial = sum(1 for f in payload["findings"] if f["verdict"] == "partial")
    gaps = sum(1 for f in payload["findings"] if f["verdict"] == "gap")

    e2e = payload["latency"]["threat_fast_path"]
    print("=== NeuroSwarmAI Audit Evidence Pack ===\n")
    print(f"Overall: {payload['overall_verdict']}")
    print(f"Findings: {supported} supported/remediated, {partial} partial, {gaps} gap")
    print(f"Threat-fast p50={e2e['p50_ms']}ms p99={e2e['p99_ms']}ms")
    print(f"Enterprise-full p50={payload['latency']['enterprise_full_octopus']['p50_ms']}ms")
    print(f"Elapsed: {payload['elapsed_s']}s")
    print(f"\nJSON: {out_json}")
    print(f"MD:   {out_md}")
    sys.exit(0 if gaps == 0 else 1)


if __name__ == "__main__":
    main()