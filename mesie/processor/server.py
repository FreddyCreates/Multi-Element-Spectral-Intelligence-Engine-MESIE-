"""HTTP Virtual Processor Server — port 8750, for coding agents + MCP bridges."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from mesie.processor.virtual_processor import VirtualProcessor

app = FastAPI(title="MESIE Virtual Processor", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/processor/market-research")
def market_research() -> Dict[str, Any]:
    from mesie.processor.market_research import build_market_research

    return build_market_research()


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