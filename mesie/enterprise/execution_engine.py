"""Enterprise Execution Engine — unified workflow across 3 repos + all products."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable
STATE = ROOT / "deliverables" / "enterprise" / "EXECUTION_ENGINE_STATE.json"
DAG_PATH = ROOT / "deliverables" / "enterprise" / "ENTERPRISE_WORKFLOW_DAG.json"
RECEIPTS = ROOT / "deliverables" / "enterprise" / "EXECUTION_RECEIPTS.jsonl"

StepFn = Callable[[], Dict[str, Any]]


@dataclass
class WorkflowNode:
    node_id: str
    name: str
    phase: str
    deps: List[str] = field(default_factory=list)
    critical: bool = True


ENTERPRISE_DAG: List[WorkflowNode] = [
    WorkflowNode("n01", "unify_repos", "UNIFY", []),
    WorkflowNode("n02", "grok_protocol", "CONNECT", ["n01"]),
    WorkflowNode("n03", "triple_protocol", "CONNECT", ["n01"]),
    WorkflowNode("n04", "multimodal_protocol", "CONNECT", ["n03"]),
    WorkflowNode("n05", "token_budget", "EFFICIENCY", ["n01"]),
    WorkflowNode("n06", "nova_snapshot", "RUNTIME", ["n01"]),
    WorkflowNode("n07", "compute_benchmark", "MESIE", ["n01"]),
    WorkflowNode("n08", "colony_bridge", "SOVEREIGN", ["n01"]),
    WorkflowNode("n09", "research_metamaterial", "RESEARCH", ["n07"], critical=False),
    WorkflowNode("n10", "sandbox_loop", "SANDBOX", ["n02"]),
    WorkflowNode("n11", "tri_agent_quality", "VERIFY", ["n07", "n10"]),
    WorkflowNode("n12", "package_release", "SHIP", ["n11"]),
    WorkflowNode("n13", "receipt_chain", "PERSIST", ["n12"]),
]


def _topo_sort(nodes: List[WorkflowNode]) -> List[WorkflowNode]:
    by_id = {n.node_id: n for n in nodes}
    done: set[str] = set()
    out: List[WorkflowNode] = []
    while len(out) < len(nodes):
        progressed = False
        for n in nodes:
            if n.node_id in done:
                continue
            if all(d in done for d in n.deps):
                out.append(n)
                done.add(n.node_id)
                progressed = True
        if not progressed:
            break
    return out


def _run(cmd: List[str], *, timeout: int = 300) -> Dict[str, Any]:
    try:
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout, check=False)
        return {"ok": r.returncode == 0, "exit_code": r.returncode, "tail": (r.stdout or r.stderr)[-400:]}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _write_dag() -> None:
    DAG_PATH.parent.mkdir(parents=True, exist_ok=True)
    DAG_PATH.write_text(
        json.dumps(
            {
                "protocol": "MESIE-ENTERPRISE-WORKFLOW/1.0",
                "nodes": [
                    {"id": n.node_id, "name": n.name, "phase": n.phase, "deps": n.deps, "critical": n.critical}
                    for n in ENTERPRISE_DAG
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


class EnterpriseExecutionEngine:
    """Run full enterprise workflow with receipt chain persistence."""

    def __init__(self, *, mission_id: str = "enterprise-default") -> None:
        self.mission_id = mission_id
        self._handlers: Dict[str, StepFn] = {
            "unify_repos": self._step_unify,
            "grok_protocol": self._step_grok,
            "triple_protocol": self._step_triple,
            "multimodal_protocol": self._step_multimodal,
            "token_budget": self._step_token,
            "nova_snapshot": self._step_nova,
            "compute_benchmark": self._step_compute,
            "colony_bridge": self._step_colony,
            "research_metamaterial": self._step_research,
            "sandbox_loop": self._step_sandbox,
            "tri_agent_quality": self._step_tri_agent,
            "package_release": self._step_package,
            "receipt_chain": self._step_receipt,
        }

    def run(self, *, stop_on_fail: bool = True, skip: Optional[List[str]] = None) -> Dict[str, Any]:
        skip = set(skip or [])
        _write_dag()
        order = _topo_sort(ENTERPRISE_DAG)
        results: List[Dict[str, Any]] = []
        chain = None

        for node in order:
            if node.name in skip:
                results.append({"node": node.node_id, "name": node.name, "skipped": True})
                continue
            fn = self._handlers.get(node.name)
            if not fn:
                results.append({"node": node.node_id, "name": node.name, "ok": False, "error": "no_handler"})
                continue
            t0 = time.time()
            res = fn()
            res.update({"node": node.node_id, "name": node.name, "phase": node.phase, "elapsed_s": round(time.time() - t0, 2)})
            results.append(res)
            self._log_receipt(node.name, res)
            if not res.get("ok") and node.critical and stop_on_fail:
                break

        critical_names = {n.name for n in ENTERPRISE_DAG if n.critical}
        ok = all(
            r.get("ok") or r.get("skipped")
            for r in results
            if r.get("name") in critical_names
        )

        out = {
            "protocol": "MESIE-ENTERPRISE-EXECUTION-ENGINE/1.0",
            "mission_id": self.mission_id,
            "ok": ok,
            "nodes_run": len(results),
            "results": results,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        STATE.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        return out

    def _log_receipt(self, name: str, res: Dict[str, Any]) -> None:
        from mesie.compute.token_budget import append_receipt

        append_receipt(f"ENT:{name}", json.dumps({"ok": res.get("ok")}, separators=(",", ":")), production=True)
        RECEIPTS.parent.mkdir(parents=True, exist_ok=True)
        with RECEIPTS.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"name": name, **res}, separators=(",", ":")) + "\n")

    def _step_unify(self) -> Dict[str, Any]:
        from mesie.enterprise.repo_unifier import write_thread_manifest

        return write_thread_manifest()

    def _step_grok(self) -> Dict[str, Any]:
        from mesie.grok.protocol import write_protocol_manifest

        return write_protocol_manifest()

    def _step_triple(self) -> Dict[str, Any]:
        from mesie.cloud.triple_protocol import write_triple_manifest

        write_triple_manifest()
        return {"ok": True}

    def _step_multimodal(self) -> Dict[str, Any]:
        from mesie.cloud.multimodal_triple_protocol import write_manifest

        return write_manifest()

    def _step_token(self) -> Dict[str, Any]:
        from mesie.compute.token_budget import snapshot

        snap = snapshot()
        return {"ok": True, "uplift": snap.get("uplift")}

    def _step_nova(self) -> Dict[str, Any]:
        return _run([PYTHON, "scripts/run_nova_runtime.py", "--once"], timeout=180)

    def _step_compute(self) -> Dict[str, Any]:
        return _run([PYTHON, "-m", "mesie.compute.hub", "--benchmark", "--trials", "15"], timeout=120)

    def _step_colony(self) -> Dict[str, Any]:
        return _run([PYTHON, "-m", "mesie.cloud.colony_bridge", "--action", "status"], timeout=60)

    def _step_research(self) -> Dict[str, Any]:
        return _run([PYTHON, "-m", "mesie.research.acoustic_metamaterial_agent", "--run"], timeout=120)

    def _step_sandbox(self) -> Dict[str, Any]:
        return _run([PYTHON, "-m", "mesie.grok", "sandbox"], timeout=120)

    def _step_tri_agent(self) -> Dict[str, Any]:
        return _run([PYTHON, "-m", "mesie.compute.tri_agent_squads", "--squad", "quality-triad"], timeout=300)

    def _step_package(self) -> Dict[str, Any]:
        return _run([PYTHON, "scripts/package_full_release.py"], timeout=300)

    def _step_receipt(self) -> Dict[str, Any]:
        from mesie.enterprise.receipt_chain import ComputationalReceiptChain

        chain = ComputationalReceiptChain()
        rec, token = chain.append_spectral_cycle(
            cycle_id=self.mission_id,
            record_id="enterprise-execution",
            work={"engine": "MESIE-ENTERPRISE-EXECUTION-ENGINE/1.0", "state": str(STATE)},
            solus_proof={"logic_confidence": 0.9, "proof_steps": 1, "signal_ratio": 0.618},
        )
        return {"ok": True, "receipt_id": rec.receipt_id, "token_id": token.token_id, "verified": chain.verify_chain().verified}


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Enterprise Execution Engine")
    p.add_argument("--mission", default="enterprise-ship")
    p.add_argument("--skip", nargs="*", default=[])
    p.add_argument("--list", action="store_true")
    args = p.parse_args()
    if args.list:
        _write_dag()
        print(json.dumps(json.loads(DAG_PATH.read_text(encoding="utf-8")), indent=2))
        return 0
    eng = EnterpriseExecutionEngine(mission_id=args.mission)
    print(json.dumps(eng.run(skip=args.skip), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())