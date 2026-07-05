"""Tri-Agent Squads — groups of 3 AI auto-agents for system workflow and maintenance."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List

ROOT = Path(__file__).resolve().parents[2]
SQUAD_STATE = ROOT / "deliverables" / "compute" / "TRI_AGENT_SQUAD_STATE.json"
PYTHON = sys.executable

AgentFn = Callable[[], Dict[str, Any]]


@dataclass
class TriAgent:
    agent_id: str
    role: str
    script: str

    def to_dict(self) -> Dict[str, Any]:
        return {"agent_id": self.agent_id, "role": self.role, "script": self.script}


@dataclass
class TriSquad:
    squad_id: str
    name: str
    mission: str
    agents: List[TriAgent] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "squad_id": self.squad_id,
            "name": self.name,
            "mission": self.mission,
            "agents": [a.to_dict() for a in self.agents],
        }


def _run_script(args: List[str], timeout: int = 120) -> Dict[str, Any]:
    try:
        r = subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout, check=False)
        return {"ok": r.returncode == 0, "exit_code": r.returncode, "tail": (r.stdout or r.stderr)[-500:]}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


SQUADS = [
    TriSquad(
        squad_id="ops-triad",
        name="Ops Triad",
        mission="Health, benchmarks, colony bridge sync",
        agents=[
            TriAgent("ops-α", "Health Monitor", "processor_status"),
            TriAgent("ops-β", "Benchmark Runner", "compute_benchmark"),
            TriAgent("ops-γ", "Bridge Sync", "colony_sync"),
        ],
    ),
    TriSquad(
        squad_id="quality-triad",
        name="Quality Triad",
        mission="Tests, commercial pack, metrics export",
        agents=[
            TriAgent("qual-α", "Pytest Gate", "pytest_smoke"),
            TriAgent("qual-β", "Commercial Pack", "official_pack"),
            TriAgent("qual-γ", "Metrics Export", "live_metrics"),
        ],
    ),
    TriSquad(
        squad_id="intel-triad",
        name="Intel Triad",
        mission="Embed, match, scientific text generation",
        agents=[
            TriAgent("intel-α", "Embed Pulse", "embed_pulse"),
            TriAgent("intel-β", "Match Pulse", "match_pulse"),
            TriAgent("intel-γ", "Signal Generate", "signal_generate"),
        ],
    ),
    TriSquad(
        squad_id="research-triad",
        name="Research Triad",
        mission="Acoustic metamaterial, domain suites, release package",
        agents=[
            TriAgent("res-α", "Metamaterial Agent", "metamaterial_research"),
            TriAgent("res-β", "Domain Suite", "metamaterial_domain"),
            TriAgent("res-γ", "Release Pack", "full_release_pack"),
        ],
    ),
]

AGENT_TASKS: Dict[str, AgentFn] = {
    "processor_status": lambda: _run_script([PYTHON, "-c", "import urllib.request,json; print(json.dumps(json.loads(urllib.request.urlopen('http://127.0.0.1:8750/processor/status',timeout=5).read().decode())))"]),
    "compute_benchmark": lambda: _run_script([PYTHON, "-m", "mesie.compute.hub", "--benchmark"]),
    "colony_sync": lambda: _run_script([PYTHON, "-m", "mesie.cloud.colony_bridge", "--action", "status"]),
    "pytest_smoke": lambda: _run_script([PYTHON, "-m", "pytest", "tests/test_triple_protocol.py", "tests/test_sovereign_os.py", "-q"], timeout=180),
    "official_pack": lambda: _run_script([PYTHON, "scripts/run_official_commercial_pack.py", "--quick"]),
    "live_metrics": lambda: _run_script([PYTHON, "-m", "mesie.compute.live_metrics"]),
    "embed_pulse": lambda: _run_script([PYTHON, "-c", "from mesie.processor.virtual_processor import VirtualProcessor; import json; print(json.dumps(VirtualProcessor().embed('ref-earthquake-psd-001').to_dict()))"]),
    "match_pulse": lambda: _run_script([PYTHON, "-c", "from mesie.sdk.fast_compute import FastSpectralCompute; from data import list_references, load_reference_record; import json; refs=list_references()[:2] or ['earthquake_psd_reference']; recs=[load_reference_record(r) for r in refs]; fc=FastSpectralCompute(); fc.build_index(recs); print(json.dumps({'hits':fc.cosine_search(recs[0],3)}))"]),
    "signal_generate": lambda: _run_script([PYTHON, "-c", "from mesie.processor.virtual_processor import VirtualProcessor; import json; print(json.dumps(VirtualProcessor().generate_text({'metric':'latency','value':0.68},style='research_brief').to_dict()))"]),
    "metamaterial_research": lambda: _run_script([PYTHON, "-m", "mesie.research.acoustic_metamaterial_agent", "--run"]),
    "metamaterial_domain": lambda: _run_script([PYTHON, "-c", "from mesie.domains.acoustic_metamaterial import run_metamaterial_suite; import json; print(json.dumps(run_metamaterial_suite()))"]),
    "full_release_pack": lambda: _run_script([PYTHON, "scripts/package_full_release.py"], timeout=300),
}


def execute_squad(squad_id: str) -> Dict[str, Any]:
    squad = next((s for s in SQUADS if s.squad_id == squad_id), None)
    if not squad:
        return {"ok": False, "error": f"unknown squad: {squad_id}"}

    results: Dict[str, Any] = {"squad_id": squad_id, "name": squad.name, "agents": [], "ok": True}
    for agent in squad.agents:
        task_key = agent.script
        fn = AGENT_TASKS.get(task_key)
        if not fn:
            r = {"ok": False, "error": f"no task: {task_key}"}
        else:
            r = fn()
        results["agents"].append({"agent": agent.to_dict(), "result": r})
        if not r.get("ok"):
            results["ok"] = False

    results["executed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    SQUAD_STATE.parent.mkdir(parents=True, exist_ok=True)
    SQUAD_STATE.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return results


def execute_all_squads() -> Dict[str, Any]:
    reports = [execute_squad(s.squad_id) for s in SQUADS]
    return {
        "ok": all(r["ok"] for r in reports),
        "squads": len(reports),
        "reports": reports,
        "executed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def list_squads() -> List[Dict[str, Any]]:
    return [s.to_dict() for s in SQUADS]


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Tri-Agent Maintenance Squads")
    parser.add_argument("--squad", default="")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    if args.list:
        print(json.dumps(list_squads(), indent=2))
        return 0
    if args.all:
        print(json.dumps(execute_all_squads(), indent=2))
        return 0
    if args.squad:
        print(json.dumps(execute_squad(args.squad), indent=2))
        return 0
    print(json.dumps(execute_all_squads(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())