"""4-tier market ready loop — tiers, manifest, cycle."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_four_tiers_defined():
    from mesie.market.four_tier_loop import FOUR_TIERS

    assert len(FOUR_TIERS) == 4
    ids = {t.tier_id for t in FOUR_TIERS}
    assert ids == {"prove", "package", "platform", "ship"}
    squads = {t.squad_id for t in FOUR_TIERS}
    assert "ops-triad" in squads
    assert "quality-triad" in squads


def test_market_manifest():
    from mesie.market.four_tier_loop import market_ready_manifest

    m = market_ready_manifest(write=True)
    assert m["protocol"] == "MESIE-FOUR-TIER-MARKET-READY/1.0"
    assert m["tier_count"] == 4
    assert (ROOT / "deliverables" / "market" / "FOUR_TIER_MARKET_READY.json").is_file()


def test_single_tier_prove_light():
    from mesie.market.four_tier_loop import run_tier

    r = run_tier("prove", cycle_num=2, light=True)
    assert r["tier_id"] == "prove"
    assert "tasks" in r
    assert any(t.get("skipped") for t in r["tasks"])


def test_market_cycle_once():
    from mesie.market.four_tier_loop import run_market_cycle

    snap = run_market_cycle(light=True)
    assert snap["protocol"] == "MESIE-FOUR-TIER-MARKET-READY/1.0"
    assert snap["tier_count"] == 4
    assert len(snap["results"]) == 4
    assert (ROOT / "deliverables" / "market" / "FOUR_TIER_MARKET_READY_STATE.json").is_file()
    state = json.loads((ROOT / "deliverables" / "market" / "FOUR_TIER_MARKET_READY_STATE.json").read_text(encoding="utf-8"))
    assert state["cycles"] >= 1