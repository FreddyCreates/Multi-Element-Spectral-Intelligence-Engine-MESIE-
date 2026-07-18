"""Orchestrate a frozen external-validation run."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .datasets import load_config, load_dataset
from .evaluate import evaluate_feature_set
from .features import (
    fft_features,
    mesie_features,
    mesie_temporal_spectral_features,
    statistical_features,
)
from .reporting import write_outputs
from .sovereign import bind_sovereign


def run(
    config_path: Path,
    mesie_root: Path,
    output_dir: Path | None = None,
    *,
    sovereign_root: Path | None = None,
    require_sovereign: bool = True,
) -> dict[str, Any]:
    config_bytes = config_path.read_bytes()
    config = load_config(config_path)
    cache_dir = config_path.parent.parent / config.get("cache_dir", "data/cache")
    output = output_dir or config_path.parent.parent / config.get("output_dir", "artifacts")
    margin = float(config.get("support_margin", 0.0))
    sovereign_binding = bind_sovereign(sovereign_root, required=require_sovereign)

    datasets = []
    supported = 0
    for spec in config["datasets"]:
        loaded = load_dataset(spec, cache_dir)
        extractors = [
            ("statistics", statistical_features),
            ("fft-32", lambda x: fft_features(x, bins=32)),
            ("mesie", lambda x, root=mesie_root: mesie_features(x, root, n_bands=8)),
            (
                "mesie-temporal-spectral-v2",
                lambda x, root=mesie_root: mesie_temporal_spectral_features(x, root),
            ),
        ]
        metrics = [
            evaluate_feature_set(
                name,
                loaded.train.values,
                loaded.train.labels,
                loaded.test.values,
                loaded.test.labels,
                extractor,
            )
            for name, extractor in extractors
        ]
        by_name = {item["feature_set"]: item for item in metrics}
        stronger_baseline = max(by_name["statistics"]["accuracy"], by_name["fft-32"]["accuracy"])
        candidate = by_name["mesie-temporal-spectral-v2"]
        externally_supported = candidate["accuracy"] >= stronger_baseline + margin
        supported += int(externally_supported)
        datasets.append({
            "id": loaded.dataset_id,
            "domain": loaded.domain,
            "provenance": loaded.provenance,
            "results": metrics,
            "externally_supported": externally_supported,
            "stronger_baseline_accuracy": stronger_baseline,
            "original_mesie_accuracy": by_name["mesie"]["accuracy"],
            "advanced_mesie_accuracy": candidate["accuracy"],
        })

    total = len(datasets)
    conclusion = (
        f"MESIE met the frozen external-support rule on {supported}/{total} public datasets. "
        "This result measures reproducible classification utility; it does not establish universal "
        "cross-domain semantics or production readiness."
    )
    result = {
        "schema_version": 1,
        "run_id": datetime.now(timezone.utc).strftime("mesie-external-%Y%m%dT%H%M%SZ"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "mesie_source": "configured checkout or installed package",
        "support_margin": margin,
        "sovereign_binding": sovereign_binding,
        "supported_datasets": supported,
        "total_datasets": total,
        "conclusion": conclusion,
        "datasets": datasets,
    }
    json_path, md_path = write_outputs(result, output)
    result["output_json"] = str(json_path)
    result["output_markdown"] = str(md_path)
    return result
