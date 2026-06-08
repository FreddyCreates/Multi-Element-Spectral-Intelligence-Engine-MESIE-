"""MESIE command-line interface.

Default: terminal + AI copilot (maesi). Also: corpus, REPL, bootstrap.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def cmd_load_corpus(args: argparse.Namespace) -> None:
    from mesie.io.corpus import SpectralCorpus

    path = Path(args.path)
    print(f"Loading spectral corpus from: {path}")
    corpus = SpectralCorpus.from_directory(
        path,
        recursive=not args.no_recursive,
        skip_errors=args.skip_errors,
    )
    print(f"Loaded {len(corpus)} records")
    if args.list:
        for record_id in corpus.record_ids:
            print(f"  - {record_id}")


def cmd_info(args: argparse.Namespace) -> None:
    from mesie.io.loaders import load_record

    record = load_record(args.file)
    print(f"Record ID:      {record.record_id}")
    print(f"Components:     {len(record.components)}")
    print(f"Representation: {record.representation}")
    for comp in record.components:
        freq_range = f"[{comp.frequency[0]:.2f}, {comp.frequency[-1]:.2f}]"
        print(f"  - {comp.name}: {len(comp.frequency)} points, freq {freq_range}")


def cmd_repl(args: argparse.Namespace) -> None:
    import code

    from mesie.sdk import SpectralIntelligenceSDK

    engine = SpectralIntelligenceSDK()
    banner = (
        f"MESIE Spectral Intelligence Engine v{engine.version}\n"
        f"SDK available as 'engine'. Type help(engine) for usage.\n"
    )
    local_vars = {"engine": engine, "SpectralIntelligenceSDK": SpectralIntelligenceSDK}
    if args.corpus:
        corpus = engine.load_corpus(args.corpus, skip_errors=True)
        print(f"Corpus loaded: {len(corpus)} records from {args.corpus}")
        local_vars["corpus"] = corpus
    code.interact(banner=banner, local=local_vars)


def cmd_terminal(args: argparse.Namespace) -> int:
    from mesie.sdk.terminal_copilot import run_copilot_terminal

    return run_copilot_terminal(tier=args.tier)


def cmd_bootstrap(args: argparse.Namespace) -> int:
    from mesie.release.bootstrap import bootstrap

    bootstrap(install_profile=args.install_profile)
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="mesie",
        description="MESIE — Multi-Element Spectral Intelligence Engine",
    )
    subparsers = parser.add_subparsers(dest="command")

    p_terminal = subparsers.add_parser(
        "terminal",
        help="Terminal + AI copilot (default experience)",
    )
    p_terminal.add_argument(
        "--tier",
        choices=["sovereign", "samgov", "research"],
        default="sovereign",
    )
    p_terminal.set_defaults(func=cmd_terminal)

    p_boot = subparsers.add_parser("bootstrap", help="Install terminal bootstrap to ~/.mesie")
    p_boot.add_argument("--install-profile", action="store_true")
    p_boot.set_defaults(func=cmd_bootstrap)

    p_corpus = subparsers.add_parser("load-corpus", help="Load a spectral library")
    p_corpus.add_argument("path")
    p_corpus.add_argument("--no-recursive", action="store_true")
    p_corpus.add_argument("--skip-errors", action="store_true")
    p_corpus.add_argument("--list", action="store_true")
    p_corpus.set_defaults(func=cmd_load_corpus)

    p_info = subparsers.add_parser("info", help="Display spectral record info")
    p_info.add_argument("file")
    p_info.set_defaults(func=cmd_info)

    p_repl = subparsers.add_parser("repl", help="Researcher Python REPL")
    p_repl.add_argument("--corpus")
    p_repl.set_defaults(func=cmd_repl)

    args = parser.parse_args(argv)
    if not args.command:
        sys.exit(cmd_terminal(argparse.Namespace(tier="sovereign")))

    result = args.func(args)
    if isinstance(result, int):
        sys.exit(result)


if __name__ == "__main__":
    main()