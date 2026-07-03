"""HTTP Virtual Processor Server — port 8750, for coding agents + MCP bridges."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[2]

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from mesie.processor.virtual_processor import VirtualProcessor

from mesie.version_info import MESIE_VERSION

app = FastAPI(title="MESIE Virtual Processor", version=MESIE_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_WEB_ROOT = ROOT / "websites"
if _WEB_ROOT.is_dir():
    app.mount("/websites", StaticFiles(directory=str(_WEB_ROOT), html=True), name="websites")


@app.get("/")
def web_root() -> RedirectResponse:
    return RedirectResponse(url="/websites/platform-hub/index.html")


@app.get("/processor/surfaces")
def web_surfaces_catalog() -> Dict[str, Any]:
    """All MESIE web apps — open via http://127.0.0.1:8750/websites/..."""
    base = "http://127.0.0.1:8750/websites"
    apps = [
        {"id": "platform-hub", "title": "Platform Hub", "path": f"{base}/platform-hub/index.html", "role": "home"},
        {"id": "reality-engine", "title": "Reality Engine", "path": f"{base}/reality-engine/index.html", "role": "3d-showcase"},
        {"id": "model-hub", "title": "Model Hub", "path": f"{base}/model-hub/index.html", "role": "models"},
        {"id": "solus-console", "title": "SOLUS Console", "path": f"{base}/solus-console/index.html", "role": "logic"},
        {"id": "auro-studio", "title": "Auro Studio", "path": f"{base}/auro-studio/index.html", "role": "speech"},
        {"id": "producer-lab", "title": "Producer Lab", "path": f"{base}/producer-lab/index.html", "role": "pipeline"},
        {"id": "computing-family", "title": "Computing Family", "path": f"{base}/computing-family/index.html", "role": "compute"},
        {"id": "virtual-silicon", "title": "Virtual Silicon", "path": f"{base}/virtual-silicon/index.html", "role": "chips"},
        {"id": "enterprise-4k", "title": "Enterprise 4K", "path": f"{base}/enterprise-4k/index.html", "role": "enterprise"},
        {"id": "hermes-fleet", "title": "HERMES Fleet", "path": f"{base}/hermes-fleet/index.html", "role": "workers"},
        {"id": "market-hub", "title": "Market Hub", "path": f"{base}/market-hub/index.html", "role": "market"},
        {"id": "mesie-landing", "title": "MESIE Landing", "path": f"{base}/mesie-landing/index.html", "role": "landing"},
    ]
    return {
        "ok": True,
        "protocol": "MESIE-WEB-SURFACES/1.0",
        "processor": "http://127.0.0.1:8750",
        "reality_engine": f"{base}/reality-engine/index.html",
        "app_count": len(apps),
        "apps": apps,
    }


_processor: Optional[VirtualProcessor] = None


def _proc() -> VirtualProcessor:
    global _processor
    if _processor is None:
        _processor = VirtualProcessor()
    return _processor


class ExecRequest(BaseModel):
    tool_id: str
    timeout_s: int = Field(default=120, ge=5, le=600)


class MatchRequest(BaseModel):
    path_a: str
    path_b: str


class EmbedRequest(BaseModel):
    record_path: str = "ref-earthquake-psd-001"


class BenchmarkRequest(BaseModel):
    trials: int = Field(default=200, ge=10, le=5000)


class VirtualChipRequest(BaseModel):
    chip_id: str = Field(default="MESIE-VS1")


class ReadSignalRequest(BaseModel):
    payload: Any
    hint: Optional[str] = None
    source_id: Optional[str] = None


class GenerateTextRequest(BaseModel):
    payload: Any
    style: str = Field(default="analyst_brief")
    max_chars: int = Field(default=1200, ge=100, le=8000)
    use_native_voice: bool = False
    hint: Optional[str] = None


@app.get("/processor/status")
def status() -> Dict[str, Any]:
    return _proc().status()


@app.get("/processor/accounting")
def accounting() -> Dict[str, Any]:
    return _proc().ledger.export_status()


