"""MESIE Edge Robotics Spectral Dataset (MERSD) — Zenodo release builder.

Novel gap: open robotics corpora are vision/IMU-heavy; edge contested spectral
records (UAV swarm EW + machinery vibration + fusion/neuromorphic features) are scarce.
"""

from __future__ import annotations

import json
import shutil
import time
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from mesie.robotics.multimodal_fusion import FusionConfig, Modality, ModalityStream, MultiModalFusion
from mesie.robotics.neuromorphic_runtime import EncodingScheme, NeuromorphicRuntime, RuntimeConfig
from mesie.robotics.spectral_memory import MemoryConfig, SpectralMemory

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
DEFAULT_OUT = ROOT / "datasets" / "zenodo_mersd_v1"

MERSD_VERSION = "1.0.0"
MERSD_DOI_PLACEHOLDER = "10.5281/zenodo.TBD"


@dataclass
class EpisodeLabel:
    episode_id: str
    robot_class: str
    task: str
    environment: str
    fault_state: str
    jam_state: str
    swarm_outcome: str
    economic_sector: str
    zenodo_keywords: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MERSDEpisode:
    episode_id: str
    scenario_id: str
    domain: str
    label: EpisodeLabel
    record_paths: List[str]
    fusion_embedding: List[float]
    spike_count: int
    neuromorphic_energy: float
    memory_top_match: str
    memory_similarity: float
    n_agents: int
    ms_per_agent: float
    seed: int

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


@dataclass
class MERSDManifest:
    version: str
    title: str
    description: str
    episode_count: int
    record_count: int
    robot_classes: List[str]
    splits: Dict[str, int]
    keywords: List[str]
    license: str
    generated_at: str
    mesie_version: str
    gaps_filled: List[str]
    zenodo_targets: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ref_path(name: str) -> Path:
    return DATA / "reference" / f"{name}.json" if not name.endswith(".json") else DATA / "reference" / name


def _scenario_catalog() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for fname, domain, robot_class, sector in (
        ("military_drone_scenarios.json", "uav_swarm", "aerial_swarm", "defense_robotics"),
        ("enterprise_civilian_scenarios.json", "ground_industrial", "mobile_manipulator", "economic_impact"),
    ):
        path = DATA / "scenarios" / fname
        if not path.is_file():
            continue
        for sc in _load_json(path).get("scenarios", []):
            sc = dict(sc)
            sc["_domain"] = domain
            sc["_robot_class"] = robot_class
            sc["_sector"] = sector
            out.append(sc)
    return out


def _spectral_vector_from_ref(ref: Dict[str, Any], *, seed: int, noise: float = 0.05) -> np.ndarray:
    rng = np.random.default_rng(seed)
    comp = ref["components"][0]
    amps = np.array(comp.get("amplitude", comp.get("amplitudes", [])), dtype=float)
    if len(amps) == 0:
        amps = rng.random(128)
    vec = amps[:256] if len(amps) >= 256 else np.pad(amps, (0, 256 - len(amps)))
    vec = vec + rng.normal(0, noise, size=vec.shape)
    return np.clip(vec, 1e-12, None)


def _write_episode_record(
    episode_id: str,
    ref: Dict[str, Any],
    *,
    out_dir: Path,
    variant: str,
) -> Path:
    rec = dict(ref)
    rec["record_id"] = f"mersd-{episode_id}-{variant}"
    rec["metadata"] = dict(rec.get("metadata", {}))
    rec["metadata"]["mersd_episode"] = episode_id
    rec["metadata"]["mersd_variant"] = variant
    rec["metadata"]["dataset"] = f"MERSD/{MERSD_VERSION}"
    path = out_dir / "records" / f"{rec['record_id']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    return path


