"""Command-line interface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .runner import run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate MESIE against external public datasets")
    subparsers = parser.add_subparsers(dest="command", required=True)
    command = subparsers.add_parser("run", help="download, evaluate, and report")
    command.add_argument("--config", type=Path, required=True)
    command.add_argument(
        "--mesie-root",
        type=Path,
        default=Path.cwd(),
        help="MESIE checkout root (defaults to the current directory)",
    )
    command.add_argument("--output-dir", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run(args.config, args.mesie_root, args.output_dir)
    print(json.dumps({
        "conclusion": result["conclusion"],
        "json": result["output_json"],
        "markdown": result["output_markdown"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
