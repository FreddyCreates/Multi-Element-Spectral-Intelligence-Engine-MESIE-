"""Technical concept library for the MAESI SDK.

Encodes 20 core technical concepts as spectral-aware knowledge entries
covering STFT, salient time-frequency, LSH/ANN, robotics, vibration,
power systems, Schumann resonances, orbital mechanics, seismic FAS/PSD,
and internal API architecture.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

import numpy as np


class TechnicalDomain(Enum):
    """Technical domain classification."""

    SIGNAL_PROCESSING = "signal_processing"
    MACHINE_LEARNING = "machine_learning"
    ROBOTICS = "robotics"
    VIBRATION = "vibration"
    POWER_SYSTEMS = "power_systems"
    GEOPHYSICS = "geophysics"
    ORBITAL_MECHANICS = "orbital_mechanics"
    SEISMOLOGY = "seismology"
    NETWORKING = "networking"
    SPECTRAL_ANALYSIS = "spectral_analysis"


@dataclass
class TechnicalConcept:
    """A technical concept encoded with spectral metadata.

    Attributes
    ----------
    concept_id : str
        Unique identifier.
    title : str
        Human-readable title.
    domain : TechnicalDomain
        Primary domain classification.
    description : str
        Brief description of the concept.
    spectral_relevance : float
        Relevance to spectral intelligence (0-1).
    keywords : List[str]
        Search keywords.
    frequency_range_hz : tuple
        Characteristic frequency range (low, high).
    embedding : np.ndarray
        128-dim spectral embedding for similarity search.
    """

    concept_id: str
    title: str
    domain: TechnicalDomain
    description: str
    spectral_relevance: float = 0.8
    keywords: List[str] = field(default_factory=list)
    frequency_range_hz: tuple = (0.0, 1000.0)
    embedding: np.ndarray = field(default_factory=lambda: np.zeros(128))

    def __post_init__(self):
        if np.all(self.embedding == 0):
            rng = np.random.default_rng(hash(self.concept_id) % (2**32))
            self.embedding = rng.standard_normal(128)
            self.embedding /= np.linalg.norm(self.embedding)

    def to_embedding(self) -> np.ndarray:
        """Return the 128-dim embedding vector."""
        return self.embedding.copy()


def _build_library() -> List[TechnicalConcept]:
    """Build the 20 technical concepts."""
    concepts = [
        TechnicalConcept(
            "tc_stft", "Short-Time Fourier Transform (STFT)",
            TechnicalDomain.SIGNAL_PROCESSING,
            "Windowed DFT for time-frequency representation of non-stationary signals.",
            0.95, ["STFT", "windowing", "spectrogram", "DFT", "time-frequency"],
            (0.01, 20000.0),
        ),
        TechnicalConcept(
            "tc_salient_tf", "Salient Time-Frequency Features",
            TechnicalDomain.SIGNAL_PROCESSING,
            "Extraction of perceptually or energetically significant TF regions.",
            0.92, ["salient", "time-frequency", "feature extraction", "energy peaks"],
            (0.1, 10000.0),
        ),
        TechnicalConcept(
            "tc_lsh", "Locality-Sensitive Hashing (LSH)",
            TechnicalDomain.MACHINE_LEARNING,
            "Probabilistic dimensionality reduction for approximate nearest neighbor search.",
            0.85, ["LSH", "hashing", "ANN", "approximate", "nearest neighbor"],
            (0.0, 0.0),
        ),
        TechnicalConcept(
            "tc_ann", "Approximate Nearest Neighbor (ANN)",
            TechnicalDomain.MACHINE_LEARNING,
            "Sublinear-time search over high-dimensional embedding spaces.",
            0.88, ["ANN", "HNSW", "search", "embeddings", "vector database"],
            (0.0, 0.0),
        ),
        TechnicalConcept(
            "tc_robot_vibration", "Robotic Joint Vibration Monitoring",
            TechnicalDomain.ROBOTICS,
            "Real-time spectral monitoring of robotic actuators for predictive maintenance.",
            0.90, ["robotics", "vibration", "actuator", "joint", "predictive maintenance"],
            (10.0, 5000.0),
        ),
        TechnicalConcept(
            "tc_structural_vibration", "Structural Health Monitoring (SHM)",
            TechnicalDomain.VIBRATION,
            "Modal analysis and damage detection via spectral decomposition of structural response.",
            0.94, ["SHM", "modal", "structural", "damage detection", "natural frequency"],
            (0.1, 200.0),
        ),
        TechnicalConcept(
            "tc_rotating_machinery", "Rotating Machinery Diagnostics",
            TechnicalDomain.VIBRATION,
            "Spectral signature analysis of bearings, gearboxes, and turbines.",
            0.93, ["bearing", "gearbox", "turbine", "fault diagnosis", "envelope spectrum"],
            (1.0, 20000.0),
        ),
        TechnicalConcept(
            "tc_power_spectral", "Power System Spectral Analysis",
            TechnicalDomain.POWER_SYSTEMS,
            "Harmonic analysis and power quality assessment in electrical grids.",
            0.89, ["harmonics", "THD", "power quality", "grid", "50Hz", "60Hz"],
            (50.0, 3000.0),
        ),
        TechnicalConcept(
            "tc_schumann", "Schumann Resonances",
            TechnicalDomain.GEOPHYSICS,
            "Extremely low frequency resonances in the Earth-ionosphere cavity.",
            0.91, ["Schumann", "ELF", "resonance", "ionosphere", "7.83Hz"],
            (7.83, 45.0),
        ),
        TechnicalConcept(
            "tc_orbital_link", "Orbital Link Budget Analysis",
            TechnicalDomain.ORBITAL_MECHANICS,
            "Signal propagation and spectral attenuation in satellite-ground links.",
            0.82, ["satellite", "link budget", "orbital", "propagation", "attenuation"],
            (1e9, 40e9),
        ),
        TechnicalConcept(
            "tc_seismic_fas", "Fourier Amplitude Spectrum (FAS)",
            TechnicalDomain.SEISMOLOGY,
            "Frequency-domain representation of earthquake ground motion acceleration.",
            0.96, ["FAS", "seismic", "earthquake", "acceleration", "ground motion"],
            (0.01, 50.0),
        ),
        TechnicalConcept(
            "tc_seismic_psd", "Power Spectral Density (PSD) for Seismic Data",
            TechnicalDomain.SEISMOLOGY,
            "Energy distribution across frequency bands for seismic ground motion.",
            0.96, ["PSD", "seismic", "energy", "spectral density", "ground motion"],
            (0.01, 50.0),
        ),
        TechnicalConcept(
            "tc_octopus_arch", "Octopus Distributed Architecture",
            TechnicalDomain.NETWORKING,
            "Multi-arm parallel processing architecture inspired by octopus neural distribution.",
            0.78, ["octopus", "distributed", "parallel", "multi-arm", "architecture"],
            (0.0, 0.0),
        ),
        TechnicalConcept(
            "tc_internal_api", "Internal API Bus Architecture",
            TechnicalDomain.NETWORKING,
            "Cross-engine communication bus for MESIE module inter-operation.",
            0.80, ["API", "bus", "internal", "cross-engine", "communication"],
            (0.0, 0.0),
        ),
        TechnicalConcept(
            "tc_edge_spectral", "Edge Spectral Processing",
            TechnicalDomain.SIGNAL_PROCESSING,
            "On-device spectral computation for low-latency embedded systems.",
            0.87, ["edge", "embedded", "on-device", "low-latency", "FPGA"],
            (0.1, 48000.0),
        ),
        TechnicalConcept(
            "tc_fingerprint", "Spectral Fingerprinting",
            TechnicalDomain.SPECTRAL_ANALYSIS,
            "Compact signature extraction for spectral identity and retrieval.",
            0.94, ["fingerprint", "signature", "identity", "hash", "retrieval"],
            (0.01, 20000.0),
        ),
        TechnicalConcept(
            "tc_transfer_learn", "Spectral Transfer Learning",
            TechnicalDomain.MACHINE_LEARNING,
            "Domain adaptation of spectral models across application domains.",
            0.86, ["transfer learning", "domain adaptation", "fine-tuning", "pre-training"],
            (0.0, 0.0),
        ),
        TechnicalConcept(
            "tc_coherence", "Spectral Coherence Analysis",
            TechnicalDomain.SIGNAL_PROCESSING,
            "Cross-spectral coherence for multi-channel signal alignment.",
            0.91, ["coherence", "cross-spectrum", "multi-channel", "alignment", "phase"],
            (0.01, 20000.0),
        ),
        TechnicalConcept(
            "tc_wavelet", "Wavelet Spectral Decomposition",
            TechnicalDomain.SIGNAL_PROCESSING,
            "Multi-resolution time-frequency analysis via wavelet transforms.",
            0.93, ["wavelet", "CWT", "DWT", "multi-resolution", "time-frequency"],
            (0.01, 20000.0),
        ),
        TechnicalConcept(
            "tc_resonance_track", "Resonance Tracking and Avoidance",
            TechnicalDomain.VIBRATION,
            "Real-time tracking of resonant frequencies for structural safety.",
            0.95, ["resonance", "tracking", "avoidance", "natural frequency", "safety"],
            (0.1, 500.0),
        ),
    ]
    return concepts


_LIBRARY: Optional[List[TechnicalConcept]] = None


def get_technical_library() -> List[TechnicalConcept]:
    """Return the full technical concept library (20 entries)."""
    global _LIBRARY
    if _LIBRARY is None:
        _LIBRARY = _build_library()
    return _LIBRARY


def get_technical_by_domain(domain: TechnicalDomain) -> List[TechnicalConcept]:
    """Filter technical concepts by domain."""
    return [c for c in get_technical_library() if c.domain == domain]


def get_technical_matrix() -> np.ndarray:
    """Return stacked embedding matrix (N×128) for all concepts."""
    lib = get_technical_library()
    return np.stack([c.to_embedding() for c in lib])
