"""Production field router — aliases, pathfinding, presets, policies."""

from __future__ import annotations

import hashlib
import json
import time
from collections import deque
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from mesie.sovereign.field_access import WorldComputerMesh

FIELD_ROUTER_VERSION = "1.0.0"
DEFAULT_ROUTES_PATH = Path(__file__).resolve().parents[2] / "library" / "field_access_routes.json"


class RoutePolicy(str, Enum):
    SHORTEST = "shortest"
    LADDER_ONLY = "ladder_only"
    ORBITAL_PREFERRED = "orbital_preferred"


@dataclass
class FieldRoute:
    """Structured production route through the sovereign field mesh."""

    ok: bool
    route_id: str
    source: str
    destination: str
    resolved_source: str
    resolved_destination: str
    hops: List[str]
    access_mode: str
    policy: str
    total_latency_ms: float
    ladder_hops: int
    path_hz: List[float]
    sovereign: bool = True
    airgapped: bool = True
    third_party: bool = False
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RoutePreset:
    preset_id: str
    source: str
    destination: str
    label: str


class FieldRouteRegistry:
    """Load aliases and preset routes from library/field_access_routes.json."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or DEFAULT_ROUTES_PATH
        self.version = FIELD_ROUTER_VERSION
        self.aliases: Dict[str, str] = {}
        self.policies: List[str] = [p.value for p in RoutePolicy]
        self.presets: List[RoutePreset] = []
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.version = str(data.get("version", FIELD_ROUTER_VERSION))
        self.aliases = {k.lower(): v for k, v in data.get("aliases", {}).items()}
        self.policies = list(data.get("policies", self.policies))
        self.presets = [
            RoutePreset(
                preset_id=p["id"],
                source=p["from"],
                destination=p["to"],
                label=p.get("label", p["id"]),
            )
            for p in data.get("presets", [])
        ]

    def resolve(self, node_ref: str, mesh_nodes: Dict[str, Any]) -> str:
        key = node_ref.strip().lower()
        if key in mesh_nodes:
            return key
        if key in self.aliases:
            return self.aliases[key]
        alias_target = self.aliases.get(key)
        if alias_target and alias_target in mesh_nodes:
            return alias_target
        if key.startswith("anchor:"):
            anchor = key.split(":", 1)[1]
            for nid, node in mesh_nodes.items():
                meta = getattr(node, "metadata", {}) or {}
                if anchor in str(meta) or anchor in nid:
                    return nid
        return node_ref


class FieldRouter:
    """Production router over the world-computer field mesh."""

    def __init__(self, mesh: WorldComputerMesh, registry: Optional[FieldRouteRegistry] = None) -> None:
        self.mesh = mesh
        self.registry = registry or FieldRouteRegistry()
        self._graph: Dict[str, List[str]] = {}
        self._rebuild_graph()

    def _rebuild_graph(self) -> None:
        nodes = self.mesh.field_nodes
        g: Dict[str, set[str]] = {nid: set() for nid in nodes}

        def link(a: str, b: str) -> None:
            if a in g and b in g:
                g[a].add(b)
                g[b].add(a)

        if "ground-schumann" in g and "ionosphere-cavity" in g:
            link("ground-schumann", "ionosphere-cavity")

        ladder_ids = sorted(nid for nid in g if nid.startswith("ladder-"))
        for i in range(len(ladder_ids) - 1):
            link(ladder_ids[i], ladder_ids[i + 1])

        if ladder_ids and "ionosphere-cavity" in g:
            link("ionosphere-cavity", ladder_ids[0])
        if ladder_ids and "world-computer-root" in g:
            link(ladder_ids[-1], "world-computer-root")
            for lid in ladder_ids:
                link(lid, "world-computer-root")

        orbital_ids = [nid for nid in g if nid.startswith("orbital-")]
        for oid in orbital_ids:
            node = nodes[oid]
            tier = node.ladder_tier_id
            if tier is not None:
                lid = f"ladder-{tier}"
                if lid not in g and ladder_ids:
                    lid = ladder_ids[min(tier, len(ladder_ids) - 1)]
                link(oid, lid)
            if "world-computer-root" in g:
                link(oid, "world-computer-root")

        leo = [n for n in orbital_ids if "leo" in n]
        geo = [n for n in orbital_ids if "geo" in n]
        meo = [n for n in orbital_ids if "meo" in n]
        for l in leo:
            for m in meo:
                link(l, m)
        for m in meo:
            for ge in geo:
                link(m, ge)

        self._graph = {k: sorted(v) for k, v in g.items()}

    def resolve(self, node_ref: str) -> str:
        return self.registry.resolve(node_ref, self.mesh.field_nodes)

    def neighbors(self, node_ref: str) -> List[str]:
        nid = self.resolve(node_ref)
        return list(self._graph.get(nid, []))

    def _bfs(self, src: str, dst: str, *, allowed: Optional[set[str]] = None) -> List[str]:
        if src not in self.mesh.field_nodes or dst not in self.mesh.field_nodes:
            return []
        if src == dst:
            return [src]
        q: deque[str] = deque([src])
        prev: Dict[str, Optional[str]] = {src: None}
        while q:
            cur = q.popleft()
            for nxt in self._graph.get(cur, []):
                if allowed is not None and nxt not in allowed and nxt != dst:
                    continue
                if nxt in prev:
                    continue
                prev[nxt] = cur
                if nxt == dst:
                    path = [dst]
                    while prev[path[-1]] is not None:
                        path.append(prev[path[-1]])  # type: ignore[arg-type]
                    return list(reversed(path))
                q.append(nxt)
        return []

    def _allowed_nodes(self, policy: RoutePolicy) -> Optional[set[str]]:
        if policy == RoutePolicy.LADDER_ONLY:
            return {nid for nid in self.mesh.field_nodes if nid.startswith("ladder-") or nid in {"ground-schumann", "ionosphere-cavity", "world-computer-root"}}
        return None

    def _compute_segment(self, src_id: str, dst_id: str) -> Dict[str, Any]:
        src = self.mesh.field_nodes[src_id]
        dst = self.mesh.field_nodes[dst_id]
        if src.orbital_node_id and dst.orbital_node_id:
            seg = self.mesh.orbital_network.compute_route(src.orbital_node_id, dst.orbital_node_id)
            if "error" not in seg:
                return {
                    "access": "orbital_hz_ladder",
                    "latency_ms": float(seg.get("total_latency_ms", 0)),
                    "ladder_hops": int(seg.get("hops", 0)),
                }
        tier_src = self.mesh.ladder.frequency_to_tier(src.primary_hz())
        tier_dst = self.mesh.ladder.frequency_to_tier(dst.primary_hz())
        path = []
        if tier_src and tier_dst:
            path = self.mesh.ladder.route_vertical(tier_src.tier_id, tier_dst.tier_id)
        return {
            "access": "frequency_field",
            "latency_ms": sum(l.latency_ms for l in path),
            "ladder_hops": len(path),
        }

    def route(
        self,
        source: str,
        destination: str,
        *,
        policy: str | RoutePolicy = RoutePolicy.SHORTEST,
    ) -> FieldRoute:
        pol = RoutePolicy(policy) if isinstance(policy, str) else policy
        src_raw, dst_raw = source, destination
        src = self.resolve(source)
        dst = self.resolve(destination)

        if src not in self.mesh.field_nodes:
            return self._fail(src_raw, dst_raw, src, dst, pol, f"unknown source: {source}")
        if dst not in self.mesh.field_nodes:
            return self._fail(src_raw, dst_raw, src, dst, pol, f"unknown destination: {destination}")

        allowed = self._allowed_nodes(pol)
        hops = self._bfs(src, dst, allowed=allowed)

        if not hops and pol == RoutePolicy.ORBITAL_PREFERRED:
            hops = self._bfs(src, dst)

        if not hops:
            direct = self.mesh.route_field(src, dst)
            if direct.get("ok"):
                hops = [src, dst]
            else:
                return self._fail(src_raw, dst_raw, src, dst, pol, direct.get("error", "no path"))

        total_ms = 0.0
        ladder_hops = 0
        access_modes: List[str] = []
        for i in range(len(hops) - 1):
            seg = self._compute_segment(hops[i], hops[i + 1])
            total_ms += seg["latency_ms"]
            ladder_hops += seg["ladder_hops"]
            access_modes.append(seg["access"])

        if all(m == "orbital_hz_ladder" for m in access_modes):
            access_mode = "orbital_hz_ladder"
        elif any(m == "orbital_hz_ladder" for m in access_modes):
            access_mode = "mixed"
        else:
            access_mode = "frequency_field"

        path_hz = [self.mesh.field_nodes[h].primary_hz() for h in hops]
        route_key = f"{src}>{dst}:{pol.value}:{','.join(hops)}"
        route_id = hashlib.sha256(route_key.encode()).hexdigest()[:16]

        return FieldRoute(
            ok=True,
            route_id=route_id,
            source=src_raw,
            destination=dst_raw,
            resolved_source=src,
            resolved_destination=dst,
            hops=hops,
            access_mode=access_mode,
            policy=pol.value,
            total_latency_ms=round(total_ms, 3),
            ladder_hops=ladder_hops,
            path_hz=path_hz,
            metadata={"segments": len(hops) - 1, "version": FIELD_ROUTER_VERSION},
        )

    def route_to_anchor(self, source: str, anchor_id: str) -> FieldRoute:
        anchor_id = anchor_id.lower().replace("anchor:", "")
        for a in self.mesh.bridge.anchors:
            if a.anchor_id == anchor_id or a.name.lower() == anchor_id:
                role_map = {
                    "ground": "ground-schumann",
                    "ionosphere": "ionosphere-cavity",
                    "ladder": "ladder-0",
                    "orbital": "orbital-leo-edge-000",
                    "world": "world-computer-root",
                }
                dest = role_map.get(a.role.value, "world-computer-root")
                route = self.route(source, dest)
                route.metadata["target_anchor"] = a.anchor_id
                route.metadata["anchor_hz"] = a.frequency_Hz
                return route
        return self._fail(source, anchor_id, self.resolve(source), anchor_id, RoutePolicy.SHORTEST, f"unknown anchor: {anchor_id}")

    def list_presets(self) -> List[Dict[str, Any]]:
        out = []
        for p in self.registry.presets:
            r = self.route(p.source, p.destination)
            out.append({
                "preset_id": p.preset_id,
                "label": p.label,
                "from": p.source,
                "to": p.destination,
                "ok": r.ok,
                "hops": len(r.hops),
                "latency_ms": r.total_latency_ms,
                "access_mode": r.access_mode,
            })
        return out

    def route_table(self) -> Dict[str, Any]:
        return {
            "version": self.registry.version,
            "router_version": FIELD_ROUTER_VERSION,
            "nodes": len(self.mesh.field_nodes),
            "aliases": len(self.registry.aliases),
            "presets": len(self.registry.presets),
            "policies": self.registry.policies,
            "graph_edges": sum(len(v) for v in self._graph.values()) // 2,
        }

    def health(self) -> Dict[str, Any]:
        nodes = [n for n in self.mesh.field_nodes.values() if n.active]
        sample = self.route("ground", "world")
        return {
            "ok": sample.ok,
            "router_version": FIELD_ROUTER_VERSION,
            "registry_version": self.registry.version,
            "active_nodes": len(nodes),
            "aliases": len(self.registry.aliases),
            "graph_ready": len(self._graph) > 0,
            "default_route_ok": sample.ok,
            "sovereign": True,
            "third_party": False,
            "airgapped": True,
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    def _fail(
        self,
        src_raw: str,
        dst_raw: str,
        src: str,
        dst: str,
        pol: RoutePolicy,
        error: str,
    ) -> FieldRoute:
        return FieldRoute(
            ok=False,
            route_id="",
            source=src_raw,
            destination=dst_raw,
            resolved_source=src,
            resolved_destination=dst,
            hops=[],
            access_mode="none",
            policy=pol.value,
            total_latency_ms=0.0,
            ladder_hops=0,
            path_hz=[],
            error=error,
        )