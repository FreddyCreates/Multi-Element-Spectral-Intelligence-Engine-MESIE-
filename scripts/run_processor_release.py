#!/usr/bin/env python3
"""Virtual Processor production release gate + devkit export."""

from __future__ import annotations

import json
import sys

from mesie.processor.release import export_devkit, run_processor_release


def main() -> int:
    rep = run_processor_release(export=True)
    devkit = export_devkit()
    print(json.dumps({"release": rep.to_dict(), "devkit": str(devkit)}, indent=2))
    return 0 if rep.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())