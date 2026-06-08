"""SOLUS MEMORY arm + computational receipt chain + default math layer."""

from dataclasses import asdict

from data import list_references, load_reference_record
from mesie.enterprise import ComputationalReceiptChain
from mesie.octopus import OctopusController, OctopusConfig
from mesie.octopus.solus_memory import SolusMemoryArm
from mesie.sdk import MAESIClient, SolusMathLayer
from mesie.sdk.solus import SDKSolusOrganism


def test_receipt_chain_seal_and_verify():
    chain = ComputationalReceiptChain()
    r1, t1 = chain.append_spectral_cycle(
        cycle_id="c1",
        record_id="rec_a",
        work={"match_score": 0.8, "similarity": 0.8},
        solus_proof={"logic_confidence": 0.9, "signal_ratio": 0.7, "proof_steps": 4},
    )
    r2, t2 = chain.append_spectral_cycle(
        cycle_id="c2",
        record_id="rec_b",
        work={"match_score": 0.6},
        solus_proof={"logic_confidence": 0.8, "signal_ratio": 0.5, "proof_steps": 3},
    )
    state = chain.verify_chain()
    assert state.verified
    assert state.chain_length == 2
    assert r2.prev_hash != r1.prev_hash
    assert len(t1.token_id) == 32
    assert t2.work_units > 0


def test_organism_reason_spectral_cycle():
    org = SDKSolusOrganism()
    refs = load_reference_record(list_references()[0])
    comp = refs.components[0]
    out = org.reason_spectral_cycle(
        comp.frequency.tolist(),
        comp.amplitude.tolist(),
        cycle_context={"record_id": refs.record_id, "match_score": 0.75, "valid": True},
    )
    assert out["sovereign"]
    assert set(out["formal_models"].keys()) == {"logic", "reasoning", "emergence", "adaptation"}
    assert out["third_party"] is False
    assert out["formula"]
    assert "conclusion" in out


def test_solus_memory_arm_mints_token():
    refs = [load_reference_record(n) for n in list_references()[:2]]
    arm = SolusMemoryArm()
    result = arm.run_cycle(
        refs[0],
        cycle_context={"match_score": 0.7, "similarity": 0.7, "anomaly": 1.2, "valid": True},
    )
    assert result["minted_token"]["token_id"]
    assert result["receipt_chain"]["verified"]
    assert result["solus_cycle"]["conclusion"]


def test_octopus_memory_arm_every_cycle():
    refs = [load_reference_record(n) for n in list_references()[:2]]
    octo = OctopusController(config=OctopusConfig(use_solus_memory=True))
    report = octo.run_standard_cycle(refs[0], candidate=refs[1])
    assert report.solus_memory["sovereign"]
    assert report.solus_memory["minted_token"]["token_id"]
    assert report.receipt_chain["verified"]
    assert report.enterprise_ai["memory_arm"] == "solus"
    assert "SOLUS MEMORY" in report.plain_summary


def test_maesi_default_math_layer():
    refs = [load_reference_record(n) for n in list_references()[:2]]
    client = MAESIClient(fast=True, use_solus_math_layer=True)
    assert client.math_layer is not None
    report = client.run_full(refs, benchmark=False)
    assert report.solus_organism is not None


def test_math_layer_local_only():
    layer = SolusMathLayer()
    proof = layer.prove("local math only — no third party")
    assert proof["sovereign"]
    assert proof["ok"]
    vals = [0.1, 0.5, 0.9, 0.3, 0.7, 0.2]
    analysis = layer.analyze_values(vals)
    assert analysis["sovereign"]
    assert analysis["ok"]