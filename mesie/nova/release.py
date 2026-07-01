"""NOVA production release orchestrator — micro satellites + MESIE gate."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from mesie.agentic.micro import MicroCareer, MicroOrchestrator
from mesie.nova.sphere import NovaSphere

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class NovaReleaseReport:
    ready: bool
    nova_version: str
    mininova_version: str
    mesie_version: str
    checks: List[Dict[str, Any]] = field(default_factory=list)
    micro_pulses: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ready": self.ready,
            "nova_version": self.nova_version,
            "mininova_version": self.mininova_version,
            "mesie_version": self.mesie_version,
            "checks": self.checks,
            "micro_pulses": self.micro_pulses,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }


def _run_pytest(tests: List[str]) -> Dict[str, Any]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", *tests, "-q"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    return {"ok": r.returncode == 0, "detail": (r.stdout or r.stderr)[-400:]}


def run_nova_release(*, export: bool = True) -> NovaReleaseReport:
    from mesie.version_info import (
        MESIE_VERSION,
        MININOVA_VERSION,
        NOVA_VERSION,
    )

    checks: List[Dict[str, Any]] = []
    from mesie.agentic.micro.tasks import register_production_tasks

    micro = MicroOrchestrator()
    register_production_tasks(micro, mesie_root=ROOT)

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    for career in (
        MicroCareer.VERSION_AUDITOR,
        MicroCareer.RELEASE_SENTINEL,
        MicroCareer.MANIFEST_WRITER,
        MicroCareer.LINGUIST,
    ):
        micro.spawn(career, satellite=False)

    pulses = micro.run_all_once()
    for p in pulses:
        res = p.get("result", {})
        name = p.get("pulse", {}).get("career", "micro")
        add(f"micro_{name}", res.get("ok", False), str(res)[:200])

    # MESIE readiness gate
    try:
        from mesie.release.readiness_check import run_release_check

        mesie_rep = run_release_check()
        add("mesie_readiness", mesie_rep.ready, mesie_rep.mesie_version)
    except Exception as exc:
        add("mesie_readiness", False, str(exc))

    ready = all(c["ok"] for c in checks)
    report = NovaReleaseReport(
        ready=ready,
        nova_version=NOVA_VERSION,
        mininova_version=MININOVA_VERSION,
        mesie_version=MESIE_VERSION,
        checks=checks,
        micro_pulses=pulses,
    )

    if export:
        out_dir = ROOT / "deliverables" / "nova"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "NOVA_Production_Release.json").write_text(
            json.dumps(report.to_dict(), indent=2), encoding="utf-8"
        )
        NovaSphere().status()
        sphere = NovaSphere(session_id="release-export")
        manifest = {
            "product": "NOVA",
            "version": NOVA_VERSION,
            "mesie_version": MESIE_VERSION,
            "status": sphere.status(),
            "sample": sphere.process("NOVA production manifest sample").to_dict(),
        }
        (out_dir / "NOVA_Sphere_Manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )

        from mesie.mininova.sphere import MiniNovaSphere

        mini_dir = ROOT / "deliverables" / "mininova"
        mini_dir.mkdir(parents=True, exist_ok=True)
        mini = MiniNovaSphere(session_id="release-mininova-export")
        mini_manifest = {
            "product": "MININOVA",
            "version": MININOVA_VERSION,
            "mesie_version": MESIE_VERSION,
            "status": mini.status(),
            "sample": mini.process("MININOVA production release sample").to_dict(),
        }
        (mini_dir / "MININOVA_Sphere_Manifest.json").write_text(
            json.dumps(mini_manifest, indent=2), encoding="utf-8"
        )

    return report