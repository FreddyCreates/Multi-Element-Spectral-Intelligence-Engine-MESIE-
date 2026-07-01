#!/usr/bin/env python3
"""Run NOVA micro-agent satellite fleet — production lab background workers."""

from __future__ import annotations

import argparse
import json
import sys
import time

from mesie.nova.sphere import NovaSphere


def main() -> int:
    parser = argparse.ArgumentParser(description="NOVA micro satellite fleet")
    parser.add_argument("--interval", type=float, default=5.0, help="Status print interval (seconds)")
    parser.add_argument("--once", action="store_true", help="Print fleet status once and exit")
    args = parser.parse_args()

    from mesie.agentic.micro import NOVA_ORG_SIZE, organization_status

    sphere = NovaSphere(session_id="lab-micro-fleet")
    sphere.activate_satellites()
    print(f"NOVA organization: {NOVA_ORG_SIZE} careers activated", file=sys.stderr)

    if args.once:
        print(json.dumps(organization_status(sphere.micro), indent=2))
        sphere.stop_satellites()
        return 0

    print("Micro satellite fleet active. Ctrl+C to stop.", file=sys.stderr)
    try:
        while True:
            print(json.dumps(organization_status(sphere.micro), indent=2))
            time.sleep(args.interval)
    except KeyboardInterrupt:
        sphere.stop_satellites()
        print("Stopped.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())