"""Enterprise AI — agent memory, SOLUS MEMORY arm, sovereign copilot tools."""

from dataclasses import asdict

from data import list_references, load_reference_record
from mesie.enterprise import EnterpriseAICopilot, EnterpriseAgentMemory, build_enterprise_tool_schemas
from mesie.octopus import OctopusController, OctopusConfig
from mesie.sdk.solus import SDKSolusOrganism


def test_enterprise_tool_schemas():
    schemas = build_enterprise_tool_schemas()
    names = {s["function"]["name"] for s in schemas}
    assert "mesie_agent_memory_recall" in names
    assert "mesie_solus_reason" in names
    assert "mesie_enterprise_copilot_cycle" in names


def test_agent_memory_store_recall():
    refs = [load_reference_record(n) for n in list_references()[:4]]
    mem = EnterpriseAgentMemory()
    mem.index_corpus(refs)
    mem.store_turn(
        "s1",
        refs[0],
        neighbors=[{"record_id": "a", "similarity": 0.9}],
        research_hits=["hit"],
        technical_hits=["tech"],
        solus_conclusion="ok",
        elapsed_ms=12.0,
    )
    recall = mem.recall(refs[0], session_id="s1")
    assert recall["ok"]
    assert recall["session_turns"] == 1


def test_solus_tend_agent_session():
    org = SDKSolusOrganism()
    out = org.tend_agent_session({"session_id": "e1", "turns": 2, "neighbors": 3, "sla_ok": True})
    assert out["enterprise_ai"]
    assert out["sovereign"]
    assert out["logic_caretaker"]["ok"]


def test_enterprise_copilot_cycle():
    refs = [load_reference_record(n) for n in list_references()[:4]]
    copilot = EnterpriseAICopilot(session_id="test-copilot", sla_latency_ms=500.0)
    copilot.index_corpus(refs)
    report = copilot.run_cycle(refs[0])
    assert report.sovereign
    assert len(report.maesi_neighbors) >= 1
    assert report.memory_recall["ok"]


def test_octopus_enterprise_ai_memory_arm():
    refs = [load_reference_record(n) for n in list_references()[:2]]
    octo = OctopusController(config=OctopusConfig(use_solus_memory=True))
    report = octo.run_standard_cycle(refs[0], candidate=refs[1])
    assert report.enterprise_ai["sovereign"]
    assert report.enterprise_ai["memory_arm"] == "solus"
    assert report.solus_memory["minted_token"]["token_id"]
    assert report.receipt_chain["verified"]


def test_invoke_sovereign_tools():
    refs = [load_reference_record(n) for n in list_references()[:3]]
    copilot = EnterpriseAICopilot()
    copilot.index_corpus(refs)
    solus = copilot.invoke_tool("mesie_solus_reason", {"record": refs[0]})
    assert solus["ok"]
    cycle = copilot.invoke_tool(
        "mesie_enterprise_copilot_cycle",
        {"record": refs[0], "session_id": "invoke-test"},
    )
    assert cycle["sovereign"]
    assert "plain_summary" in cycle
    assert cycle.get("minted_token")
    assert cycle.get("sovereign_vault", {}).get("deposited")


def test_enterprise_copilot_mints_receipt():
    refs = [load_reference_record(n) for n in list_references()[:3]]
    copilot = EnterpriseAICopilot(sla_latency_ms=500.0)
    copilot.index_corpus(refs)
    report = copilot.run_cycle(refs[0])
    assert report.minted_token
    assert report.receipt_chain.get("verified") is True
    assert report.sovereign_vault.get("deposited")