"""Enterprise AI suite — sovereign agent memory, SOLUS MEMORY arm, copilot tools."""

from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data import list_references, load_reference_record
from mesie.enterprise import EnterpriseAICopilot, build_enterprise_tool_schemas
from mesie.octopus import OctopusController, OctopusConfig
from mesie.sdk import SOLUS_BRAND


def _scenario_agent_memory(copilot: EnterpriseAICopilot, refs: list) -> dict:
    copilot.index_corpus(refs)
    r1 = copilot.run_cycle(refs[0], session_id="ent-session-1")
    r2 = copilot.run_cycle(refs[1], session_id="ent-session-1")
    recall = copilot.memory.recall(refs[0], session_id="ent-session-1")
    return {
        "name": "agent_memory",
        "ok": len(r1.maesi_neighbors) >= 1 and recall["ok"],
        "sla_ok": r1.sla_ok and r2.sla_ok,
        "turns": copilot.memory.session_summary("ent-session-1"),
        "recall": recall,
    }


def _scenario_solus_memory_arm(refs: list) -> dict:
    octo = OctopusController(config=OctopusConfig(use_solus_memory=True))
    report = octo.run_standard_cycle(refs[0], candidate=refs[1])
    ea = report.enterprise_ai
    return {
        "name": "solus_memory_arm",
        "ok": (
            ea.get("sovereign")
            and ea.get("memory_arm") == "solus"
            and report.receipt_chain.get("verified")
            and report.solus_memory.get("minted_token")
        ),
        "minted_token": ea.get("minted_token"),
        "receipt_chain": report.receipt_chain,
        "solus_conclusion": ea.get("conclusion", "")[:120],
        "summary": report.plain_summary[:200],
    }


def _scenario_sovereign_tools(copilot: EnterpriseAICopilot, refs: list) -> dict:
    schemas = build_enterprise_tool_schemas()
    names = [s["function"]["name"] for s in schemas]
    invoke_recall = copilot.invoke_tool(
        "mesie_agent_memory_recall",
        {"record": refs[0], "session_id": "tool-test", "top_k": 2},
    )
    invoke_solus = copilot.invoke_tool(
        "mesie_solus_reason",
        {"record": refs[0], "theorem": "enterprise copilot tools are sovereign"},
    )
    return {
        "name": "sovereign_tools",
        "ok": len(names) >= 6 and invoke_solus.get("ok"),
        "tool_count": len(names),
        "tools": names,
        "invoke_recall_ok": invoke_recall.get("ok", False),
        "invoke_solus_ok": invoke_solus.get("ok", False),
    }


def _scenario_sovereign_vault(copilot: EnterpriseAICopilot, refs: list) -> dict:
    """Minted tokens deposited, embedded, and recalled from sovereign vault."""
    r1 = copilot.run_cycle(refs[0], session_id="vault-suite")
    r2 = copilot.run_cycle(refs[1], session_id="vault-suite")
    status = copilot.invoke_tool("mesie_vault_status", {})
    recall = copilot.invoke_tool(
        "mesie_vault_recall",
        {"results": {"match_score": 0.7}, "top_k": 2},
    )
    return {
        "name": "sovereign_vault",
        "ok": (
            r1.sovereign_vault.get("deposited")
            and r2.sovereign_vault.get("vault_size", 0) >= 2
            and status.get("vault_size", 0) >= 2
            and recall.get("ok")
        ),
        "vault_size": status.get("vault_size"),
        "compound_work_units": status.get("total_work_units"),
        "recall_hits": len(recall.get("hits", [])),
    }


def _scenario_monte_carlo_alignment(copilot: EnterpriseAICopilot, refs: list) -> dict:
    """Align with enterprise use case ai_copilot_rag: neighbors >= 1 and latency < 100ms."""
    t0 = time.perf_counter()
    report = copilot.run_cycle(refs[0], session_id="mc-align")
    ms = (time.perf_counter() - t0) * 1000
    ok = len(report.maesi_neighbors) >= 1 and ms < 100
    return {
        "name": "monte_carlo_ai_copilot_rag",
        "ok": ok,
        "latency_ms": round(ms, 2),
        "neighbors": len(report.maesi_neighbors),
        "metric": "neighbors >= 1 and latency < 100ms",
    }


def main() -> None:
    print(f"=== Enterprise AI Suite — {SOLUS_BRAND} sovereign copilot ===\n")
    refs = [load_reference_record(n) for n in list_references()[:6]]
    copilot = EnterpriseAICopilot(session_id="enterprise-suite", sla_latency_ms=100.0)

    scenarios = [
        _scenario_agent_memory(copilot, refs),
        _scenario_solus_memory_arm(refs),
        _scenario_sovereign_tools(copilot, refs),
        _scenario_sovereign_vault(copilot, refs),
        _scenario_monte_carlo_alignment(copilot, refs),
    ]
    passed = sum(1 for s in scenarios if s["ok"])
    cycle = copilot.run_cycle(refs[0], session_id="final-report")

    payload = {
        "brand": SOLUS_BRAND,
        "focus": "enterprise_ai",
        "formal_stack": "Logic ⊗ Reasoning ⊗ Emergence ⊗ Adaptation",
        "own_models_only": True,
        "sovereign": True,
        "third_party_deps": False,
        "scenarios": scenarios,
        "passed": passed,
        "total": len(scenarios),
        "all_pass": passed == len(scenarios),
        "final_cycle": asdict(cycle),
        "tool_schemas": build_enterprise_tool_schemas(),
    }

    out = ROOT / "deliverables" / "Enterprise_AI_Suite_Report.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    for s in scenarios:
        mark = "PASS" if s["ok"] else "FAIL"
        print(f"  [{mark}] {s['name']}")
    print(f"\n{passed}/{len(scenarios)} scenarios passed | SLA cycle: {'PASS' if cycle.sla_ok else 'REVIEW'}")
    print(f"Summary: {cycle.plain_summary}")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()