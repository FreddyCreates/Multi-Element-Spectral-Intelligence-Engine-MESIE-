"""Dispatch agent calls to Medina systems — no reinventing."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class DispatchResult:
    ok: bool
    system: str
    action: str
    detail: str
    exit_code: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "system": self.system,
            "action": self.action,
            "detail": self.detail,
            "exit_code": self.exit_code,
        }


class SurfaceDispatcher:
    """Route agent invocations to real Medina infrastructure."""

    MESIE_ACTIONS = {
        "benchmark": ["python", "scripts/run_sdk_major_benchmarks.py"],
        "nova-release": ["python", "scripts/run_nova_release.py"],
        "neuroswarm-readiness": ["python", "scripts/run_neuroswarm_readiness.py"],
        "virtual-silicon": ["python", "scripts/run_virtual_silicon_suite.py"],
        "spacetime": ["python", "scripts/run_spacetime_suite.py"],
        "proof-substrate": ["python", "scripts/run_proof_substrate.py"],
        "release-ready": ["python", "scripts/run_release_ready.py"],
        "surface-refresh": ["python", "scripts/medina_surface.py", "--export"],
        "virtual-processor": ["python", "scripts/run_virtual_processor.py"],
        "processor-benchmarks": ["python", "scripts/run_processor_benchmarks.py"],
        "service-package": ["python", "scripts/package_services.py", "--all"],
    }

    def invoke(self, system: str, action: str, *, extra_args: Optional[List[str]] = None) -> DispatchResult:
        system = system.lower().strip()
        action = action.lower().strip()
        extra = extra_args or []

        if system == "mesie":
            return self._mesie(action, extra)
        if system in ("processor", "virtual-processor"):
            return self._processor(action)
        if system in ("memory-desk", "smd"):
            return self._memory_desk(action)
        if system in ("coding-lab", "lab"):
            return self._coding_lab(action)
        return DispatchResult(False, system, action, f"unknown system: {system}", 1)

    def _mesie(self, action: str, extra: List[str]) -> DispatchResult:
        from mesie.tools.registry import tool_by_id

        if action in self.MESIE_ACTIONS:
            cmd = self.MESIE_ACTIONS[action] + extra
        else:
            tool = tool_by_id(action)
            if not tool:
                known = ", ".join(sorted(self.MESIE_ACTIONS.keys()))
                return DispatchResult(
                    False, "mesie", action,
                    f"unknown action. shortcuts: {known}. or use any mesie tool id from: python -m mesie.tools.cli list",
                    1,
                )
            cmd = [sys.executable] + tool.command.split()[1:] if tool.command.startswith("python ") else tool.command.split()

        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=600)
        tail = (r.stdout or r.stderr)[-1200:]
        return DispatchResult(r.returncode == 0, "mesie", action, tail, r.returncode)

    def _coding_lab(self, action: str) -> DispatchResult:
        import urllib.request

        base = "http://127.0.0.1:8770"
        routes = {
            "health": "/api/health",
            "repos": "/api/repos",
            "micro": "/api/micro/fleet",
            "scan": "/api/repos/scan",
        }
        try:
            if action == "activate-micro":
                req = urllib.request.Request(f"{base}/api/micro/activate", method="POST", data=b"")
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return DispatchResult(True, "coding-lab", action, resp.read().decode()[:800])
            path = routes.get(action)
            if not path:
                return DispatchResult(
                    False, "coding-lab", action,
                    f"actions: {', '.join(sorted(routes))}, activate-micro",
                    1,
                )
            method = "POST" if action == "scan" else "GET"
            req = urllib.request.Request(f"{base}{path}", method=method, data=b"" if method == "POST" else None)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return DispatchResult(True, "coding-lab", action, resp.read().decode()[:800])
        except Exception as exc:
            return DispatchResult(False, "coding-lab", action, str(exc), 1)

    def _memory_desk(self, action: str) -> DispatchResult:
        import urllib.request

        base = "http://127.0.0.1:8740"
        try:
            if action == "health":
                with urllib.request.urlopen(f"{base}/api/health", timeout=5) as resp:
                    return DispatchResult(True, "memory-desk", action, resp.read().decode()[:800])
            return DispatchResult(False, "memory-desk", action, "actions: health", 1)
        except Exception as exc:
            return DispatchResult(False, "memory-desk", action, str(exc), 1)

    def _processor(self, action: str) -> DispatchResult:
        import urllib.request

        base = "http://127.0.0.1:8750"
        routes = {
            "status": ("GET", "/processor/status", None),
            "accounting": ("GET", "/processor/accounting", None),
            "tools": ("GET", "/processor/tools", None),
            "benchmark": ("POST", "/processor/benchmark", b'{"trials": 50}'),
            "virtual-chip": ("POST", "/processor/virtual-chip", b"{}"),
            "robotics-pulse": ("POST", "/processor/robotics-pulse", b"{}"),
        }
        if action in ("virtual-processor", "start"):
            return DispatchResult(
                False, "processor", action,
                "start via: python -m mesie.processor --serve  or  Start-VirtualProcessor.ps1",
                1,
            )
        try:
            spec = routes.get(action)
            if not spec:
                return DispatchResult(
                    False, "processor", action,
                    f"actions: {', '.join(sorted(routes))}, virtual-processor (start hint)",
                    1,
                )
            method, path, body = spec
            req = urllib.request.Request(
                f"{base}{path}",
                data=body,
                method=method,
                headers={"Content-Type": "application/json"} if body else {},
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                return DispatchResult(True, "processor", action, resp.read().decode()[:1200])
        except Exception as exc:
            return DispatchResult(False, "processor", action, str(exc), 1)