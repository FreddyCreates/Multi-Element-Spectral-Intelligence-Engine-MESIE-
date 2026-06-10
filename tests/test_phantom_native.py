"""Tests for phantom_native — Sovereign Native Stack (Phantom-MESIE Integration)."""

import math

import pytest

from phantom_native.sovereign_tensor import SovereignTensor
from phantom_native.neurocore import SovereignNeuroCore
from phantom_native.swarm_runtime import (
    ExecutionReceipt,
    SovereignSwarmRuntime,
    SovereignVault,
    ShadowWireEnvelope,
)


# ==================================================================
# SovereignTensor tests
# ==================================================================


class TestSovereignTensor:
    def test_creation_basic(self):
        t = SovereignTensor([1.0, 2.0, 3.0], (3,))
        assert t.shape == (3,)
        assert t.data == [1.0, 2.0, 3.0]
        assert t.size == 3

    def test_creation_2d(self):
        t = SovereignTensor([1.0, 2.0, 3.0, 4.0], (2, 2))
        assert t.shape == (2, 2)
        assert t.size == 4

    def test_shape_mismatch_raises(self):
        with pytest.raises(ValueError, match="Shape / data mismatch"):
            SovereignTensor([1.0, 2.0], (3,))

    def test_zeros_and_ones(self):
        z = SovereignTensor.zeros((4,))
        assert z.data == [0.0, 0.0, 0.0, 0.0]
        o = SovereignTensor.ones((2, 3))
        assert o.size == 6
        assert all(x == 1.0 for x in o.data)

    def test_add(self):
        a = SovereignTensor([1.0, 2.0], (2,))
        b = SovereignTensor([3.0, 4.0], (2,))
        c = a.add(b)
        assert c.data == [4.0, 6.0]

    def test_add_shape_mismatch(self):
        a = SovereignTensor([1.0, 2.0], (2,))
        b = SovereignTensor([1.0, 2.0, 3.0], (3,))
        with pytest.raises(ValueError, match="Shape mismatch"):
            a.add(b)

    def test_sub(self):
        a = SovereignTensor([5.0, 3.0], (2,))
        b = SovereignTensor([1.0, 2.0], (2,))
        c = a.sub(b)
        assert c.data == [4.0, 1.0]

    def test_scale(self):
        t = SovereignTensor([2.0, 4.0], (2,))
        s = t.scale(0.5)
        assert s.data == [1.0, 2.0]

    def test_dot(self):
        a = SovereignTensor([1.0, 2.0, 3.0], (3,))
        b = SovereignTensor([4.0, 5.0, 6.0], (3,))
        assert a.dot(b) == pytest.approx(32.0)

    def test_matmul(self):
        # 2x2 identity-like matmul
        a = SovereignTensor([1.0, 0.0, 0.0, 1.0], (2, 2))
        b = SovereignTensor([5.0, 6.0, 7.0, 8.0], (2, 2))
        c = a.matmul(b)
        assert c.shape == (2, 2)
        # resonance_score defaults to 1.0 * 1.0 = 1.0
        assert c.data == pytest.approx([5.0, 6.0, 7.0, 8.0])

    def test_matmul_with_resonance(self):
        a = SovereignTensor(
            [1.0, 0.0, 0.0, 1.0], (2, 2), {"resonance": 0.5}
        )
        b = SovereignTensor(
            [2.0, 2.0, 2.0, 2.0], (2, 2), {"resonance": 2.0}
        )
        c = a.matmul(b)
        # resonance = 0.5 * 2.0 = 1.0, so same as plain matmul
        assert c.data == pytest.approx([2.0, 2.0, 2.0, 2.0])

    def test_norm(self):
        t = SovereignTensor([3.0, 4.0], (2,))
        assert t.norm() == pytest.approx(5.0)

    def test_to_bytes_roundtrip(self):
        t = SovereignTensor([1.5, 2.5, 3.5], (3,))
        raw = t.to_bytes()
        t2 = SovereignTensor.from_bytes(raw, (3,))
        assert t2.data == pytest.approx(t.data, rel=1e-5)

    def test_from_mesie_component(self):
        component = {
            "frequency": [1.0, 2.0, 3.0],
            "amplitude": [0.5, 1.0, 1.5],
            "element_weight": 0.8,
            "node_id": "node_42",
        }
        t = SovereignTensor.from_mesie_component(component)
        assert t.shape == (3,)
        assert t.data == [0.5, 1.0, 1.5]
        assert t.resonance_score == 0.8
        assert t.lineage == "node_42"

    def test_from_mesie_component_empty(self):
        t = SovereignTensor.from_mesie_component({})
        assert t.shape == (1,)
        assert t.data == [0.0]

    def test_quantize_int8(self):
        t = SovereignTensor([1.0, -0.5, 0.25], (3,))
        q = t.quantize_int8()
        assert "quant_scale" in q.spectral_meta
        # All values should be in [-127, 127] range
        for v in q.data:
            assert -127.0 <= v <= 127.0

    def test_quantize_dequantize_roundtrip(self):
        t = SovereignTensor([1.0, -0.5, 0.25], (3,))
        q = t.quantize_int8()
        d = q.dequantize()
        # Expect some quantization error but close
        for orig, recovered in zip(t.data, d.data):
            assert recovered == pytest.approx(orig, abs=0.02)

    def test_repr(self):
        t = SovereignTensor([1.0, 2.0], (2,))
        r = repr(t)
        assert "SovereignTensor" in r
        assert "shape=(2,)" in r


