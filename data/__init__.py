"""MESIE reference data loader.

Provides convenience functions for loading bundled reference datasets.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).parent


def get_reference_path(name: str) -> Path:
    """Get the full path to a reference data file.

    Args:
        name: Filename (with or without .json extension).

    Returns:
        Full path to the data file.
    """
    if not name.endswith(".json"):
        name = f"{name}.json"

    # Check reference directory
    ref_path = DATA_DIR / "reference" / name
    if ref_path.exists():
        return ref_path

    # Check benchmarks directory
    bench_path = DATA_DIR / "benchmarks" / name
    if bench_path.exists():
        return bench_path

    raise FileNotFoundError(f"Data file not found: {name}")


def load_reference(name: str) -> dict[str, Any]:
    """Load a reference dataset by name.

    Args:
        name: Dataset name (e.g., 'earthquake_psd_reference').

    Returns:
        Parsed JSON data as a dictionary.
    """
    path = get_reference_path(name)
    with open(path) as f:
        return json.load(f)


def load_benchmark(name: str) -> dict[str, Any]:
    """Load a benchmark dataset by name.

    Args:
        name: Benchmark name (e.g., 'spectral_classification_benchmark').

    Returns:
        Parsed JSON data as a dictionary.
    """
    if not name.endswith(".json"):
        name = f"{name}.json"
    path = DATA_DIR / "benchmarks" / name
    if not path.exists():
        raise FileNotFoundError(f"Benchmark file not found: {name}")
    with open(path) as f:
        return json.load(f)


def list_references() -> list[str]:
    """List all available reference datasets."""
    ref_dir = DATA_DIR / "reference"
    if not ref_dir.exists():
        return []
    return [f.stem for f in ref_dir.glob("*.json")]


def list_benchmarks() -> list[str]:
    """List all available benchmark datasets."""
    bench_dir = DATA_DIR / "benchmarks"
    if not bench_dir.exists():
        return []
    return [f.stem for f in bench_dir.glob("*.json")]
