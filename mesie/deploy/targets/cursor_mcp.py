"""Merge MESIE MCP snippets into ~/.cursor/mcp.json without touching Loom keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from mesie.deploy.registry import LOOM_PROTECTED_MCP_KEYS, ServiceDefinition

ROOT = Path(__file__).resolve().parents[3]
SANDBOX = ROOT / "deliverables" / "deploy" / "sandbox"


def _cursor_mcp_path() -> Path:
    return Path.home() / ".cursor" / "mcp.json"


def plan_cursor_mcp(svc: ServiceDefinition) -> Dict[str, Any]:
    snippet_path = SANDBOX / svc.id / "mcp-snippet.json"
    cursor_path = _cursor_mcp_path()
    plan: Dict[str, Any] = {
        "action": "merge_mcp_snippet",
        "snippet_path": str(snippet_path),
        "cursor_mcp_path": str(cursor_path),
        "snippet_exists": snippet_path.is_file(),
        "protected_keys": sorted(LOOM_PROTECTED_MCP_KEYS),
    }
    if snippet_path.is_file():
        snippet = json.loads(snippet_path.read_text(encoding="utf-8"))
        plan["keys_to_add"] = list(snippet.get("mcpServers", {}).keys())
    else:
        plan["keys_to_add"] = []
        plan["note"] = f"no MCP shim for {svc.id}"
    return plan


def apply_cursor_mcp(svc: ServiceDefinition) -> Dict[str, Any]:
    plan = plan_cursor_mcp(svc)
    snippet_path = Path(plan["snippet_path"])
    if not snippet_path.is_file():
        return {**plan, "applied": False, "reason": "no mcp-snippet.json"}

    snippet = json.loads(snippet_path.read_text(encoding="utf-8"))
    new_servers = snippet.get("mcpServers", {})
    if not new_servers:
        return {**plan, "applied": False, "reason": "empty mcpServers"}

    cursor_path = _cursor_mcp_path()
    existing: Dict[str, Any] = {}
    if cursor_path.is_file():
        existing = json.loads(cursor_path.read_text(encoding="utf-8")) or {}

    servers = existing.setdefault("mcpServers", {})
    for key in LOOM_PROTECTED_MCP_KEYS:
        if key in servers:
            plan.setdefault("preserved", []).append(key)

    for key, cfg in new_servers.items():
        if key in LOOM_PROTECTED_MCP_KEYS:
            continue
        servers[key] = cfg

    cursor_path.parent.mkdir(parents=True, exist_ok=True)
    bak = cursor_path.with_suffix(".json.mesie-deploy-bak")
    if cursor_path.is_file() and not bak.is_file():
        bak.write_text(cursor_path.read_text(encoding="utf-8"), encoding="utf-8")

    cursor_path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    return {**plan, "applied": True, "merged_keys": list(new_servers.keys())}
