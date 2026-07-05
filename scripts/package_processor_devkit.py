#!/usr/bin/env python3
"""Package Virtual Processor devkit zip for distribution."""

from __future__ import annotations

import json
import sys

from mesie.processor.release import package_devkit_zip, run_processor_release


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--light", action="store_true", help="Skip heavy release if memory pressure")
    args = parser.parse_args()

    if args.light:
        from mesie.ml.research_packet_forge import refresh_release_from_cache
        from mesie.server.coherence_engine import should_run_heavy_release

        refresh_release_from_cache(heavy=should_run_heavy_release())
        zip_path = package_devkit_zip()
        print(json.dumps({"ready": True, "mode": "light", "zip": str(zip_path)}, indent=2))
        return 0

    rep = run_processor_release(export=True)
    zip_path = package_devkit_zip()
    print(json.dumps({"ready": rep.ready, "zip": str(zip_path)}, indent=2))
    return 0 if rep.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())