@app.post("/processor/embed")
def embed(body: EmbedRequest) -> Dict[str, Any]:
    return _proc().embed(body.record_path).to_dict()


@app.post("/processor/match")
def match(body: MatchRequest) -> Dict[str, Any]:
    return _proc().match_pair(body.path_a, body.path_b).to_dict()


@app.post("/processor/benchmark")
def benchmark(body: BenchmarkRequest) -> Dict[str, Any]:
    return _proc().benchmark(trials=body.trials).to_dict()


@app.post("/processor/exec")
def exec_tool(body: ExecRequest) -> Dict[str, Any]:
    return _proc().exec_tool(body.tool_id, timeout_s=body.timeout_s).to_dict()


@app.get("/processor/chips")
def list_chips() -> Dict[str, Any]:
    return _proc().list_chips().to_dict()


@app.get("/processor/virtual-silicon")
def virtual_silicon_catalog() -> Dict[str, Any]:
    return _proc().virtual_silicon_catalog().to_dict()


@app.post("/processor/virtual-chip")
def virtual_chip(body: VirtualChipRequest = VirtualChipRequest()) -> Dict[str, Any]:
    return _proc().virtual_chip_certify(chip_id=body.chip_id).to_dict()


@app.post("/processor/robotics-pulse")
def robotics_pulse() -> Dict[str, Any]:
    return _proc().robotics_pulse().to_dict()


@app.post("/processor/read-signal")
def read_signal(body: ReadSignalRequest) -> Dict[str, Any]:
    return _proc().read_signal(body.payload, hint=body.hint, source_id=body.source_id).to_dict()


@app.post("/processor/generate-text")
def generate_text(body: GenerateTextRequest) -> Dict[str, Any]:
    return _proc().generate_text(
        body.payload,
        style=body.style,
        max_chars=body.max_chars,
        use_native_voice=body.use_native_voice,
        hint=body.hint,
    ).to_dict()


@app.get("/processor/architecture")
def architecture() -> Dict[str, Any]:
    from mesie.processor.stack_architecture import stack_architecture_snapshot

    return stack_architecture_snapshot()


@app.get("/processor/use-cases")
def use_cases_catalog() -> Dict[str, Any]:
    from mesie.enterprise.use_case_registry import registry_manifest

    return registry_manifest()


@app.get("/processor/depth")
def depth_catalog() -> Dict[str, Any]:
    from mesie.depth.registry import depth_manifest
    from mesie.depth.envelope_router import list_depth_routes

    manifest = depth_manifest(include_line_counts=True)
    manifest["routes"] = list_depth_routes()
    return manifest


@app.get("/processor/depth/{pillar_id}")
def depth_pillar_status(pillar_id: str) -> Dict[str, Any]:
    from mesie.depth.registry import count_pillar_lines, pillar_by_id
    from mesie.depth.envelope_router import depth_envelope_spec

    p = pillar_by_id(pillar_id)
    if not p:
        raise HTTPException(status_code=404, detail=f"unknown depth pillar: {pillar_id}")
    counts = count_pillar_lines(pillar_id)
    manifest_path = ROOT / "mesie" / "depth" / pillar_id / "engines" / "manifest.json"
    engine_manifest = {}
    if manifest_path.is_file():
        engine_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {
        "ok": True,
        "pillar": {
            "pillar_id": p.pillar_id,
            "title": p.title,
            "category": p.category,
            "engines": list(p.engines),
            "envelope_topic": p.envelope_topic,
        },
        "line_counts": counts,
        "meets_minimum": counts["total"] >= 5000,
        "envelope_spec": depth_envelope_spec(pillar_id),
        "engine_manifest": engine_manifest,
    }


class DepthEnvelopeRequest(BaseModel):
    agent_id: str = "any-ai"
    tool: str = "depth.invoke"
    payload: Dict[str, Any] = Field(default_factory=dict)
    engine: Optional[str] = None
    prior_hash: Optional[str] = None


