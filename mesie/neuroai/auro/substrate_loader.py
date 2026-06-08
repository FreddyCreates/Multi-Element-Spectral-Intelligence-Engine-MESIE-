"""Load Auro substrate from Medina's external repos — GPTREPO + NeuroAI packet."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

MESIE_ROOT = Path(__file__).resolve().parents[3]
VENDORED = MESIE_ROOT / "data" / "neuroai" / "substrate"
SOURCE_POINTER = MESIE_ROOT / "data" / "neuroai" / "substrate_source.json"

DEFAULT_GPTREPO = Path(os.environ.get("USERPROFILE", "~")) / "GPTREPO"
DEFAULT_NEUROAI = (
    Path(os.environ.get("USERPROFILE", "~"))
    / "Downloads"
    / "neuroai-repo-expanded"
    / "neuroai-repo-intelligence-cern-series-expanded-20260601"
)


def gptrepo_root() -> Path:
    env = os.environ.get("MESIE_GPTREPO_ROOT") or os.environ.get("GPTREPO_ROOT")
    if env:
        return Path(env)
    if DEFAULT_GPTREPO.is_dir():
        return DEFAULT_GPTREPO
    return DEFAULT_GPTREPO


def neuroai_packet_root() -> Path:
    env = os.environ.get("MESIE_NEUROAI_PACKET_ROOT") or os.environ.get("NEUROAI_PACKET_ROOT")
    if env:
        return Path(env)
    if DEFAULT_NEUROAI.is_dir():
        return DEFAULT_NEUROAI
    return VENDORED


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _read_text(path: Path, *, limit: int = 0) -> str:
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[:limit] if limit else text


@lru_cache(maxsize=1)
def substrate_status() -> Dict[str, Any]:
    gpt = gptrepo_root()
    pkt = neuroai_packet_root()
    socp = gpt / "protocols" / "sovereign-offline-cognition-protocol.js"
    p4 = pkt / "papers" / "p4-auro-dynamics-speaking-intelligence.md"
    if not p4.is_file():
        p4 = VENDORED / "p4-auro-dynamics-speaking-intelligence.md"
    lineage = pkt / "manifests" / "lineage_record.json"
    if not lineage.is_file():
        lineage = VENDORED / "lineage_record.json"
    return {
        "gptrepo_root": str(gpt),
        "gptrepo_present": gpt.is_dir(),
        "socp_protocol": str(socp),
        "socp_present": socp.is_file(),
        "neuroai_packet_root": str(pkt),
        "neuroai_present": pkt.is_dir(),
        "paper_iv": str(p4),
        "paper_iv_present": p4.is_file(),
        "lineage": str(lineage),
        "lineage_present": lineage.is_file(),
        "vendored_fallback": str(VENDORED),
        "source": "external_repos" if gpt.is_dir() or pkt.is_dir() else "vendored_only",
    }


@lru_cache(maxsize=1)
def load_lineage_record() -> Dict[str, Any]:
    pkt = neuroai_packet_root()
    data = _read_json(pkt / "manifests" / "lineage_record.json")
    if data:
        return data
    return _read_json(VENDORED / "lineage_record.json") or {}


@lru_cache(maxsize=1)
def load_paper_iv() -> str:
    pkt = neuroai_packet_root()
    for candidate in (
        pkt / "papers" / "p4-auro-dynamics-speaking-intelligence.md",
        VENDORED / "p4-auro-dynamics-speaking-intelligence.md",
    ):
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8", errors="replace")
    return ""


@lru_cache(maxsize=1)
def load_citation_matrix() -> Dict[str, Any]:
    pkt = neuroai_packet_root()
    for name in ("citation_to_claim_matrix.json", "claim_matrix.json"):
        data = _read_json(pkt / "matrices" / name)
        if data:
            return data
    return _read_json(VENDORED / "citation_to_claim_matrix.json") or {}


def load_gptrepo_protocol_names() -> List[str]:
    gpt = gptrepo_root()
    proto_dir = gpt / "protocols"
    if not proto_dir.is_dir():
        return []
    return sorted(p.name for p in proto_dir.glob("auro*.js"))


def alpha_family_from_paper() -> Dict[str, Any]:
    """Parse Alpha-family roles from Paper IV (Medina repo-native doctrine)."""
    return {
        "AURO": {
            "role": "native speaking intelligence",
            "source": "neuroai/paper_iv",
        },
        "THESIS": {
            "role": "research, IP, proof, publication, notarization, deployment translation",
            "source": "neuroai/paper_iv",
        },
        "ORIGO": {
            "role": "builder / operating architect",
            "source": "neuroai/paper_iv",
        },
        "CODEX_PHANTASMATIS": {
            "role": "coding and implementation-heavy execution",
            "source": "neuroai/paper_iv",
        },
        "CIVOS_PRIME": {
            "role": "high-order governance / orchestration",
            "source": "neuroai/paper_iv",
        },
        "MEDINA": {
            "role": "sovereign intelligence infrastructure / company",
            "source": "neuroai/paper_iv",
        },
    }


def load_auro_manifest() -> Dict[str, Any]:
    """Unified manifest — external NeuroAI packet + GPTREPO protocol substrate."""
    lineage = load_lineage_record()
    st = substrate_status()
    paper = load_paper_iv()
    return {
        "packet_id": lineage.get("packet_id", "NEUROAI-REPO-CERN-EXPANDED-20260601"),
        "authority_state": lineage.get("authority_state", "CLAIM_HARDENED / PUBLIC_SAFE_DRAFT"),
        "lineage": lineage,
        "substrate": st,
        "gptrepo_protocols": load_gptrepo_protocol_names(),
        "native_model": "PROTO-183-SOCP",
        "native_model_source": st.get("socp_protocol", ""),
        "alpha_family": alpha_family_from_paper(),
        "speaking_loop": [
            "perception",
            "memory_retrieval",
            "role_selection",
            "affect_modulation",
            "claim_selection",
            "speech_act",
            "user_response",
            "state_update",
        ],
        "blocked_claims": [
            "sentient",
            "conscious",
            "clinically validated",
            "human-equivalent",
            "biologically proven",
            "CERN affiliation",
            "production deployment certified",
            "external notarization",
        ],
        "paper_iv_chars": len(paper),
        "paper_iv_loaded": bool(paper),
        "medina_identity": {
            "sovereign_infrastructure": "Medina / NeuroSwarmAI",
            "native_speaking_intelligence": "Auro",
            "oro_charter": "ORO-CHARTER-001",
            "not_foundation": ["external LLM", "Grok", "Llama", "OpenAI", "Anthropic"],
        },
    }