def _build_episode(
    scenario: Dict[str, Any],
    *,
    variant_idx: int,
    out_dir: Path,
    fusion: MultiModalFusion,
    runtime: NeuromorphicRuntime,
    memory: SpectralMemory,
) -> Optional[MERSDEpisode]:
    primary = scenario.get("primary_data", "")
    ref_path = _ref_path(primary)
    if not ref_path.is_file():
        return None
    ref = _load_json(ref_path)
    seed = hash(scenario["id"]) % 10_000 + variant_idx
    rng = np.random.default_rng(seed)

    jam = bool(scenario.get("jam_ground", False))
    jam_state = "ground_jam" if jam else ("orbital_preferred" if variant_idx % 3 == 0 else "clear")
    n_agents = int(scenario.get("n_agents", 64))
    ms_per_agent = float(rng.uniform(0.02, 0.45))

    spec = _spectral_vector_from_ref(ref, seed=seed)
    imu = rng.normal(0, 1, 64)
    audio = rng.normal(0, 0.5, 128) * (1.5 if jam else 1.0)

    fusion.clear()
    fusion.feed(ModalityStream(modality=Modality.SPECTRAL, data=spec[: fusion.config.output_dim], confidence=0.9))
    fusion.feed(ModalityStream(modality=Modality.IMU, data=imu[: fusion.config.output_dim], confidence=0.7))
    fusion.feed(ModalityStream(modality=Modality.AUDIO, data=audio[: fusion.config.output_dim], confidence=0.6 if jam else 0.8))
    fused = fusion.fuse()

    spikes = runtime.process(spec[: runtime.neuron_count])
    metrics = runtime.get_metrics()

    mem_entry = memory.store(fused.vector, label=scenario["id"], importance=0.5 + variant_idx * 0.05)
    query = memory.query(fused.vector, top_k=3)

    ep_id = f"{scenario['id']}_v{variant_idx:02d}"
    rec_primary = _write_episode_record(ep_id, ref, out_dir=out_dir, variant="primary")
    record_paths = [str(rec_primary.relative_to(out_dir)).replace("\\", "/")]

    secondary = scenario.get("secondary_data")
    if secondary:
        sec_path = _ref_path(secondary)
        if sec_path.is_file():
            sec_ref = _load_json(sec_path)
            rec_sec = _write_episode_record(ep_id, sec_ref, out_dir=out_dir, variant="secondary")
            record_paths.append(str(rec_sec.relative_to(out_dir)).replace("\\", "/"))

    fault = "anomaly_suspected" if fused.quality_score < 0.35 else "nominal"
    if scenario.get("_domain") == "uav_swarm" and jam:
        fault = "ew_degraded"
    swarm_outcome = "mission_ok" if ms_per_agent < 0.5 and not (jam and variant_idx % 5 == 4) else "degraded"

    label = EpisodeLabel(
        episode_id=ep_id,
        robot_class=scenario.get("_robot_class", "unknown"),
        task=scenario.get("label", scenario["id"]),
        environment=scenario.get("doctrine", scenario.get("industry", "edge")),
        fault_state=fault,
        jam_state=jam_state,
        swarm_outcome=swarm_outcome,
        economic_sector=scenario.get("_sector", "research"),
        zenodo_keywords=_keywords_for(scenario),
    )

    emb_path = out_dir / "embeddings" / f"{ep_id}.json"
    emb_path.parent.mkdir(parents=True, exist_ok=True)
    emb_path.write_text(
        json.dumps({
            "episode_id": ep_id,
            "dim": len(fused.vector),
            "vector": fused.vector.tolist(),
            "modality_contributions": fused.modality_contributions,
            "quality_score": fused.quality_score,
        }, indent=2),
        encoding="utf-8",
    )

    return MERSDEpisode(
        episode_id=ep_id,
        scenario_id=scenario["id"],
        domain=scenario.get("_domain", "robotics"),
        label=label,
        record_paths=record_paths,
        fusion_embedding=fused.vector.tolist(),
        spike_count=len(spikes),
        neuromorphic_energy=metrics.energy_score,
        memory_top_match=query.entries[0][0].label if query.entries else "",
        memory_similarity=float(query.entries[0][1]) if query.entries else 0.0,
        n_agents=n_agents,
        ms_per_agent=round(ms_per_agent, 4),
        seed=seed,
    )


def _keywords_for(scenario: Dict[str, Any]) -> List[str]:
    base = ["robotics", "spectral", "edge computing", "open dataset"]
    if scenario.get("_domain") == "uav_swarm":
        base += ["UAV", "drone swarm", "electronic warfare", "contested environment"]
    else:
        base += ["predictive maintenance", "condition monitoring", "economic impact"]
    return base


def _split_episodes(episodes: List[MERSDEpisode]) -> Dict[str, List[str]]:
    ids = [e.episode_id for e in episodes]
    n = len(ids)
    n_train = int(n * 0.7)
    n_val = int(n * 0.15)
    return {
        "train": ids[:n_train],
        "val": ids[n_train : n_train + n_val],
        "test": ids[n_train + n_val :],
    }