@app.post("/processor/depth/{pillar_id}/envelope")
def depth_pillar_envelope(pillar_id: str, body: DepthEnvelopeRequest) -> Dict[str, Any]:
    from mesie.depth.envelope_router import route_envelope_to_engine, seal_depth_envelope

    sealed = seal_depth_envelope(
        pillar_id=pillar_id,
        agent_id=body.agent_id,
        tool=body.tool,
        payload=body.payload,
        engine=body.engine,
        prior_hash=body.prior_hash,
    )
    if not sealed.get("ok"):
        raise HTTPException(status_code=404, detail=sealed.get("error", "pillar not found"))
    routed = route_envelope_to_engine(sealed["envelope"])
    return {"sealed": sealed, "route": routed}


@app.get("/processor/design")
def design_ecosystem_catalog() -> Dict[str, Any]:
    from mesie.design.registry import design_ecosystem_manifest

    return design_ecosystem_manifest()


@app.get("/processor/design/cores/{core_id}")
def design_core_status(core_id: str) -> Dict[str, Any]:
    from mesie.design.core_engine import core_snapshot

    snap = core_snapshot(core_id)
    if not snap.get("ok"):
        raise HTTPException(status_code=404, detail=snap.get("error", "core not found"))
    return snap


class DesignBriefRequest(BaseModel):
    brief: Dict[str, Any] = Field(default_factory=dict)
    agent_id: str = "any-ai"
    paradigm_id: Optional[str] = None


@app.post("/processor/design/cores/{core_id}/orchestrate")
def design_core_orchestrate(core_id: str, body: DesignBriefRequest) -> Dict[str, Any]:
    from mesie.design.orchestrator import orchestrate_design_brief

    return orchestrate_design_brief(core_id, body.brief, agent_id=body.agent_id)


@app.post("/processor/design/cores/{core_id}/invoke")
def design_paradigm_invoke(core_id: str, body: DesignBriefRequest) -> Dict[str, Any]:
    from mesie.design.core_engine import invoke_paradigm_agent

    if not body.paradigm_id:
        raise HTTPException(status_code=400, detail="paradigm_id required")
    return invoke_paradigm_agent(core_id, body.paradigm_id, body.brief)


@app.get("/processor/reality/status")
def reality_engine_status() -> Dict[str, Any]:
    from mesie.design.reality_engine import RealityEngine

    return RealityEngine().status()


@app.post("/processor/reality/invoke")
def reality_engine_invoke(body: Dict[str, Any]) -> Dict[str, Any]:
    from mesie.design.envelope import RealityEngineEnvelope
    from mesie.design.reality_engine import RealityEngine

    env = RealityEngineEnvelope.from_dict(body)
    return RealityEngine().invoke(env)


@app.get("/processor/hermes")
def hermes_fleet_catalog() -> Dict[str, Any]:
    from mesie.hermes.registry import hermes_manifest
    from mesie.hermes.nova_protocol import build_nova_protocol_hermes

    return {
        "hermes": hermes_manifest(),
        "nova_protocol": build_nova_protocol_hermes(),
    }


@app.get("/processor/hermes/nova-protocol")
def hermes_nova_protocol() -> Dict[str, Any]:
    from mesie.hermes.nova_protocol import build_nova_protocol_hermes

    return build_nova_protocol_hermes()


@app.post("/processor/hermes/forge")
def hermes_forge() -> Dict[str, Any]:
    from mesie.hermes.forge import forge_hermes_fleet

    return forge_hermes_fleet()


class HermesInvokeRequest(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict)


