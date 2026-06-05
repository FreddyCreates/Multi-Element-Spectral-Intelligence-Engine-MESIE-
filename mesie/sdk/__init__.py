"""MAESI — Multi-Agent Embodied Spectral Intelligence.

Powered by NeuroAIX™ — The Connectome Intelligence Engine.

This SDK provides the complete integration layer between the physical universe
(laws, elements, organisms) encoded as spectral entities and the NeuroAIX
connectome intelligence backend. Every physical constant, chemical element,
and biological system is represented as a first-class spectral citizen within
the MESIE cognitive architecture.

Architecture
------------
    Physical Universe (Laws · Elements · Organisms)
            ↓  spectral encoding
    MAESI Observation Layer
            ↓  embedding projection
    NeuroAIX Connectome (44 regions · 68 tracts · 3D propagation)
            ↓  cognitive integration
    Agent Policy / Memory / World-State

Branding
--------
    MAESI — Multi-Agent Embodied Spectral Intelligence
    NeuroAIX — Neural Architecture for Intelligent eXperience
    MESIE — Multi-Element Spectral Intelligence Engine (foundation)

Copyright (c) 2024-2026 MESIE Contributors. All rights reserved.
"""

__sdk_version__ = "1.1.0"
__brand__ = "MAESI Powered by NeuroAIX"
__engine__ = "MESIE — Multi-Element Spectral Intelligence Engine"

from mesie.sdk.constants import (
    PLANCK_SPECTRAL,
    BOLTZMANN_SPECTRAL,
    SPEED_OF_LIGHT_SPECTRAL,
    GRAVITATIONAL_SPECTRAL,
    AVOGADRO_SPECTRAL,
    FINE_STRUCTURE_SPECTRAL,
    UniversalSpectralConstant,
    ALL_CONSTANTS,
)
from mesie.sdk.physical_laws import (
    PhysicalLaw,
    get_fundamental_laws,
    get_law_by_name,
    SpectralLawRegistry,
)
from mesie.sdk.chemical_elements import (
    SpectralElement,
    get_periodic_table,
    get_element_by_symbol,
    get_elements_by_group,
)
from mesie.sdk.biological_systems import (
    BiologicalSystem,
    OrganismSpectralProfile,
    get_biological_systems,
    get_organism_profile,
)
from mesie.sdk.technical_library import (
    TechnicalConcept,
    TechnicalDomain,
    get_technical_library,
    get_technical_by_domain,
    get_technical_matrix,
)
from mesie.sdk.research_knowledge import (
    ResearchEntry,
    ResearchField,
    get_research_catalog,
    get_research_by_field,
    search_research,
    get_research_matrix,
)
from mesie.sdk.fast_compute import FastSpectralCompute, SpeedBenchmark
from mesie.sdk.maesi_client import MAESIClient, MAESIQueryResult, MAESIRunReport, KnowledgeStats
from mesie.sdk.neuroaix_engine import (
    NeuroAIXEngine,
    MAESIObservationEncoder,
    CognitiveIntegrationLoop,
    MAESIObservation,
)

__all__ = [
    # Brand
    "__sdk_version__",
    "__brand__",
    "__engine__",
    # Constants
    "ALL_CONSTANTS",
    "PLANCK_SPECTRAL",
    "BOLTZMANN_SPECTRAL",
    "SPEED_OF_LIGHT_SPECTRAL",
    "GRAVITATIONAL_SPECTRAL",
    "AVOGADRO_SPECTRAL",
    "FINE_STRUCTURE_SPECTRAL",
    "UniversalSpectralConstant",
    # Physical Laws
    "PhysicalLaw",
    "get_fundamental_laws",
    "get_law_by_name",
    "SpectralLawRegistry",
    # Chemical Elements
    "SpectralElement",
    "get_periodic_table",
    "get_element_by_symbol",
    "get_elements_by_group",
    # Biological Systems
    "BiologicalSystem",
    "OrganismSpectralProfile",
    "get_biological_systems",
    "get_organism_profile",
    # Technical Library
    "TechnicalConcept",
    "TechnicalDomain",
    "get_technical_library",
    "get_technical_by_domain",
    "get_technical_matrix",
    # Research Knowledge
    "ResearchEntry",
    "ResearchField",
    "get_research_catalog",
    "get_research_by_field",
    "search_research",
    "get_research_matrix",
    # Fast Compute
    "FastSpectralCompute",
    "SpeedBenchmark",
    # MAESI Client
    "MAESIClient",
    "MAESIQueryResult",
    "MAESIRunReport",
    "KnowledgeStats",
    # NeuroAIX Engine
    "NeuroAIXEngine",
    "MAESIObservationEncoder",
    "CognitiveIntegrationLoop",
    "MAESIObservation",
]
