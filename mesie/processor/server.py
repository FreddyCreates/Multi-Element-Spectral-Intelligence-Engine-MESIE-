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


@app.post("/processor/virtual-chip")
def virtual_chip() -> Dict[str, Any]:
    return _proc().virtual_chip_certify().to_dict()


@app.post("/processor/robotics-pulse")
def robotics_pulse() -> Dict[str, Any]:
    return _proc().robotics_pulse().to_dict()


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