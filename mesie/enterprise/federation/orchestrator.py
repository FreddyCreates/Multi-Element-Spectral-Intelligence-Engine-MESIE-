"""Enterprise federation orchestrator — polyglot, depth, octopus arms, hands."""

from __future__ import annotations

import time
from dataclasses import asdict
from typing import Any, Dict, Optional

from mesie.enterprise.federation.hands import HandCommand, ManipulatorHands
from mesie.enterprise.federation.protocol import (
    EnterpriseFederationEnvelope,
    build_enterprise_federation_manifest,
    export_enterprise_federation_manifest,
)
from mesie.enterprise.federation.registry import FederationRegistry
from mesie.enterprise.receipt_chain import ComputationalReceiptChain
from mesie.polyglot.contract import AISVectorMessage, PolyglotAction, RuntimeId, record_to_dict


class FederationOrchestrator:
    """Full-stack dispatch: multi-user envelope → polyglot → arms → depth → receipt."""

    def __init__(self, *, registry: Optional[FederationRegistry] = None) -> None:
        self.registry = registry or FederationRegistry()
        self.hands = ManipulatorHands()
        self._polyglot = None
        self._receipt_chain = ComputationalReceiptChain()

    def _polyglot_suite(self):
        if self._polyglot is None:
            from mesie.polyglot.suite import AISVectorPolyglotSuite

            self._polyglot = AISVectorPolyglotSuite(
                routing={
                    PolyglotAction.MATCH: RuntimeId.RUST,
                    PolyglotAction.FINGERPRINT: RuntimeId.HASKELL,
                    PolyglotAction.EMBED: RuntimeId.JULIA,
                }
            )
        return self._polyglot

    def status(self) -> Dict[str, Any]:
        suite = self._polyglot_suite()
        health = suite.health()
        return {
            "protocol": "MESIE-ENTERPRISE-FEDERATION/1.0",
            "registry": self.registry.status(),
            "polyglot": asdict(health),
            "manifest": build_enterprise_federation_manifest(),
        }

    def invoke(self, envelope: EnterpriseFederationEnvelope) -> Dict[str, Any]:
        t0 = time.perf_counter()
        if not self.registry.authorize(
            agent_id=envelope.agent_id,
            tenant_id=envelope.tenant_id,
            org_id=envelope.org_id,
        ):
            self.registry.register_agent(
                envelope.agent_id,
                tenant_id=envelope.tenant_id,
                org_id=envelope.org_id,
            )

        sealed = envelope.seal_enterprise()
        tool = envelope.tool
        payload = envelope.payload or {}
        result: Dict[str, Any] = {"sealed": sealed, "tool": tool}

        if tool.startswith("polyglot.") or tool in ("validate", "match", "embed", "fingerprint"):
            action_name = tool.replace("polyglot.", "") if tool.startswith("polyglot.") else tool
            runtime = (
                RuntimeId(envelope.runtime)
                if envelope.runtime in RuntimeId._value2member_map_
                else RuntimeId.PYTHON
            )
            suite = self._polyglot_suite()
            from data import load_reference_record

            rec = load_reference_record(payload.get("record", "earthquake_psd_reference"))
            if action_name == "match":
                b = load_reference_record(payload.get("record_b", "vibration_monitoring_reference"))
                resp = suite.match(rec, b, runtime=runtime)
            elif action_name == "embed":
                resp = suite.embed(rec, runtime=runtime)
            elif action_name == "fingerprint":
                resp = suite.dispatch(
                    AISVectorMessage(
                        action=PolyglotAction.FINGERPRINT,
                        runtime=runtime,
                        record=record_to_dict(rec),
                    )
                )
            else:
                resp = suite.validate(rec, runtime=runtime)
            result["polyglot"] = resp.to_dict()

        elif tool.startswith("arm.") or envelope.arm_id:
            from mesie.octopus.arms import ArmId
            from mesie.octopus.controller import OctopusController

            arm_name = envelope.arm_id or tool.replace("arm.", "")
            ctrl = OctopusController(polyglot_suite=self._polyglot_suite())
            arm_id = ArmId(arm_name) if arm_name in ArmId._value2member_map_ else ArmId.SENSE
            rep = ctrl._arms[arm_id].reach(action=payload.get("action"), payload=payload)
            result["arm"] = rep.to_dict()

        elif tool.startswith("hands.") or envelope.hand_command:
            cmd_data = envelope.hand_command or payload
            cmd = HandCommand(
                action=str(cmd_data.get("action", "pulse")),
                dof=int(cmd_data.get("dof", 6)),
                grip_strength=float(cmd_data.get("grip_strength", 0.85)),
                spectral_target=dict(cmd_data.get("spectral_target") or {}),
            )
            result["hands"] = self.hands.execute(cmd).to_dict()

        elif tool.startswith("depth.") or envelope.pillar_id:
            from mesie.depth.envelope_router import route_envelope_to_engine, seal_depth_envelope

            pillar_id = envelope.pillar_id or tool.replace("depth.", "")
            sealed_depth = seal_depth_envelope(
                pillar_id,
                envelope.agent_id,
                tool,
                payload=payload,
            )
            route = route_envelope_to_engine(sealed_depth.get("envelope", sealed))
            result["depth"] = {"sealed": sealed_depth, "route": route}

        elif tool == "octopus.run":
            from mesie.octopus.controller import OctopusController
            from data import load_reference_record

            ctrl = OctopusController(polyglot_suite=self._polyglot_suite())
            a = load_reference_record(payload.get("a", "earthquake_psd_reference"))
            b = load_reference_record(payload.get("b", "vibration_monitoring_reference"))
            report = ctrl.run_standard_cycle(a, candidate=b)
            result["octopus"] = asdict(report)

        elif tool.startswith("design.") or tool.startswith("reality."):
            from mesie.design.envelope import RealityEngineEnvelope
            from mesie.design.reality_engine import RealityEngine

            core_id = str(payload.get("core_id", "core_realitas"))
            env = RealityEngineEnvelope(
                agent_id=envelope.agent_id,
                core_id=core_id,
                brief=payload.get("brief") or payload,
                paradigm_id=payload.get("paradigm_id"),
                language_id=payload.get("language_id"),
            )
            result["reality"] = RealityEngine().invoke(env)

        else:
            result["note"] = "envelope sealed; use polyglot.*, arm.*, hands.*, depth.*, design.*, reality.*, or octopus.run"

        work_score = 0.5
        if "polyglot" in result:
            work_score = float(result["polyglot"].get("data", {}).get("composite_score", 0.5) or 0.5)
        receipt, token = self._receipt_chain.append_spectral_cycle(
            cycle_id=f"federation-{envelope.envelope_id[:8]}",
            record_id=str(payload.get("record", envelope.tool)),
            work={"tool": tool, "match_score": work_score, "tenant_id": envelope.tenant_id},
            solus_proof={"logic_confidence": 0.85, "proof_steps": 1, "signal_ratio": work_score},
        )
        result["receipt"] = asdict(receipt)
        result["token"] = asdict(token)
        result["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        result["ok"] = True
        return result

    def export_manifest(self) -> str:
        return str(export_enterprise_federation_manifest())
