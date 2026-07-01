#!/usr/bin/env python3
"""NOVA Runtime — never-stop production supervisor.

Starts 55 micro careers (real tasks) + robotics_satellite swarm.
Enterprise: one process, watchdog restarts, feed on disk.

  python scripts/run_nova_runtime.py
  python scripts/run_nova_runtime.py --once   # snapshot and exit
"""

from __future__ import annotations

import argparse
import json
import sys

from mesie.agentic.micro.runtime_supervisor import NovaRuntimeSupervisor


def main() -> int:
    parser = argparse.ArgumentParser(description="NOVA never-stop runtime supervisor")
    parser.add_argument("--once", action="store_true", help="Start, snapshot once, exit")
    parser.add_argument("--watchdog-s", type=float, default=30.0)
    args = parser.parse_args()

    sup = NovaRuntimeSupervisor(watchdog_interval_s=args.watchdog_s)
    if args.once:
        snap = sup.start()
        print(json.dumps(snap, indent=2))
        if sup._robotics_proc:
            sup._robotics_proc.terminate()
        if sup._sphere:
            sup._sphere.stop_satellites()
        return 0

    sup.run_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())