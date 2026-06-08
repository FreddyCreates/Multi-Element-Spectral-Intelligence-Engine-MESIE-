"""Enterprise AI copilot — Octopus + MAESI + SOLUS sovereign agent workflows."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from mesie.enterprise.agent_memory import EnterpriseAgentMemory
from mesie.enterprise.receipt_chain import ComputationalReceipt, ComputationalReceiptChain, MintedWorkToken
from mesie.enterprise.sovereign_vault import SovereignVault
from mesie.enterprise.tool_schemas import build_enterprise_tool_schemas
from mesie.io.loaders import RecordInput
from mesie.octopus.controller import OctopusConfig, OctopusController
from mesie.sdk import MAESIClient
from mesie.sdk.solus import SDKSolusOrganism, SOLUS_BRAND


@dataclass
class EnterpriseCycleReport:
    session_id: str
    sovereign: bool
    brand: str
    query_latency_ms: float
    memory_recall: Dict[str, Any]
    solus: Dict[str, Any]
    maesi_neighbors: List[Dict[str, Any]]
    octopus_summary: str
    sla_ok: bool
    plain_summary: str
    tool_schemas: List[Dict[str, Any]] = field(default_factory=list)
    octopus_enterprise: Dict[str, Any] = field(default_factory=dict)
    minted_token: Optional[Dict[str, Any]] = None
    receipt_chain: Dict[str, Any] = field(default_factory=dict)
    sovereign_vault: Dict[str, Any] = field(default_factory=dict)


class EnterpriseAICopilot:
    """On-prem enterprise copilot: agent memory, SOLUS caretakers, Octopus orchestration."""

    def __init__(
        self,
        *,
        session_id: str = "enterprise-default",
        use_octopus: bool = True,
        sla_latency_ms: float = 100.0,
    ) -> None:
        self.session_id = session_id
        self.sla_latency_ms = sla_latency_ms
        self.client = MAESIClient(fast=True, use_fingerprint=True, use_solus_caretakers=True)
        self.organism = self.client.organism or SDKSolusOrganism()
        self.memory = EnterpriseAgentMemory()
        self.receipts = ComputationalReceiptChain()
        self.vault = SovereignVault()
        self.octopus: Optional[OctopusController] = None
        if use_octopus:
            self.octopus = OctopusController(
                config=OctopusConfig(use_polyglot_arms=True),
            )
        self._corpus_indexed = False
        self._fast_cycle = None

    def index_corpus(self, records: Sequence[RecordInput]) -> int:
        n = self.client.index_corpus(records)
        self.memory.index_corpus(records)
        self._corpus_indexed = True
        return n

    def solus_reason(self, record: RecordInput, *, theorem: Optional[str] = None) -> Dict[str, Any]:
        from mesie.io.loaders import load_record

        rec = load_record(record)
        comp = rec.components[0]
        analysis = self.organism.analyze_spectrum(
            comp.frequency.tolist(),
            comp.amplitude.tolist(),
        )
        logic = None
        if theorem:
            r = self.organism.logic_action("prove", theorem=theorem)
            logic = {"ok": r.ok, "conclusion": r.brain.get("conclusion", ""), "confidence": r.brain.get("confidence")}
        xray_ratio = analysis.get("xray", {}).get("signal_ratio", 0.0)
        conclusion = f"spectral_signal_ratio={xray_ratio:.3f}"
        if logic:
            conclusion = logic["conclusion"]
        return {
            "ok": True,
            "brand": SOLUS_BRAND,
            "sovereign": True,
            "analysis": analysis,
            "logic": logic,
            "conclusion": conclusion,
        }

    def run_cycle(
        self,
        record: RecordInput,
        *,
        candidate: Optional[RecordInput] = None,
        session_id: Optional[str] = None,
    ) -> EnterpriseCycleReport:
        sid = session_id or self.session_id
        t0 = time.perf_counter()

        if not self._corpus_indexed:
            raise RuntimeError("Call index_corpus() before run_cycle()")

        q = self.client.query(record, top_k=3)
        solus = self.solus_reason(
            record,
            theorem=f"agent_session_{sid}: spectral query yields actionable memory",
        )
        recall = self.memory.recall(record, top_k=3, session_id=sid)
        vault_prior = self.vault.recall(
            results={"neighbors": len(q.neighbors)},
            workflow={"workflow_id": sid},
            top_k=3,
        )

        oct_summary = ""
        enterprise_octopus: Dict[str, Any] = {}
        minted_token: Optional[Dict[str, Any]] = None
        receipt_chain: Dict[str, Any] = {}
        if self.octopus:
            oct_report = self.octopus.run_standard_cycle(record, candidate=candidate)
            oct_summary = oct_report.plain_summary
            enterprise_octopus = getattr(oct_report, "enterprise_ai", {}) or {}
            minted_token = enterprise_octopus.get("minted_token")
            receipt_chain = getattr(oct_report, "receipt_chain", {}) or {}

        from mesie.io.loaders import load_record as _load

        rec_id = _load(record).record_id
        local_receipt, local_token = self.receipts.append_spectral_cycle(
            cycle_id=f"enterprise_{sid}",
            record_id=rec_id,
            work={
                "neighbors": len(q.neighbors),
                "latency_ms": 0,
                "session_id": sid,
            },
            solus_proof={
                "conclusion": str(solus.get("conclusion", "")),
                "logic_confidence": float(
                    (solus.get("logic") or {}).get("confidence", 0.5)
                ),
                "signal_ratio": float(
                    (solus.get("analysis") or {}).get("xray", {}).get("signal_ratio", 0.5)
                ),
                "proof_steps": 1,
            },
        )
        if not minted_token:
            from dataclasses import asdict as _asdict

            minted_token = _asdict(local_token)
        receipt_chain = receipt_chain or self.receipts.to_dict()

        vault_report: Dict[str, Any] = {}
        solus_cycle = solus.get("analysis") or solus
        if isinstance(enterprise_octopus.get("solus_cycle"), dict):
            solus_cycle = enterprise_octopus["solus_cycle"]
        entry = self.vault.deposit(
            token=local_token,
            receipt=local_receipt,
            composition=solus_cycle if isinstance(solus_cycle, dict) else {},
            results={
                "conclusion": str(solus.get("conclusion", "")),
                "neighbors": len(q.neighbors),
                "session_id": sid,
            },
            workflow={
                "workflow_id": sid,
                "completed": bool(oct_summary),
                "prior_hits": vault_prior.get("hits", []),
            },
            ai_patterns={
                "formal_models": list((solus_cycle.get("formal_models") or {}).keys())
                if isinstance(solus_cycle, dict)
                else [],
            },
            record_id=rec_id,
            cycle_id=f"enterprise_{sid}",
        )
        vault_report = {
            "vault_id": entry.vault_id,
            "token_id": entry.token_id,
            "deposited": True,
            "vault_size": self.vault.size,
            "compound_work_units": self.vault.compound().total_work_units,
            "prior_hits": vault_prior.get("hits", []),
        }

        turn_ms = (time.perf_counter() - t0) * 1000
        self.memory.store_turn(
            sid,
            record,
            neighbors=q.neighbors,
            research_hits=q.research_hits,
            technical_hits=q.technical_hits,
            solus_conclusion=str(solus.get("conclusion", "")),
            elapsed_ms=turn_ms,
        )

        sla_ok = len(q.neighbors) >= 1 and turn_ms < self.sla_latency_ms
        plain = (
            f"Enterprise AI [{SOLUS_BRAND}]: session={sid}, neighbors={len(q.neighbors)}, "
            f"recall_corpus={len(recall.get('corpus_hits', []))}, "
            f"latency={turn_ms:.1f}ms, sla={'PASS' if sla_ok else 'REVIEW'}. "
            f"SOLUS: {str(solus.get('conclusion', ''))[:80]}."
        )

        return EnterpriseCycleReport(
            session_id=sid,
            sovereign=True,
            brand=SOLUS_BRAND,
            query_latency_ms=round(turn_ms, 2),
            memory_recall=recall,
            solus=solus,
            maesi_neighbors=q.neighbors,
            octopus_summary=oct_summary,
            sla_ok=sla_ok,
            plain_summary=plain,
            tool_schemas=build_enterprise_tool_schemas(),
            octopus_enterprise=enterprise_octopus,
            minted_token=minted_token,
            receipt_chain=receipt_chain,
            sovereign_vault=vault_report,
        )

    def invoke_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Local tool handler for copilot runtimes — no external API."""
        if name == "mesie_agent_memory_recall":
            return self.memory.recall(
                arguments["record"],
                top_k=int(arguments.get("top_k", 5)),
                session_id=arguments.get("session_id"),
            )
        if name == "mesie_solus_reason":
            return self.solus_reason(arguments["record"], theorem=arguments.get("theorem"))
        if name == "mesie_enterprise_copilot_cycle":
            return asdict(
                self.run_cycle(
                    arguments["record"],
                    candidate=arguments.get("candidate"),
                    session_id=arguments.get("session_id", self.session_id),
                )
            )
        if name == "mesie_verify_receipt_chain":
            return self.receipts.to_dict()
        if name == "mesie_vault_recall":
            return self.vault.recall(
                composition=arguments.get("composition"),
                results=arguments.get("results"),
                workflow=arguments.get("workflow"),
                ai_patterns=arguments.get("ai_patterns"),
                top_k=int(arguments.get("top_k", 5)),
            )
        if name == "mesie_vault_status":
            return self.vault.to_dict()
        if name == "mesie_field_route":
            from mesie.sovereign.field_access import get_field_access_engine

            fa = get_field_access_engine()
            return fa.route(
                arguments["source"],
                arguments["destination"],
                policy=arguments.get("policy", "shortest"),
            ).to_dict()
        if name == "mesie_field_bridge":
            from mesie.sovereign.field_access import get_field_access_engine

            fa = get_field_access_engine()
            return asdict(fa.bridge(arguments["record"]))
        if name == "mesie_field_status":
            from mesie.sovereign.field_access import get_field_access_engine

            return get_field_access_engine().status()
        if name == "mesie_field_ingest_csv":
            from mesie.field_io import CSVSpectralIngest
            from mesie.sovereign.field_access import get_field_access_engine

            rec, rep = CSVSpectralIngest().ingest(
                arguments["path"],
                record_id=arguments.get("record_id"),
            )
            br = get_field_access_engine().bridge(rec)
            return {"ok": True, "ingest": rep.to_dict(), "bridge": asdict(br)}
        if name == "mesie_field_ingest_udp":
            import base64

            from mesie.field_io import UDPSpectralFrameParser
            from mesie.sovereign.field_access import get_field_access_engine

            payload = base64.b64decode(arguments["payload_b64"])
            rec, rep = UDPSpectralFrameParser().parse(payload)
            br = get_field_access_engine().bridge(rec)
            return {"ok": True, "frame": rep.to_dict(), "bridge": asdict(br)}
        if name == "mesie_anchor_calibrate":
            from mesie.sovereign.anchor_calibration import calibrate_field_anchors

            return calibrate_field_anchors().to_dict()
        if name == "mesie_swarm_hive_coordinate":
            from mesie.library.domain_corpus import load_domain_corpus
            from mesie.swarm.hive_mind import HiveMindCoordinator

            corpus = load_domain_corpus()
            hive = HiveMindCoordinator(corpus)
            return hive.coordinate(
                arguments["record"],
                n_agents=int(arguments.get("n_agents", 1000)),
            ).to_dict()
        if name == "mesie_drone_swarm_coordinate":
            from mesie.library.domain_corpus import load_domain_corpus
            from mesie.swarm.drone_coordination import DecentralizedSwarmCoordinator

            corpus = load_domain_corpus()
            coord = DecentralizedSwarmCoordinator(corpus)
            return coord.coordinate(
                arguments["record"],
                n_agents=int(arguments.get("n_agents", 1000)),
                jam_ground=bool(arguments.get("jam_ground", False)),
                attrition_rate=float(arguments.get("attrition_rate", 0.0)),
            ).to_dict()
        if name == "mesie_swarm_routing_validate":
            from mesie.library.domain_corpus import load_domain_corpus
            from mesie.swarm.drone_coordination import DecentralizedSwarmCoordinator

            return DecentralizedSwarmCoordinator(load_domain_corpus()).routing_validation()
        if name == "mesie_swarm_mission_plan":
            from mesie.library.domain_corpus import load_domain_corpus
            from mesie.swarm.mission_planner import SwarmMissionPlanner

            return SwarmMissionPlanner(load_domain_corpus()).execute_mission(
                arguments["record"],
                preset_id=arguments.get("preset_id", "ew"),
                n_agents=int(arguments.get("n_agents", 1000)),
                jam_ground=bool(arguments.get("jam_ground", False)),
            ).to_dict()
        if name == "mesie_swarm_task_allocate":
            import numpy as np
            from mesie.swarm.task_allocation import MARLTaskAllocator, ParticleSwarmAllocator, SwarmTask

            n = int(arguments["n_agents"])
            urg = float(arguments.get("spectral_urgency", 0.8))
            tasks = [
                SwarmTask(f"t{i}", t, 1.0 - i * 0.1, np.array([50 + i * 20, 30, 10]), urg)
                for i, t in enumerate(["intercept", "scan", "relay"])
            ]
            if arguments.get("method") == "marl":
                return MARLTaskAllocator().allocate(min(n, 256), tasks).to_dict()
            return ParticleSwarmAllocator().allocate(min(n, 256), tasks).to_dict()
        if name == "mesie_swarm_formation":
            from mesie.swarm.formation import FormationController

            return FormationController().simulate(
                int(arguments.get("n_agents", 100)),
                attrition_rate=float(arguments.get("attrition_rate", 0.1)),
            ).to_dict()
        if name == "mesie_mesh_export":
            from mesie.sovereign.sovereign_mesh import SovereignMesh

            return SovereignMesh().export_bundle(self.receipts).to_dict()
        if name == "mesie_mesh_peers":
            from mesie.sovereign.sovereign_mesh import SovereignMesh

            return {"peers": [p.to_dict() for p in SovereignMesh().list_peers()]}
        if name == "mesie_domain_catalog":
            from mesie.library.domain_corpus import domain_catalog

            return domain_catalog()
        if name == "mesie_fast_enterprise_cycle":
            from mesie.enterprise.fast_cycle import FastEnterpriseCycle
            from mesie.library.domain_corpus import load_domain_corpus

            if self._fast_cycle is None:
                self._fast_cycle = FastEnterpriseCycle()
                self._fast_cycle.index_corpus(load_domain_corpus())
            return self._fast_cycle.run(
                arguments["record"],
                candidate=arguments.get("candidate"),
                session_id=arguments.get("session_id", self.session_id),
            ).to_dict()
        if name == "mesie_external_benchmark":
            from mesie.evaluation.external_benchmarks import ExternalBenchmarkPack

            return ExternalBenchmarkPack(
                n_trials=int(arguments.get("n_trials", 200)),
            ).run().to_dict()
        if name == "mesie_rf_ingest":
            from mesie.sdk import MAESIClient

            return MAESIClient().rf_ingest(simulated=arguments.get("simulated", True))
        if name == "mesie_production_health":
            from mesie.production.appliance import ProductionAppliance

            return ProductionAppliance().health().to_dict()
        if name == "mesie_specialized_reason":
            from mesie.library.domain_corpus import load_domain_corpus
            from mesie.sdk.fast_compute import FastSpectralCompute

            domains = arguments.get("domains")
            corpus = load_domain_corpus(domains)
            fc = FastSpectralCompute()
            fc.build_index(corpus)
            hits = fc.cosine_search(arguments["record"], top_k=5)
            solus = self.solus_reason(arguments["record"])
            return {
                "ok": True,
                "domains": domains or "all",
                "corpus_size": len(corpus),
                "neighbors": [{"id": h[0], "score": round(h[1], 4)} for h in hits],
                "solus": solus,
            }
        if self.octopus and self.octopus.polyglot_suite:
            return self.octopus.polyglot_suite.third_party.invoke_tool(name, arguments)
        return {"ok": False, "error": f"unknown tool: {name}"}

    def sovereign_tools(self) -> List[Dict[str, Any]]:
        return build_enterprise_tool_schemas()