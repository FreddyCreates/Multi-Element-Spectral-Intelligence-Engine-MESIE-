"""Platform worker gateway — dispatch service invocations to native backends."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.platform.mvp_bridge import bridge_envelope
from mesie.platform.registry import service_by_id
from mesie.version_info import MESIE_VERSION

ROOT = Path(__file__).resolve().parents[2]
FEED = ROOT / "deliverables" / "platform" / "PLATFORM_WORKER_FEED.jsonl"


class PlatformWorkerGateway:
    """Route platform service calls through WorkerBus + native engines."""

    def __init__(self, *, mission_id: str = "platform-default") -> None:
        self.mission_id = mission_id

    def invoke(self, service_id: str, *, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        svc = service_by_id(service_id)
        if not svc:
            return {"ok": False, "error": f"unknown service: {service_id}"}

        envelope_wrap = bridge_envelope(service_id, payload=payload, mission_id=self.mission_id)
        if not envelope_wrap.get("ok"):
            return envelope_wrap

        handlers = {
            "platform_models": self._models,
            "platform_encode": self._encode,
            "platform_forge": self._forge,
            "platform_solus": self._solus,
            "platform_auro": self._auro,
            "platform_producer": self._producer,
            "platform_design": self._design,
            "platform_status": self._status,
            "platform_benchmark": self._benchmark,
            "platform_compute": self._compute,
            "virtual_silicon_catalog": self._virtual_silicon,
            "platform_hermes": self._hermes,
            "processor_status": self._processor_status,
        }
        fn = handlers.get(svc.worker_action, self._passthrough)
        result = fn(service_id, payload or {})
        out = {
            "ok": result.get("ok", True),
            "service_id": service_id,
            "envelope": envelope_wrap["envelope"],
            "result": result,
            "mesie_version": MESIE_VERSION,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        self._log(service_id, out)
        return out

    def _log(self, service_id: str, result: Dict[str, Any]) -> None:
        FEED.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": time.time(),
            "mission_id": self.mission_id,
            "service_id": service_id,
            "ok": result.get("ok"),
        }
        with FEED.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, separators=(",", ":")) + "\n")

    def _models(self, _: str, __: Dict[str, Any]) -> Dict[str, Any]:
        from mesie.platform.model_catalog import build_unified_model_catalog

        return {"ok": True, "catalog": build_unified_model_catalog()}

    def _encode(self, _: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        from mesie.compute.hub import MESIEComputeHub

        model = str(payload.get("model", "ST-φ-256"))
        text = payload.get("payload") or payload.get("text") or "MESIE sovereign encode"
        return MESIEComputeHub(model_id=model).encode(text)

    def _forge(self, _: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        from mesie.compute.transformer_forge import forge_all_nova, forge_model

        model_id = payload.get("model_id")
        if model_id:
            return forge_model(str(model_id), corpus_sample=payload.get("probe_text"))
        return forge_all_nova()

    def _solus(self, _: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        from mesie.sdk.solus.organism import SDKSolusOrganism

        org = SDKSolusOrganism()
        freqs = payload.get("frequencies") or [1.0, 2.0, 3.0, 5.0, 8.0]
        amps = payload.get("amplitudes") or [0.5, 0.7, 0.9, 0.6, 0.8]
        ctx = payload.get("cycle_context") or {"record_id": payload.get("record_id", "platform_cycle")}
        composed = org.reason_spectral_cycle(freqs, amps, cycle_context=ctx)
        return {"ok": True, "solus": composed}

    def _auro(self, _: str, __: Dict[str, Any]) -> Dict[str, Any]:
        path = ROOT / "deliverables" / "Auro_Native_Speaking_Manifest.json"
        if not path.is_file():
            return {"ok": False, "error": "Auro manifest missing"}
        data = json.loads(path.read_text(encoding="utf-8"))
        return {"ok": True, "auro": data.get("status", {}), "eval": data.get("eval", {})}

    def _producer(self, _: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        from mesie.ml.producer import produce_cycle, producer_status

        if payload.get("status_only"):
            return {"ok": True, **producer_status()}
        return produce_cycle(forge_corpus=payload.get("forge_corpus", True), encode=payload.get("encode", True))

    def _design(self, _: str, __: Dict[str, Any]) -> Dict[str, Any]:
        from mesie.design.registry import design_ecosystem_manifest

        return {"ok": True, "design": design_ecosystem_manifest()}

    def _status(self, _: str, __: Dict[str, Any]) -> Dict[str, Any]:
        from mesie.platform.registry import platform_manifest
        from mesie.platform.mvp_bridge import bridge_manifest

        return {
            "ok": True,
            "platform": platform_manifest(),
            "bridge": bridge_manifest(),
        }

    def _benchmark(self, _: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        from mesie.compute.hub import MESIEComputeHub

        model = str(payload.get("model", "ST-φ-256"))
        trials = int(payload.get("trials", 100))
        return MESIEComputeHub(model_id=model).full_benchmark(trials=trials)

    def _compute(self, _: str, __: Dict[str, Any]) -> Dict[str, Any]:
        from mesie.compute.hub import compute_hub_snapshot
        from mesie.compute.virtual_products import load_products
        from mesie.compute.tri_agent_squads import list_squads

        return {
            "ok": True,
            "hub": compute_hub_snapshot(),
            "products": [p.to_dict() for p in load_products()],
            "squads": list_squads(),
        }

    def _virtual_silicon(self, _: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        from mesie.silicon.vs1_spec import virtual_silicon_catalog
        from mesie.silicon.virtual_chip import VirtualSiliconChip

        chip_id = str(payload.get("chip_id", "MESIE-VS1"))
        if payload.get("certify"):
            chip = VirtualSiliconChip.from_sku(chip_id)
            cert = chip.certify()
            return {
                "ok": True,
                "certification": cert.to_dict(sku_meta=chip._sku_cert_meta()),
                "chip_id": chip_id,
            }
        return {"ok": True, "catalog": virtual_silicon_catalog()}

    def _hermes(self, _: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        from mesie.hermes.executor import HermesExecutor
        from mesie.hermes.forge import forge_hermes_fleet
        from mesie.hermes.registry import hermes_manifest
        from mesie.hermes.nova_protocol import build_nova_protocol_hermes

        worker_id = payload.get("worker_id")
        if worker_id:
            return HermesExecutor().invoke(str(worker_id), payload=payload)
        if payload.get("forge"):
            return forge_hermes_fleet()
        return {
            "ok": True,
            "hermes": hermes_manifest(),
            "nova_protocol": build_nova_protocol_hermes(),
        }

    def _processor_status(self, _: str, __: Dict[str, Any]) -> Dict[str, Any]:
        import urllib.request

        try:
            with urllib.request.urlopen("http://127.0.0.1:8750/processor/status", timeout=5) as resp:
                return {"ok": True, "processor": json.loads(resp.read().decode())}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def _passthrough(self, service_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        from mesie.grok.worker_bus import WorkerBus, WorkerRole

        svc = service_by_id(service_id)
        if not svc:
            return {"ok": False, "error": "no service"}
        try:
            role = WorkerRole(svc.worker_role)
        except ValueError:
            role = WorkerRole.WORKER
        return WorkerBus(mission_id=self.mission_id).dispatch(role, svc.worker_action, payload=payload)