"""NOVA Runtime Supervisor — never stop. Enterprise always-on.

Mirrors SovereignForge agentHeartbeat pattern:
  - 55 micro careers on SatelliteAgent timers (real tasks)
  - robotics_satellite subprocess (fusion + LRC + threat_p50)
  - watchdog restarts dead workers
  - feed written to deliverables/nova/NOVA_RUNTIME_FEED.jsonl
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[3]
FEED = ROOT / "deliverables" / "nova" / "NOVA_RUNTIME_FEED.jsonl"
ROBOTICS_LOG = ROOT / "deliverables" / "processor" / "robotics_satellite.jsonl"
STATE = ROOT / "deliverables" / "nova" / "NOVA_RUNTIME_STATE.json"


@dataclass
class NovaRuntimeSupervisor:
    """Always-on production runtime — do not let the swarm stop."""

    session_id: str = "nova-runtime-production"
    watchdog_interval_s: float = 30.0
    robotics_interval_s: float = 300.0
    _sphere: Any = field(default=None, init=False, repr=False)
    _robotics_proc: Optional[subprocess.Popen] = field(default=None, init=False, repr=False)
    _started_at: float = field(default_factory=time.time, init=False)
    _restarts: int = field(default=0, init=False)

    def start(self) -> Dict[str, Any]:
        from mesie.agentic.micro import NOVA_ORG_SIZE, organization_status
        from mesie.agentic.micro.organization import activate_nova_organization, boot_nova_organization
        from mesie.nova.sphere import NovaSphere

        FEED.parent.mkdir(parents=True, exist_ok=True)
        self._sphere = NovaSphere(session_id=self.session_id)
        boot_nova_organization(self._sphere.micro, satellite=False)
        activate_nova_organization(self._sphere.micro)
        self._ensure_robotics()
        snap = self._snapshot()
        self._write_feed(snap)
        self._write_state(snap)
        print(
            f"[nova-runtime] STARTED careers={snap['micro_org']['size']}/{NOVA_ORG_SIZE} "
            f"robotics={'up' if snap['robotics']['process_alive'] else 'down'}",
            flush=True,
        )
        return snap

    def _ensure_robotics(self) -> None:
        if self._robotics_proc and self._robotics_proc.poll() is None:
            return
        self._robotics_proc = subprocess.Popen(
            [sys.executable, "-m", "mesie.processor.satellite_robotics"],
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        self._restarts += 1
        print(f"[nova-runtime] robotics_satellite (re)started pid={self._robotics_proc.pid}", flush=True)

    def _tail_robotics(self, n: int = 3) -> List[Dict[str, Any]]:
        if not ROBOTICS_LOG.is_file():
            return []
        lines = ROBOTICS_LOG.read_text(encoding="utf-8").strip().splitlines()
        out = []
        for line in lines[-n:]:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        return out

    def _snapshot(self) -> Dict[str, Any]:
        from mesie.agentic.micro import NOVA_ORG_SIZE, organization_status

        org = organization_status(self._sphere.micro) if self._sphere else {}
        recent = self._tail_robotics(5)
        last = recent[-1] if recent else {}
        last_out = (last.get("result") or {}).get("output") or {}
        proc_alive = self._robotics_proc is not None and self._robotics_proc.poll() is None
        return {
            "ts": time.time(),
            "uptime_s": round(time.time() - self._started_at, 1),
            "session_id": self.session_id,
            "never_stop": True,
            "micro_org": {
                "size": org.get("size", 0),
                "expected": NOVA_ORG_SIZE,
                "pulsing": org.get("pulsing", 0),
                "satellites_active": org.get("satellites_active", 0),
                "teams": org.get("teams", {}),
            },
            "robotics": {
                "process_alive": proc_alive,
                "pid": self._robotics_proc.pid if self._robotics_proc else None,
                "log": str(ROBOTICS_LOG),
                "total_cycles": sum(1 for _ in ROBOTICS_LOG.open(encoding="utf-8")) if ROBOTICS_LOG.is_file() else 0,
                "last_cycle": last.get("cycle"),
                "last_threat_p50_ms": last_out.get("threat_p50_ms"),
                "last_lrc": (last.get("result") or {}).get("lrc", {}).get("lrc_id"),
                "fusion_dims": last_out.get("fusion_dims"),
            },
            "restarts": self._restarts,
        }

    def _write_feed(self, snap: Dict[str, Any]) -> None:
        with FEED.open("a", encoding="utf-8") as f:
            f.write(json.dumps(snap) + "\n")

    def _write_state(self, snap: Dict[str, Any]) -> None:
        STATE.write_text(json.dumps(snap, indent=2), encoding="utf-8")

    def watchdog_once(self) -> Dict[str, Any]:
        self._ensure_robotics()
        snap = self._snapshot()
        self._write_feed(snap)
        self._write_state(snap)
        return snap

    def run_forever(self) -> None:
        self.start()
        print(f"[nova-runtime] watchdog every {self.watchdog_interval_s}s — Ctrl+C to stop", flush=True)
        try:
            while True:
                time.sleep(self.watchdog_interval_s)
                snap = self.watchdog_once()
                r = snap["robotics"]
                m = snap["micro_org"]
                print(
                    f"[nova-runtime] micro {m['pulsing']}/{m['size']} pulsing · "
                    f"robotics cycle={r['last_cycle']} threat_p50={r['last_threat_p50_ms']}ms "
                    f"LRC={r['last_lrc']} proc={'alive' if r['process_alive'] else 'DEAD'}",
                    flush=True,
                )
        except KeyboardInterrupt:
            if self._robotics_proc and self._robotics_proc.poll() is None:
                self._robotics_proc.terminate()
            if self._sphere:
                self._sphere.stop_satellites()
            print("[nova-runtime] stopped by operator", flush=True)


def load_runtime_state() -> Dict[str, Any]:
    if STATE.is_file():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"ok": False, "note": "NOVA runtime not started — run: python scripts/run_nova_runtime.py"}