"""Smoke tests for sovereign local mode and 120-test suite wiring."""

from mesie.sovereign import SovereignLocalMode, sovereign_active


def test_sovereign_local_mode_defaults():
    mode = SovereignLocalMode.active()
    assert mode.sovereign is True
    assert mode.third_party is False
    assert mode.own_models_only is True
    manifest = mode.manifest()
    assert manifest["sovereign"] is True
    assert manifest["third_party"] is False
    assert manifest["mode"] == "sovereign-local"


def test_sovereign_active_singleton_shape():
    assert sovereign_active().brand == "SOLUS"


def test_sovereign_local_suite_count():
    from scripts.run_sovereign_local_suite import run_suite

    report = run_suite()
    assert report.n_tests == 120
    assert report.passed >= 108