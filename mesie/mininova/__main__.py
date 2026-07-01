"""CLI: python -m mesie.mininova"""

from __future__ import annotations

import argparse
import json

from mesie.mininova.sphere import MiniNovaSphere


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MININOVA — mini sphere on NOVAMINI")
    parser.add_argument("text", nargs="?", help="Process text through MININOVA")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--satellites", action="store_true", help="Activate timer satellites")
    args = parser.parse_args(argv)

    sphere = MiniNovaSphere()
    if args.status:
        print(json.dumps(sphere.status(), indent=2))
        return 0

    if args.satellites:
        sphere.activate_satellites()
        print("MININOVA satellites active. Ctrl+C to stop.")
        try:
            import time
            while True:
                time.sleep(10)
                print(json.dumps(sphere.micro.fleet_status(), indent=2))
        except KeyboardInterrupt:
            sphere.stop_satellites()
        return 0

    text = args.text or "What is MININOVA around MESIE?"
    resp = sphere.process(text)
    print(resp.spoken)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())