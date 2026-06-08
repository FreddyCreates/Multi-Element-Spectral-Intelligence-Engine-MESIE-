"""maesi — unified MAESI terminal + AI copilot entry (pip install default)."""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="maesi",
        description="MAESI SDK — terminal + sovereign/Sam.gov/research AI copilot",
    )
    parser.add_argument("--tier", choices=["sovereign", "samgov", "research"], default="sovereign")
    parser.add_argument("--bootstrap", action="store_true", help="Re-run install bootstrap")
    parser.add_argument("--install-profile", action="store_true", help="Hook PowerShell profile")
    args = parser.parse_args(argv)

    if args.bootstrap or args.install_profile:
        from mesie.release.bootstrap import bootstrap

        bootstrap(install_profile=args.install_profile)
        if args.bootstrap and not args.install_profile:
            return 0

    from mesie.sdk.terminal_copilot import run_copilot_terminal

    return run_copilot_terminal(tier=args.tier)


if __name__ == "__main__":
    raise SystemExit(main())