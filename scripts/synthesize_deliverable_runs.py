#!/usr/bin/env python3
"""Preserve both deliverable snapshots, synthesize what changed, restore full committed copies."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.release.deliverable_versioning import DeliverableVersioning, synthesize_json_runs, synthesize_theater_state

PAIRS = [
    {
        "key": "sov_del",
        "suite": "sovereign_local",
        "base": ROOT / "deliverables" / "native_ai" / "sovereign_local",
        "files": ["NativeAI_sov_del.json", "NativeAI_sov_del_vault.json"],
    },
    {
        "key": "theater_alpha_week_001",
        "suite": "mission_world",
        "base": ROOT / "library" / "mission_worlds",
        "files": ["theater_alpha_week_001_state.json"],
    },
]


def _git_head_json(rel: str) -> dict:
    raw = subprocess.check_output(["git", "show", f"HEAD:{rel}"], cwd=str(ROOT), text=True, encoding="utf-8")
    return json.loads(raw)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out_root = ROOT / "trust" / "production_readiness" / "synthesis"
    out_root.mkdir(parents=True, exist_ok=True)
    report: dict = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "runs": []}

    for spec in PAIRS:
        base: Path = spec["base"]
        ver = DeliverableVersioning(base)
        committed_dir = base / "runs" / f"{stamp}_committed_full_{spec['key']}"
        partial_dir = base / "runs" / f"{stamp}_partial_local_{spec['key']}"
        committed_dir.mkdir(parents=True, exist_ok=True)
        partial_dir.mkdir(parents=True, exist_ok=True)

        entry = {"run_key": spec["key"], "suite": spec["suite"], "files": {}}

        for fname in spec["files"]:
            rel = str((base / fname).relative_to(ROOT)).replace("\\", "/")
            committed_path = committed_dir / fname
            partial_path = partial_dir / fname
            canon = base / fname

            # Save partial (current disk) snapshot
            if canon.is_file():
                shutil.copy2(canon, partial_path)
            # Save committed (git HEAD) snapshot
            try:
                data_head = _git_head_json(rel)
                committed_path.write_text(json.dumps(data_head, indent=2) + "\n", encoding="utf-8")
            except subprocess.CalledProcessError:
                entry["files"][fname] = {"error": "not in git HEAD"}
                continue

            data_partial = _load_json(partial_path) if partial_path.is_file() else _load_json(committed_path)

            if "theater" in fname or "state" in fname:
                diff = synthesize_theater_state(data_head, data_partial)
            else:
                diff = synthesize_json_runs(
                    label_a="committed_full",
                    data_a=data_head,
                    label_b="partial_local",
                    data_b=data_partial,
                )

            # Restore full committed version to canonical path
            canon.write_text(json.dumps(data_head, indent=2) + "\n", encoding="utf-8")

            entry["files"][fname] = {
                "committed_snapshot": str(committed_path.relative_to(ROOT)),
                "partial_snapshot": str(partial_path.relative_to(ROOT)),
                "canonical_restored_from": "git HEAD (full run)",
                "synthesis": diff,
            }

        # Update lineage ledger
        ledger = ver.load_ledger(spec["key"], suite=spec["suite"])
        ledger.history.append({
            "event": "synthesis_restore",
            "stamp": stamp,
            "committed_dir": str(committed_dir.relative_to(base)),
            "partial_dir": str(partial_dir.relative_to(base)),
            "note": "Preserved both snapshots; canonical paths restored to committed full run.",
        })
        ver.save_ledger(ledger)
        report["runs"].append(entry)

    out_path = out_root / "Deliverable_Run_Synthesis.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# Deliverable Run Synthesis",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "Both snapshots are preserved under each suite's `runs/` folder. Canonical paths were restored to the **committed full** versions from git.",
        "",
    ]
    for run in report["runs"]:
        md_lines.append(f"## {run['run_key']} ({run['suite']})")
        md_lines.append("")
        for fname, info in run["files"].items():
            if "error" in info:
                md_lines.append(f"- **{fname}**: {info['error']}")
                continue
            md_lines.append(f"### `{fname}`")
            md_lines.append(f"- Committed: `{info['committed_snapshot']}`")
            md_lines.append(f"- Partial (June 24 disk): `{info['partial_snapshot']}`")
            syn = info["synthesis"]
            if "theater_detail" in syn:
                td = syn["theater_detail"]
                md_lines.append(f"- **Ticks:** committed {td.get('ticks_lost', 0) + len(_load_json(ROOT / info['partial_snapshot']).get('ticks', []))} → partial had {len(_load_json(ROOT / info['partial_snapshot']).get('ticks', []))} (lost {td['ticks_lost']})")
                md_lines.append(f"- **Ops only in full run:** {', '.join(td['operations_in_old_only']) or 'none'}")
                md_lines.append(f"- **Peak agents:** {td['peak_agents']}")
                md_lines.append(f"- **Attrition:** {td['attrition']}")
                md_lines.append(f"- {td['interpretation']}")
            else:
                for ch in syn.get("field_changes", [])[:8]:
                    md_lines.append(f"- `{ch['field']}`: {ch.get('type')} — {json.dumps({k: ch[k] for k in ch if k not in ('field', 'type')}, default=str)[:200]}")
            md_lines.append("")

    md_path = out_root / "Deliverable_Run_Synthesis.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(json.dumps({"ok": True, "json": str(out_path), "markdown": str(md_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
