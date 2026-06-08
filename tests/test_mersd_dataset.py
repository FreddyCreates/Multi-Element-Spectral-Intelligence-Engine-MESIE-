"""MERSD Zenodo robotics dataset builder tests."""

from __future__ import annotations

import json
from pathlib import Path

from mesie.robotics.zenodo_dataset import build_mersd


def test_build_mersd_package(tmp_path):
    out, manifest = build_mersd(tmp_path / "mersd", variants_per_scenario=2, zip_archive=True)
    assert manifest.episode_count >= 10
    assert (out / "manifest.json").is_file()
    assert (out / "zenodo_metadata.json").is_file()
    assert (out / "README.md").is_file()
    assert (out / "CITATION.cff").is_file()
    assert (out / "records").is_dir()
    assert (out / "embeddings").is_dir()
    assert (out / "splits" / "train.json").is_file()

    ep_files = list((out / "episodes").glob("*.json"))
    ep = json.loads(ep_files[0].read_text(encoding="utf-8"))
    assert "fusion_embedding" in ep
    assert "label" in ep
    assert ep["label"]["fault_state"]

    meta = json.loads((out / "zenodo_metadata.json").read_text(encoding="utf-8"))
    assert meta["upload_type"] == "dataset"
    assert "UAV" in " ".join(meta["keywords"])

    zip_path = tmp_path / f"MERSD_v{manifest.version}.zip"
    assert zip_path.is_file()