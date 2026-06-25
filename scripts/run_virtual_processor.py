#!/usr/bin/env python3
"""Start MESIE Virtual Processor HTTP server (port 8750)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("mesie.processor.server:app", host="127.0.0.1", port=8750, reload=False)