"""Reality Engine — 10 cores × 20 languages, front↔middle↔back orchestration."""

from __future__ import annotations

import time
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from mesie.design.envelope import RealityEngineEnvelope
from mesie.design.languages import CANONICAL_PROTOCOL_COUNT, REALITY_PROTOCOL, language_bindings_manifest
from mesie.design.orchestrator import orchestrate_design_brief
from mesie.design.protocols import protocol_bus_manifest
from mesie.design.reality_stack import reality_stack_manifest
from mesie.design.registry import DESIGN_CORES, core_by_id, design_ecosystem_manifest, paradigm_count


class RealityEngine:
    """Unreal-class web reality engines — modular enterprises in 10 cores."""

    def status(self) -> Dict[str, Any]:
        eco = design_ecosystem_manifest()
        return {
            "protocol": REALITY_PROTOCOL,
            "core_count": len(DESIGN_CORES),
            "paradigm_count": paradigm_count(),
            "paradigms_per_core": 20,
            "canonical_protocol_count": CANONICAL_PROTOCOL_COUNT,
            "protocol_bus_count": protocol_bus_manifest()["protocol_count"],
            "stack": reality_stack_manifest(),
            "languages": language_bindings_manifest(),
            "ecosystem": {
                "cores": [c.core_id for c in DESIGN_CORES],
                "surfaces": eco.get("surfaces", {}),
            },
            "vision": "Video-game roots → enterprise product showcase — compete with Unreal-class pipelines on web",
        }

    def invoke(self, envelope: RealityEngineEnvelope) -> Dict[str, Any]:
        t0 = time.perf_counter()
        sealed = envelope.seal()
        core = core_by_id(envelope.core_id)
        if not core:
            return {"ok": False, "error": f"unknown core: {envelope.core_id}", "sealed": sealed}

        from mesie.design.core_engine import invoke_paradigm_agent

        orchestration = orchestrate_design_brief(
            envelope.core_id,
            envelope.brief,
            agent_id=envelope.agent_id,
        )

        agent_results: List[Dict[str, Any]] = []
        if envelope.paradigm_id:
            agent_results.append(
                invoke_paradigm_agent(envelope.core_id, envelope.paradigm_id, envelope.brief)
            )
        else:
            # Sample orchestrator + one worker per layer for latency budget
            sample = [p for p in core.paradigms if p.role == "orchestrator"][:1]
            sample += [p for p in core.paradigms if p.role == "worker"][:2]
            for p in sample:
                agent_results.append(invoke_paradigm_agent(envelope.core_id, p.paradigm_id, envelope.brief))

        receipt = self._mint_receipt(envelope, orchestration)
        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "ok": True,
            "sealed": sealed,
            "core_id": envelope.core_id,
            "latin_name": core.latin_name,
            "reality_class": core.reality_class,
            "orchestration": orchestration.get("orchestration"),
            "agents": agent_results,
            "receipt": receipt,
            "latency_ms": elapsed,
        }

    def _mint_receipt(self, envelope: RealityEngineEnvelope, orchestration: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from mesie.enterprise.receipt_chain import ComputationalReceiptChain

            orch = orchestration.get("orchestration") or {}
            work_score = float(orch.get("agents_invoked", 10)) / 20.0
            receipt, token = ComputationalReceiptChain().append_spectral_cycle(
                cycle_id=f"reality-{envelope.envelope_id[:8]}",
                record_id=envelope.core_id,
                work={"core": envelope.core_id, "match_score": work_score},
                solus_proof={"logic_confidence": 0.9, "proof_steps": 1, "signal_ratio": work_score},
            )
            return {"receipt": asdict(receipt), "token": asdict(token)}
        except Exception as exc:
            return {"note": "receipt deferred", "error": str(exc)}
