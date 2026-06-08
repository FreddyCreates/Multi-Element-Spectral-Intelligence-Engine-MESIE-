"""Cluster edge fabric — interior DC + OTA mesh + STAR swarm."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.production.cluster_edge import ClusterEdgeFabric


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes", type=int, default=4)
    parser.add_argument("--agents", type=int, default=1000)
    args = parser.parse_args()

    fabric = ClusterEdgeFabric(n_nodes=args.nodes, n_agents=args.agents)
    path = fabric.export()
    report = fabric.run()

    print("=== MESIE Cluster Edge ===")
    print(f"Nodes: {report.n_nodes} | DC shards: {report.interior_dc_shards}")
    print(f"OTA ok: {report.ota_mesh_ok} | ms/agent: {report.cluster_ms_per_agent}")
    print(f"Cloud required: {report.cloud_required} | OK: {report.ok}")
    print(f"Report: {path}")
    sys.exit(0 if report.ok else 1)


if __name__ == "__main__":
    main()