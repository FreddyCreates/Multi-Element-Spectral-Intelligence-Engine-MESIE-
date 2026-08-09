"""Shippable agent harnesses for local core and edge API execution."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from mesie.agentic.ghost import TaskSpec
from mesie.engines.core_engine import CoreConfig, CoreEngine


@dataclass(frozen=True)
class HarnessProfile:
    name: str
    max_agents: int
    network_width: int
    timeout_s: float
    edge_timeout_s: float


PROFILES: Dict[str, HarnessProfile] = {
    "local": HarnessProfile("local", max_agents=32, network_width=2, timeout_s=10.0, edge_timeout_s=3.0),
    "dev": HarnessProfile("dev", max_agents=64, network_width=4, timeout_s=15.0, edge_timeout_s=5.0),
    "prod": HarnessProfile("prod", max_agents=128, network_width=8, timeout_s=20.0, edge_timeout_s=8.0),
}


@dataclass
class HarnessRunReport:
    harness: str
    mode: str
    profile: str
    ok: bool
    category: str
    summary: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _sample_record(record_id: str) -> Dict[str, Any]:
    return {
        "record_id": record_id,
        "components": [
            {
                "name": "component_0",
                "frequency": [1.0, 2.0, 3.0, 4.0],
                "amplitude": [0.2, 0.5, 0.3, 0.1],
            }
        ],
    }


def _failure_category(exc: Exception) -> str:
    if isinstance(exc, HTTPError):
        if exc.code in (401, 403):
            return "auth_failure"
        if 400 <= exc.code < 500:
            return "request_failure"
        return "service_failure"
    if isinstance(exc, URLError):
        return "connectivity_failure"
    return "runtime_failure"


class PythonCoreHarness:
    """Stable local/CI harness wrapping ghost/spawner + workflow execution."""

    def __init__(self, profile: str = "local", core: Optional[CoreEngine] = None) -> None:
        if profile not in PROFILES:
            raise ValueError(f"Unknown profile: {profile}")
        self.profile = PROFILES[profile]
        self.core = core or CoreEngine(
            config=CoreConfig(
                max_agents=self.profile.max_agents,
                network_width=self.profile.network_width,
            )
        )

    def health_check(self) -> HarnessRunReport:
        try:
            engines = set(self.core.registry.names())
            probe = self.core.dispatch("validation", "validate", {"record": _sample_record("health-probe")})
            if not probe.ok:
                return HarnessRunReport(
                    harness="python_core",
                    mode="local",
                    profile=self.profile.name,
                    ok=False,
                    category="engine_failure",
                    summary="Core validation probe failed.",
                    details={"error": probe.error},
                )
            expected = {"core", "validation", "workflow"}
            missing = sorted(expected - engines)
            ok = not missing
            return HarnessRunReport(
                harness="python_core",
                mode="local",
                profile=self.profile.name,
                ok=ok,
                category="ok" if ok else "startup_failure",
                summary="Core harness healthy." if ok else "Core harness missing required engines.",
                details={"engines": sorted(engines), "missing_engines": missing},
            )
        except Exception as exc:  # pragma: no cover - defensive
            return HarnessRunReport(
                harness="python_core",
                mode="local",
                profile=self.profile.name,
                ok=False,
                category=_failure_category(exc),
                summary="Core harness health check raised an exception.",
                details={"error": str(exc)},
            )

    def startup_validation(self) -> HarnessRunReport:
        try:
            record = _sample_record("harness-startup")
            task = TaskSpec(
                intent="startup_validation",
                timeout_s=self.profile.timeout_s,
                actions=[
                    {"engine": "validation", "action": "validate", "payload": {"record": record}},
                    {"engine": "embedding", "action": "transform", "payload": {"record": record}},
                ],
            )
            ghost_result = self.core.spawn_ghost(task)
            define_resp = self.core.dispatch(
                "workflow",
                "define",
                {
                    "workflow_id": "harness_startup",
                    "steps": [
                        {"name": "validate", "engine": "validation", "action": "validate"},
                        {"name": "reason", "engine": "intelligence", "action": "reason"},
                    ],
                },
            )
            run_resp = self.core.dispatch(
                "workflow",
                "run",
                {"context": {"record": record}},
            )
            ok = ghost_result.success and define_resp.ok and run_resp.ok and run_resp.data.get("completed", False)
            return HarnessRunReport(
                harness="python_core",
                mode="local",
                profile=self.profile.name,
                ok=ok,
                category="ok" if ok else "startup_failure",
                summary="Core harness startup validation passed." if ok else "Core harness startup validation failed.",
                details={
                    "ghost_success": ghost_result.success,
                    "ghost_error": ghost_result.error,
                    "workflow_defined": define_resp.ok,
                    "workflow_completed": run_resp.data.get("completed", False),
                    "workflow_error": run_resp.error,
                },
            )
        except Exception as exc:
            return HarnessRunReport(
                harness="python_core",
                mode="local",
                profile=self.profile.name,
                ok=False,
                category=_failure_category(exc),
                summary="Core harness startup validation raised an exception.",
                details={"error": str(exc)},
            )


class EdgeAPIHarness:
    """Deployable harness over MESIE edge API routes."""

    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:8787",
        profile: str = "local",
        api_key: Optional[str] = None,
    ) -> None:
        if profile not in PROFILES:
            raise ValueError(f"Unknown profile: {profile}")
        self.profile = PROFILES[profile]
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _request(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        body = None
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"******"
            headers["X-MESIE-Key"] = self.api_key
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
        req = Request(f"{self.base_url}{path}", data=body, method=method, headers=headers)
        with urlopen(req, timeout=self.profile.edge_timeout_s) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def health_check(self) -> HarnessRunReport:
        try:
            data = self._request("GET", "/health")
            ok = data.get("status") == "ok"
            return HarnessRunReport(
                harness="edge_api",
                mode="edge",
                profile=self.profile.name,
                ok=ok,
                category="ok" if ok else "service_failure",
                summary="Edge harness healthy." if ok else "Edge harness unhealthy.",
                details={"health": data},
            )
        except Exception as exc:
            return HarnessRunReport(
                harness="edge_api",
                mode="edge",
                profile=self.profile.name,
                ok=False,
                category=_failure_category(exc),
                summary="Edge harness health check failed.",
                details={"error": str(exc)},
            )

    def validate(self, record: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/v1/validate", record)

    def match(self, reference: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/v1/match", {"reference": reference, "candidate": candidate})

    def startup_validation(self) -> HarnessRunReport:
        try:
            health = self._request("GET", "/health")
            reference = _sample_record("edge-ref")
            candidate = _sample_record("edge-cand")
            candidate["components"][0]["amplitude"] = [0.21, 0.49, 0.29, 0.12]
            validate_result = self.validate(reference)
            match_result = self.match(reference, candidate)
            ok = (
                health.get("status") == "ok"
                and bool(validate_result.get("is_valid"))
                and "composite_score" in match_result
            )
            return HarnessRunReport(
                harness="edge_api",
                mode="edge",
                profile=self.profile.name,
                ok=ok,
                category="ok" if ok else "startup_failure",
                summary="Edge harness startup validation passed." if ok else "Edge harness startup validation failed.",
                details={
                    "health_status": health.get("status"),
                    "validate_is_valid": validate_result.get("is_valid"),
                    "match_score": match_result.get("composite_score"),
                },
            )
        except Exception as exc:
            return HarnessRunReport(
                harness="edge_api",
                mode="edge",
                profile=self.profile.name,
                ok=False,
                category=_failure_category(exc),
                summary="Edge harness startup validation failed.",
                details={"error": str(exc)},
            )


def run_control_plane(
    *,
    mode: str,
    profile: str = "local",
    operation: str = "startup",
    edge_url: str = "http://127.0.0.1:8787",
    edge_api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Run local, edge, or hybrid harness operations from one entrypoint."""
    if operation not in {"startup", "health"}:
        raise ValueError("operation must be one of: startup, health")
    if mode not in {"local", "edge", "hybrid"}:
        raise ValueError("mode must be one of: local, edge, hybrid")

    reports: Dict[str, Dict[str, Any]] = {}

    if mode in {"local", "hybrid"}:
        local = PythonCoreHarness(profile=profile)
        report = local.startup_validation() if operation == "startup" else local.health_check()
        reports["local"] = report.to_dict()

    if mode in {"edge", "hybrid"}:
        edge = EdgeAPIHarness(base_url=edge_url, profile=profile, api_key=edge_api_key)
        report = edge.startup_validation() if operation == "startup" else edge.health_check()
        reports["edge"] = report.to_dict()

    ok = all(rep.get("ok", False) for rep in reports.values())
    return {
        "mode": mode,
        "operation": operation,
        "profile": profile,
        "ok": ok,
        "reports": reports,
    }
