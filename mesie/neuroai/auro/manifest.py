"""Auro manifest — loaded from GPTREPO + NeuroAI packet (not invented in MESIE)."""

from mesie.neuroai.auro.substrate_loader import (
    alpha_family_from_paper,
    gptrepo_root,
    load_auro_manifest,
    load_citation_matrix,
    load_lineage_record,
    load_paper_iv,
    neuroai_packet_root,
    substrate_status,
)

AURO_PACKET_ID = "NEUROAI-REPO-CERN-EXPANDED-20260601"
AURO_EDITION = "auro-native-v1"

__all__ = [
    "AURO_PACKET_ID",
    "AURO_EDITION",
    "alpha_family_from_paper",
    "gptrepo_root",
    "load_auro_manifest",
    "load_citation_matrix",
    "load_lineage_record",
    "load_paper_iv",
    "neuroai_packet_root",
    "substrate_status",
]