def build_mersd(
    output_dir: Optional[Path] = None,
    *,
    variants_per_scenario: int = 4,
    zip_archive: bool = True,
) -> Tuple[Path, MERSDManifest]:
    """Build full Zenodo-ready MERSD package."""
    import mesie

    out = output_dir or DEFAULT_OUT
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    fusion = MultiModalFusion(config=FusionConfig(output_dim=256))
    runtime = NeuromorphicRuntime(config=RuntimeConfig(n_neurons=128, encoding=EncodingScheme.RATE_CODING))
    memory = SpectralMemory(config=MemoryConfig(vector_dim=256))

    scenarios = _scenario_catalog()
    episodes: List[MERSDEpisode] = []
    record_count = 0

    for sc in scenarios:
        for v in range(variants_per_scenario):
            ep = _build_episode(sc, variant_idx=v, out_dir=out, fusion=fusion, runtime=runtime, memory=memory)
            if ep:
                episodes.append(ep)
                record_count += len(ep.record_paths)
                ep_path = out / "episodes" / f"{ep.episode_id}.json"
                ep_path.parent.mkdir(parents=True, exist_ok=True)
                ep_path.write_text(json.dumps(ep.to_dict(), indent=2), encoding="utf-8")

    splits = _split_episodes(episodes)
    splits_dir = out / "splits"
    splits_dir.mkdir(exist_ok=True)
    for name, ids in splits.items():
        (splits_dir / f"{name}.json").write_text(json.dumps(ids, indent=2), encoding="utf-8")

    labels = {
        "fault_classes": sorted({e.label.fault_state for e in episodes}),
        "jam_states": sorted({e.label.jam_state for e in episodes}),
        "swarm_outcomes": sorted({e.label.swarm_outcome for e in episodes}),
        "robot_classes": sorted({e.label.robot_class for e in episodes}),
        "economic_sectors": sorted({e.label.economic_sector for e in episodes}),
    }
    (out / "labels" / "taxonomy.json").parent.mkdir(parents=True, exist_ok=True)
    (out / "labels" / "taxonomy.json").write_text(json.dumps(labels, indent=2), encoding="utf-8")

    manifest = MERSDManifest(
        version=MERSD_VERSION,
        title="MESIE Edge Robotics Spectral Dataset (MERSD v1.0)",
        description=(
            "Open spectral robotics corpus for edge UAV swarms under EW contest and "
            "industrial ground-robot condition monitoring. Each episode includes MESIE "
            "spectral JSON records, 256-d multi-modal fusion embeddings, neuromorphic "
            "spike features, and swarm/fault/jam labels. Fills gap vs vision-only robotics datasets on Zenodo."
        ),
        episode_count=len(episodes),
        record_count=record_count,
        robot_classes=labels["robot_classes"],
        splits={k: len(v) for k, v in splits.items()},
        keywords=[
            "robotics", "UAV", "drone swarm", "spectral intelligence", "edge robotics",
            "electronic warfare", "predictive maintenance", "condition monitoring",
            "multi-modal fusion", "neuromorphic", "open data", "economic impact",
        ],
        license="Apache-2.0",
        generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        mesie_version=mesie.__version__,
        gaps_filled=[
            "No open EW-contested UAV swarm spectral episode corpus on Zenodo (vision/IMU dominate)",
            "Spectral JSON + fusion embedding + neuromorphic labels in one robotics package",
            "Dual-use: defense edge robotics + industrial economic-impact condition monitoring",
        ],
        zenodo_targets=[
            "High-download categories: robotics dataset, UAV swarm, condition monitoring",
            "Keywords: spectral, edge computing, open dataset — underserved vs RGB-D corpora",
        ],
    )
    (out / "manifest.json").write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")

    _write_zenodo_metadata(out, manifest)
    _write_readme(out, manifest)
    _write_citation(out)
    _write_loader(out)

    if zip_archive:
        zip_path = out.parent / f"MERSD_v{MERSD_VERSION}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in out.rglob("*"):
                if f.is_file():
                    zf.write(f, arcname=str(f.relative_to(out.parent)))
        manifest_path = out / "manifest.json"
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["zip_archive"] = str(zip_path.name)
        manifest_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return out, manifest


