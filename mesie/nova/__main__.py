"""CLI: python -m mesie.nova"""

from __future__ import annotations

import argparse
import json
import sys

from mesie.nova.release import run_nova_release
from mesie.nova.sphere import NovaSphere


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NOVA Sphere — MESIE intelligence shell")
    parser.add_argument("text", nargs="?", help="Process text through NOVA sphere")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--release", action="store_true", help="Run full production release gate")
    parser.add_argument("--satellites", action="store_true", help="Activate timer satellites (demo 5s)")
    args = parser.parse_args(argv)

    if args.release:
        rep = run_nova_release()
        print(json.dumps(rep.to_dict(), indent=2))
        return 0 if rep.ready else 1

    sphere = NovaSphere()
    if args.status:
        print(json.dumps(sphere.status(), indent=2))
        return 0

    if args.satellites:
        sphere.activate_satellites()
        print("Satellites activated. Press Ctrl+C to stop.")
        try:
            import time
            while True:
                time.sleep(5)
                print(json.dumps(sphere.micro.fleet_status(), indent=2))
        except KeyboardInterrupt:
            sphere.stop_satellites()
        return 0

    text = args.text or "What is the NOVA sphere around MESIE?"
    resp = sphere.process(text)
    print(resp.spoken_summary)
    if "--json" in sys.argv:
        print(json.dumps(resp.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())