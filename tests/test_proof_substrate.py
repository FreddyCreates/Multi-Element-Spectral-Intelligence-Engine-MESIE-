"""Proof substrate — sealed evidence graph."""

from __future__ import annotations

import json

from mesie.verification.proof_substrate import ProofSubstrateEngine


def test_build_has_seal_and_verdict():
    engine = ProofSubstrateEngine()
    report = engine.build()
    assert report.verdict == "partially_true_software_substrate"
    assert len(report.seal_digest) == 64
    assert len(report.claims) >= 8
    assert report.gaps_open >= 2


def test_export_and_verify_seal(tmp_path):
    engine = ProofSubstrateEngine()
    out = engine.export(tmp_path / "Proof_Substrate.json")
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert engine.verify_seal(payload)
    assert payload["substrate_version"] == "1.0.0"
    assert "artifact_index" in payload