def _write_zenodo_metadata(out: Path, manifest: MERSDManifest) -> None:
    meta = {
        "upload_type": "dataset",
        "publication_date": manifest.generated_at[:10],
        "title": manifest.title,
        "description": manifest.description,
        "creators": [{"name": "Medina, Alfredo", "affiliation": "NeuroSwarmAI / IT'S NOT AI LABS"}],
        "keywords": manifest.keywords,
        "license": "Apache-2.0",
        "version": manifest.version,
        "notes": (
            "Upload MERSD_v1.0.0.zip to Zenodo. Target communities: robotics, UAV, "
            "condition monitoring. Economic impact track: ent_factory_vibration episodes."
        ),
        "communities": [{"identifier": "robotics"}, {"identifier": "opendata"}],
        "related_identifiers": [
            {"relation": "isSupplementTo", "identifier": "https://github.com/FreddyCreates/Multi-Element-Spectral-Intelligence-Engine-MESIE-", "resource_type": "software"}
        ],
    }
    (out / "zenodo_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


def _write_readme(out: Path, manifest: MERSDManifest) -> None:
    text = f"""# {manifest.title}

**Version:** {manifest.version}  
**License:** {manifest.license}  
**Generated:** {manifest.generated_at}

## Why this dataset exists

Most open robotics datasets on Zenodo are **vision, LiDAR, or IMU** heavy. **MERSD** fills a gap:

- **Edge UAV swarm** spectral episodes under **electronic warfare** (jam / failover labels)
- **Ground industrial robotics** vibration / condition monitoring (economic impact track)
- **MESIE spectral JSON** records + **256-d fusion embeddings** + **neuromorphic spike** features per episode

## Contents

| Path | Description |
|------|-------------|
| `records/` | MESIE-compatible spectral JSON per episode |
| `embeddings/` | Multi-modal fusion vectors (256-d) |
| `episodes/` | Episode metadata + labels |
| `labels/taxonomy.json` | Fault, jam, swarm outcome classes |
| `splits/` | train / val / test episode IDs |
| `scripts/load_mersd.py` | Minimal Python loader |

## Stats

- Episodes: **{manifest.episode_count}**
- Spectral records: **{manifest.record_count}**
- Robot classes: {', '.join(manifest.robot_classes)}
- Splits: {manifest.splits}

## Quick load

```python
from pathlib import Path
import json

root = Path("zenodo_mersd_v1")
ep = json.loads((root / "episodes" / "mil_ew_contested_jam_v00.json").read_text())
emb = json.loads((root / "embeddings" / ep["episode_id"] + ".json").read_text())
```

Or: `python scripts/load_mersd.py --demo`

## Zenodo upload

1. Upload `MERSD_v{manifest.version}.zip`
2. Paste fields from `zenodo_metadata.json`
3. Communities: robotics, opendata
4. Keywords: {', '.join(manifest.keywords[:6])}, ...

## Citation

See `CITATION.cff`. DOI assigned after Zenodo deposit.

## Honest limits

Software-generated spectral episodes from bundled reference libraries — **not** live combat RF captures or factory floor certified labels. Use for benchmark, fusion research, and edge robotics prototyping.
"""
    (out / "README.md").write_text(text, encoding="utf-8")


def _write_citation(out: Path) -> None:
    cff = f"""cff-version: 1.2.0
title: "MESIE Edge Robotics Spectral Dataset (MERSD v1.0)"
version: {MERSD_VERSION}
license: Apache-2.0
authors:
  - family-names: Medina
    given-names: Alfredo
    affiliation: NeuroSwarmAI
abstract: >-
  Open edge robotics spectral dataset: UAV swarm EW episodes and industrial
  condition monitoring with fusion embeddings and neuromorphic features.
keywords:
  - robotics
  - UAV
  - spectral intelligence
  - edge computing
  - dataset
"""
    (out / "CITATION.cff").write_text(cff, encoding="utf-8")


def _write_loader(out: Path) -> None:
    loader = '''"""Load MERSD episodes — Zenodo robotics spectral dataset."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterator, List

def iter_episodes(root: Path) -> Iterator[Dict[str, Any]]:
    for p in sorted((root / "episodes").glob("*.json")):
        yield json.loads(p.read_text(encoding="utf-8"))

def load_embedding(root: Path, episode_id: str) -> Dict[str, Any]:
    return json.loads((root / "embeddings" / f"{episode_id}.json").read_text(encoding="utf-8"))

def load_records(root: Path, episode: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [json.loads((root / rp).read_text(encoding="utf-8")) for rp in episode["record_paths"]]

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--demo", action="store_true")
    args = p.parse_args()
    root = Path(args.root)
    for i, ep in enumerate(iter_episodes(root)):
        if i >= 3 and args.demo:
            break
        print(ep["episode_id"], ep["label"]["fault_state"], ep["label"]["jam_state"])
'''
    scripts = out / "scripts"
    scripts.mkdir(exist_ok=True)
    (scripts / "load_mersd.py").write_text(loader, encoding="utf-8")