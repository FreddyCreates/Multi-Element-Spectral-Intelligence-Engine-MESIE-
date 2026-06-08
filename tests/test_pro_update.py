"""Pro update — field I/O, domain corpus, fast cycle, hive mind."""

from __future__ import annotations

import base64
from pathlib import Path

import pytest

from mesie.enterprise import EnterpriseAICopilot, build_enterprise_tool_schemas
from mesie.enterprise.fast_cycle import FastEnterpriseCycle
from mesie.field_io import CSVSpectralIngest, UDPSpectralFrameParser
from mesie.library.domain_corpus import domain_catalog, load_domain_corpus
from mesie.sovereign.anchor_calibration import calibrate_field_anchors


ROOT = Path(__file__).resolve().parents[1]


def test_domain_corpus_expanded():
    cat = domain_catalog()
    assert len(cat["domains"]) >= 8
    corpus = load_domain_corpus()
    assert len(corpus) >= 12


def test_copilot_tools_expanded():
    schemas = build_enterprise_tool_schemas()
    names = {s["function"]["name"] for s in schemas}
    assert len(schemas) >= 20
    assert "mesie_field_ingest_csv" in names
    assert "mesie_fast_enterprise_cycle" in names


def test_csv_udp_ingest(tmp_path):
    sample = ROOT / "data" / "samples" / "spectral_ingest_sample.csv"
    if not sample.exists():
        from data import load_reference_record
        ref = load_reference_record("earthquake_psd_reference")
        c = ref.components[0]
        sample.parent.mkdir(parents=True, exist_ok=True)
        lines = ["frequency,amplitude"] + [f"{f},{a}" for f, a in zip(c.frequency[:32], c.amplitude[:32])]
        sample.write_text("\n".join(lines))
    rec, rep = CSVSpectralIngest().ingest(sample)
    assert rep.ok and rep.points >= 32
    payload = UDPSpectralFrameParser().encode_json(rec)
    rec2, fr = UDPSpectralFrameParser().parse(payload)
    assert fr.ok


def test_anchor_calibration():
    cal = calibrate_field_anchors()
    assert cal.ok
    assert cal.calibrated >= 1


def test_fast_enterprise_cycle():
    corpus = load_domain_corpus()
    fc = FastEnterpriseCycle(sla_fast_ms=10.0)
    fc.index_corpus(corpus)
    rep = fc.run(corpus[0], candidate=corpus[1])
    assert rep.latency_ms < 50.0
    assert rep.match_score > 0


def test_copilot_invoke_new_tools():
    copilot = EnterpriseAICopilot()
    cat = copilot.invoke_tool("mesie_domain_catalog", {})
    assert cat["total_indexable"] >= 12
    fast = copilot.invoke_tool(
        "mesie_fast_enterprise_cycle",
        {"record": load_domain_corpus()[0]},
    )
    assert "latency_ms" in fast