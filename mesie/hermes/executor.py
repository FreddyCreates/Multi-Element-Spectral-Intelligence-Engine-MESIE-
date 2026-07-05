"""HERMES executor — local simulate worker ops + deploy pack status."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from mesie.hermes.forge import forge_hermes_fleet
from mesie.hermes.nova_protocol import build_nova_protocol_hermes
from mesie.hermes.registry import worker_by_id

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "deliverables" / "hermes"


class HermesExecutor:
    """Route HERMES worker invocations to native MESIE backends."""

    def invoke(self, worker_id: str, *, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        w = worker_by_id(worker_id)
        if not w:
            return {"ok": False, "error": f"unknown worker: {worker_id}"}

        body = payload or {}
        handlers = {
            "hermes-ingest": self._ingest,
            "hermes-embed": self._embed,
            "hermes-validate": self._validate,
            "hermes-match": self._match,
            "hermes-envelope": self._envelope,
            "hermes-icp-cli": self._icp_cli,
            "hermes-wrangler": self._wrangler,
            "hermes-sdk-pack": self._sdk_pack,
            "hermes-json-corpus": self._corpus,
            "hermes-nova-pulse": self._nova_pulse,
            "hermes-clean-feed": self._clean_feed,
            "hermes-deploy-shot": self._deploy_shot,
        }
        fn = handlers.get(worker_id, self._package_only)
        result = fn(body)
        return {
            "ok": result.get("ok", True),
            "worker_id": worker_id,
            "slot": w.slot,
            "category": w.category,
            "result": result,
        }

    def _package_only(self, body: Dict[str, Any]) -> Dict[str, Any]:
        wid = body.get("worker_id", "unknown")
        pkg = OUT / "packages" / f"{wid}.json"
        if pkg.is_file():
            return {"ok": True, "package": json.loads(pkg.read_text(encoding="utf-8"))}
        return {"ok": False, "error": "package not forged — run forge first"}

    def _ingest(self, body: Dict[str, Any]) -> Dict[str, Any]:
        from mesie.processor.virtual_processor import VirtualProcessor

        vp = VirtualProcessor()
        record = body.get("record") or {"record_id": body.get("record_id", "hermes-ingest")}
        return {"ok": True, "ingest": {"record": record, "vp_status": vp.status()}}

    def _embed(self, body: Dict[str, Any]) -> Dict[str, Any]:
        from mesie.compute.hub import MESIEComputeHub

        text = body.get("payload") or body.get("text") or "HERMES embed"
        model = str(body.get("model", "ST-φ-256"))
        return MESIEComputeHub(model_id=model).encode(text)

    def _validate(self, _: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": True, "validate": {"schema_levels": "1-6", "gate": "spectral_json"}}

    def _match(self, body: Dict[str, Any]) -> Dict[str, Any]:
        from mesie.processor.virtual_processor import VirtualProcessor

        vp = VirtualProcessor()
        ref = body.get("reference", "ref-earthquake-psd-001")
        m = vp.match_pair(ref, ref)
        return {"ok": m.ok, "match": m.output if m.ok else m.error}

    def _envelope(self, body: Dict[str, Any]) -> Dict[str, Any]:
        from mesie.platform.mvp_bridge import bridge_envelope

        sid = body.get("service_id", "model-hub")
        return bridge_envelope(sid, payload=body.get("payload"))

    def _icp_cli(self, _: Dict[str, Any]) -> Dict[str, Any]:
        path = OUT / "icp" / "HERMES_ICP_CLI.json"
        if not path.is_file():
            forge_hermes_fleet(zip_sdk=False)
        return {"ok": True, "icp_cli": json.loads(path.read_text(encoding="utf-8"))}

    def _wrangler(self, _: Dict[str, Any]) -> Dict[str, Any]:
        root = OUT / "wrangler.toml"
        workers = list((OUT / "workers").glob("*/wrangler.toml")) if (OUT / "workers").is_dir() else []
        return {
            "ok": root.is_file(),
            "wrangler_root": root.read_text(encoding="utf-8")[:800] if root.is_file() else None,
            "worker_tomls": [str(p) for p in workers],
        }

    def _sdk_pack(self, _: Dict[str, Any]) -> Dict[str, Any]:
        path = OUT / "sdk" / "HERMES_SDK_MANIFEST.json"
        if not path.is_file():
            forge_hermes_fleet()
        return {"ok": True, "sdk": json.loads(path.read_text(encoding="utf-8"))}

    def _corpus(self, body: Dict[str, Any]) -> Dict[str, Any]:
        from mesie.platform.worker_gateway import PlatformWorkerGateway

        return PlatformWorkerGateway().invoke(
            "producer-pipeline",
            payload={"status_only": body.get("status_only", False)},
        )

    def _nova_pulse(self, _: Dict[str, Any]) -> Dict[str, Any]:
        from mesie.grok.protocol import build_protocol_manifest

        return {"ok": True, "nova": build_protocol_manifest()}

    def _clean_feed(self, _: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": True, "clean_feed": build_nova_protocol_hermes()["clean_feed_doctrine"]}

    def _deploy_shot(self, body: Dict[str, Any]) -> Dict[str, Any]:
        if body.get("forge") or not (OUT / "DEPLOY_SHOT.json").is_file():
            forged = forge_hermes_fleet()
        else:
            forged = {"ok": True, "note": "using existing pack"}
        shot = json.loads((OUT / "DEPLOY_SHOT.json").read_text(encoding="utf-8"))
        return {"ok": True, "deploy_shot": shot, "forge": forged}