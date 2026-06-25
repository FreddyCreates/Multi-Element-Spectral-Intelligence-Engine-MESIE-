"""Medina Surface HTTP — port 8760. Agents call this first."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from mesie.surface.catalog import build_catalog
from mesie.surface.dispatcher import SurfaceDispatcher

app = FastAPI(title="Medina Surface", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_dispatcher = SurfaceDispatcher()


class InvokeRequest(BaseModel):
    system: str = Field(description="mesie | memory-desk | loom (via MCP)")
    action: str = Field(description="tool id or shortcut: benchmark, nova-release, etc.")
    args: list[str] = Field(default_factory=list)


@app.get("/surface/status")
def status() -> Dict[str, Any]:
    cat = build_catalog(export=True)
    return cat.to_dict()


@app.post("/surface/invoke")
def invoke(body: InvokeRequest) -> Dict[str, Any]:
    return _dispatcher.invoke(body.system, body.action, extra_args=body.args).to_dict()


@app.get("/surface/systems")
def systems() -> Dict[str, Any]:
    cat = build_catalog(export=False)
    return {"systems": [s.to_dict() for s in cat.systems]}


@app.get("/surface/deliverables")
def deliverables() -> Dict[str, Any]:
    cat = build_catalog(export=False)
    return {"deliverables": [d.to_dict() for d in cat.deliverables[:40]]}