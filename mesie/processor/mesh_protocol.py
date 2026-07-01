"""VP-MESH — Virtual Processor Network Mesh Protocol (production).

Layers:
  - UDP multicast beacons (NSOT-compatible tier metadata)
  - LAN peer bundles (sovereign file-drop)
  - HTTP health + compute routing across processor nodes
  - LRC receipt gossip for cross-node accounting proof
"""

from __future__ import annotations

import hashlib
import json
import socket
import struct
import threading
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import asdict, dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from mesie.edge.hz_ladder import STANDARD_TIERS
from mesie.silicon.ota_mesh import PROPAGATION_TIER, run_ota_mesh_round
from mesie.sovereign.sovereign_mesh import SovereignMesh

ROOT = Path(__file__).resolve().parents[2]
MESH_VERSION = "1.2.0"
MESH_MAGIC = b"VPM1"
MESH_HEADER = struct.Struct("<4sBBHI")  # magic, ver, msg_type, seq, plen
MESH_MCAST = "239.192.77.2"
MESH_PORT = 37542
STATE_PATH = ROOT / "deliverables" / "processor" / "VP_MESH_STATE.json"
FEED_PATH = ROOT / "deliverables" / "processor" / "VP_MESH_FEED.jsonl"
PEER_DIR = ROOT / "library" / "mesh_peers" / "vp_nodes"


class MeshMessageType(IntEnum):
    BEACON = 1
    COMPUTE_OFFER = 2
    LRC_SYNC = 3
    GOSSIP = 4
    HEARTBEAT = 5


@dataclass
class VPMeshPeer:
    node_id: str
    hostname: str
    lan_ip: str
    processor_url: str
    operations: List[str]
    threat_p50_ms: Optional[float] = None
    lrc_id: Optional[str] = None
    last_seen: float = 0.0
    healthy: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VPMeshPulseReport:
    ok: bool
    node_id: str
    peers_seen: int
    ota_frames_received: int
    ota_mesh_ok: bool
    beacons_sent: int
    beacons_received: int
    sovereign_bundle_hash: str
    routed_local: bool
    latency_ms: float
    propagation_tier: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VPMeshFrame:
    msg_type: MeshMessageType
    node_id: str
    seq: int
    body: Dict[str, Any]

    def to_bytes(self) -> bytes:
        payload = json.dumps({
            "node_id": self.node_id,
            "msg_type": self.msg_type.value,
            "body": self.body,
        }, separators=(",", ":")).encode("utf-8")
        return MESH_HEADER.pack(MESH_MAGIC, 1, int(self.msg_type), self.seq, len(payload)) + payload

    @classmethod
    def from_bytes(cls, data: bytes) -> "VPMeshFrame":
        magic, ver, msg_type, seq, plen = MESH_HEADER.unpack_from(data)
        if magic != MESH_MAGIC:
            raise ValueError("bad VP-MESH magic")
        body = json.loads(data[MESH_HEADER.size : MESH_HEADER.size + plen].decode("utf-8"))
        return cls(
            msg_type=MeshMessageType(msg_type),
            node_id=body["node_id"],
            seq=seq,
            body=body.get("body", {}),
        )


