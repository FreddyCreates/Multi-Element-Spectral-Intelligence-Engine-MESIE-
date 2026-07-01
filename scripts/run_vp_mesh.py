#!/usr/bin/env python3
"""VP-MESH — Virtual Processor Network Mesh (pulse, soak, or supervisor)."""

from __future__ import annotations

import argparse
import json
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="VP-MESH virtual processor network mesh")
    parser.add_argument("--pulse", action="store_true", help="Single mesh pulse")
    parser.add_argument("--soak", action="store_true", help="Run mesh soak benchmark")
    parser.add_argument("--supervise", action="store_true", help="Never-stop mesh supervisor")
    parser.add_argument("--processor-url", default="http://127.0.0.1:8750")
    parser.add_argument("--nodes", type=int, default=4)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--interval", type=float, default=60.0)
    args = parser.parse_args()

    if args.supervise:
        from mesie.processor.mesh_supervisor import run_mesh_supervisor

        run_mesh_supervisor(interval_s=args.interval, processor_url=args.processor_url)
        return 0

    if args.soak:
        from mesie.processor.mesh_protocol import run_mesh_soak

        out = run_mesh_soak(n_nodes=args.nodes, rounds=args.rounds)
        path = __import__("pathlib").Path(__file__).resolve().parents[1] / "deliverables" / "processor" / "VP_MESH_SOAK.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(json.dumps({**out, "path": str(path)}, indent=2))
        return 0 if out.get("ok") else 1

    from mesie.processor.mesh_protocol import VirtualProcessorMeshNode

    node = VirtualProcessorMeshNode(processor_url=args.processor_url)
    rep = node.pulse(ota_nodes=args.nodes)
    print(json.dumps(rep.to_dict(), indent=2))
    node.stop()
    return 0 if rep.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())