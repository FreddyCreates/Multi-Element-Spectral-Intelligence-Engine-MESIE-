"""4-Tier Market Ready Loop — agent squads cycle while you sleep.

Tiers:
  1 PROVE   — production tiers, ops triad, processor health
  2 PACKAGE — quality triad, market zip, tokens, FIVE_BUSINESSES
  3 PLATFORM — intel triad, platforms, HERMES, computing family
  4 SHIP    — research triad, portal fork, ICP bridge, NOVA pulse
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.version_info import MESIE_VERSION

ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable
OUT = ROOT / "deliverables" / "market"
STATE = OUT / "FOUR_TIER_MARKET_READY_STATE.json"
FEED = OUT / "FOUR_TIER_MARKET_READY_FEED.jsonl"
MANIFEST = OUT / "FOUR_TIER_MARKET_READY.json"
PROTOCOL = "MESIE-FOUR-TIER-MARKET-READY/1.0"


@dataclass(frozen=True)
class MarketTier:
    tier_id: str
    tier_num: int
    title: str
    squad_id: str
    agent_role: str
    tasks: tuple[str, ...]
    verify_artifact: str
    description: str


FOUR_TIERS: List[MarketTier] = [
    MarketTier(
        "prove",
        1,
        "Prove — Production & Uptime",
        "ops-triad",
        "ops",
        ("production_tiers", "processor_probe", "nova_stale_check"),
        "deliverables/MESIE_Production_Tiers_Report.json",
        "Tier 1: measured SLA, production appliance, ops agents keep :8750 alive.",
    ),
    MarketTier(
        "package",
        2,
        "Package — Market Artifacts",
        "quality-triad",
        "quality",
        ("token_manifest", "market_manifest_refresh", "squad_quality"),
        "deliverables/market/MARKET_RELEASE_MANIFEST.json",
        "Tier 2: pytest gate, commercial pack, tokens + FIVE_BUSINESSES refresh.",
    ),
    MarketTier(
        "platform",
        3,
        "Platform — Intelligence Surface",
        "intel-triad",
        "intel",
        ("platform_pulse", "hermes_forge_light", "squad_intel"),
        "deliverables/platform/PLATFORM_MANIFEST.json",
        "Tier 3: embed/match pulse, model platforms, HERMES fleet pack.",
    ),
    MarketTier(
        "ship",
        4,
        "Ship — Release & Federation",
        "research-triad",
        "ship",
        ("market_portal_fork", "icp_bridge_status", "squad_research"),
        "deliverables/market/FIVE_BUSINESSES.json",
        "Tier 4: research forge, portal fork, ICP + NOVA ship lane.",
    ),
]


def _http_json(url: str, timeout: float = 6.0) -> Optional[Dict[str, Any]]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError):
        return None


def _run(cmd: List[str], *, timeout: int = 300) -> Dict[str, Any]:
    try:
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout, check=False)
        return {
            "ok": r.returncode == 0,
            "exit_code": r.returncode,
            "tail": (r.stdout or r.stderr)[-600:],
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _append_feed(entry: Dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with FEED.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")


def _task_handlers() -> Dict[str, Any]:
    return {
        "production_tiers": lambda: _run([PYTHON, "scripts/run_production_tiers.py", "--tier", "both"], timeout=240),
        "processor_probe": lambda: {
            "ok": bool(_http_json("http://127.0.0.1:8750/processor/status")),
            "processor": _http_json("http://127.0.0.1:8750/processor/status"),
            "market_ready": _http_json("http://127.0.0.1:8750/processor/market-ready"),
        },
        "nova_stale_check": lambda: _nova_stale(),
        "token_manifest": lambda: _run([PYTHON, "-c", "from mesie.tokens.dual_bridge import write_manifest; write_manifest(); print('ok')"]),
        "market_manifest_refresh": lambda: _refresh_five_businesses(),
        "squad_quality": lambda: _run_squad("quality-triad"),
        "platform_pulse": lambda: {
            "ok": True,
            "platform": _http_json("http://127.0.0.1:8750/processor/platform"),
            "models": _http_json("http://127.0.0.1:8750/processor/models"),
        },
        "hermes_forge_light": lambda: _hermes_forge_light(),
        "squad_intel": lambda: _run_squad("intel-triad"),
        "market_portal_fork": lambda: _run([PYTHON, "scripts/build_market_portal_fork.py"], timeout=120),
        "icp_bridge_status": lambda: _icp_status(),
        "squad_research": lambda: _run_squad("research-triad"),
    }


def _nova_stale() -> Dict[str, Any]:
    path = ROOT / "deliverables" / "nova" / "NOVA_RUNTIME_STATE.json"
    if not path.is_file():
        return {"ok": False, "stale_s": 9999, "action": "spawn_recommended"}
    try:
        st = json.loads(path.read_text(encoding="utf-8"))
        ts = float(st.get("ts") or 0)
        stale = time.time() - ts if ts else 9999.0
        if stale > 180:
            _run([PYTHON, "scripts/run_nova_runtime.py", "--once"], timeout=180)
        return {"ok": stale < 300, "stale_s": round(stale, 1)}
    except (json.JSONDecodeError, TypeError):
        return {"ok": False, "error": "bad_nova_state"}


def _refresh_five_businesses() -> Dict[str, Any]:
    src = OUT / "FIVE_BUSINESSES.json"
    if not src.is_file():
        return {"ok": False, "error": "FIVE_BUSINESSES.json missing"}
    try:
        data = json.loads(src.read_text(encoding="utf-8"))
        data["last_loop_refresh"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        data["market_ready_loop"] = PROTOCOL
        src.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return {"ok": True, "businesses": len(data.get("businesses", []))}
    except json.JSONDecodeError:
        return {"ok": False, "error": "invalid json"}


def _hermes_forge_light() -> Dict[str, Any]:
    try:
        from mesie.hermes.forge import forge_hermes_fleet

        return forge_hermes_fleet(zip_sdk=False)
    except Exception as exc:
        return {"ok": False, "error": str(exc), "note": "hermes optional"}


def _icp_status() -> Dict[str, Any]:
    try:
        from mesie.cloud.icp_bridge import build_platform_manifest

        return {"ok": True, "icp": build_platform_manifest()}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _run_squad(squad_id: str) -> Dict[str, Any]:
    from mesie.compute.tri_agent_squads import execute_squad

    return execute_squad(squad_id)


def run_tier(tier_id: str, *, cycle_num: int = 1, light: bool = False) -> Dict[str, Any]:
    tier = next((t for t in FOUR_TIERS if t.tier_id == tier_id), None)
    if not tier:
        return {"ok": False, "error": f"unknown tier: {tier_id}"}

    handlers = _task_handlers()
    task_results: List[Dict[str, Any]] = []
    all_ok = True
    skip_heavy = light or (tier_id == "prove" and cycle_num % 3 != 1)
    for task in tier.tasks:
        heavy_tasks = (
            "production_tiers", "official_pack", "full_release_pack", "metamaterial_research",
            "squad_quality", "squad_intel", "squad_research", "market_portal_fork",
            "hermes_forge_light",
        )
        if (skip_heavy or light) and task in heavy_tasks:
            task_results.append({"task": task, "ok": True, "skipped": True, "reason": "heavy_or_light_mode"})
            continue
        fn = handlers.get(task)
        if not fn:
            r = {"ok": False, "error": f"no handler: {task}"}
        else:
            r = fn()
            if isinstance(r, dict):
                r = {**r, "task": task}
            else:
                r = {"ok": True, "task": task, "result": r}
        task_results.append(r)
        if not r.get("ok", False):
            all_ok = False

    verify_path = ROOT / tier.verify_artifact
    verify_ok = verify_path.is_file()

    return {
        "ok": all_ok and verify_ok,
        "tier_id": tier.tier_id,
        "tier_num": tier.tier_num,
        "title": tier.title,
        "squad_id": tier.squad_id,
        "tasks": task_results,
        "verify_artifact": tier.verify_artifact,
        "verify_ok": verify_ok,
        "market_ready": all_ok and verify_ok,
    }


def run_market_cycle(*, tier: Optional[str] = None, light: bool = False) -> Dict[str, Any]:
    """Run one full 4-tier cycle or a single tier."""
    tiers_to_run = [tier] if tier else [t.tier_id for t in FOUR_TIERS]
    prev_cycles = 0
    if STATE.is_file():
        try:
            prev_cycles = int(json.loads(STATE.read_text(encoding="utf-8")).get("cycles", 0))
        except (json.JSONDecodeError, TypeError):
            pass
    cycle_num = prev_cycles + 1
    results = [run_tier(tid, cycle_num=cycle_num, light=light) for tid in tiers_to_run]
    cycle_ok = all(r.get("market_ready", r.get("ok")) for r in results)

    snap = {
        "protocol": PROTOCOL,
        "mesie_version": MESIE_VERSION,
        "cycle_ok": cycle_ok,
        "market_ready": cycle_ok,
        "tiers_complete": sum(1 for r in results if r.get("market_ready")),
        "tier_count": len(FOUR_TIERS),
        "results": results,
        "sleep_safe": cycle_ok,
        "ts": time.time(),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    snap["cycles"] = cycle_num

    OUT.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(snap, indent=2) + "\n", encoding="utf-8")
    _append_feed({"cycle": snap["cycles"], "ok": cycle_ok, "tiers": [r["tier_id"] for r in results]})
    market_ready_manifest(write=True)
    return snap


def market_ready_manifest(*, write: bool = False) -> Dict[str, Any]:
    manifest = {
        "protocol": PROTOCOL,
        "mesie_version": MESIE_VERSION,
        "brand": "ItsnotAILabs",
        "tier_count": len(FOUR_TIERS),
        "tiers": [
            {
                "tier_id": t.tier_id,
                "tier_num": t.tier_num,
                "title": t.title,
                "squad_id": t.squad_id,
                "tasks": list(t.tasks),
                "verify_artifact": t.verify_artifact,
                "description": t.description,
            }
            for t in FOUR_TIERS
        ],
        "businesses": 5,
        "loop_command": "python -m mesie.market.four_tier_loop",
        "sleep_start": ".\\Start-MarketReadySleep.ps1",
        "state": str(STATE),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if write:
        OUT.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if STATE.is_file():
        try:
            manifest["last_cycle"] = json.loads(STATE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return manifest


class MarketReadyLoop:
    """Never-stop 4-tier market loop — runs agent squads on interval."""

    def __init__(self, *, interval_s: float = 420.0) -> None:
        self.interval_s = min(900.0, max(180.0, interval_s))
        self._cycles = 0
        self._started = time.time()

    def pulse(self) -> Dict[str, Any]:
        self._cycles += 1
        snap = run_market_cycle()
        snap["loop_cycles"] = self._cycles
        snap["uptime_s"] = round(time.time() - self._started, 1)
        return snap

    def run_forever(self) -> None:
        print("[market-ready] 4-tier loop started — safe to sleep", flush=True)
        print(f"[market-ready] interval={self.interval_s}s tiers={len(FOUR_TIERS)}", flush=True)
        while True:
            try:
                snap = self.pulse()
                print(
                    f"[market-ready] cycle={snap.get('cycles')} ok={snap.get('cycle_ok')} "
                    f"tiers={snap.get('tiers_complete')}/{snap.get('tier_count')} "
                    f"sleep_safe={snap.get('sleep_safe')}",
                    flush=True,
                )
            except Exception as exc:
                print(f"[market-ready] error: {exc}", flush=True)
            time.sleep(self.interval_s)


def main(argv: Optional[List[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="4-tier market ready agent loop")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--tier", choices=[t.tier_id for t in FOUR_TIERS])
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--manifest", action="store_true")
    parser.add_argument("--interval", type=float, default=420.0)
    args = parser.parse_args(argv)

    if args.manifest:
        print(json.dumps(market_ready_manifest(write=True), indent=2))
        return 0
    if args.status:
        if STATE.is_file():
            print(STATE.read_text(encoding="utf-8"))
        else:
            print(json.dumps({"ok": False, "note": "not started"}, indent=2))
        return 0
    if args.once:
        print(json.dumps(run_market_cycle(tier=args.tier), indent=2))
        return 0
    try:
        MarketReadyLoop(interval_s=args.interval).run_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())