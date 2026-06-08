"""SOLUS — your sovereign local math AI caretakers inside the MAESI SDK organism."""

from mesie.sdk.solus.adaptation_model import SolusAdaptationModel
from mesie.sdk.solus.constants import (
    FORMAL_COMPOSITION,
    GOLDEN_ANGLE,
    HEARTBEAT_MS,
    LOCAL_ENGINE,
    OWN_MODELS_ONLY,
    PHI,
    SOLUS_BRAND,
)
from mesie.sdk.solus.emergence_model import SolusEmergenceModel
from mesie.sdk.solus.formal_models import FormalModelReport, FormalModelSpec, composition_manifest
from mesie.sdk.solus.formal_stack import SolusFormalStack
from mesie.sdk.solus.logic_prover import LogicProverReport, SolusLogicProver
from mesie.sdk.solus.mini_brain import BrainThought, MiniBrain
from mesie.sdk.solus.mini_heart import MiniHeart, VitalsSnapshot
from mesie.sdk.solus.organism import OrganismCaretakerResult, OrganismVitals, SDKSolusOrganism
from mesie.sdk.solus.math_layer import SolusMathLayer
from mesie.sdk.solus.pattern_forge import PatternForgeReport, SolusPatternForge
from mesie.sdk.solus.reasoning_model import SolusReasoningModel

__all__ = [
    "BrainThought",
    "FORMAL_COMPOSITION",
    "FormalModelReport",
    "FormalModelSpec",
    "GOLDEN_ANGLE",
    "HEARTBEAT_MS",
    "LOCAL_ENGINE",
    "OWN_MODELS_ONLY",
    "LogicProverReport",
    "MiniBrain",
    "MiniHeart",
    "OrganismCaretakerResult",
    "OrganismVitals",
    "PHI",
    "PatternForgeReport",
    "SDKSolusOrganism",
    "SOLUS_BRAND",
    "SolusAdaptationModel",
    "SolusEmergenceModel",
    "SolusFormalStack",
    "SolusLogicProver",
    "SolusMathLayer",
    "SolusPatternForge",
    "SolusReasoningModel",
    "composition_manifest",
    "VitalsSnapshot",
]