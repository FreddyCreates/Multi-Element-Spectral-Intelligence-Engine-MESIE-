"""Is This True verification engine."""

from __future__ import annotations

from mesie.verification.is_this_true import IsThisTrueEngine


def test_not_marketing_yes():
    resp = IsThisTrueEngine().answer()
    assert resp.verdict == "partially_true_software_substrate"
    assert "Not fully true" in resp.short_answer or "not" in resp.short_answer.lower()
    assert len(resp.what_is_not_proven) >= 3


def test_grok_critique_mapped():
    resp = IsThisTrueEngine().answer()
    assert len(resp.grok_critique_mapping) >= 4