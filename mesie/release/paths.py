"""Workspace and install path resolution — dev checkout vs pip install."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

_PACKAGE_DIR = Path(__file__).resolve().parent.parent
_ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def package_dir() -> Path:
    return _PACKAGE_DIR


def bundled_assets_dir() -> Path:
    return _ASSETS_DIR


def user_config_dir() -> Path:
    base = os.environ.get("MESIE_HOME")
    if base:
        return Path(base)
    return Path.home() / ".mesie"


def resolve_workspace_root() -> Path:
    """Repo root when developing; ~/.mesie when pip-installed only."""
    env = os.environ.get("MESIE_REPO_ROOT")
    if env:
        return Path(env)

    here = _PACKAGE_DIR
    for candidate in (here.parent, here.parent.parent):
        if (candidate / "pyproject.toml").is_file() and (candidate / "mesie").is_dir():
            return candidate

    cfg = user_config_dir()
    cfg.mkdir(parents=True, exist_ok=True)
    return cfg


def script_source(name: str) -> Optional[Path]:
    """Resolve PowerShell helper — bundled assets first, then repo scripts/."""
    asset = _ASSETS_DIR / name
    if asset.is_file():
        return asset
    root = resolve_workspace_root()
    repo_script = root / "scripts" / name
    if repo_script.is_file():
        return repo_script
    return None