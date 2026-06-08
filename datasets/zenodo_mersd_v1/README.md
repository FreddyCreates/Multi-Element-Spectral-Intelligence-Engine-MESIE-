# MESIE Edge Robotics Spectral Dataset (MERSD v1.0)

**Version:** 1.0.0  
**License:** Apache-2.0  
**Generated:** 2026-06-08T23:07:20Z

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

- Episodes: **48**
- Spectral records: **64**
- Robot classes: aerial_swarm, mobile_manipulator
- Splits: {'train': 33, 'val': 7, 'test': 8}

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

1. Upload `MERSD_v1.0.0.zip`
2. Paste fields from `zenodo_metadata.json`
3. Communities: robotics, opendata
4. Keywords: robotics, UAV, drone swarm, spectral intelligence, edge robotics, electronic warfare, ...

## Citation

See `CITATION.cff`. DOI assigned after Zenodo deposit.

## Honest limits

Software-generated spectral episodes from bundled reference libraries — **not** live combat RF captures or factory floor certified labels. Use for benchmark, fusion research, and edge robotics prototyping.
