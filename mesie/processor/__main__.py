"""CLI: python -m mesie.processor --serve"""

from __future__ import annotations

import argparse
import json
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MESIE Virtual Processor — HTTP compute server")
    parser.add_argument("--serve", action="store_true", help="Start HTTP server on port 8750")
    parser.add_argument("--port", type=int, default=8750, help="HTTP port (default 8750)")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default 127.0.0.1)")
    parser.add_argument("--status", action="store_true", help="Print status JSON and exit")
    parser.add_argument("--export-manifest", metavar="PATH", nargs="?", const="default", help="Write manifest JSON")
    args = parser.parse_args(argv)

    from mesie.processor.virtual_processor import VirtualProcessor

    proc = VirtualProcessor()

    if args.export_manifest:
        from mesie.processor.virtual_processor import DEFAULT_MANIFEST_PATH

        path = DEFAULT_MANIFEST_PATH if args.export_manifest == "default" else args.export_manifest
        out = proc.export_manifest(path)
        print(json.dumps({"ok": True, "path": str(out)}, indent=2))
        return 0

    if args.status:
        print(json.dumps(proc.status(), indent=2))
        return 0

    if args.serve:
        try:
            import uvicorn
        except ImportError:
            print("uvicorn required: pip install mesie[server]", file=sys.stderr)
            return 1
        uvicorn.run("mesie.processor.server:app", host=args.host, port=args.port, reload=False)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
