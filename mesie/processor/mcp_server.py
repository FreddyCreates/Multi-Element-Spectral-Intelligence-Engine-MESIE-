#!/usr/bin/env python3
"""Thin MCP stdio server — proxies MESIE Virtual Processor HTTP :8750."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

SERVER_NAME = "mesie-processor"
SERVER_VERSION = "1.0.0"
MCP_VERSION = "2024-11-05"
BASE_URL = os.environ.get("MESIE_PROCESSOR_URL", "http://127.0.0.1:8750").rstrip("/")

TOOLS: Dict[str, Dict[str, Any]] = {
    "processor_status": {
        "description": "MESIE Virtual Processor status — operations, accounting, vault path.",
        "inputSchema": {"type": "object", "properties": {}},
        "method": "GET",
        "path": "/processor/status",
    },
    "processor_accounting": {
        "description": "Local LRC accounting ledger export.",
        "inputSchema": {"type": "object", "properties": {}},
        "method": "GET",
        "path": "/processor/accounting",
    },
    "processor_embed": {
        "description": "Embed one spectral record via FastSpectralCompute.",
        "inputSchema": {
            "type": "object",
            "properties": {"record_path": {"type": "string", "default": "ref-earthquake-psd-001"}},
        },
        "method": "POST",
        "path": "/processor/embed",
        "body_keys": ["record_path"],
    },
    "processor_benchmark": {
        "description": "Run threat + virtual chip benchmark lane.",
        "inputSchema": {
            "type": "object",
            "properties": {"trials": {"type": "integer", "default": 200}},
        },
        "method": "POST",
        "path": "/processor/benchmark",
        "body_keys": ["trials"],
    },
    "processor_exec": {
        "description": "Execute a MESIE native tool by id (no chat).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tool_id": {"type": "string"},
                "timeout_s": {"type": "integer", "default": 120},
            },
            "required": ["tool_id"],
        },
        "method": "POST",
        "path": "/processor/exec",
        "body_keys": ["tool_id", "timeout_s"],
    },
}


def _http_call(method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Any:
    url = f"{BASE_URL}{path}"
    data = json.dumps(body or {}).encode("utf-8") if method == "POST" else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if data else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {"ok": False, "error": exc.read().decode("utf-8", errors="replace")[:800]}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _tool_list() -> List[Dict[str, Any]]:
    return [
        {"name": name, "description": spec["description"], "inputSchema": spec["inputSchema"]}
        for name, spec in TOOLS.items()
    ]


def _handle_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    spec = TOOLS.get(name)
    if not spec:
        return {"content": [{"type": "text", "text": json.dumps({"error": f"unknown tool: {name}"})}], "isError": True}
    body = None
    if spec["method"] == "POST":
        keys = spec.get("body_keys", [])
        body = {k: arguments.get(k, spec["inputSchema"].get("properties", {}).get(k, {}).get("default")) for k in keys}
        body = {k: v for k, v in body.items() if v is not None}
    result = _http_call(spec["method"], spec["path"], body)
    return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}


def _respond(msg_id: Any, result: Any) -> None:
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": result}) + "\n")
    sys.stdout.flush()


def _error(msg_id: Any, code: int, message: str) -> None:
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}) + "\n")
    sys.stdout.flush()


def _handle(msg: Dict[str, Any]) -> None:
    msg_id = msg.get("id")
    method = msg.get("method", "")

    if method == "initialize":
        _respond(msg_id, {
            "protocolVersion": MCP_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        })
        return

    if method == "notifications/initialized":
        return

    if method == "tools/list":
        _respond(msg_id, {"tools": _tool_list()})
        return

    if method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name", "")
        arguments = params.get("arguments") or {}
        _respond(msg_id, _handle_tool(name, arguments))
        return

    if msg_id is not None:
        _error(msg_id, -32601, f"method not found: {method}")


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        _handle(msg)


if __name__ == "__main__":
    main()
