"""Evaluation framework for spectral foundation models.

Provides comprehensive evaluation metrics, probing tasks,
and downstream benchmarks for assessing pretrained models.
"""

from mesie.foundation.evaluation.metrics import (
    SpectralMetrics,
    ReconstructionMetrics,
    RepresentationMetrics,
    DownstreamMetrics,
)
from mesie.foundation.evaluation.probing import (
    LinearProbe,
    KNNProbe,
    MLPProbe,
    ModalityClassificationProbe,
    FrequencyResolutionProbe,
)
from mesie.foundation.evaluation.benchmarks import (
    SpectralBenchmarkSuite,
    CrossModalRetrievalBenchmark,
    FewShotClassificationBenchmark,
    AnomalyDetectionBenchmark,
)

__all__ = [
    "SpectralMetrics",
    "ReconstructionMetrics",
    "RepresentationMetrics",
    "DownstreamMetrics",
    "LinearProbe",
    "KNNProbe",
    "MLPProbe",
    "ModalityClassificationProbe",
    "FrequencyResolutionProbe",
    "SpectralBenchmarkSuite",
    "CrossModalRetrievalBenchmark",
    "FewShotClassificationBenchmark",
    "AnomalyDetectionBenchmark",
]
