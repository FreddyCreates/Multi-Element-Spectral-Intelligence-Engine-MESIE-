"""MESIE — Multi-Element Spectral Intelligence Engine.

A modular Python framework for spectral matching, signal generation,
resonance-aware embeddings, and AI-native spectral representation.
"""

__version__ = "0.1.0"

from mesie.core.records import MultiElementRecord, SpectralComponent, SpectralMetadata
from mesie.core.config import GenerationConfig
from mesie.validation.validators import validate_record, ValidationReport
from mesie.io.loaders import load_record
from mesie.processing.normalize import normalize_record
from mesie.matching.matcher import match_records, SpectralMatcher, MatchResult
from mesie.generation.psd import generate_psd
from mesie.generation.fas import generate_fas
from mesie.generation.rotdnn import generate_rotdnn
from mesie.embeddings.vectorizers import SpectralVectorizer
from mesie.cosmology.layers import CosmicSpectralDecomposer, CosmicLayer, LayerDomain
from mesie.cosmology.token_governor import CalendricalTokenGovernor, TokenBudget
from mesie.cosmology.teotl_flow import TeotlEnergyFlow

__all__ = [
    "__version__",
    "CalendricalTokenGovernor",
    "CosmicLayer",
    "CosmicSpectralDecomposer",
    "GenerationConfig",
    "LayerDomain",
    "MatchResult",
    "MultiElementRecord",
    "SpectralComponent",
    "SpectralMatcher",
    "SpectralMetadata",
    "SpectralVectorizer",
    "TeotlEnergyFlow",
    "TokenBudget",
    "ValidationReport",
    "generate_fas",
    "generate_psd",
    "generate_rotdnn",
    "load_record",
    "match_records",
    "normalize_record",
    "validate_record",
]
