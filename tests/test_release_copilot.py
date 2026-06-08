"""Release bootstrap + terminal copilot tiers."""

from __future__ import annotations

from mesie.enterprise.samgov_suite import SamGovSuite
from mesie.release.bootstrap import bootstrap, user_config_dir
from mesie.sdk.terminal_copilot import CopilotTier, TerminalCopilot


def test_bootstrap_writes_config(tmp_path, monkeypatch):
    monkeypatch.setenv("MESIE_HOME", str(tmp_path))
    result = bootstrap(quiet=True)
    assert result["bootstrapped"]
    assert (tmp_path / "config.json").is_file()
    assert (tmp_path / "MESIE.ps1").is_file()


def test_copilot_tiers():
    for tier in CopilotTier:
        c = TerminalCopilot(tier=tier)
        assert c.handle("help")
        assert c.handle("status")


def test_samgov_workflows():
    rep = SamGovSuite().build_report()
    assert len(rep.workflows) >= 5
    assert len(rep.opportunity_refs) >= 3
    assert "SAM_API_KEY" in rep.honest_limits[0]


def test_copilot_sovereign_spectral():
    c = TerminalCopilot(tier=CopilotTier.SOVEREIGN)
    out = c.handle("run a spectral match")
    assert "run" in out.lower() or "tool" in out.lower()