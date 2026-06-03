"""MESIE — Multi-Element Spectral Intelligence Engine.

A modular Python framework for spectral matching, signal generation,
resonance-aware embeddings, and AI-native spectral representation.
"""

__version__ = "0.2.0"

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
from mesie.ai.models import SpectralAutoencoder, SpectralClassifier, SpectralTransformer
from mesie.ai.training import TrainingPipeline, TrainingConfig
from mesie.ai.inference import InferenceEngine, PredictionResult
from mesie.ai.transfer import TransferAdapter, DomainAdaptation
from mesie.ai.intelligence_protocols import (
    IntelligenceProtocol,
    IntelligenceConfig,
    IntelligenceLevel,
    ReasoningResult,
    ReasoningStrategy,
    SpectralMemoryBuffer,
    AttentionFocusModule,
)
from mesie.ai.transformer_pipeline import (
    SpectralTransformerPipeline,
    TransformerConfig,
    TransformerOutput,
    SpectralTokenizer,
)
from mesie.protocols.spectral_protocol import SpectralDataProtocol, ProtocolMessage
from mesie.protocols.streaming import StreamingProtocol, StreamBuffer
from mesie.protocols.serialization import SpectralSerializer, SerializationFormat

__all__ = [
    "__version__",
    "AttentionFocusModule",
    "DomainAdaptation",
    "GenerationConfig",
    "InferenceEngine",
    "IntelligenceConfig",
    "IntelligenceLevel",
    "IntelligenceProtocol",
    "MatchResult",
    "MultiElementRecord",
    "PredictionResult",
    "ProtocolMessage",
    "ReasoningResult",
    "ReasoningStrategy",
    "SerializationFormat",
    "SpectralAutoencoder",
    "SpectralClassifier",
    "SpectralComponent",
    "SpectralDataProtocol",
    "SpectralMatcher",
    "SpectralMemoryBuffer",
    "SpectralMetadata",
    "SpectralSerializer",
    "SpectralTokenizer",
    "SpectralTransformer",
    "SpectralTransformerPipeline",
    "SpectralVectorizer",
    "StreamBuffer",
    "StreamingProtocol",
    "TrainingConfig",
    "TrainingPipeline",
    "TransferAdapter",
    "TransformerConfig",
    "TransformerOutput",
    "ValidationReport",
    "generate_fas",
    "generate_psd",
    "generate_rotdnn",
    "load_record",
    "match_records",
    "normalize_record",
    "validate_record",
]
