"""MESIE command-line interface.

Provides a thin CLI for the Spectral Intelligence Engine, including
corpus loading, record inspection, and interactive REPL access.

Usage:
    mesie load-corpus /path/to/library
    mesie info record.json
    mesie repl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def cmd_load_corpus(args: argparse.Namespace) -> None:
    """Load a spectral corpus directory and print summary."""
    from mesie.io.corpus import SpectralCorpus

    path = Path(args.path)
    print(f"Loading spectral corpus from: {path}")

    corpus = SpectralCorpus.from_directory(
        path,
        recursive=not args.no_recursive,
        skip_errors=args.skip_errors,
    )

    print(f"✓ Loaded {len(corpus)} records")
    if args.list:
        for record_id in corpus.record_ids:
            print(f"  • {record_id}")


def cmd_info(args: argparse.Namespace) -> None:
    """Display information about a spectral record."""
    from mesie.io.loaders import load_record

    record = load_record(args.file)
    print(f"Record ID:      {record.record_id}")
    print(f"Components:     {len(record.components)}")
    print(f"Representation: {record.representation}")
    for comp in record.components:
        freq_range = f"[{comp.frequency[0]:.2f}, {comp.frequency[-1]:.2f}]"
        print(f"  • {comp.name}: {len(comp.frequency)} points, freq {freq_range}")


def cmd_repl(args: argparse.Namespace) -> None:
    """Start an interactive REPL with the SDK pre-loaded."""
    import code

    from mesie.sdk import SpectralIntelligenceSDK

    engine = SpectralIntelligenceSDK()
    banner = (
        f"MESIE Spectral Intelligence Engine v{engine.version}\n"
        f"SDK available as 'engine'. Type help(engine) for usage.\n"
    )
    local_vars = {"engine": engine, "SpectralIntelligenceSDK": SpectralIntelligenceSDK}

    # Pre-load corpus if path was given
    if args.corpus:
        corpus = engine.load_corpus(args.corpus, skip_errors=True)
        print(f"Corpus loaded: {len(corpus)} records from {args.corpus}")
        local_vars["corpus"] = corpus

    code.interact(banner=banner, local=local_vars)


def cmd_harness(args: argparse.Namespace) -> None:
    """Run local/edge/hybrid harness checks from one control-plane command."""
    from mesie.harnesses import run_control_plane

    report = run_control_plane(
        mode=args.mode,
        profile=args.profile,
        operation=args.operation,
        edge_url=args.edge_url,
        edge_api_key=args.edge_api_key,
    )
    print(json.dumps(report, indent=2))


def main(argv: list[str] | None = None) -> None:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="mesie",
        description="MESIE — Multi-Element Spectral Intelligence Engine",
    )
    subparsers = parser.add_subparsers(dest="command")

    # load-corpus
    p_corpus = subparsers.add_parser(
        "load-corpus",
        help="Load a spectral library from a directory",
    )
    p_corpus.add_argument("path", help="Path to spectral library directory")
    p_corpus.add_argument("--no-recursive", action="store_true", help="Don't search subdirectories")
    p_corpus.add_argument("--skip-errors", action="store_true", help="Skip unloadable files")
    p_corpus.add_argument("--list", action="store_true", help="List all record IDs")
    p_corpus.set_defaults(func=cmd_load_corpus)

    # info
    p_info = subparsers.add_parser(
        "info",
        help="Display info about a spectral record file",
    )
    p_info.add_argument("file", help="Path to a spectral record (JSON or CSV)")
    p_info.set_defaults(func=cmd_info)

    # repl
    p_repl = subparsers.add_parser(
        "repl",
        help="Start an interactive REPL with the SDK pre-loaded",
    )
    p_repl.add_argument("--corpus", help="Path to corpus directory to pre-load")
    p_repl.set_defaults(func=cmd_repl)

    # harness
    p_harness = subparsers.add_parser(
        "harness",
        help="Run shippable harness checks (local, edge, or hybrid)",
    )
    p_harness.add_argument("--mode", choices=["local", "edge", "hybrid"], default="local")
    p_harness.add_argument("--operation", choices=["health", "startup"], default="startup")
    p_harness.add_argument("--profile", choices=["local", "dev", "prod"], default="local")
    p_harness.add_argument("--edge-url", default="http://127.0.0.1:8787")
    p_harness.add_argument("--edge-api-key", default=None)
    p_harness.set_defaults(func=cmd_harness)

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
