#!/usr/bin/env python3
"""Never-stop persistent virtual MESIE servers."""

from __future__ import annotations

from mesie.server.persistent_supervisor import main

if __name__ == "__main__":
    raise SystemExit(main())