class VirtualProcessorMeshNode:
    """One sovereign processor node on the VP-MESH."""

    def __init__(
        self,
        *,
        processor_url: str = "http://127.0.0.1:8750",
        mcast_group: str = MESH_MCAST,
        port: int = MESH_PORT,
        bind_host: str = "0.0.0.0",
    ) -> None:
        self.node_id = hashlib.sha256(f"{socket.gethostname()}-{uuid.uuid4().hex[:6]}".encode()).hexdigest()[:12]
        self.processor_url = processor_url.rstrip("/")
        self.mcast_group = mcast_group
        self.port = port
        self.bind_host = bind_host
        self._seq = 0
        self._peers: Dict[str, VPMeshPeer] = {}
        self._inbox: List[VPMeshFrame] = []
        self._seen: Set[str] = set()
        self._sent = 0
        self._received = 0
        self._sock: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None
        tier = STANDARD_TIERS[PROPAGATION_TIER]
        self._propagation_tier = tier.name
        PEER_DIR.mkdir(parents=True, exist_ok=True)

    def start(self) -> None:
        if self._sock:
            return
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except (AttributeError, OSError):
            pass
        self._sock.bind((self.bind_host, self.port))
        mreq = struct.pack("4sl", socket.inet_aton(self.mcast_group), socket.INADDR_ANY)
        self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self._sock.settimeout(0.05)
        self._thread = threading.Thread(target=self._listen, daemon=True, name="vp-mesh-udp")
        self._thread.start()

    def stop(self) -> None:
        if self._sock:
            self._sock.close()
            self._sock = None

    def _listen(self) -> None:
        while self._sock:
            try:
                data, addr = self._sock.recvfrom(8192)
                frame = VPMeshFrame.from_bytes(data)
                key = f"{frame.node_id}:{frame.seq}:{frame.msg_type.value}"
                if key in self._seen:
                    continue
                self._seen.add(key)
                self._inbox.append(frame)
                self._received += 1
                if frame.msg_type == MeshMessageType.BEACON:
                    self._ingest_beacon(frame.body, source_ip=addr[0])
            except socket.timeout:
                continue
            except OSError:
                break

    def _ingest_beacon(self, body: Dict[str, Any], *, source_ip: str) -> None:
        nid = str(body.get("node_id", ""))
        if not nid or nid == self.node_id:
            return
        self._peers[nid] = VPMeshPeer(
            node_id=nid,
            hostname=str(body.get("hostname", "peer")),
            lan_ip=str(body.get("lan_ip", source_ip)),
            processor_url=str(body.get("processor_url", "")),
            operations=list(body.get("operations", [])),
            threat_p50_ms=body.get("threat_p50_ms"),
            lrc_id=body.get("lrc_id"),
            last_seen=time.time(),
            healthy=bool(body.get("healthy", False)),
        )

    def _lan_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("10.255.255.255", 1))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except OSError:
            return "127.0.0.1"

    def _local_processor_status(self) -> Dict[str, Any]:
        try:
            with urllib.request.urlopen(f"{self.processor_url}/processor/status", timeout=4) as resp:
                return json.loads(resp.read().decode())
        except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError):
            return {}

    def beacon(self) -> VPMeshFrame:
        self._seq += 1
        status = self._local_processor_status()
        acct = {}
        try:
            with urllib.request.urlopen(f"{self.processor_url}/processor/accounting", timeout=4) as resp:
                acct = json.loads(resp.read().decode())
        except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError):
            pass
        body = {
            "node_id": self.node_id,
            "hostname": socket.gethostname(),
            "lan_ip": self._lan_ip(),
            "processor_url": self.processor_url,
            "operations": status.get("operations", []),
            "processor_version": status.get("processor_version", MESH_VERSION),
            "threat_p50_ms": acct.get("last_threat_p50_ms"),
            "lrc_id": acct.get("lrc_id"),
            "healthy": bool(status.get("product")),
            "mesh_version": MESH_VERSION,
            "propagation_tier": self._propagation_tier,
            "ts": time.time(),
        }
        frame = VPMeshFrame(MeshMessageType.BEACON, self.node_id, self._seq, body)
        payload = frame.to_bytes()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        s.sendto(payload, (self.mcast_group, self.port))
        s.close()
        self._sent += 1
        self._persist_peer_record(body)
        return frame

    def _persist_peer_record(self, body: Dict[str, Any]) -> None:
        out = PEER_DIR / f"node_{self.node_id}.json"
        out.write_text(json.dumps({"mesh_version": MESH_VERSION, **body}, indent=2), encoding="utf-8")

    def discover_file_peers(self, *, limit: int = 16) -> List[VPMeshPeer]:
        peers: List[VPMeshPeer] = []
        paths = sorted(PEER_DIR.glob("node_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        for path in paths[:limit]:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            nid = str(data.get("node_id", path.stem.replace("node_", "")))
            if nid == self.node_id:
                continue
            peer = VPMeshPeer(
                node_id=nid,
                hostname=str(data.get("hostname", "peer")),
                lan_ip=str(data.get("lan_ip", "127.0.0.1")),
                processor_url=str(data.get("processor_url", "")),
                operations=list(data.get("operations", [])),
                threat_p50_ms=data.get("threat_p50_ms"),
                lrc_id=data.get("lrc_id"),
                last_seen=float(data.get("ts", 0)),
                healthy=bool(data.get("healthy", False)),
            )
            self._peers[nid] = peer
            peers.append(peer)
        return peers

    def probe_peers(self, *, limit: int = 8) -> int:
        healthy = 0
        ranked = sorted(self._peers.values(), key=lambda p: p.last_seen, reverse=True)
        for peer in ranked[:limit]:
            if not peer.processor_url:
                continue
            try:
                with urllib.request.urlopen(f"{peer.processor_url}/processor/status", timeout=3) as resp:
                    peer.healthy = resp.status == 200
                    if peer.healthy:
                        healthy += 1
                    peer.last_seen = time.time()
            except (urllib.error.URLError, OSError, TimeoutError):
                peer.healthy = False
        return healthy

    def route_target(self) -> VPMeshPeer:
        """Phi-weighted lowest-latency peer selection; default local."""
        local = VPMeshPeer(
            node_id=self.node_id,
            hostname=socket.gethostname(),
            lan_ip=self._lan_ip(),
            processor_url=self.processor_url,
            operations=[],
            healthy=True,
            last_seen=time.time(),
        )
        candidates = [p for p in self._peers.values() if p.healthy and p.processor_url]
        if not candidates:
            return local
        phi_inv = 0.618033988749895

        def score(p: VPMeshPeer) -> float:
            lat = float(p.threat_p50_ms or 999.0)
            return lat * phi_inv + (1.0 - phi_inv) * (time.time() - p.last_seen)

        return min(candidates, key=score)

    def pulse(self, *, ota_nodes: int = 4) -> VPMeshPulseReport:
        t0 = time.perf_counter()
        self.start()
        self.beacon()
        time.sleep(0.08)
        self.discover_file_peers()
        for _ in self._inbox:
            pass  # inbox drained via listener ingest
        healthy = self.probe_peers()
        ota = run_ota_mesh_round(n_nodes=ota_nodes, rounds=3)
        sovereign = SovereignMesh().export_bundle()
        target = self.route_target()
        routed_local = target.node_id == self.node_id
        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        report = VPMeshPulseReport(
            ok=ota.ok and bool(sovereign.bundle_hash),
            node_id=self.node_id,
            peers_seen=len(self._peers),
            ota_frames_received=ota.frames_received,
            ota_mesh_ok=ota.ok,
            beacons_sent=self._sent,
            beacons_received=self._received,
            sovereign_bundle_hash=sovereign.bundle_hash,
            routed_local=routed_local,
            latency_ms=elapsed,
            propagation_tier=self._propagation_tier,
        )
        self._write_state(report, healthy_peers=healthy)
        self._append_feed(report)
        return report

    def status(self) -> Dict[str, Any]:
        return {
            "protocol": "VP-MESH",
            "version": MESH_VERSION,
            "node_id": self.node_id,
            "processor_url": self.processor_url,
            "mcast_group": self.mcast_group,
            "port": self.port,
            "propagation_tier": self._propagation_tier,
            "peers": len(self._peers),
            "beacons_sent": self._sent,
            "beacons_received": self._received,
            "peer_dir": str(PEER_DIR),
            "sovereign": True,
            "airgapped_lan": True,
        }

    def _write_state(self, report: VPMeshPulseReport, *, healthy_peers: int) -> None:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "mesh_version": MESH_VERSION,
            "ts": time.time(),
            "node": self.status(),
            "peers": [p.to_dict() for p in self._peers.values()],
            "healthy_peers": healthy_peers,
            "last_pulse": report.to_dict(),
            "route_target": self.route_target().to_dict(),
        }
        STATE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _append_feed(self, report: VPMeshPulseReport) -> None:
        FEED_PATH.parent.mkdir(parents=True, exist_ok=True)
        with FEED_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": time.time(), "pulse": report.to_dict()}) + "\n")


def load_mesh_state() -> Dict[str, Any]:
    if not STATE_PATH.is_file():
        return {"ok": False, "note": "no mesh state yet — POST /processor/mesh/pulse"}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def run_mesh_soak(*, n_nodes: int = 4, rounds: int = 5) -> Dict[str, Any]:
    """Production soak — OTA + beacons + sovereign export proof."""
    node = VirtualProcessorMeshNode()
    node.start()
    pulses = []
    for _ in range(rounds):
        pulses.append(node.pulse(ota_nodes=n_nodes).to_dict())
    node.stop()
    ok = all(p.get("ok") for p in pulses) and pulses[-1].get("ota_mesh_ok", False)
    return {
        "ok": ok,
        "protocol": "VP-MESH",
        "version": MESH_VERSION,
        "rounds": rounds,
        "n_nodes": n_nodes,
        "pulses": pulses,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }