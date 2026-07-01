"""Timestamped deliverable runs — never overwrite without archiving + lineage."""

from __future__ import annotations

import hashlib
import json
import shutil
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

ROOT = Path(__file__).resolve().parents[2]


def _utc_stamp() -> str:
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


@dataclass
class RunSnapshot:
    run_key: str
    stamp: str
    suite: str
    paths: Dict[str, str]
    bytes_total: int
    prior_stamp: Optional[str] = None
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LineageLedger:
    run_key: str
    suite: str
    latest_stamp: str
    latest_paths: Dict[str, str] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_key": self.run_key,
            "suite": self.suite,
            "latest_stamp": self.latest_stamp,
            "latest_paths": self.latest_paths,
            "history": self.history,
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }


class DeliverableVersioning:
    """Archive prior artifacts, write timestamped run folders, maintain lineage ledgers."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = Path(base_dir)
        self.runs_dir = self.base_dir / "runs"
        self.lineage_dir = self.base_dir / "lineage"
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.lineage_dir.mkdir(parents=True, exist_ok=True)

    def _ledger_path(self, run_key: str) -> Path:
        return self.lineage_dir / f"LINEAGE_{run_key}.json"

    def load_ledger(self, run_key: str, *, suite: str) -> LineageLedger:
        p = self._ledger_path(run_key)
        if not p.is_file():
            return LineageLedger(run_key=run_key, suite=suite, latest_stamp="")
        data = json.loads(p.read_text(encoding="utf-8"))
        return LineageLedger(
            run_key=data["run_key"],
            suite=data.get("suite", suite),
            latest_stamp=data.get("latest_stamp", ""),
            latest_paths=data.get("latest_paths", {}),
            history=data.get("history", []),
        )

    def save_ledger(self, ledger: LineageLedger) -> Path:
        p = self._ledger_path(ledger.run_key)
        p.write_text(json.dumps(ledger.to_dict(), indent=2) + "\n", encoding="utf-8")
        return p

    def archive_existing(self, paths: Dict[str, Path], *, run_key: str, suite: str, note: str = "") -> Optional[RunSnapshot]:
        existing = {k: p for k, p in paths.items() if p.is_file()}
        if not existing:
            return None
        ledger = self.load_ledger(run_key, suite=suite)
        stamp = _utc_stamp()
        run_dir = self.runs_dir / f"{stamp}_prior_{run_key}"
        run_dir.mkdir(parents=True, exist_ok=True)
        archived: Dict[str, str] = {}
        total = 0
        for name, src in existing.items():
            dest = run_dir / src.name
            shutil.copy2(src, dest)
            archived[name] = str(dest.relative_to(self.base_dir))
            total += dest.stat().st_size
        snap = RunSnapshot(
            run_key=run_key,
            stamp=stamp,
            suite=suite,
            paths=archived,
            bytes_total=total,
            prior_stamp=ledger.latest_stamp or None,
            note=note or "archived before new write",
        )
        ledger.history.append(snap.to_dict())
        ledger.latest_stamp = stamp
        ledger.latest_paths = archived
        self.save_ledger(ledger)
        return snap

    def write_versioned(
        self,
        artifacts: Dict[str, Union[str, Dict[str, Any]]],
        *,
        run_key: str,
        suite: str,
        canonical_names: Dict[str, Path],
        note: str = "",
    ) -> RunSnapshot:
        """Archive canonical files if present, write new stamp folder + update canonical copies."""
        self.archive_existing(canonical_names, run_key=run_key, suite=suite, note=f"prior to {note or 'new run'}")

        stamp = _utc_stamp()
        run_dir = self.runs_dir / f"{stamp}_run_{run_key}"
        run_dir.mkdir(parents=True, exist_ok=True)
        written: Dict[str, str] = {}
        total = 0

        for logical, content in artifacts.items():
            canon = canonical_names.get(logical)
            if canon is None:
                continue
            if isinstance(content, dict):
                text = json.dumps(content, indent=2, default=str) + "\n"
            else:
                text = content if content.endswith("\n") else content + "\n"
            run_path = run_dir / canon.name
            run_path.write_text(text, encoding="utf-8")
            canon.parent.mkdir(parents=True, exist_ok=True)
            canon.write_text(text, encoding="utf-8")
            rel = str(run_path.relative_to(self.base_dir))
            written[logical] = rel
            total += len(text.encode("utf-8"))

        ledger = self.load_ledger(run_key, suite=suite)
        prior = ledger.latest_stamp or None
        snap = RunSnapshot(
            run_key=run_key,
            stamp=stamp,
            suite=suite,
            paths=written,
            bytes_total=total,
            prior_stamp=prior,
            note=note or "new run",
        )
        ledger.history.append(snap.to_dict())
        ledger.latest_stamp = stamp
        ledger.latest_paths = written
        self.save_ledger(ledger)
        return snap


def synthesize_json_runs(
    *,
    label_a: str,
    data_a: Dict[str, Any],
    label_b: str,
    data_b: Dict[str, Any],
) -> Dict[str, Any]:
    """Human-readable diff summary for two JSON deliverable snapshots."""
    summary: Dict[str, Any] = {
        "labels": [label_a, label_b],
        "top_level_keys": {
            "only_a": sorted(set(data_a) - set(data_b)),
            "only_b": sorted(set(data_b) - set(data_a)),
            "shared": sorted(set(data_a) & set(data_b)),
        },
        "field_changes": [],
    }

    for key in sorted(set(data_a) & set(data_b)):
        va, vb = data_a[key], data_b[key]
        if va == vb:
            continue
        entry: Dict[str, Any] = {"field": key}
        if isinstance(va, list) and isinstance(vb, list):
            entry["type"] = "list"
            entry["len_a"] = len(va)
            entry["len_b"] = len(vb)
            entry["delta"] = len(vb) - len(va)
            if va and isinstance(va[0], dict) and vb and isinstance(vb[0], dict):
                keys_a = set(va[0].keys())
                keys_b = set(vb[0].keys())
                entry["item_keys_only_a"] = sorted(keys_a - keys_b)
                entry["item_keys_only_b"] = sorted(keys_b - keys_a)
        elif isinstance(va, dict) and isinstance(vb, dict):
            entry["type"] = "object"
            entry["json_chars_a"] = len(json.dumps(va, default=str))
            entry["json_chars_b"] = len(json.dumps(vb, default=str))
            entry["delta_chars"] = entry["json_chars_b"] - entry["json_chars_a"]
        else:
            entry["type"] = "scalar"
            entry["a"] = va
            entry["b"] = vb
        summary["field_changes"].append(entry)

    return summary


def synthesize_theater_state(old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    base = synthesize_json_runs(label_a="committed_full", data_a=old, label_b="partial_rerun", data_b=new)
    old_ticks = old.get("ticks") or []
    new_ticks = new.get("ticks") or []
    old_ids = [t.get("operation_id") for t in old_ticks]
    new_ids = [t.get("operation_id") for t in new_ticks]
    base["theater_detail"] = {
        "ticks_lost": max(0, len(old_ticks) - len(new_ticks)),
        "ticks_gained": max(0, len(new_ticks) - len(old_ticks)),
        "operations_in_old_only": sorted(set(old_ids) - set(new_ids)),
        "operations_in_new_only": sorted(set(new_ids) - set(old_ids)),
        "peak_agents": {"old": old.get("agents_deployed_peak"), "new": new.get("agents_deployed_peak")},
        "attrition": {"old": old.get("attrition_cumulative"), "new": new.get("attrition_cumulative")},
        "jam_level": {"old": old.get("jam_level"), "new": new.get("jam_level")},
        "sim_progress": {
            "old": f"day {old.get('sim_day')} hour {old.get('sim_hour')}",
            "new": f"day {new.get('sim_day')} hour {new.get('sim_hour')}",
        },
        "interpretation": (
            "Partial rerun kept only early-day ISR baseline ticks; full week ops (days 2–7, 10K surge) "
            "are present in the committed snapshot only."
            if len(new_ticks) < len(old_ticks)
            else "New run matches or exceeds committed tick count."
        ),
    }
    return base
