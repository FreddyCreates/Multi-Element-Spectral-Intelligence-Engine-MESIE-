"""Cognitive architecture adapters for spectral integration."""

from mesie.cognitive.memory_adapter import SpectralMemoryAdapter
from mesie.cognitive.attention_adapter import SpectralAttentionAdapter
from mesie.cognitive.agent_state_adapter import AgentStateSpectralAdapter, SpectralAnomalyAdapter
from mesie.cognitive.taurus_memory import (
    TaurusMemoryStore,
    TaurusWorkingMemory,
    MemoryTrace,
    RetrievalResult,
)
from mesie.cognitive.neurocores import (
    SpectralNeuroCore,
    NeuroCoreCluster,
    NeuroCoreConfig,
    CoreProcessingResult,
)

__all__ = [
    "AgentStateSpectralAdapter",
    "CoreProcessingResult",
    "MemoryTrace",
    "NeuroCoreCluster",
    "NeuroCoreConfig",
    "RetrievalResult",
    "SpectralAnomalyAdapter",
    "SpectralAttentionAdapter",
    "SpectralMemoryAdapter",
    "SpectralNeuroCore",
    "TaurusMemoryStore",
    "TaurusWorkingMemory",
]
