"""Auro — Medina's native speaking intelligence (repo-native, zero third-party inference)."""

from mesie.neuroai.auro.engine import AuroSpeakingEngine, AuroSpeechAct
from mesie.neuroai.auro.eval import AuroEvalSuite, AuroEvalReport
from mesie.neuroai.auro.manifest import load_auro_manifest
from mesie.neuroai.auro.roles import AlphaRole, RoleBoundary

__all__ = [
    "AuroSpeakingEngine",
    "AuroSpeechAct",
    "AuroEvalSuite",
    "AuroEvalReport",
    "AlphaRole",
    "RoleBoundary",
    "load_auro_manifest",
]