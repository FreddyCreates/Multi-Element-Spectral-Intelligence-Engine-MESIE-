"""Inventory Medina infrastructure — papers, deliverables, services, MCP, tools."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.version_info import MESIE_VERSION, MAESI_SDK_VERSION

HOME = Path.home()
MESIE_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class SurfaceEntry:
    id: str
    name: str
    kind: str
    path: str
    callable_via: str
    proof: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "path": self.path,
            "callable_via": self.callable_via,
            "proof": self.proof,
        }


@dataclass
class SurfaceCatalog:
    operator: str = "Medin"
    mesie_version: str = MESIE_VERSION
    sdk_version: str = MAESI_SDK_VERSION
    generated_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    systems: List[SurfaceEntry] = field(default_factory=list)
    papers: List[SurfaceEntry] = field(default_factory=list)
    deliverables: List[SurfaceEntry] = field(default_factory=list)
    services: List[SurfaceEntry] = field(default_factory=list)
    agent_entrypoints: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product": "Medina Surface",
            "operator": self.operator,
            "mesie_version": self.mesie_version,
            "sdk_version": self.sdk_version,
            "generated_at": self.generated_at,
            "instruction_for_agents": (
                "Call medina_surface first. Do not reinvent. "
                "Use invoke(system, action) — talk is external; solids come from here."
            ),
            "agent_entrypoints": self.agent_entrypoints,
            "counts": {
                "systems": len(self.systems),
                "papers": len(self.papers),
                "deliverables": len(self.deliverables),
                "services": len(self.services),
            },
            "systems": [s.to_dict() for s in self.systems],
            "papers": [p.to_dict() for p in self.papers],
            "deliverables": [d.to_dict() for d in self.deliverables],
            "services": [s.to_dict() for s in self.services],
        }


def _proof_path(p: Path) -> Dict[str, Any]:
    if not p.exists():
        return {"exists": False}
    st = p.stat()
    return {"exists": True, "bytes": st.st_size, "mtime": st.st_mtime}


def build_catalog(*, export: bool = True) -> SurfaceCatalog:
    cat = SurfaceCatalog()

    cat.agent_entrypoints = [
        {"id": "surface_cli", "command": "python scripts/medina_surface.py --status"},
        {"id": "surface_invoke", "command": "python scripts/medina_surface.py invoke --system mesie --action <tool-id>"},
        {"id": "surface_http", "url": "http://127.0.0.1:8760/surface/status"},
        {"id": "processor_http", "url": "http://127.0.0.1:8750/processor/status"},
        {"id": "loom_mcp", "note": "MCP server loom — loom_status, skills_run, runspace_exec, knowledge_mint"},
        {"id": "mesie_cli", "command": "python -m mesie.tools.cli run <tool-id>"},
    ]

    systems = [
        ("mesie", "MESIE / MAESI / NeuroAIX", MESIE_ROOT),
        ("loom", "Loom MCP + Medina Vault", HOME / ".medina"),
        ("memory-desk", "Sovereign Memory Desk", HOME / "Documents/Enterprise-OS-intelligence/sovereign-memory-desk"),
        ("command-platform", "Command Platform (ICP organism)", HOME / "command-platform"),
        ("neuroswarm", "NeuroSwarmAI", HOME / "NEUROSWARMAI"),
        ("pegasus", "Spatium Computationis", HOME / "pegasus-battleops/spatium-computationis"),
        ("terminalis", "Terminalis Native Language Runtime", HOME / "OneDrive/Documents/Terminalis_Native_Language_Runtime"),
        ("parallax", "PARALLAX Exchange Clearinghouse", HOME / "PARALLAX-Exchange-Clearinghouse"),
        ("gptrepo", "GPTREPO / Auro protocols", HOME / "GPTREPO"),
        (
            "coding-lab",
            "Medina Coding Lab — 2 seats + repo fleet + micro agents",
            HOME / "Documents/Enterprise-OS-intelligence/medina-coding-lab",
        ),
    ]
    for sid, name, path in systems:
        cat.systems.append(
            SurfaceEntry(
                id=sid,
                name=name,
                kind="system",
                path=str(path),
                callable_via=f"medina_surface invoke --system {sid}",
                proof=_proof_path(path),
            )
        )

    paper_dir = MESIE_ROOT / "docs" / "papers"
    if paper_dir.is_dir():
        for p in sorted(paper_dir.glob("paper_*.md")):
            cat.papers.append(
                SurfaceEntry(
                    id=p.stem,
                    name=p.stem.replace("_", " "),
                    kind="paper",
                    path=str(p),
                    callable_via="read path",
                    proof=_proof_path(p),
                )
            )

    deliv = MESIE_ROOT / "deliverables"
    if deliv.is_dir():
        for p in sorted(deliv.rglob("*.json"))[:80]:
            rel = p.relative_to(deliv)
            cat.deliverables.append(
                SurfaceEntry(
                    id=str(rel).replace("\\", "/").replace(".json", ""),
                    name=rel.name,
                    kind="deliverable",
                    path=str(p),
                    callable_via="read JSON proof",
                    proof=_proof_path(p),
                )
            )

    from mesie.tools.registry import TOOLS

    cat.services.append(
        SurfaceEntry(
            id="mesie-tools",
            name=f"MESIE native tools ({len(TOOLS)})",
            kind="tool_registry",
            path=str(MESIE_ROOT / "mesie/tools/registry.py"),
            callable_via="python -m mesie.tools.cli run <id>",
            proof={"count": len(TOOLS), "exists": True},
        )
    )

    processor_manifest = MESIE_ROOT / "deliverables" / "processor" / "MESIE_Processor_Manifest.json"
    cat.services.append(
        SurfaceEntry(
            id="virtual-processor",
            name="MESIE Virtual Processor",
            kind="http_service",
            path=str(MESIE_ROOT / "mesie/processor"),
            callable_via="http://127.0.0.1:8750/processor/status | medina_surface invoke --system mesie --action virtual-processor",
            proof=_proof_path(processor_manifest),
        )
    )
    cat.services.append(
        SurfaceEntry(
            id="medina-surface-http",
            name="Medina Surface HTTP",
            kind="http_service",
            path=str(MESIE_ROOT / "mesie/surface"),
            callable_via="http://127.0.0.1:8760/surface/status",
            proof=_proof_path(deliv / "MEDINA_SURFACE_MANIFEST.json"),
        )
    )

    if export:
        out = deliv / "MEDINA_SURFACE_MANIFEST.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(cat.to_dict(), indent=2), encoding="utf-8")

    return cat