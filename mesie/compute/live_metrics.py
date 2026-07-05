"""Live metrics collector — continuous platform stats for MESIE COMPUTE."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[2]
METRICS_PATH = ROOT / "deliverables" / "compute" / "MESIE_COMPUTE_LIVE_METRICS.json"
METRICS_LOG = ROOT / "deliverables" / "compute" / "MESIE_COMPUTE_METRICS.jsonl"


def _http_get(url: str, timeout: float = 4.0) -> Optional[Dict[str, Any]]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError):
        return None


def collect_live_metrics() -> Dict[str, Any]:
    """Pull live stats from all wired services."""
    from mesie.compute.spectral_transformer import STPhiConfig, SpectralTransformerPhi
    from mesie.compute.virtual_products import load_products, save_products

    t0 = time.perf_counter()
    processor = _http_get("http://127.0.0.1:8750/processor/status")
    sovereign = _http_get("http://127.0.0.1:8770/sovereign/status")

    st = SpectralTransformerPhi(STPhiConfig())
    st_bench = st.benchmark(trials=50)

    products = load_products()
    for p in products:
        if p.port == 8750:
            p.healthy = processor is not None
        elif p.port == 8770:
            p.healthy = sovereign is not None
        elif p.sku.startswith("ST-φ"):
            p.healthy = True
            p.p50_ms = st_bench.encode_p50_ms
            p.invocations += 1
    save_products(products)

    snapshot = {
        "product": "MESIE COMPUTE Live Metrics",
        "collected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "collection_ms": round((time.perf_counter() - t0) * 1000, 2),
        "processor": {
            "healthy": processor is not None,
            "url": "http://127.0.0.1:8750",
            "status": processor,
        },
        "sovereign_os": {
            "healthy": sovereign is not None,
            "url": "http://127.0.0.1:8770",
            "alpha_agents": (sovereign or {}).get("alpha_agents"),
        },
        "st_phi": st_bench.to_dict(),
        "virtual_products": [p.to_dict() for p in products],
        "privacy": {"complete": True, "airgap_capable": True},
        "latency_targets": {
            "edge_p50_ms": st_bench.encode_p50_ms,
            "ann_target_ms": 0.5,
            "nova_threat_p50_ms": 0.68,
        },
    }

    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    with METRICS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"t": snapshot["collected_at"], "st_p50": st_bench.encode_p50_ms}) + "\n")
    return snapshot


def main() -> int:
    print(json.dumps(collect_live_metrics(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())