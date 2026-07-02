"""Enterprise federation — multi-user, polyglot, arms/hands."""

from __future__ import annotations

from mesie.enterprise.federation.protocol import EnterpriseFederationEnvelope
from mesie.enterprise.federation.registry import FederationRegistry
from mesie.polyglot.contract import RuntimeId


def test_federation_registry_multi_tenant():
    reg = FederationRegistry()
    reg.register_tenant("acme-corp", org_id="acme", name="ACME Defense")
    reg.register_agent("agent-alpha", tenant_id="acme-corp", org_id="acme", roles=["analyst"])
    assert reg.authorize(agent_id="agent-alpha", tenant_id="acme-corp", org_id="acme")


def test_enterprise_envelope_seal():
    env = EnterpriseFederationEnvelope(
        agent_id="test-agent",
        tenant_id="default",
        user_id="user-1",
        tool="polyglot.validate",
        runtime="julia",
        delegation_chain=["grok", "mesie"],
    )
    sealed = env.seal_enterprise()
    assert sealed["enterprise"]["tenant_id"] == "default"
    assert sealed["protocol"] == "MESIE-FEDERATED-ENVELOPE/1.0"


def test_haskell_adapter_fingerprint():
    from mesie.polyglot.adapters.haskell_adapter import HaskellAdapter
    from mesie.polyglot.contract import AISVectorMessage, PolyglotAction
    from data import load_reference_record
    from mesie.polyglot.contract import record_to_dict

    ad = HaskellAdapter()
    msg = AISVectorMessage(
        action=PolyglotAction.FINGERPRINT,
        runtime=RuntimeId.HASKELL,
        record=record_to_dict(load_reference_record("earthquake_psd_reference")),
    )
    resp = ad.dispatch(msg)
    assert resp.ok
    assert resp.data.get("score") is not None


def test_federation_invoke_polyglot():
    from mesie.enterprise.federation import FederationOrchestrator

    orch = FederationOrchestrator()
    env = EnterpriseFederationEnvelope(
        agent_id="pytest-federation",
        tenant_id="default",
        tool="polyglot.validate",
        runtime="python",
        payload={"record": "earthquake_psd_reference"},
    )
    out = orch.invoke(env)
    assert out["ok"]
    assert "polyglot" in out
    assert "receipt" in out


def test_federation_hands_invoke():
    from mesie.enterprise.federation import FederationOrchestrator

    env = EnterpriseFederationEnvelope(
        agent_id="pytest-hands",
        tenant_id="default",
        tool="hands.pulse",
        hand_command={"action": "pulse", "dof": 4},
    )
    out = FederationOrchestrator().invoke(env)
    assert out["ok"]
    assert "hands" in out


def test_processor_federation_status():
    from mesie.processor.virtual_processor import VirtualProcessor

    proc = VirtualProcessor()
    result = proc.federation_status()
    assert result.ok
    assert result.output["protocol"] == "MESIE-ENTERPRISE-FEDERATION/1.0"
