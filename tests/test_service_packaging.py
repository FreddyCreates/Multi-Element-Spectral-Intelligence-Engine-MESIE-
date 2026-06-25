"""Tests for MESIE service packaging."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def sandbox_tmp(tmp_path: Path):
    return tmp_path / "sandbox"


def test_package_service_writes_bundle(sandbox_tmp: Path):
    from mesie.deploy.packager import package_service

    bundle_path = package_service("virtual-processor", sandbox_root=sandbox_tmp)
    assert bundle_path.is_file()
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    assert bundle["ready"] is True
    assert bundle["service_id"] == "virtual-processor"
    assert (sandbox_tmp / "virtual-processor" / "manifest.json").is_file()
    assert (sandbox_tmp / "virtual-processor" / "launcher.ps1").is_file()
    assert (sandbox_tmp / "virtual-processor" / "mcp-snippet.json").is_file()


def test_package_all_services(sandbox_tmp: Path):
    from mesie.deploy.packager import package_all
    from mesie.deploy.registry import SERVICE_REGISTRY

    bundles = package_all(sandbox_root=sandbox_tmp)
    assert len(bundles) == len(SERVICE_REGISTRY)
    for sid in SERVICE_REGISTRY:
        assert (sandbox_tmp / sid / "bundle.json").is_file()


def test_deploy_dry_run_no_side_effects():
    from mesie.deploy.router import deploy_service

    result = deploy_service("virtual-processor", "local-http", dry_run=True)
    assert result.dry_run is True
    assert result.applied is False
    assert result.plan["action"] == "start_subprocess"
    assert "8750" in (result.plan.get("health_url") or "")


def test_deploy_powershell_dry_run():
    from mesie.deploy.router import deploy_service

    result = deploy_service("virtual-processor", "powershell", dry_run=True)
    assert result.plan["action"] == "copy_launcher"
    assert "Start-VirtualProcessor.ps1" in result.plan["destination"]


def test_mcp_snippet_has_processor_key(sandbox_tmp: Path):
    from mesie.deploy.packager import package_service

    package_service("virtual-processor", sandbox_root=sandbox_tmp)
    snippet = json.loads(
        (sandbox_tmp / "virtual-processor" / "mcp-snippet.json").read_text(encoding="utf-8")
    )
    assert "mesie-processor" in snippet["mcpServers"]


def test_surface_catalog_lists_processor():
    from mesie.surface.catalog import build_catalog

    cat = build_catalog(export=False)
    ids = [s.id for s in cat.services]
    assert "virtual-processor" in ids


def test_dispatcher_processor_shortcuts():
    from mesie.surface.dispatcher import SurfaceDispatcher

    disp = SurfaceDispatcher()
    r = disp.invoke("processor", "virtual-processor")
    assert r.system == "processor"
    assert "serve" in r.detail.lower() or "Start-VirtualProcessor" in r.detail
