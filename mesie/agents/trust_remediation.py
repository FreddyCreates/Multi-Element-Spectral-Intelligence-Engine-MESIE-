"""Trust remediation agents — scan gaps, run fixes, commit on branch."""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.verification.evidence_tiers import EvidenceTier
from mesie.verification.is_this_true import IsThisTrueEngine
from mesie.verification.claim_registry import default_claim_registry

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BRANCH = "trust/production-readiness"


@dataclass
class AgentAction:
    agent: str
    action: str
    ok: bool
    detail: str
    artifact: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RemediationReport:
    branch: str
    actions: List[AgentAction]
    gaps_before: int
    gaps_after: int
    committed: bool
    commit_hash: str
    production_ready: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TrustRemediationOrchestrator:
    """Three agents: Auditor → Runner → Committer."""

    def __init__(self, *, branch: str = DEFAULT_BRANCH, dry_run: bool = False) -> None:
        self.branch = branch
        self.dry_run = dry_run

    def _run_cmd(self, cmd: List[str], cwd: Optional[Path] = None) -> tuple[bool, str]:
        try:
            r = subprocess.run(
                cmd,
                cwd=str(cwd or ROOT),
                capture_output=True,
                text=True,
                timeout=300,
            )
            out = (r.stdout or "") + (r.stderr or "")
            return r.returncode == 0, out.strip()[:2000]
        except (subprocess.TimeoutExpired, OSError) as e:
            return False, str(e)

    def agent_auditor(self) -> AgentAction:
        engine = IsThisTrueEngine()
        gaps = [c for c in engine.registry if c.tier in (EvidenceTier.GAP, EvidenceTier.ASSERTION_ONLY)]
        path = engine.export()
        return AgentAction(
            agent="auditor",
            action="export_is_this_true",
            ok=True,
            detail=f"{len(gaps)} gaps in registry; honest response exported",
            artifact=str(path),
        )

    def agent_runner(self) -> List[AgentAction]:
        scripts = [
            ("verification_harness", ["python", "scripts/run_is_this_true.py"]),
            ("mission_world_week", ["python", "scripts/run_mission_world_week.py", "--days", "7"]),
            ("scenario_sim", ["python", "scripts/run_scenario_simulation_suite.py"]),
            ("production_tiers", ["python", "scripts/run_production_tiers.py", "--tier", "both"]),
        ]
        actions = []
        for name, cmd in scripts:
            if self.dry_run:
                actions.append(AgentAction(agent="runner", action=name, ok=True, detail="dry_run skip"))
                continue
            ok, detail = self._run_cmd(cmd)
            actions.append(AgentAction(agent="runner", action=name, ok=ok, detail=detail[:500]))
        return actions

    def agent_committer(self, actions: List[AgentAction]) -> AgentAction:
        if self.dry_run:
            return AgentAction(agent="committer", action="git_commit", ok=True, detail="dry_run skip")

        ok_branch, _ = self._run_cmd(["git", "checkout", "-B", self.branch])
        if not ok_branch:
            return AgentAction(agent="committer", action="git_branch", ok=False, detail="branch failed")

        add_paths = [
            "mesie/worlds",
            "mesie/verification",
            "mesie/agents",
            "data/worlds",
            "scripts/run_mission_world_week.py",
            "scripts/run_is_this_true.py",
            "scripts/run_trust_remediation_agents.py",
            "tests/test_mission_world.py",
            "tests/test_is_this_true.py",
            "deliverables/Is_This_True_Response.json",
            "deliverables/Is_This_True_Response.md",
            "deliverables/mission_worlds",
            "deliverables/Trust_Remediation_Report.json",
        ]
        for p in add_paths:
            full = ROOT / p
            if full.exists():
                self._run_cmd(["git", "add", p])

        self._run_cmd(["git", "add", "deliverables/MESIE_Scenario_Simulation_Report.json"])
        self._run_cmd(["git", "add", "mesie/tools/registry.py"])

        msg = (
            "trust: mission world week sim + is_this_true engine + remediation agents\n\n"
            "Addresses Grok/X critique with honest evidence tiers, not marketing yes."
        )
        ok_commit, out = self._run_cmd(["git", "commit", "-m", msg])
        ok_hash, hash_out = self._run_cmd(["git", "rev-parse", "--short", "HEAD"])
        return AgentAction(
            agent="committer",
            action="git_commit",
            ok=ok_commit,
            detail=out or hash_out,
            artifact=hash_out.strip() if ok_hash else "",
        )

    def run(self) -> RemediationReport:
        gaps_before = sum(
            1 for c in default_claim_registry()
            if c.tier in (EvidenceTier.GAP, EvidenceTier.ASSERTION_ONLY)
        )
        actions: List[AgentAction] = []
        actions.append(self.agent_auditor())
        actions.extend(self.agent_runner())
        commit_act = self.agent_committer(actions)
        actions.append(commit_act)

        report = RemediationReport(
            branch=self.branch,
            actions=[a.to_dict() for a in actions],
            gaps_before=gaps_before,
            gaps_after=gaps_before,
            committed=commit_act.ok,
            commit_hash=commit_act.artifact,
            production_ready=all(a.ok for a in actions if a.agent == "runner"),
        )
        out = ROOT / "deliverables" / "Trust_Remediation_Report.json"
        out.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
        return report