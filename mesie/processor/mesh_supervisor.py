"""VP-MESH supervisor — background mesh pulses (never-stop fabric)."""

from __future__ import annotations

import time
from pathlib import Path

from mesie.processor.mesh_protocol import VirtualProcessorMeshNode

ROOT = Path(__file__).resolve().parents[2]


def run_mesh_supervisor(*, interval_s: float = 60.0, processor_url: str = "http://127.0.0.1:8750") -> None:
    node = VirtualProcessorMeshNode(processor_url=processor_url)
    node.start()
    cycles = 0
    print(f"[vp-mesh] interval={interval_s}s node={node.node_id}")
    try:
        while True:
            cycles += 1
            rep = node.pulse()
            print(
                f"[vp-mesh] cycle={cycles} peers={rep.peers_seen} "
                f"ota_rx={rep.ota_frames_received} local_route={rep.routed_local} "
                f"latency_ms={rep.latency_ms}",
                flush=True,
            )
            time.sleep(interval_s)
    except KeyboardInterrupt:
        node.stop()
        print("[vp-mesh] stopped")