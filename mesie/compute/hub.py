"""MESIE COMPUTE Hub — wires transformers, kernel, products, squads, live metrics."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[2]
HUB_MANIFEST = ROOT / "deliverables" / "compute" / "MESIE_COMPUTE_HUB.json"


class MESIEComputeHub:
    """First-class compute orchestrator used by processor, sovereign OS, and agents."""

    def __init__(self, model_id: str = "ST-φ-256") -> None:
        from mesie.compute.spectral_transformer import STPhiConfig, SpectralTransformerPhi, write_model_registry
        from mesie.compute.phi_kernel import PhiKernel

        cfg_map = {
            "ST-φ-128": STPhiConfig(model_id="ST-φ-128", d_model=128, n_heads=4, n_layers=1, seq_len=16, mode="fast"),
            "ST-φ-256": STPhiConfig(model_id="ST-φ-256", d_model=256, n_heads=8, n_layers=2, seq_len=16, mode="fast"),
            "ST-φ-512": STPhiConfig(model_id="ST-φ-512", d_model=512, n_heads=8, n_layers=3, seq_len=32, mode="full"),
        }
        self.transformer = SpectralTransformerPhi(cfg_map.get(model_id, cfg_map["ST-φ-256"]))
        self.kernel = PhiKernel()
        self.model_id = model_id
        write_model_registry()

    def encode(self, payload: Any) -> Dict[str, Any]:
        from mesie.compute.virtual_products import record_invocation

        t0 = time.perf_counter()
        vec = self.transformer.encode(payload)
        ms = (time.perf_counter() - t0) * 1000
        record_invocation(self.model_id, ms)
        slice_rec = self.kernel.compress_embedding(vec, source="st_phi_encode")
        return {
            "ok": True,
            "model": self.model_id,
            "dims": len(vec),
            "latency_ms": round(ms, 4),
            "embedding_preview": vec[:8].tolist(),
            "phi_kernel_slice": slice_rec.to_dict(),
            "native": True,
            "vs_huggingface": "no_torch",
        }

    def full_benchmark(self, *, trials: int = 200) -> Dict[str, Any]:
        from mesie.compute.virtual_products import record_invocation
        from mesie.sdk.fast_compute import FastSpectralCompute
        from data import load_reference_record

        st = self.transformer.benchmark(trials=trials)
        record_invocation(self.model_id, st.encode_p50_ms)

        fc = FastSpectralCompute()
        try:
            fc.load_library_index()
            ann = fc.benchmark_ann_p50(load_reference_record("ref-earthquake-psd-001"), n_trials=min(trials, 100))
            ann_stats = ann.to_dict()
        except Exception:
            ann_stats = {"p50_ms": None, "note": "index not loaded"}

        from mesie.processor.virtual_processor import VirtualProcessor

        vp = VirtualProcessor()
        vp_bench = vp.benchmark(trials=min(trials, 100))

        report = {
            "product": "MESIE COMPUTE Hub Benchmark",
            "trials": trials,
            "st_phi": st.to_dict(),
            "fast_ann": ann_stats,
            "virtual_processor": vp_bench.output if vp_bench.ok else {},
            "phi_kernel": self.kernel.export_index(),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        HUB_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        HUB_MANIFEST.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return report

    def snapshot(self) -> Dict[str, Any]:
        from mesie.compute.live_metrics import collect_live_metrics
        from mesie.compute.tri_agent_squads import list_squads
        from mesie.compute.virtual_products import load_products

        return {
            "hub": "MESIE COMPUTE",
            "first_class": True,
            "model": self.model_id,
            "products": [p.to_dict() for p in load_products()],
            "squads": list_squads(),
            "live_metrics": collect_live_metrics(),
        }


def compute_hub_snapshot(model_id: str = "ST-φ-256") -> Dict[str, Any]:
    return MESIEComputeHub(model_id=model_id).snapshot()


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="MESIE COMPUTE Hub")
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--snapshot", action="store_true")
    parser.add_argument("--encode", default="")
    parser.add_argument("--model", default="ST-φ-256")
    parser.add_argument("--trials", type=int, default=200)
    args = parser.parse_args()

    hub = MESIEComputeHub(model_id=args.model)
    if args.benchmark:
        print(json.dumps(hub.full_benchmark(trials=args.trials), indent=2))
        return 0
    if args.snapshot:
        print(json.dumps(hub.snapshot(), indent=2))
        return 0
    if args.encode:
        payload = json.loads(args.encode) if args.encode.startswith("{") else args.encode
        print(json.dumps(hub.encode(payload), indent=2))
        return 0
    print(json.dumps(hub.snapshot(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())