"""Multi-machine sovereign mesh — LAN file-drop peer sync (no internet)."""

from __future__ import annotations

import hashlib
import json
import socket
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.enterprise.receipt_chain import ComputationalReceiptChain
from mesie.sovereign.field_access import get_field_access_engine

MESH_VERSION = "1.0.0"
DEFAULT_MESH_DIR = Path(__file__).resolve().parents[2] / "library" / "mesh_peers"


@dataclass
class MeshPeer:
    peer_id: str
    hostname: str
    lan_ip: str
    sovereign: bool = True
    airgapped: bool = True
    third_party: bool = False
    field_nodes: int = 0
    last_sync: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MeshExportBundle:
    peer_id: str
    version: str
    route_table: Dict[str, Any]
    receipt_chain: Dict[str, Any]
    field_status: Dict[str, Any]
    exported_at: str
    bundle_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SovereignMesh:
    """Export/import route table + receipt chain for LAN sovereign peers."""

    def __init__(self, mesh_dir: Optional[Path] = None) -> None:
        self.mesh_dir = mesh_dir or DEFAULT_MESH_DIR
        self.mesh_dir.mkdir(parents=True, exist_ok=True)
        self.peer_id = hashlib.sha256(socket.gethostname().encode()).hexdigest()[:12]

    def local_peer(self) -> MeshPeer:
        fa = get_field_access_engine()
        st = fa.status()
        return MeshPeer(
            peer_id=self.peer_id,
            hostname=socket.gethostname(),
            lan_ip=self._lan_ip(),
            field_nodes=int(st.get("field_nodes", 0)),
            last_sync=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    def export_bundle(self, receipts: Optional[ComputationalReceiptChain] = None) -> MeshExportBundle:
        fa = get_field_access_engine()
        rc = receipts or ComputationalReceiptChain()
        route_table = fa.route_table()
        field_status = fa.status()
        exported_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        peer = self.local_peer()
        payload = {
            "peer_id": self.peer_id,
            "hostname": peer.hostname,
            "lan_ip": peer.lan_ip,
            "version": MESH_VERSION,
            "route_table": route_table,
            "receipt_chain": rc.to_dict(),
            "field_status": {
                "airgapped": field_status.get("airgapped"),
                "sovereign": field_status.get("sovereign"),
                "field_nodes": field_status.get("field_nodes"),
            },
            "exported_at": exported_at,
        }
        bundle_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:24]
        bundle = MeshExportBundle(
            peer_id=self.peer_id,
            version=MESH_VERSION,
            route_table=route_table,
            receipt_chain=rc.to_dict(),
            field_status=payload["field_status"],
            exported_at=exported_at,
            bundle_hash=bundle_hash,
        )
        out = self.mesh_dir / f"peer_{self.peer_id}.json"
        out.write_text(json.dumps(bundle.to_dict(), indent=2), encoding="utf-8")
        return bundle

    def list_peers(self) -> List[MeshPeer]:
        peers: List[MeshPeer] = []
        for p in sorted(self.mesh_dir.glob("peer_*.json")):
            data = json.loads(p.read_text(encoding="utf-8"))
            peers.append(
                MeshPeer(
                    peer_id=data["peer_id"],
                    hostname=data.get("hostname", "remote"),
                    lan_ip=data.get("lan_ip", "0.0.0.0"),
                    field_nodes=int(data.get("field_status", {}).get("field_nodes", 0)),
                    last_sync=data.get("exported_at", ""),
                )
            )
        return peers

    def import_peer(self, peer_id: str) -> Dict[str, Any]:
        path = self.mesh_dir / f"peer_{peer_id}.json"
        if not path.exists():
            return {"ok": False, "error": f"peer not found: {peer_id}"}
        data = json.loads(path.read_text(encoding="utf-8"))
        return {
            "ok": True,
            "peer_id": peer_id,
            "bundle_hash": data.get("bundle_hash"),
            "routes": len(data.get("route_table", {}).get("presets", [])),
            "receipts": len(data.get("receipt_chain", {}).get("receipts", [])),
            "airgapped": data.get("field_status", {}).get("airgapped"),
        }

    @staticmethod
    def _lan_ip() -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("10.255.255.255", 1))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except OSError:
            return "127.0.0.1"