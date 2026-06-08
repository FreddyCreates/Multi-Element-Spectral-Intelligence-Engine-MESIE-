"""Production CLI for sovereign field routing — airgapped, alias-based."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.sovereign import get_field_access_engine


def cmd_list(args: argparse.Namespace) -> int:
    fa = get_field_access_engine()
    if args.nodes:
        payload = fa.nodes(args.role)
        print(json.dumps(payload, indent=2))
        return 0
    if args.presets:
        print(json.dumps(fa.list_presets(), indent=2))
        return 0
    table = fa.route_table()
    print(f"Field router v{table['router_version']} | nodes={table['nodes']} | aliases={table['aliases']}")
    for p in fa.list_presets():
        mark = "ok" if p["ok"] else "FAIL"
        print(f"  [{mark}] {p['preset_id']:22} {p['from']:8} → {p['to']:8}  {p['hops']} hops  {p['latency_ms']:.1f} ms")
    return 0


def cmd_route(args: argparse.Namespace) -> int:
    fa = get_field_access_engine()
    route = fa.route(args.source, args.destination, policy=args.policy)
    out = route.to_dict()
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        if not route.ok:
            print(f"ROUTE FAIL: {route.error}")
            return 1
        print(f"route {route.route_id}")
        print(f"  {route.source} → {route.destination}")
        print(f"  resolved: {route.resolved_source} → {route.resolved_destination}")
        print(f"  hops ({len(route.hops)}): {' → '.join(route.hops)}")
        print(f"  access: {route.access_mode} | policy: {route.policy}")
        print(f"  latency: {route.total_latency_ms:.2f} ms | ladder_hops: {route.ladder_hops}")
    return 0 if route.ok else 1


def cmd_health(_: argparse.Namespace) -> int:
    fa = get_field_access_engine()
    print(json.dumps(fa.health(), indent=2))
    return 0 if fa.health().get("ok") else 1


def main() -> int:
    p = argparse.ArgumentParser(description="Sovereign field router — airgapped world-computer mesh")
    sub = p.add_subparsers(dest="cmd", required=True)

    ls = sub.add_parser("list", help="List presets, nodes, or route table")
    ls.add_argument("--presets", action="store_true", help="JSON preset routes")
    ls.add_argument("--nodes", action="store_true", help="JSON field nodes")
    ls.add_argument("--role", default=None, help="Filter nodes by role")
    ls.set_defaults(func=cmd_list)

    rt = sub.add_parser("route", help="Route between nodes (aliases: ground, world, leo0, geo)")
    rt.add_argument("source")
    rt.add_argument("destination")
    rt.add_argument("--policy", default="shortest", choices=["shortest", "ladder_only", "orbital_preferred"])
    rt.add_argument("--json", action="store_true")
    rt.set_defaults(func=cmd_route)

    h = sub.add_parser("health", help="Router health check")
    h.set_defaults(func=cmd_health)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())