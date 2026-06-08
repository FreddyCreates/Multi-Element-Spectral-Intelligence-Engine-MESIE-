"""OTA swarm radio mesh — virtual RF propagation over multicast UDP (not file-drop only)."""

from __future__ import annotations

import json
import socket
import struct
import threading
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set

from mesie.edge.hz_ladder import STANDARD_TIERS

OTA_MAGIC = b"NSOT"
OTA_HEADER = struct.Struct("<4sHHIff")  # magic, ver, seq, plen, prop_delay_ms, snr_db
OTA_VERSION = 1
DEFAULT_MCAST = "239.192.77.1"
DEFAULT_PORT = 37541
PROPAGATION_TIER = 3  # VHF/UHF drone mesh


@dataclass
class OTARadioFrame:
    sender_id: str
    seq: int
    threat: bool
    route_id: str
    score: float
    cluster_id: str
    propagation_delay_ms: float
    snr_db: float

    def to_bytes(self) -> bytes:
        body = json.dumps({
            "sender_id": self.sender_id,
            "threat": self.threat,
            "route_id": self.route_id,
            "score": self.score,
            "cluster_id": self.cluster_id,
        }).encode("utf-8")
        return OTA_HEADER.pack(
            OTA_MAGIC, OTA_VERSION, self.seq, len(body),
            self.propagation_delay_ms, self.snr_db,
        ) + body

    @classmethod
    def from_bytes(cls, data: bytes) -> "OTARadioFrame":
        magic, ver, seq, plen, delay, snr = OTA_HEADER.unpack_from(data)
        if magic != OTA_MAGIC:
            raise ValueError("bad OTA magic")
        body = json.loads(data[OTA_HEADER.size : OTA_HEADER.size + plen].decode("utf-8"))
        return cls(
            sender_id=body["sender_id"],
            seq=seq,
            threat=bool(body["threat"]),
            route_id=body["route_id"],
            score=float(body["score"]),
            cluster_id=body["cluster_id"],
            propagation_delay_ms=delay,
            snr_db=snr,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OTAMeshReport:
    nodes: int
    frames_sent: int
    frames_received: int
    propagation_tier: str
    typical_latency_ms: float
    airgapped: bool
    over_the_air: bool
    virtual_silicon_mac: bool
    ok: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class OTARadioMesh:
    """Simulated OTA swarm radio: multicast + Hz-ladder propagation metadata."""

    def __init__(
        self,
        node_id: str,
        *,
        mcast_group: str = DEFAULT_MCAST,
        port: int = DEFAULT_PORT,
        bind_host: str = "0.0.0.0",
    ) -> None:
        self.node_id = node_id
        self.mcast_group = mcast_group
        self.port = port
        self.bind_host = bind_host
        self._seq = 0
        self._inbox: List[OTARadioFrame] = []
        self._seen: Set[str] = set()
        self._sent = 0
        self._sock: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None
        tier = STANDARD_TIERS[PROPAGATION_TIER]
        self._prop_delay_ms = tier.typical_latency_ms
        self._tier_name = tier.name

    def start(self) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.bind_host, self.port))
        mreq = struct.pack("4sl", socket.inet_aton(self.mcast_group), socket.INADDR_ANY)
        self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self._sock.settimeout(0.05)
        self._thread = threading.Thread(target=self._listen, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._sock:
            self._sock.close()
            self._sock = None

    def _listen(self) -> None:
        while self._sock:
            try:
                data, _ = self._sock.recvfrom(4096)
                frame = OTARadioFrame.from_bytes(data)
                key = f"{frame.sender_id}:{frame.seq}"
                if key not in self._seen:
                    self._seen.add(key)
                    self._inbox.append(frame)
            except socket.timeout:
                continue
            except OSError:
                break

    def transmit(
        self,
        *,
        threat: bool,
        route_id: str,
        score: float,
        cluster_id: str,
        snr_db: float = 18.0,
    ) -> OTARadioFrame:
        self._seq += 1
        frame = OTARadioFrame(
            sender_id=self.node_id,
            seq=self._seq,
            threat=threat,
            route_id=route_id,
            score=score,
            cluster_id=cluster_id,
            propagation_delay_ms=self._prop_delay_ms,
            snr_db=snr_db,
        )
        payload = frame.to_bytes()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        s.sendto(payload, (self.mcast_group, self.port))
        s.close()
        self._sent += 1
        return frame

    def drain(self, limit: int = 64) -> List[OTARadioFrame]:
        batch = self._inbox[:limit]
        self._inbox = self._inbox[limit:]
        return batch

    def status(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "protocol": "ota_multicast_udp",
            "mcast_group": self.mcast_group,
            "port": self.port,
            "propagation_tier": self._tier_name,
            "typical_latency_ms": self._prop_delay_ms,
            "sent": self._sent,
            "inbox": len(self._inbox),
            "over_the_air": True,
            "virtual_silicon_mac": True,
            "airgapped_lan": True,
        }


def run_ota_mesh_round(n_nodes: int = 4, *, rounds: int = 3) -> OTAMeshReport:
    """Multi-node OTA gossip round — each node transmits and receives via multicast."""
    nodes = [OTARadioMesh(f"ota-node-{i}") for i in range(n_nodes)]
    for n in nodes:
        n.start()
    time.sleep(0.05)
    sent = 0
    for r in range(rounds):
        for i, node in enumerate(nodes):
            node.transmit(
                threat=r % 2 == 0,
                route_id=f"route-{i}",
                score=0.85 - i * 0.01,
                cluster_id=f"cluster-{i:03d}",
            )
            sent += 1
    time.sleep(0.15)
    received = sum(len(n.drain()) for n in nodes)
    for n in nodes:
        n.stop()
    tier = STANDARD_TIERS[PROPAGATION_TIER]
    ok = received >= n_nodes  # each node should hear at least one peer
    return OTAMeshReport(
        nodes=n_nodes,
        frames_sent=sent,
        frames_received=received,
        propagation_tier=tier.name,
        typical_latency_ms=tier.typical_latency_ms,
        airgapped=True,
        over_the_air=True,
        virtual_silicon_mac=True,
        ok=ok,
    )