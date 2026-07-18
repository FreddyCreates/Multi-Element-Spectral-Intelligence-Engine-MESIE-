"""Download and parse public univariate time-series datasets."""

from __future__ import annotations

import hashlib
import io
import json
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True)
class DatasetSplit:
    values: np.ndarray
    labels: np.ndarray


@dataclass(frozen=True)
class LoadedDataset:
    dataset_id: str
    domain: str
    train: DatasetSplit
    test: DatasetSplit
    provenance: dict[str, Any]


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _download(url: str, timeout: int = 60) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "MESIE-External-Validation/0.1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def _read_ts(text: str) -> DatasetSplit:
    """Parse the equal-length, univariate .ts format used by UCR/TSML."""
    rows: list[list[float]] = []
    labels: list[str] = []
    in_data = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower() == "@data":
            in_data = True
            continue
        if not in_data:
            continue
        parts = line.rsplit(":", 1)
        if len(parts) != 2:
            raise ValueError("Expected univariate .ts row ending in ':class_label'")
        series, label = parts
        values = [float(v) for v in series.split(",") if v and v != "?"]
        if not values:
            raise ValueError("Encountered an empty time series")
        rows.append(values)
        labels.append(label.strip())
    if not rows:
        raise ValueError("No @data rows found in .ts payload")
    lengths = {len(row) for row in rows}
    if len(lengths) != 1:
        raise ValueError("This validation version requires equal-length series")
    return DatasetSplit(np.asarray(rows, dtype=np.float64), np.asarray(labels, dtype=str))


def _find_split(zf: zipfile.ZipFile, dataset_id: str, split: str) -> str:
    suffix = f"{dataset_id}_{split.upper()}.ts".lower()
    matches = [name for name in zf.namelist() if name.lower().endswith(suffix)]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {suffix} in archive; found {len(matches)}")
    return zf.read(matches[0]).decode("utf-8-sig")


def load_dataset(spec: dict[str, Any], cache_dir: Path) -> LoadedDataset:
    dataset_id = str(spec["id"])
    domain = str(spec["domain"])
    url = str(spec["url"])
    cache_dir.mkdir(parents=True, exist_ok=True)
    archive_path = cache_dir / f"{dataset_id}.zip"
    if archive_path.exists():
        payload = archive_path.read_bytes()
    else:
        payload = _download(url)
        archive_path.write_bytes(payload)

    digest = sha256_bytes(payload)
    expected = spec.get("sha256")
    if expected and digest.lower() != str(expected).lower():
        raise ValueError(f"SHA-256 mismatch for {dataset_id}: {digest}")

    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        train = _read_ts(_find_split(zf, dataset_id, "TRAIN"))
        test = _read_ts(_find_split(zf, dataset_id, "TEST"))

    return LoadedDataset(
        dataset_id=dataset_id,
        domain=domain,
        train=train,
        test=test,
        provenance={
            "source_url": url,
            "archive_sha256": digest,
            "train_samples": int(train.values.shape[0]),
            "test_samples": int(test.values.shape[0]),
            "series_length": int(train.values.shape[1]),
            "classes": sorted(set(train.labels.tolist() + test.labels.tolist())),
        },
    )


def load_config(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported or missing schema_version")
    if not data.get("datasets"):
        raise ValueError("Configuration must contain at least one dataset")
    return data
