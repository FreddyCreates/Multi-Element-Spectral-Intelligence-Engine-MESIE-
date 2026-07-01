#!/usr/bin/env python3
"""Package Virtual Processor devkit zip for distribution."""

from __future__ import annotations

import json
import sys

from mesie.processor.release import package_devkit_zip, run_processor_release


def main() -> int:
    rep = run_processor_release(export=True)
    zip_path = package_devkit_zip()
    print(json.dumps({"ready": rep.ready, "zip": str(zip_path)}, indent=2))
    return 0 if rep.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())