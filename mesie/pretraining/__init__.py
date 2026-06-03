"""Spectral pretraining via self-supervised world tasks.

This module provides auxiliary pretraining heads and training infrastructure
that force the model to learn spectral reasoning skills:

- Resonance detection and prediction
- Coherence estimation between channels/components
- Harmonic structure classification and reconstruction
- Spectral drift detection and quantification
- Temporal lineage inference from current spectra

Additionally provides:
- Digital twin simulation environments for agent-level pretraining
- Spectral memory store with lineage-aware retrieval
- Multi-stage training recipe orchestration
"""

from mesie.pretraining.world_tasks import (
    ResonanceHead,
    CoherenceHead,
    HarmonicStructureHead,
    SpectralDriftHead,
    TemporalLineageHead,
    WorldTaskSuite,
)
from mesie.pretraining.digital_twin import (
    DigitalTwinEnvironment,
    SpectralEntity,
    SpectralStream,
)
from mesie.pretraining.spectral_memory import (
    SpectralMemoryStore,
    MemoryEntry,
    LineageQuery,
)
from mesie.pretraining.training_recipe import (
    TrainingRecipe,
    PretrainingStage,
    EnvironmentStage,
    FineTuningStage,
)

__all__ = [
    "CoherenceHead",
    "DigitalTwinEnvironment",
    "EnvironmentStage",
    "FineTuningStage",
    "HarmonicStructureHead",
    "LineageQuery",
    "MemoryEntry",
    "PretrainingStage",
    "ResonanceHead",
    "SpectralDriftHead",
    "SpectralEntity",
    "SpectralMemoryStore",
    "SpectralStream",
    "TemporalLineageHead",
    "TrainingRecipe",
    "WorldTaskSuite",
]
