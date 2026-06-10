# phantom_native/swarm_runtime.py
"""SovereignSwarmRuntime — Native runtime for MESIE neuronet swarms.

Orchestrates multiple SovereignNeuroCores in a swarm topology,
binding them with Shadow Wire masking and QSHA-protected execution
receipts. Supports sealed-intent execution with public commitments
and private topology masking.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from phantom_native.neurocore import SovereignNeuroCore
from phantom_native.sovereign_tensor import SovereignTensor


# ------------------------------------------------------------------
# Supporting types for the swarm protocol
# ------------------------------------------------------------------


@dataclass
class ExecutionReceipt:
    """Public proof of a sealed-intent execution.

    Contains a commitment hash, the masked topology shadow, and
    non-sensitive execution metadata.
    """

    commitment: str
    shadow_wire: Dict[str, Any] = field(default_factory=dict)
    public_meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ShadowWireEnvelope:
    """Shadow Wire topology mask.

    Masks the internal wiring of the swarm so that external observers
    only see a commitment — not the actual core topology.
    """

    def mask_topology(self, core_ids: List[str]) -> Dict[str, Any]:
        """Produce a masked representation of the swarm topology.

        Args:
            core_ids: Internal identifiers of the participating cores.

        Returns:
            A dict with a masked digest and core count.
        """
        digest = hashlib.sha256("|".join(core_ids).encode()).hexdigest()[:16]
        return {
            "masked_topology": digest,
            "core_count": len(core_ids),
        }


@dataclass
class SovereignVault:
    """Minimal vault for sealed-intent operations.

    Stores sealed intents and exposes open/seal operations using
    QSHA-compatible hashing.
    """

    _store: Dict[str, bytes] = field(default_factory=dict)

    def seal_intent(self, intent: Dict[str, Any]) -> bytes:
        """Seal an intent into opaque bytes.

        Args:
            intent: The intent payload to seal.

        Returns:
            Sealed bytes representing the intent.
        """
        import json

        raw = json.dumps(intent, sort_keys=True).encode()
        tag = hashlib.sha256(raw).hexdigest()[:16]
        self._store[tag] = raw
        return tag.encode() + b":" + raw

    def open_sealed_intent(self, sealed: bytes) -> Dict[str, Any]:
        """Open a sealed intent back into its payload dict.

        Args:
            sealed: The sealed bytes produced by :meth:`seal_intent`.

        Returns:
            Original intent payload.
        """
        import json

        parts = sealed.split(b":", 1)
        if len(parts) != 2:
            raise ValueError("Invalid sealed intent format")
        return json.loads(parts[1])


# ------------------------------------------------------------------
# Main runtime
# ------------------------------------------------------------------


class SovereignSwarmRuntime:
    """Native runtime for MESIE neuronet swarms.

    Manages a collection of :class:`SovereignNeuroCore` instances,
    routes spectral data through the swarm, and produces
    QSHA-protected execution receipts with Shadow Wire topology
    masking.
    """

    def __init__(self) -> None:
        self.vault = SovereignVault()
        self.wire = ShadowWireEnvelope()
        self.cores: Dict[str, SovereignNeuroCore] = {}
        self.manifest_commitment: str = ""
        self._spawn_counter: int = 0

    # ------------------------------------------------------------------
    # Swarm management
    # ------------------------------------------------------------------

    def spawn_neuronet(self, spectral_config: Optional[Dict[str, Any]] = None) -> str:
        """Spawn a new NeuroCore and register it in the swarm.

        Args:
            spectral_config: Configuration forwarded to the NeuroCore.

        Returns:
            A QSHA-like identifier for the spawned core.
        """
        spectral_config = spectral_config or {}
        core = SovereignNeuroCore(spectral_config)
        self._spawn_counter += 1
        core_id = self._qsha(f"{self._spawn_counter}:{spectral_config}")
        self.cores[core_id] = core
        return core_id

    def remove_core(self, core_id: str) -> bool:
        """Remove a core from the swarm.

        Returns:
            True if the core was found and removed.
        """
        return self.cores.pop(core_id, None) is not None

    @property
    def swarm_size(self) -> int:
        """Number of active cores in the swarm."""
        return len(self.cores)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(self, component: Dict[str, Any]) -> List[SovereignTensor]:
        """Run a MESIE spectral component through all cores.

        Args:
            component: A MESIE SpectralComponent-like dict.

        Returns:
            List of output tensors (one per core).
        """
        tensor = SovereignTensor.from_mesie_component(component)
        results: List[SovereignTensor] = []
        for core in self.cores.values():
            out = core.forward(tensor)
            results.append(out)
        return results

    def execute_sealed_intent(self, sealed_intent: bytes) -> ExecutionReceipt:
        """Execute a sealed intent with public proof.

        Opens the sealed payload, routes the spectral data through
        all cores, computes a commitment hash, and masks the topology.

        Args:
            sealed_intent: Bytes produced by :meth:`SovereignVault.seal_intent`.

        Returns:
            An :class:`ExecutionReceipt` with commitment and shadow wire.
        """
        intent = self.vault.open_sealed_intent(sealed_intent)

        results: List[SovereignTensor] = []
        spectrum = intent.get("spectrum", {})
        for core in self.cores.values():
            tensor = SovereignTensor.from_mesie_component(spectrum)
            out = core.forward(tensor)
            results.append(out)

        # Public commitment
        commitment = self._compute_commitment(results)
        shadow = self.wire.mask_topology(list(self.cores.keys()))

        receipt = ExecutionReceipt(
            commitment=commitment,
            shadow_wire=shadow,
            public_meta={"swarm_size": len(self.cores)},
        )
        self.manifest_commitment = commitment
        return receipt

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _qsha(self, data: str) -> str:
        """Compute a QSHA-like hash for identification."""
        digest = hashlib.sha256(data.encode()).hexdigest()[:32]
        return f"qsha:{digest}"

    def _compute_commitment(self, results: List[SovereignTensor]) -> str:
        """Aggregate QSHA commitment from execution results."""
        payload = "|".join(
            hashlib.sha256(r.to_bytes()).hexdigest()[:16] for r in results
        )
        digest = hashlib.sha256(payload.encode()).hexdigest()[:32]
        return f"commit:{digest}"
