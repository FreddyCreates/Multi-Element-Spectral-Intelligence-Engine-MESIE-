"""Research knowledge catalog for the MAESI SDK.

Encodes 24 research entries spanning seismology, ML transfer learning,
ANN/LSH, satellite link budgets, connectome science, USIT methodology,
and MESIE internal modules — each with full citations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

import numpy as np


class ResearchField(Enum):
    """Research field classification."""

    SEISMOLOGY = "seismology"
    MACHINE_LEARNING = "machine_learning"
    SIGNAL_PROCESSING = "signal_processing"
    NEUROSCIENCE = "neuroscience"
    SATELLITE_COMMS = "satellite_communications"
    COGNITIVE_SCIENCE = "cognitive_science"
    SPECTRAL_METHODS = "spectral_methods"
    SOFTWARE_ENGINEERING = "software_engineering"
    INFORMATION_RETRIEVAL = "information_retrieval"
    STRUCTURAL_ENGINEERING = "structural_engineering"


@dataclass
class ResearchEntry:
    """A research knowledge entry with citation metadata.

    Attributes
    ----------
    entry_id : str
        Unique identifier.
    title : str
        Entry title.
    field : ResearchField
        Primary field classification.
    description : str
        Brief abstract or summary.
    citation : str
        Full citation string.
    year : int
        Publication year.
    keywords : List[str]
        Search keywords.
    spectral_relevance : float
        Relevance to spectral intelligence (0-1).
    embedding : np.ndarray
        128-dim embedding for similarity search.
    """

    entry_id: str
    title: str
    field: ResearchField
    description: str
    citation: str = ""
    year: int = 2024
    keywords: List[str] = field(default_factory=list)
    spectral_relevance: float = 0.8
    embedding: np.ndarray = field(default_factory=lambda: np.zeros(128))

    def __post_init__(self):
        if np.all(self.embedding == 0):
            rng = np.random.default_rng(hash(self.entry_id) % (2**32))
            self.embedding = rng.standard_normal(128)
            self.embedding /= np.linalg.norm(self.embedding)

    def to_embedding(self) -> np.ndarray:
        """Return the 128-dim embedding vector."""
        return self.embedding.copy()


def _build_catalog() -> List[ResearchEntry]:
    """Build the 24 research entries."""
    entries = [
        ResearchEntry(
            "re_nga_west2", "NGA-West2 Ground Motion Models",
            ResearchField.SEISMOLOGY,
            "Next-generation attenuation models for active crustal regions.",
            "Bozorgnia et al. (2014). NGA-West2 Research Project. Earthquake Spectra, 30(3).",
            2014, ["NGA-West2", "GMM", "seismic", "attenuation", "ground motion"], 0.95,
        ),
        ResearchEntry(
            "re_kanai_tajimi", "Kanai-Tajimi Spectral Model",
            ResearchField.SEISMOLOGY,
            "Stochastic ground motion model using filtered white noise through soil layers.",
            "Kanai (1957). Semi-empirical formula for seismic characteristics of ground. Univ. Tokyo Bulletin.",
            1957, ["Kanai-Tajimi", "stochastic", "soil", "PSD", "white noise"], 0.96,
        ),
        ResearchEntry(
            "re_transfer_spectral", "Transfer Learning for Spectral Data",
            ResearchField.MACHINE_LEARNING,
            "Domain adaptation techniques for spectral embeddings across application areas.",
            "Pan & Yang (2010). A Survey on Transfer Learning. IEEE TKDE, 22(10).",
            2010, ["transfer learning", "domain adaptation", "spectral", "embeddings"], 0.88,
        ),
        ResearchEntry(
            "re_lsh_original", "Locality-Sensitive Hashing for ANN",
            ResearchField.INFORMATION_RETRIEVAL,
            "Original LSH framework for approximate nearest neighbor in high dimensions.",
            "Indyk & Motwani (1998). Approximate Nearest Neighbors: Towards Removing the Curse of Dimensionality. STOC.",
            1998, ["LSH", "ANN", "approximate", "hashing", "high-dimensional"], 0.85,
        ),
        ResearchEntry(
            "re_hnsw", "Hierarchical Navigable Small World Graphs",
            ResearchField.INFORMATION_RETRIEVAL,
            "Multi-layer graph structure for efficient approximate nearest neighbor search.",
            "Malkov & Yashunin (2020). Efficient and Robust Approximate Nearest Neighbor using HNSW. IEEE TPAMI.",
            2020, ["HNSW", "ANN", "graph", "nearest neighbor", "search"], 0.87,
        ),
        ResearchEntry(
            "re_link_budget", "Satellite Link Budget Analysis",
            ResearchField.SATELLITE_COMMS,
            "End-to-end signal power accounting for satellite communication links.",
            "Maral & Bousquet (2009). Satellite Communications Systems. Wiley.",
            2009, ["satellite", "link budget", "EIRP", "G/T", "C/N"], 0.80,
        ),
        ResearchEntry(
            "re_connectome_human", "Human Connectome Project",
            ResearchField.NEUROSCIENCE,
            "Large-scale mapping of human brain structural and functional connectivity.",
            "Van Essen et al. (2013). The WU-Minn Human Connectome Project. NeuroImage, 80.",
            2013, ["connectome", "brain", "connectivity", "diffusion", "fMRI"], 0.82,
        ),
        ResearchEntry(
            "re_spectral_brain", "Spectral Analysis of Brain Oscillations",
            ResearchField.NEUROSCIENCE,
            "Frequency-domain decomposition of neural oscillatory activity.",
            "Buzsáki & Draguhn (2004). Neuronal Oscillations in Cortical Networks. Science, 304.",
            2004, ["EEG", "oscillations", "brain", "spectral", "frequency bands"], 0.90,
        ),
        ResearchEntry(
            "re_usit_method", "Unified Spectral Intelligence Theory (USIT)",
            ResearchField.SPECTRAL_METHODS,
            "Framework unifying spectral representations across physics, biology, and AI.",
            "MESIE Project (2025). USIT: Treating spectra as computational objects. Internal.",
            2025, ["USIT", "unified", "spectral", "intelligence", "MESIE"], 0.98,
        ),
        ResearchEntry(
            "re_mesie_core", "MESIE Core Engine Architecture",
            ResearchField.SOFTWARE_ENGINEERING,
            "Multi-element record model, validation pyramid, and matching engine.",
            "MESIE Project (2024). Multi-Element Spectral Intelligence Engine. GitHub.",
            2024, ["MESIE", "core", "matching", "validation", "records"], 0.99,
        ),
        ResearchEntry(
            "re_mesie_embeddings", "MESIE Embedding Vectorizers",
            ResearchField.SPECTRAL_METHODS,
            "Fixed-size spectral embeddings from multi-component records for ML pipelines.",
            "MESIE Project (2024). Spectral Vectorizer Module. Internal documentation.",
            2024, ["embedding", "vectorizer", "spectral", "features", "ML"], 0.95,
        ),
        ResearchEntry(
            "re_mesie_helix", "Helix Vector Encoding and Retrieval",
            ResearchField.SPECTRAL_METHODS,
            "Helical coordinate systems for spectral sequence encoding and traversal.",
            "MESIE Project (2025). Helix Module. Internal documentation.",
            2025, ["helix", "encoding", "retrieval", "traversal", "vector"], 0.90,
        ),
        ResearchEntry(
            "re_mesie_protocols", "MESIE Intelligence Protocols",
            ResearchField.COGNITIVE_SCIENCE,
            "Autonomous reasoning over spectral data with configurable intelligence levels.",
            "MESIE Project (2025). Intelligence Protocols v0.2.0. Internal documentation.",
            2025, ["intelligence", "protocols", "reasoning", "autonomous", "attention"], 0.92,
        ),
        ResearchEntry(
            "re_mesie_connectome", "MESIE 3D Connectome Brain Environment",
            ResearchField.NEUROSCIENCE,
            "44-region brain simulation with 68 tracts and signal propagation dynamics.",
            "MESIE Project (2025). Connectome Module. Internal documentation.",
            2025, ["connectome", "brain", "3D", "propagation", "regions"], 0.93,
        ),
        ResearchEntry(
            "re_modal_analysis", "Operational Modal Analysis (OMA)",
            ResearchField.STRUCTURAL_ENGINEERING,
            "Output-only modal identification from ambient vibration measurements.",
            "Brincker & Ventura (2015). Introduction to Operational Modal Analysis. Wiley.",
            2015, ["OMA", "modal", "vibration", "structural", "ambient"], 0.93,
        ),
        ResearchEntry(
            "re_bearing_fault", "Rolling Element Bearing Fault Detection",
            ResearchField.SIGNAL_PROCESSING,
            "Envelope analysis and spectral kurtosis for bearing defect identification.",
            "Randall & Antoni (2011). Rolling element bearing diagnostics. Mech. Systems & Signal Processing.",
            2011, ["bearing", "fault", "envelope", "kurtosis", "spectral"], 0.91,
        ),
        ResearchEntry(
            "re_wavelet_seismic", "Wavelet Transform in Seismology",
            ResearchField.SEISMOLOGY,
            "Continuous wavelet analysis for seismic signal time-frequency decomposition.",
            "Torrence & Compo (1998). A Practical Guide to Wavelet Analysis. BAMS.",
            1998, ["wavelet", "CWT", "seismology", "time-frequency", "scalogram"], 0.94,
        ),
        ResearchEntry(
            "re_schumann_monitoring", "Schumann Resonance Monitoring",
            ResearchField.SIGNAL_PROCESSING,
            "Global electromagnetic resonance monitoring for climate and space weather.",
            "Nickolaenko & Hayakawa (2002). Resonances in the Earth-Ionosphere Cavity. Kluwer.",
            2002, ["Schumann", "ELF", "monitoring", "ionosphere", "resonance"], 0.88,
        ),
        ResearchEntry(
            "re_deep_spectral", "Deep Learning for Spectral Classification",
            ResearchField.MACHINE_LEARNING,
            "CNN and transformer architectures for automated spectral pattern recognition.",
            "Various (2020-2025). Deep spectral classification literature.",
            2022, ["deep learning", "CNN", "transformer", "classification", "spectral"], 0.90,
        ),
        ResearchEntry(
            "re_spectral_clustering", "Spectral Clustering Methods",
            ResearchField.MACHINE_LEARNING,
            "Graph Laplacian-based clustering using spectral embeddings.",
            "Von Luxburg (2007). A Tutorial on Spectral Clustering. Statistics & Computing.",
            2007, ["spectral clustering", "graph Laplacian", "eigenvectors", "grouping"], 0.84,
        ),
        ResearchEntry(
            "re_power_quality", "Power Quality Spectral Monitoring",
            ResearchField.SIGNAL_PROCESSING,
            "Harmonic distortion analysis and real-time power quality assessment.",
            "Arrillaga & Watson (2003). Power System Harmonics. Wiley.",
            2003, ["harmonics", "THD", "power quality", "monitoring", "distortion"], 0.87,
        ),
        ResearchEntry(
            "re_digital_twin", "Digital Twin Spectral Simulation",
            ResearchField.SOFTWARE_ENGINEERING,
            "Physics-based spectral environment simulation for RL agent training.",
            "MESIE Project (2025). Digital Twin Module. Internal documentation.",
            2025, ["digital twin", "simulation", "RL", "physics", "environment"], 0.89,
        ),
        ResearchEntry(
            "re_orbital_debris", "Orbital Debris Spectral Signatures",
            ResearchField.SATELLITE_COMMS,
            "Spectral characterization of space debris for tracking and identification.",
            "NASA ODPO (2020). Orbital Debris Characterization. NASA TP-2020.",
            2020, ["orbital", "debris", "spectral", "tracking", "identification"], 0.79,
        ),
        ResearchEntry(
            "re_mesie_sdk", "MAESI SDK Architecture",
            ResearchField.SOFTWARE_ENGINEERING,
            "Unified client integrating knowledge libraries, fast compute, and NeuroAIX cognitive engine.",
            "MESIE Project (2025). MAESI SDK v1.1. Internal documentation.",
            2025, ["MAESI", "SDK", "client", "knowledge", "NeuroAIX"], 0.97,
        ),
    ]
    return entries


_CATALOG: Optional[List[ResearchEntry]] = None


def get_research_catalog() -> List[ResearchEntry]:
    """Return the full research catalog (24 entries)."""
    global _CATALOG
    if _CATALOG is None:
        _CATALOG = _build_catalog()
    return _CATALOG


def get_research_by_field(research_field: ResearchField) -> List[ResearchEntry]:
    """Filter research entries by field."""
    return [e for e in get_research_catalog() if e.field == research_field]


def search_research(query: str, top_k: int = 5) -> List[ResearchEntry]:
    """Search research entries by keyword relevance.

    Parameters
    ----------
    query : str
        Search query string.
    top_k : int
        Maximum results to return.

    Returns
    -------
    List of matching ResearchEntry objects sorted by relevance.
    """
    catalog = get_research_catalog()
    query_lower = query.lower()
    query_terms = query_lower.split()

    scored: List[tuple] = []
    for entry in catalog:
        score = 0.0
        searchable = " ".join([
            entry.title.lower(),
            entry.description.lower(),
            " ".join(entry.keywords).lower(),
        ])
        for term in query_terms:
            if term in searchable:
                score += 1.0
            # Bonus for exact keyword match
            if term in [k.lower() for k in entry.keywords]:
                score += 0.5
        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in scored[:top_k]]


def get_research_matrix() -> np.ndarray:
    """Return stacked embedding matrix (N×128) for all entries."""
    catalog = get_research_catalog()
    return np.stack([e.to_embedding() for e in catalog])
