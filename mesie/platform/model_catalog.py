"""Unified catalog of all sovereign high-end AI models."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from mesie.version_info import MESIE_VERSION

ROOT = Path(__file__).resolve().parents[2]


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _corpus_count() -> int:
    corpus = ROOT / "deliverables" / "ml" / "CORPUS.jsonl"
    if not corpus.is_file():
        return 0
    return sum(1 for line in corpus.read_text(encoding="utf-8").splitlines() if line.strip())


def build_unified_model_catalog() -> Dict[str, Any]:
    """Aggregate NOVA, ST-φ, SOLUS, foundation, cognitive, and data tiers."""
    native_reg = _load_json(ROOT / "deliverables" / "compute" / "NATIVE_MODEL_REGISTRY.json")
    st_phi = _load_json(ROOT / "deliverables" / "compute" / "ST_PHI_REGISTRY.json")
    auro = _load_json(ROOT / "deliverables" / "Auro_Native_Speaking_Manifest.json")
    design = _load_json(ROOT / "deliverables" / "design" / "DESIGN_ECOSYSTEM_MANIFEST.json")

    tiers: List[Dict[str, Any]] = []

    nova_models = native_reg.get("models", {})
    for model_id, spec in nova_models.items():
        tiers.append({
            "tier": "nova_virtual" if "NOVA" in model_id or "MINI" in model_id else "edge_transformer",
            "model_id": model_id,
            "family": spec.get("family"),
            "effective_params": spec.get("effective_params"),
            "d_model": spec.get("d_model"),
            "n_layers": spec.get("n_layers"),
            "native": True,
            "third_party_inference": False,
        })

    for m in st_phi.get("models", []):
        mid = m.get("model_id")
        if mid and not any(t["model_id"] == mid for t in tiers):
            tiers.append({
                "tier": "edge_transformer",
                "model_id": mid,
                "family": "ST-φ",
                "d_model": m.get("d_model"),
                "n_layers": m.get("n_layers"),
                "native": True,
                "third_party_inference": False,
            })

    tiers.append({
        "tier": "foundation",
        "model_id": "SpectralFoundationModel",
        "family": "foundation",
        "effective_params": "MoE 12-layer",
        "d_model": 256,
        "n_layers": 12,
        "n_experts": 8,
        "max_seq_len": 512,
        "native": True,
        "third_party_inference": False,
    })

    for model_id, layer in [
        ("solus-logic-model", "logic"),
        ("solus-reasoning-model", "reasoning"),
        ("solus-emergence-model", "emergence"),
        ("solus-adaptation-model", "adaptation"),
    ]:
        tiers.append({
            "tier": "solus_formal",
            "model_id": model_id,
            "family": "SOLUS",
            "layer": layer,
            "formula": "Logic ⊗ Reasoning ⊗ Emergence ⊗ Adaptation",
            "native": True,
            "third_party_inference": False,
        })

    auro_lm = (auro.get("status") or {}).get("lm") or {}
    tiers.append({
        "tier": "speaking_intelligence",
        "model_id": auro_lm.get("model_id", "AuroNativeLM-v1"),
        "family": "AURO",
        "knowledge_entries": auro_lm.get("knowledge_entries", 32),
        "reasoning_rules": auro_lm.get("reasoning_rules", 4),
        "native": True,
        "third_party_inference": False,
    })

    tiers.append({
        "tier": "cognitive_connectome",
        "model_id": "NeuroAIXEngine",
        "family": "NeuroAIX",
        "brain_regions": 44,
        "tracts": 68,
        "native": True,
        "third_party_inference": False,
    })

    tiers.append({
        "tier": "design_agents",
        "model_id": "LatinDesignAgents-100",
        "family": "DesignReality",
        "agent_count": design.get("paradigm_count", 100),
        "core_count": design.get("core_count", 10),
        "native": True,
        "third_party_inference": False,
    })

    return {
        "protocol": "MESIE-UNIFIED-MODEL-CATALOG/1.0",
        "mesie_version": MESIE_VERSION,
        "third_party_inference": False,
        "virtual_scaling": native_reg.get("virtual_scaling", "spectral_param_compression"),
        "model_count": len(tiers),
        "corpus_records": _corpus_count(),
        "tiers": tiers,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }