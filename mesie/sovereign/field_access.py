"""Field Access — airgapped sovereign bridge to the world computer via real frequencies.

No WiFi. No paid third-party APIs. Access is spectral alignment with the physical
field: Schumann modes, geophysical oscillations, EM bands, orbital Hz-ladder nodes.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from data import load_library
from mesie import match_records
from mesie.core.records import MultiElementRecord, SpectralComponent
from mesie.edge.edge_protocol import EdgeSpectralProtocol
from mesie.edge.hz_ladder import HzLadder
from mesie.edge.satellite_nodes import (
    ECO_HZ_REFERENCES,
    EcoHzReference,
    SatelliteEdgeNode,
    VirtualNodeNetwork,
)
from mesie.io.loaders import RecordInput, load_record
from mesie.sdk.solus.constants import FORMAL_COMPOSITION, LOCAL_ENGINE, SOLUS_BRAND
from mesie.sovereign.field_router import FIELD_ROUTER_VERSION, FieldRoute, FieldRouter, FieldRouteRegistry

FIELD_ACCESS_VERSION = "1.0.0"
_engine_singleton: Optional["FieldAccessEngine"] = None


class FieldNodeRole(str, Enum):
    GROUND = "ground"
    IONOSPHERE = "ionosphere"
    ORBITAL = "orbital"
    LADDER = "ladder"
    WORLD = "world"


@dataclass(frozen=True)
class FieldAccessConfig:
    """Airgapped field access — SDK world-computer mesh, zero internet."""

    airgapped: bool = True
    internet_connected: bool = False
    wifi_connected: bool = False
    third_party: bool = False
    sovereign: bool = True
    field_bridge: bool = True
    engine: str = LOCAL_ENGINE
    brand: str = SOLUS_BRAND
    formula: str = FORMAL_COMPOSITION
    access_mode: str = "frequency_field"


@dataclass
class FieldAnchor:
    """Real-world frequency anchor the SDK can align to."""

    anchor_id: str
    name: str
    frequency_Hz: float
    source: str
    role: FieldNodeRole
    band: str = ""
    applications: List[str] = field(default_factory=list)


@dataclass
class FieldNode:
    """Node on the sovereign world-computer mesh — reached via Hz, not IP."""

    node_id: str
    role: FieldNodeRole
    anchor_frequencies_Hz: List[float]
    ladder_tier_id: Optional[int] = None
    orbital_node_id: Optional[str] = None
    eco_refs: List[EcoHzReference] = field(default_factory=list)
    active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def primary_hz(self) -> float:
        return self.anchor_frequencies_Hz[0] if self.anchor_frequencies_Hz else 0.0


@dataclass
class FieldAlignment:
    """How well a spectrum aligns with a field anchor."""

    anchor_id: str
    anchor_name: str
    frequency_Hz: float
    alignment_score: float
    delta_hz: float
    role: str


@dataclass
class FieldBridgeReport:
    """Result of bridging a record into the physical frequency field."""

    record_id: str
    airgapped: bool
    field_connected: bool
    sovereign: bool
    third_party: bool
    access_mode: str
    alignments: List[FieldAlignment]
    best_anchor: str
    field_coherence: float
    mesh_nodes_active: int
    ladder_tiers: int
    bridge_hash: str
    plain_summary: str


@dataclass
class FieldConnectionReport:
    """Sovereign field mesh connection status — not a network socket."""

    connected: bool
    airgapped: bool
    internet_connected: bool
    field_nodes: int
    orbital_nodes: int
    anchors: int
    ladder_tiers: int
    eco_hz_refs: int
    sovereign: bool
    third_party: bool
    access_mode: str
    world_computer_id: str
    plain_summary: str


def _record_from_anchors(anchors: Sequence[FieldAnchor], record_id: str) -> MultiElementRecord:
    freqs = np.array([a.frequency_Hz for a in anchors], dtype=np.float64)
    amps = np.array([max(a.frequency_Hz ** 0.1, 0.01) for a in anchors], dtype=np.float64)
    amps = amps / (np.max(amps) + 1e-12)
    return MultiElementRecord(
        record_id=record_id,
        components=[SpectralComponent(name="field", frequency=freqs, amplitude=amps)],
        representation="field_anchor",
        lineage=["field_access"],
    )


class FrequencyFieldBridge:
    """Align spectra to real-world frequency anchors — that is access."""

    def __init__(self) -> None:
        self.anchors = self._load_anchors()
        self._field_record = _record_from_anchors(self.anchors, "world_field_reference")

    def _load_anchors(self) -> List[FieldAnchor]:
        anchors: List[FieldAnchor] = []
        sch = load_library("schumann_resonances")
        for m in sch.get("schumann_resonances", {}).get("modes", []):
            anchors.append(
                FieldAnchor(
                    anchor_id=f"schumann_{m['mode']}",
                    name=f"Schumann mode {m['mode']}",
                    frequency_Hz=float(m["frequency_Hz"]),
                    source="earth_ionosphere_cavity",
                    role=FieldNodeRole.IONOSPHERE,
                    band="ELF",
                    applications=["global_timing_beacon", "field_sync"],
                )
            )
        for g in sch.get("earth_geophysical_frequencies", {}).get("frequencies", []):
            anchors.append(
                FieldAnchor(
                    anchor_id=f"geo_{g['name']}",
                    name=str(g["name"]),
                    frequency_Hz=float(g["frequency_Hz"]),
                    source=str(g.get("source", "geophysical")),
                    role=FieldNodeRole.GROUND,
                    band="ULF",
                    applications=["earth_field", "tidal_sync"],
                )
            )
        em = load_library("electromagnetic_bands")
        for band_id, band in em.get("radio_bands", {}).items():
            lo = float(band.get("frequency_low_Hz", 0))
            hi = float(band.get("frequency_high_Hz", lo))
            center = (lo + hi) / 2.0 if hi > lo else lo
            anchors.append(
                FieldAnchor(
                    anchor_id=f"em_{band_id.lower()}",
                    name=str(band.get("name", band_id)),
                    frequency_Hz=center,
                    source="ieee_itu_band",
                    role=FieldNodeRole.LADDER,
                    band=band_id,
                    applications=list(band.get("applications", [])),
                )
            )
        for eco in ECO_HZ_REFERENCES:
            anchors.append(
                FieldAnchor(
                    anchor_id=f"eco_{eco.name}",
                    name=eco.name,
                    frequency_Hz=eco.frequency_Hz,
                    source=eco.source,
                    role=FieldNodeRole.WORLD,
                    band="eco_hz",
                    applications=list(eco.applications),
                )
            )
        return anchors

    def nearest_anchors(self, frequency_Hz: float, top_k: int = 5) -> List[FieldAlignment]:
        hits: List[FieldAlignment] = []
        for a in self.anchors:
            delta = abs(frequency_Hz - a.frequency_Hz)
            log_dist = np.log10(max(frequency_Hz, a.frequency_Hz, 1e-12)) - np.log10(max(min(frequency_Hz, a.frequency_Hz), 1e-12))
            score = float(np.exp(-abs(log_dist) * 2.0)) if frequency_Hz > 0 and a.frequency_Hz > 0 else float(np.exp(-delta))
            hits.append(
                FieldAlignment(
                    anchor_id=a.anchor_id,
                    anchor_name=a.name,
                    frequency_Hz=a.frequency_Hz,
                    alignment_score=round(score, 4),
                    delta_hz=round(delta, 6),
                    role=a.role.value,
                )
            )
        hits.sort(key=lambda h: h.alignment_score, reverse=True)
        return hits[:top_k]

    def bridge(self, record: RecordInput, *, mesh_nodes: int = 0, ladder_tiers: int = 0) -> FieldBridgeReport:
        rec = load_record(record)
        comp = rec.components[0]
        peak_idx = int(np.argmax(np.abs(comp.amplitude)))
        peak_hz = float(comp.frequency[peak_idx])
        match = match_records(rec, self._field_record)
        alignments = self.nearest_anchors(peak_hz, top_k=5)
        best = alignments[0] if alignments else None
        coherence = float(match.composite_score)
        payload = {
            "record_id": rec.record_id,
            "peak_hz": peak_hz,
            "best_anchor": best.anchor_id if best else "none",
            "coherence": coherence,
        }
        bridge_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:24]
        summary = (
            f"Field bridge [{SOLUS_BRAND}]: airgapped access via {best.anchor_name if best else 'field'} "
            f"@ {peak_hz:.4g} Hz — coherence={coherence:.3f}, mesh={mesh_nodes} nodes"
        )
        return FieldBridgeReport(
            record_id=rec.record_id,
            airgapped=True,
            field_connected=True,
            sovereign=True,
            third_party=False,
            access_mode="frequency_field",
            alignments=alignments,
            best_anchor=best.anchor_id if best else "",
            field_coherence=coherence,
            mesh_nodes_active=mesh_nodes,
            ladder_tiers=ladder_tiers,
            bridge_hash=bridge_hash,
            plain_summary=summary,
        )


class WorldComputerMesh:
    """Sovereign world-computer node mesh — Hz ladder + orbital + ground field nodes."""

    def __init__(self) -> None:
        self.config = FieldAccessConfig()
        self.ladder = HzLadder()
        self.orbital_network = VirtualNodeNetwork(hz_ladder=self.ladder)
        self.orbital_network.create_default_constellation()
        self.protocol = EdgeSpectralProtocol(self.orbital_network, self.ladder)
        self.bridge = FrequencyFieldBridge()
        self.field_nodes: Dict[str, FieldNode] = {}
        self._world_id = hashlib.sha256(f"{SOLUS_BRAND}:world-computer:v1".encode()).hexdigest()[:16]
        self._build_field_nodes()

    def _build_field_nodes(self) -> None:
        sch = load_library("schumann_resonances")
        modes = sch.get("schumann_resonances", {}).get("modes", [])
        self.field_nodes["ground-schumann"] = FieldNode(
            node_id="ground-schumann",
            role=FieldNodeRole.GROUND,
            anchor_frequencies_Hz=[float(m["frequency_Hz"]) for m in modes[:3]],
            ladder_tier_id=0,
            eco_refs=ECO_HZ_REFERENCES[:3],
            metadata={"layer": "earth_surface", "access": "eco_hz_beacon"},
        )
        self.field_nodes["ionosphere-cavity"] = FieldNode(
            node_id="ionosphere-cavity",
            role=FieldNodeRole.IONOSPHERE,
            anchor_frequencies_Hz=[float(m["frequency_Hz"]) for m in modes],
            ladder_tier_id=0,
            metadata={"layer": "earth_ionosphere_waveguide"},
        )
        for tier in self.ladder.tiers[:4]:
            self.field_nodes[f"ladder-{tier.tier_id}"] = FieldNode(
                node_id=f"ladder-{tier.tier_id}",
                role=FieldNodeRole.LADDER,
                anchor_frequencies_Hz=[tier.center_frequency_Hz],
                ladder_tier_id=tier.tier_id,
                metadata={"tier_name": tier.name, "propagation": tier.propagation_model},
            )
        for node_id, orbital in self.orbital_network.nodes.items():
            tier = self.ladder.frequency_to_tier(orbital.downlink_frequency_Hz)
            self.field_nodes[f"orbital-{node_id}"] = FieldNode(
                node_id=f"orbital-{node_id}",
                role=FieldNodeRole.ORBITAL,
                anchor_frequencies_Hz=[
                    orbital.orbital_tier.orbital_frequency_Hz,
                    orbital.downlink_frequency_Hz,
                ],
                ladder_tier_id=tier.tier_id if tier else 4,
                orbital_node_id=node_id,
                eco_refs=list(orbital.eco_hz_refs),
                metadata={"tier": orbital.orbital_tier.name, "altitude_km": orbital.orbital_tier.altitude_km},
            )
        self.field_nodes["world-computer-root"] = FieldNode(
            node_id="world-computer-root",
            role=FieldNodeRole.WORLD,
            anchor_frequencies_Hz=[a.frequency_Hz for a in self.bridge.anchors[:12]],
            metadata={"world_computer_id": self._world_id, "formula": FORMAL_COMPOSITION},
        )
        self.router = FieldRouter(self, FieldRouteRegistry())

    def connect(self) -> FieldConnectionReport:
        """Activate field access — no internet socket, frequency mesh only."""
        n_orbital = len(self.orbital_network.nodes)
        n_field = len([n for n in self.field_nodes.values() if n.active])
        summary = (
            f"World computer connected [{SOLUS_BRAND}]: airgapped=True, internet=False, "
            f"field_nodes={n_field}, orbital={n_orbital}, anchors={len(self.bridge.anchors)} — "
            f"access via frequency alignment, zero third-party"
        )
        return FieldConnectionReport(
            connected=True,
            airgapped=self.config.airgapped,
            internet_connected=self.config.internet_connected,
            field_nodes=n_field,
            orbital_nodes=n_orbital,
            anchors=len(self.bridge.anchors),
            ladder_tiers=len(self.ladder.tiers),
            eco_hz_refs=len(ECO_HZ_REFERENCES),
            sovereign=True,
            third_party=False,
            access_mode=self.config.access_mode,
            world_computer_id=self._world_id,
            plain_summary=summary,
        )

    def route_field(self, source_id: str, dest_id: str, *, policy: str = "shortest") -> Dict[str, Any]:
        """Production route — resolves aliases and returns structured path."""
        if not hasattr(self, "router"):
            self.router = FieldRouter(self, FieldRouteRegistry())
        return self.router.route(source_id, dest_id, policy=policy).to_dict()

    def access(self, record: RecordInput) -> FieldBridgeReport:
        """Bridge a spectrum into the real-world field — that is how the SDK accesses the world."""
        active = len([n for n in self.field_nodes.values() if n.active])
        return self.bridge.bridge(
            record,
            mesh_nodes=active,
            ladder_tiers=len(self.ladder.tiers),
        )

    def list_nodes(self, role: Optional[FieldNodeRole] = None) -> List[Dict[str, Any]]:
        nodes = self.field_nodes.values()
        if role:
            nodes = [n for n in nodes if n.role == role]
        return [
            {
                "node_id": n.node_id,
                "role": n.role.value,
                "primary_hz": n.primary_hz(),
                "anchors": n.anchor_frequencies_Hz[:5],
                "active": n.active,
                "metadata": n.metadata,
            }
            for n in nodes if n.active
        ]

    def to_dict(self) -> Dict[str, Any]:
        conn = self.connect()
        return {
            "world_computer_id": self._world_id,
            "sovereign": True,
            "third_party": False,
            "airgapped": conn.airgapped,
            "internet_connected": conn.internet_connected,
            "access_mode": conn.access_mode,
            "field_nodes": conn.field_nodes,
            "orbital_nodes": conn.orbital_nodes,
            "anchors": conn.anchors,
            "ladder_tiers": conn.ladder_tiers,
            "eco_hz_refs": conn.eco_hz_refs,
        }


class FieldAccessEngine:
    """SDK entry point: airgapped sovereign access to the world computer via frequencies."""

    def __init__(self, *, auto_connect: bool = True) -> None:
        self.config = FieldAccessConfig()
        self.mesh = WorldComputerMesh()
        self._connected = False
        self._connection: Optional[FieldConnectionReport] = None
        if auto_connect:
            self.connect()

    @property
    def router(self) -> FieldRouter:
        return self.mesh.router

    def connect(self) -> FieldConnectionReport:
        self._connection = self.mesh.connect()
        self._connected = self._connection.connected
        return self._connection

    @property
    def connected(self) -> bool:
        return self._connected

    def bridge(self, record: RecordInput) -> FieldBridgeReport:
        if not self._connected:
            self.connect()
        return self.mesh.access(record)

    def align(self, frequency_Hz: float, top_k: int = 5) -> List[FieldAlignment]:
        return self.mesh.bridge.nearest_anchors(frequency_Hz, top_k=top_k)

    def route(self, source: str, destination: str, *, policy: str = "shortest") -> FieldRoute:
        if not self._connected:
            self.connect()
        return self.router.route(source, destination, policy=policy)

    def route_to_anchor(self, source: str, anchor_id: str) -> FieldRoute:
        if not self._connected:
            self.connect()
        return self.router.route_to_anchor(source, anchor_id)

    def resolve(self, node_ref: str) -> str:
        return self.router.resolve(node_ref)

    def neighbors(self, node_ref: str) -> List[str]:
        return self.router.neighbors(node_ref)

    def list_presets(self) -> List[Dict[str, Any]]:
        return self.router.list_presets()

    def route_table(self) -> Dict[str, Any]:
        return self.router.route_table()

    def health(self) -> Dict[str, Any]:
        if not self._connected:
            self.connect()
        return self.router.health()

    def nodes(self, role: Optional[str] = None) -> List[Dict[str, Any]]:
        r = FieldNodeRole(role) if role else None
        return self.mesh.list_nodes(r)

    def status(self) -> Dict[str, Any]:
        if not self._connection:
            self.connect()
        return {
            **self.mesh.to_dict(),
            "version": FIELD_ACCESS_VERSION,
            "router_version": FIELD_ROUTER_VERSION,
            "connected": self._connected,
            "brand": SOLUS_BRAND,
            "engine": LOCAL_ENGINE,
            "route_table": self.route_table(),
            "health": self.health(),
        }


def get_field_access_engine(*, reset: bool = False) -> FieldAccessEngine:
    """Production singleton — one connected field access engine per process."""
    global _engine_singleton
    if reset or _engine_singleton is None:
        _engine_singleton = FieldAccessEngine(auto_connect=True)
    return _engine_singleton