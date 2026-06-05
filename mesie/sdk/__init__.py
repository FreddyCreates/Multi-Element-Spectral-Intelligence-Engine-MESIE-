"""MAESI — Multi-Agent Embodied Spectral Intelligence.

Powered by NeuroAIX™ — The Connectome Intelligence Engine.

This SDK provides the complete integration layer between the physical universe
(laws, elements, organisms) encoded as spectral entities and the NeuroAIX
connectome intelligence backend. Every physical constant, chemical element,
and biological system is represented as a first-class spectral citizen within
the MESIE cognitive architecture.

Sovereign, Private On-Device AI
-------------------------------
MAESI supports fully local "portable brain" operation — ideal for air-gapped,
secure, or low-connectivity environments (defense, remote ops, critical
infrastructure). On-device operation eliminates cloud dependency, costs,
latency, and privacy risks. Live streaming pipelines enable continuous
learning and real-time updating of spectral fingerprint libraries on-device.

Architecture
------------
    Physical Universe (Laws · Elements · Organisms)
            ↓  spectral encoding
    MAESI Observation Layer
            ↓  embedding projection
    NeuroAIX Connectome (44 regions · 68 tracts · 3D propagation)
            ↓  cognitive integration
    Agent Policy / Memory / World-State
            ↓  sovereign inference (optional cloud-free path)
    On-Device Portable Brain (air-gapped, zero-cloud)

Branding
--------
    MAESI — Multi-Agent Embodied Spectral Intelligence
    NeuroAIX — Neural Architecture for Intelligent eXperience
    MESIE — Multi-Element Spectral Intelligence Engine (foundation)

Copyright (c) 2024-2026 MESIE Contributors. All rights reserved.
"""

__sdk_version__ = "1.0.0"
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
from mesie.sdk.neuroaix_engine import (
    NeuroAIXEngine,
    MAESIObservationEncoder,
    CognitiveIntegrationLoop,
)
from mesie.sdk.sovereign_ondevice import (
    SovereignOnDeviceEngine,
    SovereignConfig,
    DeviceProfile,
    PrivacyLevel,
    OnDeviceFingerprintLibrary,
    OnDeviceStreamingPipeline,
    SpectralFingerprint,
    StreamingSample,
)

__all__ = [
    # Brand
    "__sdk_version__",
    "__brand__",
    "__engine__",
    # Constants
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
    # NeuroAIX Engine
    "NeuroAIXEngine",
    "MAESIObservationEncoder",
    "CognitiveIntegrationLoop",
    # Sovereign On-Device AI
    "SovereignOnDeviceEngine",
    "SovereignConfig",
    "DeviceProfile",
    "PrivacyLevel",
    "OnDeviceFingerprintLibrary",
    "OnDeviceStreamingPipeline",
    "SpectralFingerprint",
    "StreamingSample",
]
