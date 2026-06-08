"""LAN UDP gossip — cross-machine peer exchange (airgapped local network)."""

from __future__ import annotations

import json
import socket
import struct
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

GOSSIP_MAGIC = b"NSGM"
HEADER = struct.Struct("<4sHHI")  # magic, version, seq, payload_len
LAN_VERSION = 1
DEFAULT_PORT = 37521
DROP_DIR = Path(__file__).resolve().parents[2] / "library" / "lan_gossip"


@dataclass
class LanGossipMessage:
    sender_id: str
    seq: int
    threat: bool
    route_id: str
    score: float
    cluster_id: str
    timestamp: float

    def to_bytes(self) -> bytes:
        body = json.dumps({
            "sender_id": self.sender_id,
            "seq": self.seq,
            "threat": self.threat,
            "route_id": self.route_id,
            "score": self.score,
            "cluster_id": self.cluster_id,
            "timestamp": self.timestamp,
        }).encode("utf-8")
        return HEADER.pack(GOSSIP_MAGIC, LAN_VERSION, self.seq, len(body)) + body

    @classmethod
    def from_bytes(cls, data: bytes) -> "LanGossipMessage":
        magic, ver, seq, plen = HEADER.unpack_from(data)
        if magic != GOSSIP_MAGIC:
            raise ValueError("bad magic")
        body = json.loads(data[HEADER.size : HEADER.size + plen].decode("utf-8"))
        return cls(
            sender_id=body["sender_id"],
            seq=seq,
            threat=bool(body["threat"]),
            route_id=body["route_id"],
            score=float(body["score"]),
            cluster_id=body["cluster_id"],
            timestamp=float(body.get("timestamp", time.time())),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender_id": self.sender_id,
            "seq": self.seq,
            "threat": self.threat,
            "route_id": self.route_id,
            "score": self.score,
            "cluster_id": self.cluster_id,
            "timestamp": self.timestamp,
        }


@dataclass
class LanGossipNode:
    """UDP gossip node with file-drop fallback for offline/airgap test."""

    node_id: str
    port: int = DEFAULT_PORT
    bind_host: str = "127.0.0.1"
    fanout_peers: List[str] = field(default_factory=lambda: ["127.0.0.1"])
    _seq: int = 0
    _inbox: List[LanGossipMessage] = field(default_factory=list)
    _seen: Set[str] = field(default_factory=set)
    _server: Optional[socket.socket] = None
    _thread: Optional[threading.Thread] = None

    def start(self) -> None:
        DROP_DIR.mkdir(parents=True, exist_ok=True)
        self._server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((self.bind_host, self.port))
        self._server.settimeout(0.05)
        self._thread = threading.Thread(target=self._listen, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._server:
            self._server.close()
            self._server = None

    def _listen(self) -> None:
        while self._server:
            try:
                data, _addr = self._server.recvfrom(4096)
                msg = LanGossipMessage.from_bytes(data)
                self._receive(msg)
            except socket.timeout:
                continue
            except OSError:
                break
            self._drain_file_drop()

    def publish(
        self,
        *,
        threat: bool,
        route_id: str,
        score: float,
        cluster_id: str,
    ) -> LanGossipMessage:
        self._seq += 1
        msg = LanGossipMessage(
            sender_id=self.node_id,
            seq=self._seq,
            threat=threat,
            route_id=route_id,
            score=score,
            cluster_id=cluster_id,
            timestamp=time.time(),
        )
        payload = msg.to_bytes()
        for peer in self.fanout_peers:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.sendto(payload, (peer, self.port))
                s.close()
            except OSError:
                self._file_drop(msg)
        self._file_drop(msg)
        return msg

    def _file_drop(self, msg: LanGossipMessage) -> None:
        path = DROP_DIR / f"{self.node_id}_{msg.seq}.json"
        path.write_text(json.dumps(msg.to_dict()), encoding="utf-8")

    def _drain_file_drop(self) -> None:
        for p in DROP_DIR.glob("*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                msg = LanGossipMessage(
                    sender_id=data["sender_id"],
                    seq=int(data["seq"]),
                    threat=bool(data["threat"]),
                    route_id=data["route_id"],
                    score=float(data["score"]),
                    cluster_id=data["cluster_id"],
                    timestamp=float(data["timestamp"]),
                )
                self._receive(msg)
            except (json.JSONDecodeError, KeyError, ValueError):
                pass

    def _receive(self, msg: LanGossipMessage) -> None:
        key = f"{msg.sender_id}:{msg.seq}"
        if key in self._seen:
            return
        self._seen.add(key)
        self._inbox.append(msg)

    def drain(self, limit: int = 100) -> List[LanGossipMessage]:
        self._drain_file_drop()
        batch = self._inbox[:limit]
        self._inbox = self._inbox[limit:]
        return batch

    def status(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "port": self.port,
            "inbox_pending": len(self._inbox),
            "seen": len(self._seen),
            "drop_dir": str(DROP_DIR),
            "protocol": "udp+json",
            "airgapped_lan": True,
        }