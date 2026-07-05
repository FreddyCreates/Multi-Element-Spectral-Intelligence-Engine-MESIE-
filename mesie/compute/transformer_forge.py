"""ST-φ Transformer Forge — mint virtual native models from corpus + registry specs."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.compute.spectral_transformer import STPhiConfig, SpectralTransformerPhi
from mesie.version_info import MESIE_VERSION, TRANSFORMER_FORGE_VERSION

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "deliverables" / "compute" / "NATIVE_MODEL_REGISTRY.json"
FORGE_DIR = ROOT / "deliverables" / "compute" / "forged"
FORGE_STATE = FORGE_DIR / "TRANSFORMER_FORGE_STATE.json"


def _sha256_json(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def load_registry() -> Dict[str, Any]:
    if not REGISTRY.is_file():
        write_registry()
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def write_registry() -> Path:
    from mesie.mcp.native_config import build_native_model_registry

    payload = build_native_model_registry()
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return REGISTRY


def _virtual_param_count(spec: Dict[str, Any]) -> int:
    layers = int(spec.get("n_layers", 2))
    d = int(spec.get("d_model", 256))
    heads = int(spec.get("n_heads", 8))
    virtual_scale = float(spec.get("virtual_param_scale", 1.0))
    base = layers * (4 * d * d + 2 * d * heads)
    return int(base * virtual_scale)


def forge_model(
    model_id: str,
    *,
    corpus_sample: Optional[str] = None,
    mode: str = "fast",
) -> Dict[str, Any]:
    """Forge a spectral virtual model — deterministic weights from registry spec."""
    reg = load_registry()
    models = reg.get("models", {})
    spec = models.get(model_id)
    if not spec:
        return {"ok": False, "error": f"unknown model_id: {model_id}", "available": list(models.keys())}

    cfg = STPhiConfig(
        model_id=model_id,
        d_model=int(spec.get("d_model", 256)),
        n_heads=int(spec.get("n_heads", 8)),
        n_layers=int(spec.get("n_layers", 2)),
        seq_len=int(spec.get("seq_len", 16)),
        mode=mode,
    )
    encoder = SpectralTransformerPhi(cfg)
    probe = corpus_sample or spec.get("probe_text", "MESIE sovereign spectral forge")
    vector = encoder.encode(probe).tolist()

    artifact = {
        "model_id": model_id,
        "family": spec.get("family", "ST-φ"),
        "virtual_params": _virtual_param_count(spec),
        "effective_params_label": spec.get("effective_params", ""),
        "dims": cfg.d_model,
        "native": True,
        "third_party_inference": False,
        "probe_hash": _sha256_json({"probe": probe, "vector": vector[:8]}),
        "mesie_version": MESIE_VERSION,
        "forge_version": TRANSFORMER_FORGE_VERSION,
        "forged_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    FORGE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FORGE_DIR / f"{model_id.replace('/', '_')}.json"
    out_path.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")

    state = {"last_forge": artifact, "forge_count": 0}
    if FORGE_STATE.is_file():
        try:
            state = json.loads(FORGE_STATE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    state["forge_count"] = int(state.get("forge_count", 0)) + 1
    state["last_forge"] = artifact
    FORGE_STATE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    return {"ok": True, "artifact": artifact, "path": str(out_path), "vector_preview": vector[:8]}


def forge_all_nova() -> Dict[str, Any]:
    reg = load_registry()
    forged: List[Dict[str, Any]] = []
    for mid in reg.get("models", {}):
        if "NOVA" in mid or "NOVAMINI" in mid or "MININOVA" in mid:
            forged.append(forge_model(mid))
    return {"ok": True, "forged": forged, "count": len(forged)}


def forge_status() -> Dict[str, Any]:
    reg = load_registry()
    state = {}
    if FORGE_STATE.is_file():
        try:
            state = json.loads(FORGE_STATE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            state = {}
    return {
        "ok": True,
        "forge_version": TRANSFORMER_FORGE_VERSION,
        "registry_path": str(REGISTRY),
        "models_registered": len(reg.get("models", {})),
        "state": state,
    }