# ==================================================================
# SovereignNeuroCore tests
# ==================================================================


class TestSovereignNeuroCore:
    def test_creation_defaults(self):
        core = SovereignNeuroCore()
        assert core.d_model == 128
        assert core.n_heads == 8
        assert core.memory_cap == 32
        assert core.memory_size() == 0

    def test_creation_custom_config(self):
        core = SovereignNeuroCore({"d_model": 64, "n_heads": 4, "memory_cap": 16})
        assert core.d_model == 64
        assert core.n_heads == 4
        assert core.memory_cap == 16

    def test_forward_produces_output(self):
        core = SovereignNeuroCore({"d_model": 16})
        tensor = SovereignTensor([1.0, 2.0, 3.0, 4.0], (4,))
        out = core.forward(tensor)
        assert out.shape == (4,)
        assert len(out.data) == 4
        # Output should not be all zeros (unless input is zero)
        assert any(x != 0.0 for x in out.data)

    def test_forward_updates_taurus_memory(self):
        core = SovereignNeuroCore({"d_model": 8, "memory_cap": 5})
        tensor = SovereignTensor([1.0, 2.0], (2,))

        for _ in range(7):
            core.forward(tensor)

        # Memory should be capped at 5
        assert core.memory_size() == 5

    def test_clear_memory(self):
        core = SovereignNeuroCore({"d_model": 8})
        tensor = SovereignTensor([1.0], (1,))
        core.forward(tensor)
        assert core.memory_size() == 1
        core.clear_memory()
        assert core.memory_size() == 0

    def test_recall_recent(self):
        core = SovereignNeuroCore({"d_model": 8, "memory_cap": 10})
        for i in range(5):
            core.forward(SovereignTensor([float(i)], (1,)))
        recent = core.recall_recent(3)
        assert len(recent) == 3

    def test_resonance_attention_sums_to_one(self):
        core = SovereignNeuroCore({"d_model": 8})
        q = [0.5] * 8
        k = [0.3] * 8
        attn = core._resonance_attention(q, k)
        assert sum(attn) == pytest.approx(1.0, rel=1e-6)

    def test_repr(self):
        core = SovereignNeuroCore()
        r = repr(core)
        assert "SovereignNeuroCore" in r


# ==================================================================
# SovereignSwarmRuntime tests
# ==================================================================


class TestSovereignSwarmRuntime:
    def test_spawn_neuronet(self):
        runtime = SovereignSwarmRuntime()
        core_id = runtime.spawn_neuronet({"d_model": 16})
        assert core_id.startswith("qsha:")
        assert runtime.swarm_size == 1

    def test_spawn_multiple(self):
        runtime = SovereignSwarmRuntime()
        id1 = runtime.spawn_neuronet({"d_model": 16})
        id2 = runtime.spawn_neuronet({"d_model": 32})
        assert id1 != id2
        assert runtime.swarm_size == 2

    def test_remove_core(self):
        runtime = SovereignSwarmRuntime()
        core_id = runtime.spawn_neuronet()
        assert runtime.remove_core(core_id)
        assert runtime.swarm_size == 0
        assert not runtime.remove_core("nonexistent")

    def test_execute(self):
        runtime = SovereignSwarmRuntime()
        runtime.spawn_neuronet({"d_model": 8})
        runtime.spawn_neuronet({"d_model": 8})
        component = {"frequency": [1.0, 2.0], "amplitude": [0.5, 1.0]}
        results = runtime.execute(component)
        assert len(results) == 2
        for r in results:
            assert isinstance(r, SovereignTensor)

    def test_execute_sealed_intent(self):
        runtime = SovereignSwarmRuntime()
        runtime.spawn_neuronet({"d_model": 8})

        intent = {"spectrum": {"frequency": [1.0, 2.0], "amplitude": [0.5, 1.0]}}
        sealed = runtime.vault.seal_intent(intent)
        receipt = runtime.execute_sealed_intent(sealed)

        assert isinstance(receipt, ExecutionReceipt)
        assert receipt.commitment.startswith("commit:")
        assert receipt.public_meta["swarm_size"] == 1
        assert "masked_topology" in receipt.shadow_wire
        assert runtime.manifest_commitment == receipt.commitment

    def test_vault_seal_open_roundtrip(self):
        vault = SovereignVault()
        intent = {"key": "value", "nested": [1, 2, 3]}
        sealed = vault.seal_intent(intent)
        recovered = vault.open_sealed_intent(sealed)
        assert recovered == intent

    def test_shadow_wire_mask(self):
        wire = ShadowWireEnvelope()
        mask = wire.mask_topology(["core_a", "core_b", "core_c"])
        assert "masked_topology" in mask
        assert mask["core_count"] == 3
        # Same input → same mask (deterministic)
        mask2 = wire.mask_topology(["core_a", "core_b", "core_c"])
        assert mask == mask2

    def test_empty_swarm_execute(self):
        runtime = SovereignSwarmRuntime()
        results = runtime.execute({"amplitude": [1.0]})
        assert results == []
