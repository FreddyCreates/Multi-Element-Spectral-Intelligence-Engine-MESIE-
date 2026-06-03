# Changelog

All notable changes to MESIE will be documented in this file.

## [Unreleased]

### Added
- **Foundation Pretraining Suite** (`mesie/pretraining/foundation_objectives.py`)
  - Masked Spectral Modeling with three masking strategies (random, contiguous, band)
  - InfoNCE Contrastive Learning with full augmentation pipeline (Gaussian noise, frequency masking, amplitude scaling, circular shifts)
  - Temporal Prediction with configurable context aggregation (weighted, mean, last, concatenated)
  - Unified `FoundationObjectiveSuite` orchestrating all losses with configurable weights
- **Observation Encoder** (`mesie/pretraining/observation_encoder.py`)
  - Encodes raw world → spectra → MESIE embedding → agent observation vector
  - Multi-modality support (spectral, state, semantic) with configurable normalization and weighting
- **Digital Twin Simulation** (`mesie/pretraining/digital_twin.py`)
  - Physics-based environments (rotating machinery, structural elements, power systems, robotic joints, fluid systems)
  - RL reward signals tied to resonance avoidance, drift minimization, coherence maintenance, anomaly detection
- **Spectral Memory Store** (`mesie/pretraining/spectral_memory.py`)
  - k-NN retrieval over spectral embeddings
  - Event/time filtering and lineage reconstruction
  - Importance-weighted memory consolidation
- **3D Connectome Brain Environment** (`mesie/connectome/`)
  - 44 real brain regions with MNI 3D coordinates across 10 functional systems
  - 68 biologically-inspired white-matter tract connections
  - 3D neural simulation engine with signal propagation using ~6 mm/ms conduction velocity
  - Global coherence metrics and system-level activation tracking
  - Full 3D state export for visualization
- Example script: `examples/08_3d_connectome_brain.py`
- Test suites: `tests/test_foundation_objectives.py`, `tests/test_pretraining.py`, `tests/test_connectome.py`

## [0.1.0] - 2024-01-01

### Added
- Initial public research release
- Core spectral record data model (MultiElementRecord, SpectralComponent, SpectralMetadata)
- Spectral validation with multi-level checks
- Normalization, interpolation, and smoothing
- Spectral matching engine with composite scoring
- PSD, FAS, and RotDnn generation
- Electro-spectral feature extraction
- Node topology mapping and lineage
- Spectral embedding vectorizers
- Cognitive architecture adapters
- Example scripts and test suite
- Documentation skeleton
- Zenodo metadata and CITATION.cff
