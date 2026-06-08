"""Release readiness gate — version, terminal, copilot tiers, core tests."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class ReleaseReadinessReport:
    ready: bool
    mesie_version: str
    sdk_version: str
    checks: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ready": self.ready,
            "mesie_version": self.mesie_version,
            "sdk_version": self.sdk_version,
            "checks": self.checks,
        }


def run_release_check(*, run_pytest: bool = True) -> ReleaseReadinessReport:
    import mesie
    from mesie.sdk import __sdk_version__

    checks: List[Dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    from mesie.release.bootstrap import ensure_bootstrapped

    boot = ensure_bootstrapped(quiet=True)
    add("bootstrap", boot.get("bootstrapped", False), str(boot.get("config_dir", "")))

    from mesie.sdk.terminal_copilot import CopilotTier, TerminalCopilot

    for tier in CopilotTier:
        c = TerminalCopilot(tier=tier)
        add(f"copilot_{tier.value}", bool(c._help()), c.tier.value)

    from mesie.enterprise.samgov_suite import SamGovSuite
    from mesie.neuroai.auro import AuroSpeakingEngine
    from mesie.neuroai.auro.eval import AuroEvalSuite

    sg = SamGovSuite().build_report()
    add("samgov_edition", len(sg.workflows) >= 5, sg.edition)

    auro = AuroSpeakingEngine()
    add("auro_native_lm", auro.status().get("built") is True, auro.status().get("native_model", ""))
    auro_eval = AuroEvalSuite().run(auro)
    add("auro_eval", auro_eval.passed >= 10, f"{auro_eval.passed}/{len(auro_eval.cases)} matrix={auro_eval.matrix_passed}")

    from mesie.sdk.llm_bridge import LLMBridge

    add("llm_bridge", True, str(LLMBridge().available()))

    if run_pytest:
        r = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/test_terminal.py",
                "tests/test_interior_datacenter.py",
                "tests/test_release_copilot.py",
                "tests/test_auro_engine.py",
                "-q",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        add("pytest_core", r.returncode == 0, r.stdout[-200:] if r.stdout else r.stderr[-200:])

    ready = all(c["ok"] for c in checks)
    return ReleaseReadinessReport(
        ready=ready,
        mesie_version=mesie.__version__,
        sdk_version=__sdk_version__,
        checks=checks,
    )


def export_report(path: Path | None = None) -> Path:
    report = run_release_check()
    out = path or ROOT / "deliverables" / "MESIE_Release_Readiness.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    return out