"""MESIE COMPUTE virtual products — SKUs with live usage stats."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
PRODUCTS_STATE = ROOT / "deliverables" / "compute" / "MESIE_COMPUTE_PRODUCTS.json"


@dataclass
class VirtualProduct:
    sku: str
    name: str
    category: str
    port: Optional[int]
    description: str
    operations: List[str] = field(default_factory=list)
    invocations: int = 0
    last_latency_ms: float = 0.0
    p50_ms: float = 0.0
    healthy: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sku": self.sku,
            "name": self.name,
            "category": self.category,
            "port": self.port,
            "description": self.description,
            "operations": self.operations,
            "invocations": self.invocations,
            "last_latency_ms": self.last_latency_ms,
            "p50_ms": self.p50_ms,
            "healthy": self.healthy,
        }


def _base_catalog() -> List[VirtualProduct]:
    return [
        VirtualProduct(
            sku="MESIE-COMPUTE-EDGE",
            name="MESIE COMPUTE Edge",
            category="processor",
            port=8750,
            description="First-class spectral compute — embed, match, signals, NOVA",
            operations=["embed", "match", "benchmark", "read_signal", "generate_text", "mesh_pulse"],
        ),
        VirtualProduct(
            sku="ST-φ-256",
            name="ST-φ Spectral Transformer 256",
            category="transformer",
            port=None,
            description="Native φ-harmonic transformer — rivals HuggingFace, no torch",
            operations=["encode", "encode_batch", "benchmark"],
        ),
        VirtualProduct(
            sku="ST-φ-512",
            name="ST-φ Spectral Transformer 512",
            category="transformer",
            port=None,
            description="Research-grade 512-dim spectral encoder",
            operations=["encode", "encode_batch", "benchmark"],
        ),
        VirtualProduct(
            sku="MESIE-φ-KERNEL",
            name="φ-Kernel Compression",
            category="kernel",
            port=None,
            description="Spectral slice compression and transfer index",
            operations=["compress_embedding", "compress_file_slices", "export_index"],
        ),
        VirtualProduct(
            sku="MESIE-FAST-ANN",
            name="Fast Spectral ANN",
            category="retrieval",
            port=None,
            description="Band-sign LSH + matrix cosine — sub-ms queries",
            operations=["cosine_search", "benchmark_ann_p50"],
        ),
        VirtualProduct(
            sku="MESIE-VS1",
            name="Virtual Silicon VS1",
            category="chip",
            port=None,
            description="Certified virtual chip lane — OTA mesh",
            operations=["certify", "benchmark_lane"],
        ),
        VirtualProduct(
            sku="MESIE-SOVEREIGN-OS",
            name="Sovereign OS Dashboard",
            category="platform",
            port=8770,
            description="Airgap, Capsula, Triple Protocol control plane",
            operations=["deploy", "bridge", "metrics"],
        ),
        VirtualProduct(
            sku="MESIE-TRI-AGENT",
            name="Tri-Agent Maintenance Squads",
            category="agents",
            port=None,
            description="Groups of 3 AI auto-agents for workflow and maintenance",
            operations=["ops_triad", "quality_triad", "intel_triad"],
        ),
        VirtualProduct(
            sku="HERMES-12",
            name="HERMES Cloudflare Fleet",
            category="edge",
            port=8750,
            description="12 workers — ingest, embed, ICP CLI, wrangler, clean feed, deploy shot",
            operations=["forge", "invoke", "nova_protocol"],
        ),
        VirtualProduct(
            sku="MESIE-AGENT-INSTALL",
            name="Agent Product Install",
            category="agent",
            port=8750,
            description="All platform services + compute products wired into coding agents",
            operations=["agent_products", "benchmark_mission"],
        ),
    ]


def load_products() -> List[VirtualProduct]:
    if not PRODUCTS_STATE.is_file():
        return _base_catalog()
    try:
        data = json.loads(PRODUCTS_STATE.read_text(encoding="utf-8"))
        return [
            VirtualProduct(**{k: v for k, v in p.items() if k in VirtualProduct.__dataclass_fields__})
            for p in data.get("products", [])
        ]
    except (json.JSONDecodeError, TypeError):
        return _base_catalog()


def save_products(products: List[VirtualProduct]) -> Path:
    PRODUCTS_STATE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "product_line": "MESIE COMPUTE",
        "first_class": True,
        "products": [p.to_dict() for p in products],
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    PRODUCTS_STATE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return PRODUCTS_STATE


def record_invocation(sku: str, latency_ms: float, *, healthy: bool = True) -> None:
    products = load_products()
    for p in products:
        if p.sku == sku:
            p.invocations += 1
            p.last_latency_ms = round(latency_ms, 4)
            if p.p50_ms == 0:
                p.p50_ms = latency_ms
            else:
                p.p50_ms = round(0.618 * latency_ms + 0.382 * p.p50_ms, 4)
            p.healthy = healthy
            break
    save_products(products)


def main() -> int:
    import json

    products = load_products()
    save_products(products)
    print(json.dumps({"products": len(products)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())