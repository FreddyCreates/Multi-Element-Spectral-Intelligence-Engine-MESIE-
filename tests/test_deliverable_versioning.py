"""Tests for deliverable versioning."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mesie.release.deliverable_versioning import (
    DeliverableVersioning,
    synthesize_theater_state,
)


def test_versioned_write_archives_prior(tmp_path: Path):
    base = tmp_path / "suite"
    base.mkdir()
    canon = base / "NativeAI_test.json"
    canon.write_text('{"v": 1}\n', encoding="utf-8")

    ver = DeliverableVersioning(base)
    snap = ver.write_versioned(
        {"json": {"v": 2}},
        run_key="test",
        suite="sovereign_local",
        canonical_names={"json": canon},
        note="unit test",
    )
    assert json.loads(canon.read_text(encoding="utf-8")) == {"v": 2}
    assert (base / "runs").is_dir()
    ledger = json.loads((base / "lineage" / "LINEAGE_test.json").read_text(encoding="utf-8"))
    assert len(ledger["history"]) >= 2  # archive + new write
    assert ledger["latest_stamp"] == snap.stamp


def test_synthesize_theater_partial_vs_full():
    full = {
        "ticks": [{"operation_id": f"op_day{d}_x"} for d in range(1, 8) for _ in range(8)],
        "agents_deployed_peak": 10000,
        "attrition_cumulative": 0.56,
        "sim_day": 7,
        "sim_hour": 12,
        "jam_level": 0.8,
    }
    partial = {
        "ticks": [{"operation_id": "op_day1_isr_baseline"}] * 8,
        "agents_deployed_peak": 500,
        "attrition_cumulative": 0.024,
        "sim_day": 1,
        "sim_hour": 21,
        "jam_level": 0.0,
    }
    syn = synthesize_theater_state(full, partial)
    assert syn["theater_detail"]["ticks_lost"] == 48
    assert any("op_day2" in op for op in syn["theater_detail"]["operations_in_old_only"])
