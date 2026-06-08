"""Load MERSD episodes — Zenodo robotics spectral dataset."""
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
