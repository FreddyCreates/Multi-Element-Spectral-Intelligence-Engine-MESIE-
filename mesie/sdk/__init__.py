"""MAESI — Multi-Agent Embodied Spectral Intelligence.

Powered by NeuroAIX™ — The Connectome Intelligence Engine.
"""

from mesie.version_info import MAESI_SDK_VERSION as __sdk_version__
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
from mesie.sdk.solus import (
    FORMAL_COMPOSITION,
    OWN_MODELS_ONLY,
    SDKSolusOrganism,
    SolusFormalStack,
    SolusLogicProver,
    SolusMathLayer,
    SolusPatternForge,
    SOLUS_BRAND,
    LOCAL_ENGINE,
    composition_manifest,
)

__all__ = [
    "__sdk_version__",
    "__brand__",
    "__engine__",
    "ALL_CONSTANTS",
    "PLANCK_SPECTRAL",
    "BOLTZMANN_SPECTRAL",
    "SPEED_OF_LIGHT_SPECTRAL",
    "GRAVITATIONAL_SPECTRAL",
    "AVOGADRO_SPECTRAL",
    "FINE_STRUCTURE_SPECTRAL",
    "UniversalSpectralConstant",
    "PhysicalLaw",
    "get_fundamental_laws",
    "get_law_by_name",
    "SpectralLawRegistry",
    "SpectralElement",
    "get_periodic_table",
    "get_element_by_symbol",
    "get_elements_by_group",
    "BiologicalSystem",
    "OrganismSpectralProfile",
    "get_biological_systems",
    "get_organism_profile",
    "TechnicalConcept",
    "TechnicalDomain",
    "get_technical_library",
    "get_technical_by_domain",
    "get_technical_matrix",
    "ResearchEntry",
    "ResearchField",
    "get_research_catalog",
    "get_research_by_field",
    "search_research",
    "get_research_matrix",
    "FastSpectralCompute",
    "SpeedBenchmark",
    "MAESIClient",
    "MAESIQueryResult",
    "MAESIRunReport",
    "KnowledgeStats",
    "NeuroAIXEngine",
    "MAESIObservationEncoder",
    "CognitiveIntegrationLoop",
    "MAESIObservation",
    "FORMAL_COMPOSITION",
    "OWN_MODELS_ONLY",
    "SDKSolusOrganism",
    "SolusFormalStack",
    "SolusLogicProver",
    "SolusMathLayer",
    "SolusPatternForge",
    "SOLUS_BRAND",
    "LOCAL_ENGINE",
    "composition_manifest",
]

from mesie.sdk.terminal import TerminalSession, default_session, detect_shell, open_surfaces, open_terminal
from mesie.sdk.terminal_copilot import CopilotTier, TerminalCopilot, run_copilot_terminal
from mesie.sdk.llm_bridge import LLMBridge, LLMBridgeConfig
from mesie.sdk.intelligence_sdk import SpectralIntelligenceSDK
from mesie.sdk.native_ai import NativeLocalAIEngine, NativeAIDeliverableReport, StreamEvent, StreamPhase

__all__.extend([
    "TerminalSession",
    "default_session",
    "detect_shell",
    "open_surfaces",
    "open_terminal",
    "CopilotTier",
    "TerminalCopilot",
    "run_copilot_terminal",
    "LLMBridge",
    "LLMBridgeConfig",
    "SpectralIntelligenceSDK",
    "NativeLocalAIEngine",
    "NativeAIDeliverableReport",
    "StreamEvent",
    "StreamPhase",
    "SwarmSDK",
    "SwarmSDKReport",
])


def __getattr__(name: str):
    if name in ("SwarmSDK", "SwarmSDKReport"):
        from mesie.sdk.swarm_client import SwarmSDK, SwarmSDKReport

        return SwarmSDK if name == "SwarmSDK" else SwarmSDKReport
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
