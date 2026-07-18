from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import numpy as np

from mesie_validation.datasets import _read_ts, load_dataset
from mesie_validation.evaluate import evaluate_feature_set
from mesie_validation.features import fft_features, statistical_features, temporal_paa_features
from mesie_validation.reporting import render_markdown
from mesie_validation.sovereign import bind_sovereign


def test_ts_parser() -> None:
    split = _read_ts("@problemName Demo\n@data\n1,2,3:A\n3,2,1:B\n")
    assert split.values.shape == (2, 3)
    assert split.labels.tolist() == ["A", "B"]


def test_fft_features_are_fixed_width() -> None:
    values = np.asarray([[0, 1, 0, -1] * 8, [1, 0, -1, 0] * 8], dtype=float)
    features = fft_features(values, bins=16)
    assert features.shape == (2, 16)
    assert np.all(np.isfinite(features))


def test_temporal_features_preserve_order() -> None:
    values = np.asarray([[0, 0, 1, 1], [1, 1, 0, 0]], dtype=float)
    features = temporal_paa_features(values, bins=4)
    assert features.shape == (2, 4)
    assert not np.allclose(features[0], features[1])


def test_evaluation_finds_separable_frequency_classes() -> None:
    t = np.linspace(0, 1, 128, endpoint=False)
    train = np.vstack([np.sin(2 * np.pi * 3 * t), np.sin(2 * np.pi * 12 * t)] * 4)
    labels = np.asarray(["low", "high"] * 4)
    result = evaluate_feature_set("fft", train, labels, train, labels, fft_features)
    assert result["accuracy"] == 1.0
    assert result["macro_f1"] == 1.0


def test_report_contains_provenance() -> None:
    result = {
        "run_id": "test",
        "generated_at": "now",
        "config_sha256": "abc",
        "conclusion": "done",
        "datasets": [{
            "id": "Demo",
            "domain": "synthetic",
            "provenance": {
                "source_url": "https://example.test/demo.zip",
                "archive_sha256": "123",
                "train_samples": 2,
                "test_samples": 2,
                "series_length": 3,
                "classes": ["A", "B"],
            },
            "results": [{
                "feature_set": "fft-32", "accuracy": 1.0, "macro_f1": 1.0,
                "feature_ms_per_sample": 0.1, "query_ms_per_sample": 0.1,
            }],
        }],
    }
    rendered = render_markdown(result)
    assert "https://example.test/demo.zip" in rendered
    assert "Archive SHA-256" in rendered


def test_sovereign_contract_binding(tmp_path: Path) -> None:
    root = tmp_path / "sovereign"
    (root / "integration").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "AGENTS.md").write_text("governance", encoding="utf-8")
    (root / "docs" / "ARCHITECTURE.md").write_text("architecture", encoding="utf-8")
    contract = {
        "schema": "sovereign.training.contract.v1",
        "contract_id": "freddycreates.sovereign.training.v1",
        "repository": "FreddyCreates/sovereign",
        "attribution": {"creator": "Alfredo Medina Hernandez", "required": True},
        "required_files": ["AGENTS.md", "docs/ARCHITECTURE.md"],
        "include_globs": ["AGENTS.md", "docs/**/*.md"],
        "exclude_parts": [".git"],
    }
    (root / "integration" / "training-contract.v1.json").write_text(
        json.dumps(contract), encoding="utf-8"
    )
    receipt = bind_sovereign(root)
    assert receipt is not None
    assert receipt["records"] == 2
    assert len(receipt["receipt_sha256"]) == 64
