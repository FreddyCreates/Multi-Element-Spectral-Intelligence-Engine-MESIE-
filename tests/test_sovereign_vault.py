"""Sovereign Vault — minted tokens embedded and stored with the AI."""

from dataclasses import asdict

from data import list_references, load_reference_record
from mesie.enterprise import (
    ComputationalReceipt,
    ComputationalReceiptChain,
    MintedWorkToken,
    SovereignVault,
)
from mesie.octopus import OctopusController, OctopusConfig


def _mint_pair():
    chain = ComputationalReceiptChain()
    return chain.append_spectral_cycle(
        cycle_id="test_cycle",
        record_id="rec_test",
        work={"match_score": 0.8, "similarity": 0.75, "anomaly": 1.1},
        solus_proof={
            "conclusion": "logic holds",
            "logic_confidence": 0.9,
            "signal_ratio": 0.7,
            "proof_steps": 4,
            "formula": "Logic ⊗ Reasoning ⊗ Emergence ⊗ Adaptation",
            "formal_models": ["logic", "reasoning", "emergence", "adaptation"],
        },
    )


def test_vault_deposit_and_recall(tmp_path):
    vault = SovereignVault(persist_path=tmp_path / "vault.json", auto_persist=True)
    receipt, token = _mint_pair()
    entry = vault.deposit(
        token=token,
        receipt=receipt,
        composition={"formula": "Logic ⊗ Reasoning ⊗ Emergence ⊗ Adaptation", "composition_hash": "abc123"},
        results={"conclusion": "work done", "match_score": 0.8, "logic_confidence": 0.9},
        workflow={"workflow_id": "octopus_standard", "steps": [{"name": "memory"}]},
        ai_patterns={"formal_models": ["logic", "reasoning"]},
    )
    assert entry.vault_id
    assert len(entry.embedding) == 32
    assert entry.sovereign
    assert entry.third_party is False

    recall = vault.recall(results={"match_score": 0.8}, top_k=1)
    assert recall["ok"]
    assert len(recall["hits"]) >= 1
    assert recall["hits"][0]["token_id"] == token.token_id

    compound = vault.compound()
    assert compound.total_tokens == 1
    assert compound.total_work_units > 0

    assert (tmp_path / "vault.json").exists()


def test_vault_compounds_over_cycles(tmp_path):
    vault = SovereignVault(persist_path=tmp_path / "v.json", auto_persist=False)
    for i in range(5):
        receipt, token = _mint_pair()
        vault.deposit(
            token=token,
            receipt=receipt,
            composition={"composition_hash": f"hash_{i}"},
            results={"conclusion": f"cycle {i}", "match_score": 0.5 + i * 0.05},
            workflow={"workflow_id": "wf"},
            ai_patterns={"formal_models": ["logic"]},
            cycle_id=f"c{i}",
        )
    assert vault.size == 5
    assert vault.compound().total_work_units > 0


def test_octopus_deposits_to_vault():
    refs = [load_reference_record(n) for n in list_references()[:2]]
    octo = OctopusController(config=OctopusConfig(use_solus_memory=True))
    r1 = octo.run_standard_cycle(refs[0], candidate=refs[1])
    assert r1.solus_memory.get("vault", {}).get("deposited")
    assert r1.sovereign_vault.get("vault_id")

    r2 = octo.run_standard_cycle(refs[1], candidate=refs[0])
    assert r2.sovereign_vault.get("vault_size", 0) >= 2
    prior = r2.solus_memory.get("vault", {}).get("prior_hits", [])
    assert isinstance(prior, list)


def test_enterprise_copilot_vault(tmp_path):
    from mesie.enterprise.copilot import EnterpriseAICopilot

    refs = [load_reference_record(n) for n in list_references()[:3]]
    copilot = EnterpriseAICopilot(sla_latency_ms=500.0)
    copilot.vault = SovereignVault(persist_path=tmp_path / "copilot_vault.json", auto_persist=False)
    copilot.index_corpus(refs)
    r1 = copilot.run_cycle(refs[0], session_id="vault-s1")
    r2 = copilot.run_cycle(refs[1], session_id="vault-s1")
    assert r1.sovereign_vault.get("deposited")
    assert r2.sovereign_vault.get("vault_size", 0) >= 2
    status = copilot.invoke_tool("mesie_vault_status", {})
    assert status["vault_size"] >= 2