@app.post("/processor/hermes/{worker_id}/invoke")
def hermes_worker_invoke(worker_id: str, body: HermesInvokeRequest) -> Dict[str, Any]:
    from mesie.hermes.executor import HermesExecutor
    from mesie.hermes.registry import worker_by_id

    if not worker_by_id(worker_id):
        raise HTTPException(status_code=404, detail=f"unknown hermes worker: {worker_id}")
    result = HermesExecutor().invoke(worker_id, payload=body.payload)
    if not result.get("ok") and result.get("error"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@app.get("/processor/models")
def unified_model_catalog() -> Dict[str, Any]:
    from mesie.platform.model_catalog import build_unified_model_catalog

    return build_unified_model_catalog()


@app.get("/processor/platform")
def platform_catalog() -> Dict[str, Any]:
    from mesie.platform.mvp_bridge import bridge_manifest
    from mesie.platform.model_catalog import build_unified_model_catalog
    from mesie.platform.registry import platform_manifest

    from mesie.hermes.registry import hermes_manifest

    return {
        "platform": platform_manifest(),
        "bridge": bridge_manifest(),
        "models": build_unified_model_catalog(),
        "hermes": hermes_manifest(),
    }


class PlatformInvokeRequest(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict)
    mission_id: str = "api"


@app.post("/processor/platform/{service_id}/invoke")
def platform_invoke(service_id: str, body: PlatformInvokeRequest) -> Dict[str, Any]:
    from mesie.platform.worker_gateway import PlatformWorkerGateway

    result = PlatformWorkerGateway(mission_id=body.mission_id).invoke(
        service_id, payload=body.payload
    )
    if not result.get("ok") and result.get("error"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result


@app.get("/processor/harness")
def alpha_harness_catalog() -> Dict[str, Any]:
    from mesie.harness.alpha_registry import harness_manifest
    from mesie.harness.auto_business import auto_business_catalog
    from mesie.harness.template_library import template_manifest
    from mesie.compute.virtual_products import load_products

    latency = {}
    hub_path = ROOT / "deliverables" / "compute" / "MESIE_COMPUTE_HUB.json"
    family_path = ROOT / "deliverables" / "compute" / "MESIE_COMPUTING_FAMILY_RELEASE.json"
    if family_path.is_file():
        try:
            fam = json.loads(family_path.read_text(encoding="utf-8"))
            latency = fam.get("latency_table_ms") or {}
        except json.JSONDecodeError:
            pass
    if not latency and hub_path.is_file():
        try:
            hub = json.loads(hub_path.read_text(encoding="utf-8"))
            latency = {
                "fast_ann_p50_ms": (hub.get("fast_ann") or {}).get("p50_ms"),
                "vp_ann_p50_ms": (hub.get("virtual_processor") or {}).get("ann_p50_ms"),
                "st_phi_encode_p50_ms": (hub.get("st_phi") or {}).get("encode_p50_ms"),
                "nova_threat_p50_ms": (hub.get("virtual_processor") or {}).get("threat_p50_ms"),
            }
        except json.JSONDecodeError:
            pass

    return {
        "protocol": "MESIE-ALPHA-HARNESS-CATALOG/1.0",
        "harnesses": harness_manifest(),
        "templates": template_manifest(),
        "auto_ai_businesses": auto_business_catalog(),
        "virtual_products": [p.to_dict() for p in load_products()],
        "latency_table_ms": latency,
        "surfaces": {
            "platform_hub": "websites/platform-hub/index.html",
            "model_hub": "websites/model-hub/index.html",
            "solus_console": "websites/solus-console/index.html",
            "auro_studio": "websites/auro-studio/index.html",
            "producer_lab": "websites/producer-lab/index.html",
            "computing_family": "websites/computing-family/index.html",
            "enterprise_4k": "websites/enterprise-4k/index.html",
            "reality_engine": "websites/reality-engine/index.html",
            "hermes_fleet": "websites/hermes-fleet/index.html",
            "template_library": "deliverables/harness/TEMPLATE_LIBRARY.json",
        },
    }


@app.get("/processor/dsl")
def native_dsl_catalog() -> Dict[str, Any]:
    from mesie.native_dsl.registry import dsl_manifest

    return dsl_manifest(include_line_counts=True)


class NativeDSLRequest(BaseModel):
    source: str
    compile_only: bool = False


@app.post("/processor/dsl/{dsl_id}/compile")
def native_dsl_compile(dsl_id: str, body: NativeDSLRequest) -> Dict[str, Any]:
    from mesie.native_dsl.compiler import compile_source
    from mesie.native_dsl.registry import dsl_by_id

    if not dsl_by_id(dsl_id):
        raise HTTPException(status_code=404, detail=f"unknown native dsl: {dsl_id}")
    result = compile_source(dsl_id, body.source)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error", "compile failed"))
    return result


@app.post("/processor/dsl/{dsl_id}/run")
def native_dsl_run(dsl_id: str, body: NativeDSLRequest) -> Dict[str, Any]:
    from mesie.native_dsl.compiler import compile_and_run, compile_source
    from mesie.native_dsl.registry import dsl_by_id

    if not dsl_by_id(dsl_id):
        raise HTTPException(status_code=404, detail=f"unknown native dsl: {dsl_id}")
    if body.compile_only:
        result = compile_source(dsl_id, body.source)
    else:
        result = compile_and_run(dsl_id, body.source)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error", "dsl failed"))
    return result


@app.get("/processor/autonomous")
def autonomous_status() -> Dict[str, Any]:
    from mesie.server.coherence_engine import load_coherence
    from mesie.server.process_guardian import guardian_snapshot

    state_path = ROOT / "deliverables" / "runtime" / "AUTONOMOUS_ORCHESTRATOR_STATE.json"
    orch = {}
    if state_path.is_file():
        try:
            orch = json.loads(state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            orch = {}
    return {
        "self_executing": True,
        "coherence": load_coherence(),
        "guardian": guardian_snapshot(),
        "orchestrator": orch,
        "doctrine": "MESIE executes for AI runtime — users get workflows, platform self-heals.",
    }


@app.get("/processor/market-research")
def market_research() -> Dict[str, Any]:
    from mesie.processor.market_research import build_market_research

    return build_market_research()


@app.get("/processor/market-ready")
def market_ready_status() -> Dict[str, Any]:
    from mesie.market.four_tier_loop import market_ready_manifest

    return market_ready_manifest()


@app.post("/processor/market-ready/cycle")
def market_ready_cycle(tier: str = "") -> Dict[str, Any]:
    from mesie.market.four_tier_loop import run_market_cycle

    return run_market_cycle(tier=tier or None)


@app.get("/processor/mesh")
def mesh_status() -> Dict[str, Any]:
    from mesie.processor.mesh_protocol import VirtualProcessorMeshNode, load_mesh_state

    node = VirtualProcessorMeshNode()
    st = load_mesh_state()
    return {"live": node.status(), "state": st}


@app.post("/processor/mesh/pulse")
def mesh_pulse() -> Dict[str, Any]:
    return _proc().mesh_pulse().to_dict()


@app.post("/processor/mesh/soak")
def mesh_soak() -> Dict[str, Any]:
    from mesie.processor.mesh_protocol import run_mesh_soak

    return run_mesh_soak()


@app.get("/processor/official-dossier")
def official_dossier() -> Dict[str, Any]:
    from mesie.processor.official_pack import OFFICIAL_DIR
    import json

    path = OFFICIAL_DIR / "VIRTUAL_PROCESSOR_OFFICIAL_DOSSIER.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    from mesie.processor.official_pack import build_official_dossier

    return build_official_dossier(run_tests=False)


@app.get("/processor/official/technology")
def official_technology() -> Dict[str, Any]:
    from mesie.processor.official_pack import build_technology_overview

    return build_technology_overview()


@app.get("/processor/official/use-cases")
def official_use_cases() -> Dict[str, Any]:
    from mesie.processor.official_pack import build_use_cases

    return build_use_cases()


@app.get("/processor/official/certifications")
def official_certifications() -> Dict[str, Any]:
    from mesie.processor.official_pack import build_certification_manifest

    return build_certification_manifest(live=True)


@app.get("/processor/official/compliance")
def official_compliance() -> Dict[str, Any]:
    from mesie.processor.official_pack import build_compliance_pack

    return build_compliance_pack()


@app.post("/processor/official/commercial-tests")
def official_commercial_tests() -> Dict[str, Any]:
    from mesie.processor.official_pack import run_commercial_tests

    return run_commercial_tests(quick=True)


@app.get("/processor/nova-runtime")
def nova_runtime() -> Dict[str, Any]:
    from mesie.agentic.micro.runtime_supervisor import load_runtime_state

    return load_runtime_state()


@app.get("/processor/tools")
def list_tools() -> Dict[str, Any]:
    from mesie.tools.registry import TOOLS

    return {
        "count": len(TOOLS),
        "tools": [{"id": t.id, "name": t.name, "command": t.command} for t in TOOLS[:40]],
        "note": "POST /processor/exec {\"tool_id\": \"benchmark\"} to run without chat",
    }


# --- MESIE COMPUTE first-class endpoints ---


class ComputeEncodeRequest(BaseModel):
    payload: Any
    model: str = Field(default="ST-φ-256")


class ComputeBenchmarkRequest(BaseModel):
    trials: int = Field(default=200, ge=10, le=2000)
    model: str = Field(default="ST-φ-256")


@app.get("/processor/compute/status")
def compute_status() -> Dict[str, Any]:
    from mesie.compute.hub import compute_hub_snapshot

    return compute_hub_snapshot()


@app.get("/processor/compute/products")
def compute_products() -> Dict[str, Any]:
    from mesie.compute.virtual_products import load_products, save_products

    products = load_products()
    save_products(products)
    return {"products": [p.to_dict() for p in products], "first_class": True}


@app.get("/processor/compute/metrics")
def compute_metrics() -> Dict[str, Any]:
    from mesie.compute.live_metrics import collect_live_metrics

    return collect_live_metrics()


@app.post("/processor/compute/encode")
def compute_encode(body: ComputeEncodeRequest) -> Dict[str, Any]:
    from mesie.compute.hub import MESIEComputeHub

    return MESIEComputeHub(model_id=body.model).encode(body.payload)


@app.post("/processor/compute/benchmark")
def compute_benchmark(body: ComputeBenchmarkRequest) -> Dict[str, Any]:
    from mesie.compute.hub import MESIEComputeHub

    return MESIEComputeHub(model_id=body.model).full_benchmark(trials=body.trials)


@app.get("/processor/compute/squads")
def compute_squads() -> Dict[str, Any]:
    from mesie.compute.tri_agent_squads import list_squads

    return {"squads": list_squads()}


@app.post("/processor/compute/squads/run")
def compute_squads_run(squad_id: str = "") -> Dict[str, Any]:
    from mesie.compute.tri_agent_squads import execute_all_squads, execute_squad

    if squad_id:
        return execute_squad(squad_id)
    return execute_all_squads()


@app.get("/processor/research/acoustic-metamaterial")
def research_acoustic_metamaterial() -> Dict[str, Any]:
    from mesie.research.acoustic_metamaterial_agent import run_research_agent
    from mesie.domains.acoustic_metamaterial import run_metamaterial_suite

    return {"research": run_research_agent(write_artifacts=False), "domain_suite": run_metamaterial_suite()}


@app.get("/processor/compute/transformers")
def compute_transformers() -> Dict[str, Any]:
    from mesie.compute.spectral_transformer import list_st_phi_models, write_model_registry

    write_model_registry()
    return {"models": list_st_phi_models(), "native": True, "vs_huggingface": "no_torch_required"}


@app.get("/processor/compute/token-budget")
def compute_token_budget() -> Dict[str, Any]:
    from mesie.compute.token_budget import snapshot

    return snapshot()


@app.get("/processor/grok/protocol")
def grok_protocol() -> Dict[str, Any]:
    from mesie.grok.protocol import build_protocol_manifest

    return build_protocol_manifest()


@app.post("/processor/grok/worker")
def grok_worker(body: Dict[str, Any]) -> Dict[str, Any]:
    from mesie.grok.worker_bus import WorkerBus, WorkerRole

    role = WorkerRole(body.get("role", "worker"))
    action = str(body.get("action", "pytest_smoke"))
    payload = body.get("payload") or {}
    return WorkerBus(mission_id=str(body.get("mission_id", "api"))).dispatch(role, action, payload=payload)


@app.get("/processor/federation/status")
def federation_status() -> Dict[str, Any]:
    from mesie.enterprise.federation import FederationOrchestrator

    return FederationOrchestrator().status()


@app.post("/processor/federation/envelope")
def federation_envelope(body: Dict[str, Any]) -> Dict[str, Any]:
    from mesie.enterprise.federation.protocol import EnterpriseFederationEnvelope

    env = EnterpriseFederationEnvelope.from_dict(body)
    return env.seal_enterprise()


@app.post("/processor/federation/invoke")
def federation_invoke(body: Dict[str, Any]) -> Dict[str, Any]:
    from mesie.enterprise.federation import FederationOrchestrator
    from mesie.enterprise.federation.protocol import EnterpriseFederationEnvelope

    env = EnterpriseFederationEnvelope.from_dict(body)
    return FederationOrchestrator().invoke(env)


@app.get("/processor/enterprise/status")
def enterprise_status() -> Dict[str, Any]:
    import json
    from pathlib import Path

    from mesie.enterprise.repo_unifier import build_thread_manifest

    state_path = Path(__file__).resolve().parents[2] / "deliverables" / "enterprise" / "EXECUTION_ENGINE_STATE.json"
    state: Dict[str, Any] = {}
    if state_path.is_file():
        state = json.loads(state_path.read_text(encoding="utf-8"))
    return {"thread": build_thread_manifest(), "last_run": state}


@app.post("/processor/enterprise/run")
def enterprise_run(body: Dict[str, Any]) -> Dict[str, Any]:
    from mesie.enterprise.execution_engine import EnterpriseExecutionEngine

    mission = str(body.get("mission_id", "api-run"))
    skip = body.get("skip") or []
    return EnterpriseExecutionEngine(mission_id=mission).run(skip=skip)


@app.get("/processor/tokens/manifest")
def tokens_manifest() -> Dict[str, Any]:
    from mesie.tokens.dual_bridge import token_manifest

    return token_manifest()


@app.post("/processor/tokens/mint")
def tokens_mint(body: Dict[str, Any]) -> Dict[str, Any]:
    from mesie.tokens.dual_bridge import mint_receipt_token

    return mint_receipt_token(body or {})


@app.get("/processor/production-stack")
def production_stack() -> Dict[str, Any]:
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    deliv = root / "deliverables"

    def _load(rel: str) -> Dict[str, Any]:
        p = deliv / rel
        if not p.is_file():
            return {"exists": False}
        return {"exists": True, "data": json.loads(p.read_text(encoding="utf-8"))}

    showcase = _load("nova/NOVA_SHOWCASE.json")
    headline: Dict[str, Any] = {}
    if showcase.get("exists"):
        d = showcase["data"]
        headline = {
            "threat_p50_ms": d.get("threat", {}).get("p50_ms") or d.get("robotics", {}).get("threat_p50_ms"),
            "fusion_dims": d.get("robotics", {}).get("fusion_dims", 256),
            "library_mb": d.get("foundations", {}).get("library", {}).get("mb"),
            "engine_count": d.get("foundations", {}).get("engine_count"),
            "virtual_chip_certified": d.get("virtual_chip", {}).get("certified"),
        }

    from mesie.agentic.micro.runtime_supervisor import load_runtime_state

    return {
        "ok": True,
        "doc": str(deliv / "enterprise" / "PRODUCTION_STACK_STATUS.md"),
        "running": {
            "processor": _proc().status(),
            "nova": load_runtime_state(),
        },
        "headline": headline,
        "artifacts": {
            "release": _load("processor/VIRTUAL_PROCESSOR_RELEASE.json"),
            "devkit": _load("processor/VIRTUAL_PROCESSOR_DEVKIT.json"),
            "showcase": showcase,
            "architecture": _load("processor/MESIE_STACK_ARCHITECTURE.json"),
        },
        "mcp": "deliverables/icp/MCP_FULL_CONFIG.json",
    }