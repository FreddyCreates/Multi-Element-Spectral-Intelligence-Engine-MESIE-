"""VP-MESH virtual processor network mesh tests."""

from __future__ import annotations

from mesie.processor.mesh_protocol import (
    MESH_VERSION,
    VirtualProcessorMeshNode,
    VPMeshFrame,
    MeshMessageType,
    run_mesh_soak,
)


def test_vp_mesh_frame_roundtrip():
    frame = VPMeshFrame(MeshMessageType.BEACON, "node-test", 1, {"healthy": True})
    restored = VPMeshFrame.from_bytes(frame.to_bytes())
    assert restored.node_id == "node-test"
    assert restored.msg_type == MeshMessageType.BEACON


def test_vp_mesh_pulse():
    node = VirtualProcessorMeshNode(processor_url="http://127.0.0.1:8750")
    rep = node.pulse(ota_nodes=3)
    node.stop()
    assert rep.ota_mesh_ok is True
    assert rep.beacons_sent >= 1
    assert MESH_VERSION.startswith("1.")


def test_vp_mesh_soak():
    out = run_mesh_soak(n_nodes=3, rounds=2)
    assert out["protocol"] == "VP-MESH"
    assert len(out["pulses"]) == 2