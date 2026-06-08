"""20 multi-enterprise tests — 10 industries + 10 enterprise AI stack checks."""

from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data import list_references, load_reference_record
from mesie.enterprise import EnterpriseAICopilot, SovereignVault
from mesie.enterprise.receipt_chain import ComputationalReceiptChain
from mesie.octopus import OctopusController, OctopusConfig
from mesie.sdk import MAESIClient, SOLUS_BRAND, FORMAL_COMPOSITION
from mesie.sdk.native_ai import NativeLocalAIEngine
from mesie.sdk.solus import SolusFormalStack, composition_manifest
from scripts.monte_carlo_enterprise_benchmark import ENTERPRISE_CASES, MonteCarloEnterpriseRunner


def _row(
    test_id: str,
    name: str,
    industry: str,
    ok: bool,
    ms: float,
    detail: str,
    *,
    trials: int = 1,
    success_rate: float | None = None,
) -> dict:
    row = {
        "id": test_id,
        "name": name,
        "industry": industry,
        "ok": ok,
        "latency_ms": round(ms, 2),
        "detail": detail,
    }
    if trials > 1:
        row["trials"] = trials
    if success_rate is not None:
        row["success_rate"] = round(success_rate, 4)
    return row


def _parse_args() -> tuple[int, bool, float]:
    trials = 50
    use_benchmark = True
    pass_threshold = 0.85
    argv = sys.argv[1:]
    if "--trials" in argv:
        trials = int(argv[argv.index("--trials") + 1])
    if "--no-benchmark" in argv:
        use_benchmark = False
    if "--threshold" in argv:
        pass_threshold = float(argv[argv.index("--threshold") + 1])
    return trials, use_benchmark, pass_threshold


