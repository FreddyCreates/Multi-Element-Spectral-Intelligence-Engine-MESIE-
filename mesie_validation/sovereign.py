"""Bind MESIE evidence runs to the versioned Sovereign consumer contract."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

CONTRACT_PATH = Path("integration/training-contract.v1.json")
EXPECTED_SCHEMA = "sovereign.training.contract.v1"
EXPECTED_REPOSITORY = "FreddyCreates/sovereign"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_value(root: Path, *args: str) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
        shell=False,
    )
    return completed.stdout.strip() or None if completed.returncode == 0 else None


def discover_sovereign_root(explicit: Path | None = None) -> Path | None:
    candidates = [explicit] if explicit else []
    for name in ("MESIE_SOVEREIGN_ROOT", "SOVEREIGN_ROOT"):
        if os.environ.get(name):
            candidates.append(Path(os.environ[name]))
    repo_root = Path(__file__).resolve().parents[1]
    candidates.extend((repo_root.parent / "sovereign", Path.home() / "sovereign"))
    seen: set[str] = set()
    for candidate in candidates:
        if candidate is None:
            continue
        resolved = candidate.expanduser().resolve()
        key = str(resolved).lower()
        if key not in seen and (resolved / CONTRACT_PATH).is_file():
            return resolved
        seen.add(key)
    return None


def bind_sovereign(root: Path | None = None, *, required: bool = True) -> dict[str, Any] | None:
    resolved = discover_sovereign_root(root)
    if resolved is None:
        if required:
            raise FileNotFoundError(
                "Sovereign contract not found. Pass --sovereign-root or set MESIE_SOVEREIGN_ROOT."
            )
        return None

    contract_bytes = (resolved / CONTRACT_PATH).read_bytes()
    contract = json.loads(contract_bytes)
    if contract.get("schema") != EXPECTED_SCHEMA:
        raise ValueError(f"Unsupported Sovereign contract schema: {contract.get('schema')!r}")
    if contract.get("repository") != EXPECTED_REPOSITORY:
        raise ValueError(f"Unexpected Sovereign repository: {contract.get('repository')!r}")
    missing = [
        name for name in contract.get("required_files", []) if not (resolved / name).is_file()
    ]
    if missing:
        raise ValueError(f"Sovereign checkout is missing required files: {', '.join(missing)}")

    excluded = set(contract.get("exclude_parts", []))
    selected: dict[str, Path] = {}
    for pattern in contract.get("include_globs", []):
        for path in resolved.glob(pattern):
            if path.is_file() and not any(part in excluded for part in path.parts):
                selected[path.relative_to(resolved).as_posix()] = path
    files = [
        {"path": name, "sha256": _sha256(path.read_bytes()), "bytes": path.stat().st_size}
        for name, path in sorted(selected.items())
    ]
    if required and not files:
        raise ValueError("Sovereign contract selected no usable files")

    receipt: dict[str, Any] = {
        "schema": "mesie.sovereign.binding.v1",
        "contract_id": contract["contract_id"],
        "contract_sha256": _sha256(contract_bytes),
        "repository": contract["repository"],
        "commit": _git_value(resolved, "rev-parse", "HEAD") or "unversioned-local-source",
        "remote": _git_value(resolved, "remote", "get-url", "origin"),
        "dirty": bool(_git_value(resolved, "status", "--porcelain")),
        "records": len(files),
        "text_bytes": sum(item["bytes"] for item in files),
        "files": files,
        "attribution": contract["attribution"],
    }
    receipt["receipt_sha256"] = _sha256(
        json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    return receipt
