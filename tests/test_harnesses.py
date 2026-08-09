"""Tests for shippable agent harnesses and control-plane CLI orchestration."""

from __future__ import annotations

import json

from mesie.cli import main as cli_main
from mesie.harnesses import EdgeAPIHarness, PythonCoreHarness, run_control_plane


def test_python_core_harness_health():
    harness = PythonCoreHarness(profile="local")
    report = harness.health_check()
    assert report.ok is True
    assert report.harness == "python_core"
    assert report.category == "ok"


def test_python_core_harness_startup():
    harness = PythonCoreHarness(profile="local")
    report = harness.startup_validation()
    assert report.harness == "python_core"
    assert "workflow_completed" in report.details


def test_edge_harness_startup_validation_mock(monkeypatch):
    harness = EdgeAPIHarness(base_url="http://localhost:8787", profile="local", api_key="abc")

    def fake_request(method: str, path: str, payload=None):
        if method == "GET" and path == "/health":
            return {"status": "ok"}
        if method == "POST" and path == "/v1/validate":
            return {"is_valid": True, "level": 3, "errors": [], "warnings": []}
        if method == "POST" and path == "/v1/match":
            return {"composite_score": 0.95, "metrics": {"cosine": 1.0, "rmse": 0.1}}
        raise AssertionError(f"Unexpected request: {method} {path}")

    monkeypatch.setattr(harness, "_request", fake_request)
    report = harness.startup_validation()
    assert report.ok is True
    assert report.category == "ok"
    assert report.details["health_status"] == "ok"


def test_control_plane_hybrid(monkeypatch):
    calls = []

    def fake_request(method: str, path: str, payload=None):
        calls.append((method, path))
        if path == "/health":
            return {"status": "ok"}
        if path == "/v1/validate":
            return {"is_valid": True}
        if path == "/v1/match":
            return {"composite_score": 0.9}
        raise AssertionError(path)

    monkeypatch.setattr(EdgeAPIHarness, "_request", lambda self, method, path, payload=None: fake_request(method, path, payload))
    report = run_control_plane(mode="hybrid", profile="local", operation="startup")
    assert report["ok"] is True
    assert "local" in report["reports"]
    assert "edge" in report["reports"]
    assert ("GET", "/health") in calls


def test_cli_harness_command(monkeypatch, capsys):
    monkeypatch.setattr(
        "mesie.harnesses.run_control_plane",
        lambda **kwargs: {"mode": kwargs["mode"], "operation": kwargs["operation"], "ok": True, "reports": {}},
    )
    cli_main(["harness", "--mode", "local", "--operation", "health"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["mode"] == "local"
    assert payload["operation"] == "health"