def main() -> None:
    trials, use_benchmark, pass_threshold = _parse_args()
    bench_label = "enterprise-v2" if use_benchmark else "native"
    print(f"=== Multi-Enterprise 20 Tests — {SOLUS_BRAND} ===")
    print(f"Benchmark: {bench_label} | industry trials: {trials} | pass threshold: {pass_threshold:.0%}\n")
    t_suite = time.perf_counter()
    refs = [load_reference_record(n) for n in list_references()]
    results: list[dict] = []

    # E01–E10: Monte Carlo per industry enterprise use case
    mc = MonteCarloEnterpriseRunner(seed=42, use_enterprise_benchmark=use_benchmark)
    for i, case in enumerate(ENTERPRISE_CASES, start=1):
        t0 = time.perf_counter()
        report = mc.run_case(case, n_trials=trials)
        trial_ok = report.success_rate >= pass_threshold
        ms = (time.perf_counter() - t0) * 1000
        if report.sample_details:
            detail = report.sample_details[0]
        else:
            detail = f"score={report.mean_score:.3f} rate={report.success_rate:.1%}"
        results.append(
            _row(
                f"E{i:02d}",
                case.name,
                case.industry,
                trial_ok,
                ms,
                detail,
                trials=trials,
                success_rate=report.success_rate,
            )
        )
        mark = "PASS" if trial_ok else "FAIL"
        print(f"  [{mark}] E{i:02d} {case.industry:12} {case.name} ({report.success_rate:.0%} @ {trials} trials)")

    copilot = EnterpriseAICopilot(session_id="multi-20", sla_latency_ms=150.0)
    copilot.index_corpus(refs[:8])

    # E11 agent memory
    t0 = time.perf_counter()
    r = copilot.run_cycle(refs[0], session_id="e11")
    recall = copilot.memory.recall(refs[0], session_id="e11")
    ok = len(r.maesi_neighbors) >= 1 and recall["ok"]
    results.append(_row("E11", "Agent Spectral Memory", "Enterprise AI", ok, (time.perf_counter() - t0) * 1000, f"neighbors={len(r.maesi_neighbors)}"))
    print(f"  [{'PASS' if ok else 'FAIL'}] E11 Enterprise AI  Agent Spectral Memory")

    # E12 SOLUS MEMORY arm
    t0 = time.perf_counter()
    octo = OctopusController(config=OctopusConfig(use_solus_memory=True))
    rep = octo.run_standard_cycle(refs[0], candidate=refs[1])
    ok = rep.solus_memory.get("minted_token") and rep.receipt_chain.get("verified")
    results.append(_row("E12", "SOLUS MEMORY Arm", "Enterprise AI", ok, (time.perf_counter() - t0) * 1000, rep.enterprise_ai.get("conclusion", "")[:80]))
    print(f"  [{'PASS' if ok else 'FAIL'}] E12 Enterprise AI  SOLUS MEMORY Arm")

    # E13 sovereign vault deposit
    t0 = time.perf_counter()
    r = copilot.run_cycle(refs[2], session_id="e13-vault")
    ok = r.sovereign_vault.get("deposited", False)
    results.append(_row("E13", "Sovereign Vault Deposit", "Enterprise AI", ok, (time.perf_counter() - t0) * 1000, f"vault_size={r.sovereign_vault.get('vault_size')}"))
    print(f"  [{'PASS' if ok else 'FAIL'}] E13 Enterprise AI  Sovereign Vault Deposit")

    # E14 receipt chain
    t0 = time.perf_counter()
    chain = ComputationalReceiptChain()
    _, tok = chain.append_spectral_cycle(
        cycle_id="e14", record_id="test", work={"match_score": 0.7},
        solus_proof={"logic_confidence": 0.8, "signal_ratio": 0.6, "proof_steps": 3},
    )
    ok = chain.verify_chain().verified and bool(tok.token_id)
    results.append(_row("E14", "Receipt Chain Seal", "Enterprise AI", ok, (time.perf_counter() - t0) * 1000, f"token={tok.token_id[:12]}"))
    print(f"  [{'PASS' if ok else 'FAIL'}] E14 Enterprise AI  Receipt Chain Seal")

    # E15 formal stack
    t0 = time.perf_counter()
    stack = SolusFormalStack()
    comp = refs[0].components[0]
    out = stack.compose_cycle(comp.frequency.tolist(), comp.amplitude.tolist(), cycle_context={"record_id": refs[0].record_id})
    ok = out["third_party"] is False and set(out["formal_models"].keys()) == {"logic", "reasoning", "emergence", "adaptation"}
    results.append(_row("E15", "Formal Stack Compose", "Enterprise AI", ok, (time.perf_counter() - t0) * 1000, out.get("composition_hash", "")[:16]))
    print(f"  [{'PASS' if ok else 'FAIL'}] E15 Enterprise AI  Formal Stack Compose")

    # E16 native AI stream
    t0 = time.perf_counter()
    engine = NativeLocalAIEngine(session_id="e16", deliverable_dir=str(ROOT / "deliverables" / "native_ai" / "multi20"))
    gen = engine.stream_generate(refs[:4], run_id="multi_enterprise_20", write_deliverable=True)
    phases = []
    try:
        while True:
            ev = next(gen)
            phases.append(ev.phase.value)
    except StopIteration as stop:
        report = stop.value
    ok = report is not None and "complete" in phases and report.minted_token
    results.append(_row("E16", "Native AI Stream Generate", "Enterprise AI", ok, (time.perf_counter() - t0) * 1000, f"phases={len(phases)}"))
    print(f"  [{'PASS' if ok else 'FAIL'}] E16 Enterprise AI  Native AI Stream Generate")

    # E17 MAESI SDK + SOLUS
    t0 = time.perf_counter()
    client = MAESIClient(use_solus_caretakers=True, use_solus_math_layer=True)
    run = client.run_full(refs[:4], benchmark=False)
    ok = run.solus_organism is not None and client.math_layer is not None
    results.append(_row("E17", "MAESI SDK SOLUS Fusion", "Enterprise AI", ok, (time.perf_counter() - t0) * 1000, run.plain_summary[:80]))
    print(f"  [{'PASS' if ok else 'FAIL'}] E17 Enterprise AI  MAESI SDK SOLUS Fusion")

    # E18 vault recall
    t0 = time.perf_counter()
    vault = SovereignVault()
    vault.deposit(
        token=tok,
        receipt=chain._receipts[-1],
        composition={"formula": FORMAL_COMPOSITION, "composition_hash": "e18"},
        results={"conclusion": "recall test", "match_score": 0.7},
        workflow={"workflow_id": "e18"},
        ai_patterns={"formal_models": ["logic", "reasoning"]},
    )
    hits = vault.recall(results={"match_score": 0.7}, top_k=1)
    ok = hits.get("ok") and len(hits.get("hits", [])) >= 1
    results.append(_row("E18", "Vault Embed Recall", "Enterprise AI", ok, (time.perf_counter() - t0) * 1000, f"hits={len(hits.get('hits', []))}"))
    print(f"  [{'PASS' if ok else 'FAIL'}] E18 Enterprise AI  Vault Embed Recall")

    # E19 copilot tools
    t0 = time.perf_counter()
    tool_ok = copilot.invoke_tool("mesie_vault_status", {}).get("sovereign", False)
    solus_ok = copilot.invoke_tool("mesie_solus_reason", {"record": refs[0]}).get("ok", False)
    ok = tool_ok and solus_ok
    results.append(_row("E19", "Sovereign Copilot Tools", "Enterprise AI", ok, (time.perf_counter() - t0) * 1000, "vault_status+solus_reason"))
    print(f"  [{'PASS' if ok else 'FAIL'}] E19 Enterprise AI  Sovereign Copilot Tools")

    # E20 full stack SLA
    t0 = time.perf_counter()
    final = copilot.run_cycle(refs[0], session_id="e20-final")
    ms = (time.perf_counter() - t0) * 1000
    ok = final.sla_ok and final.sovereign_vault.get("deposited") and len(final.maesi_neighbors) >= 1
    results.append(_row("E20", "Full Stack SLA Cycle", "Enterprise AI", ok, ms, final.plain_summary[:100]))
    print(f"  [{'PASS' if ok else 'FAIL'}] E20 Enterprise AI  Full Stack SLA Cycle")

    passed = sum(1 for r in results if r["ok"])
    elapsed = time.perf_counter() - t_suite
    by_industry: dict[str, list] = {}
    for r in results:
        by_industry.setdefault(r["industry"], []).append(r)

    payload = {
        "suite": "multi_enterprise_20",
        "benchmark": bench_label,
        "industry_trials": trials,
        "pass_threshold": pass_threshold,
        "brand": SOLUS_BRAND,
        "formula": FORMAL_COMPOSITION,
        "sovereign": True,
        "third_party": False,
        "total_tests": 20,
        "passed": passed,
        "failed": 20 - passed,
        "success_rate": round(passed / 20, 4),
        "enterprise_grade": passed >= 17,
        "elapsed_s": round(elapsed, 2),
        "manifest": composition_manifest(),
        "by_industry": {
            ind: {"passed": sum(1 for x in items if x["ok"]), "total": len(items)}
            for ind, items in by_industry.items()
        },
        "tests": results,
    }

    out_json = ROOT / "deliverables" / "MESIE_Multi_Enterprise_20_Report.json"
    out_md = ROOT / "deliverables" / "MESIE_Multi_Enterprise_20_Report.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    lines = [
        "# MESIE Multi-Enterprise 20 Test Report",
        "",
        f"*Generated — 20 tests across {len(by_industry)} industries/stacks*",
        "",
        f"- **Benchmark:** {bench_label} ({trials} trials/industry, threshold {pass_threshold:.0%})",
        f"- **Passed:** {passed}/20 ({passed/20*100:.0f}%)",
        f"- **Enterprise grade (≥17):** {'PASS' if payload['enterprise_grade'] else 'REVIEW'}",
        f"- **Runtime:** {payload['elapsed_s']} s",
        "",
        "| ID | Industry | Test | Result | Rate | ms |",
        "|----|----------|------|--------|------|-----|",
    ]
    for r in results:
        rate = f"{r['success_rate']:.0%}" if "success_rate" in r else "—"
        lines.append(
            f"| {r['id']} | {r['industry']} | {r['name']} | {'PASS' if r['ok'] else 'FAIL'} | {rate} | {r['latency_ms']:.1f} |"
        )
    lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")

    print(f"\n{passed}/20 passed ({passed/20*100:.0f}%) | grade={'PASS' if payload['enterprise_grade'] else 'REVIEW'} | {elapsed:.1f}s")
    print(f"JSON: {out_json}")
    print(f"Markdown: {out_md}")
    sys.exit(0 if passed >= 17 else 1)


if __name__ == "__main__":
    main()