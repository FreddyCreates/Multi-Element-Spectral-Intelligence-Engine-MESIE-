"""Unify 3 repos into one enterprise thread manifest."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "deliverables" / "enterprise" / "UNIFIED_REPO_THREAD.json"

REPOS = [
    {
        "id": "mesie-main",
        "path": str(ROOT),
        "role": "primary — full ecosystem (MESIE + NOVA + ICP + Grok)",
    },
    {
        "id": "cloudcolony-sovereign",
        "path": str(Path.home() / "cloudcolony-sovereign"),
        "role": "sovereign stack export (CloudColony deploy handoff)",
    },
    {
        "id": "mesie-bak-jun3",
        "path": str(ROOT.parent / "Multi-Element-Spectral-Intelligence-Engine-MESIE-.bak-20260603-203359"),
        "role": "historical backup — lineage anchor",
    },
]


def _scan(path: Path) -> Dict[str, Any]:
    if not path.is_dir():
        return {"exists": False, "files": 0, "bytes": 0}
    files = [f for f in path.rglob("*") if f.is_file()]
    return {
        "exists": True,
        "files": len(files),
        "bytes": sum(f.stat().st_size for f in files),
        "mb": round(sum(f.stat().st_size for f in files) / 1e6, 2),
    }


def build_thread_manifest() -> Dict[str, Any]:
    products = [
        {"sku": "MESIE-CORE", "module": "mesie/", "start": "Start-VirtualProcessor.ps1"},
        {"sku": "MESIE-COMPUTE", "module": "mesie/compute/", "start": "Start-MESIECompute.ps1"},
        {"sku": "NOVA-RUNTIME", "module": "mesie/agentic/micro/", "start": "Start-NovaRuntime.ps1"},
        {"sku": "VIRTUAL-PROCESSOR", "module": "mesie/processor/", "start": ":8750/processor/status"},
        {"sku": "SOVEREIGN-CLOUD-ICP", "module": "icp/sovereign-cloud/", "start": "Start-SovereignColony.ps1"},
        {"sku": "SOVEREIGN-OS", "module": "sovereign-os/", "start": "Start-SovereignOS.ps1"},
        {"sku": "CLOUDCOLONY-TRIPLE", "module": "mesie/cloud/", "start": "python -m mesie.cloud.triple_protocol"},
        {"sku": "MULTIMODAL-MCP", "module": "mesie/cloud/multimodal_triple_protocol.py", "start": "MULTIMODAL_TRIPLE_PROTOCOL.json"},
        {"sku": "GROK-NOVA-MESIE", "module": "mesie/grok/", "start": "Start-GrokNovaMesie.ps1"},
        {"sku": "MCP-COLONIES", "module": "mcp-colonies/", "start": "MCP_CURSOR_CONFIG.json"},
        {"sku": "ACOUSTIC-RESEARCH", "module": "mesie/research/", "start": "acoustic_metamaterial_agent"},
        {"sku": "COMMERCIAL-PACK", "module": "deliverables/processor/official/", "start": "Deploy-MESIE.ps1 -Official"},
        {"sku": "SWARM-MISSIONS", "module": ".grok/skills/swarm-mission-*", "start": "/swarm-mission-grok"},
        {"sku": "LOAD-BEARING", "module": "mesie/compute/token_budget.py", "start": "/load-bearing-tokens"},
        {"sku": "BIOTECH-DOMAINS", "module": "mesie/domains/", "start": "domain_signal_hub career"},
        {"sku": "MCP-QUERY", "module": "mcp-colonies/query-server/", "start": "query_production_stack"},
        {"sku": "USE-CASE-CHILDREN", "module": "public-forks/mesie-usecase-*", "start": "scripts/build_use_case_child_repos.py"},
        {"sku": "AUTONOMOUS-RUNTIME", "module": "mesie/server/autonomous_orchestrator.py", "start": "Start-MESIE-Autonomous.ps1"},
    ]
    repos_out: List[Dict[str, Any]] = []
    for r in REPOS:
        p = Path(r["path"])
        repos_out.append({**r, "scan": _scan(p)})

    return {
        "protocol": "MESIE-UNIFIED-REPO-THREAD/1.0",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repos": repos_out,
        "products": products,
        "product_count": len(products),  # 16 incl biotech + mcp query
        "thread_intact": all(x["scan"].get("exists") for x in repos_out[:2]),
        "primary_repo": str(ROOT),
    }


def write_thread_manifest() -> Dict[str, Any]:
    m = build_thread_manifest()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "path": str(OUT), "manifest": m}