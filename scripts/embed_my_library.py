#!/usr/bin/env python3
"""Embed a folder of spectral JSON files into a searchable index.

Usage:
    python scripts/embed_my_library.py <input_folder> [-o output_path]

Each JSON file in the input folder should contain a spectral record with at
minimum 'frequency' and 'amplitude' arrays (or a 'components' list). Files
that cannot be parsed are skipped with a warning.

The output is a JSON index file mapping record IDs to their embeddings,
suitable for use with SpectralRetriever or direct nearest-neighbor search.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# Ensure the repository root is importable when running from scripts/
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from mesie.embeddings import SpectralVectorizer  # noqa: E402
from mesie.io.loaders import load_record  # noqa: E402


def discover_json_files(folder: Path) -> list[Path]:
    """Recursively find all .json files in a folder."""
    return sorted(folder.rglob("*.json"))


def embed_library(
    input_folder: Path,
    output_path: Path,
    verbose: bool = True,
) -> dict:
    """Embed all spectral JSON files in a folder.

    Returns:
        Dictionary with record IDs as keys and embedding lists as values.
    """
    vectorizer = SpectralVectorizer()
    json_files = discover_json_files(input_folder)

    if not json_files:
        print(f"No .json files found in {input_folder}")
        return {}

    if verbose:
        print(f"Found {len(json_files)} JSON file(s) in {input_folder}")

    index: dict = {}
    skipped = 0
    t0 = time.perf_counter()

    for filepath in json_files:
        try:
            with open(filepath) as f:
                payload = json.load(f)

            # Use filename stem as fallback record_id
            if isinstance(payload, dict) and "record_id" not in payload:
                payload["record_id"] = filepath.stem

            record = load_record(payload)
            embedding = vectorizer.transform(record)

            index[record.record_id] = {
                "embedding": embedding.tolist(),
                "source_file": str(filepath.relative_to(input_folder)),
            }
        except Exception as exc:  # noqa: BLE001
            skipped += 1
            if verbose:
                print(f"  [SKIP] {filepath.name}: {exc}")

    elapsed = time.perf_counter() - t0

    if verbose:
        print(f"Embedded {len(index)} record(s), skipped {skipped}, in {elapsed:.3f}s")

    # Write index
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(
            {
                "mesie_version": "spectral_index_v1",
                "embedding_dim": vectorizer.embedding_dim,
                "records": index,
            },
            f,
            indent=2,
        )

    if verbose:
        print(f"Index written to {output_path}")

    return index


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Embed spectral JSON files into a searchable index.",
    )
    parser.add_argument(
        "input_folder",
        type=Path,
        help="Folder containing spectral JSON files to embed.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("library/my_spectral_index.json"),
        help="Output path for the index file (default: library/my_spectral_index.json).",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress output.",
    )

    args = parser.parse_args()

    if not args.input_folder.is_dir():
        print(f"Error: {args.input_folder} is not a directory.", file=sys.stderr)
        sys.exit(1)

    embed_library(args.input_folder, args.output, verbose=not args.quiet)


if __name__ == "__main__":
    main()
