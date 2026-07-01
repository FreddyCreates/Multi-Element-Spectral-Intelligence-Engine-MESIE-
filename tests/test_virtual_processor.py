"""Tests for MESIE Virtual Processor."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_processor_status():
    from mesie.processor.virtual_processor import VirtualProcessor

    proc = VirtualProcessor()
    st = proc.status()
    assert st["product"] == "MESIE Virtual Processor"
    assert "embed" in st["operations"]
    assert st["processor_version"] == "1.2.0"


def test_processor_export_manifest(tmp_path: Path):
    from mesie.processor.virtual_processor import VirtualProcessor

    proc = VirtualProcessor()
    out = tmp_path / "manifest.json"
    path = proc.export_manifest(out)
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["product"] == "MESIE Virtual Processor"
    assert "status" in data
    assert data["deploy_artifacts"]["port"] == 8750


def test_processor_main_status(capsys):
    from mesie.processor.__main__ import main

    code = main(["--status"])
    assert code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["product"] == "MESIE Virtual Processor"


def test_processor_main_export_manifest(tmp_path: Path, monkeypatch):
    from mesie.processor import __main__ as proc_main
    from mesie.processor.virtual_processor import DEFAULT_MANIFEST_PATH

    target = tmp_path / "proc_manifest.json"
    monkeypatch.setattr(
        "mesie.processor.virtual_processor.DEFAULT_MANIFEST_PATH",
        target,
    )
    code = proc_main.main(["--export-manifest", str(target)])
    assert code == 0
    assert target.is_file()
