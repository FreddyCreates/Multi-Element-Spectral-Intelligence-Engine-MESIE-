# Changelog

All notable changes to MESIE will be documented in this file.

## [0.2.0] - 2026-06-03

### Added
- **Intelligence AI Protocols** (`mesie.ai.intelligence_protocols`)
  - `IntelligenceProtocol` — orchestrator for autonomous spectral reasoning with configurable intelligence levels (passive, reactive, adaptive, predictive, autonomous)
  - `IntelligenceConfig` — configuration for reasoning behavior, memory, and attention settings
  - `ReasoningResult` — structured output with conclusions, confidence, evidence, and recommended actions
  - `SpectralMemoryBuffer` — episodic memory with importance-weighted retention and similarity-based retrieval
  - `AttentionFocusModule` — multi-head attention mechanism that learns informative frequency regions
  - `ReasoningStrategy` enum — statistical, pattern matching, anomaly detection, causal inference, ensemble

- **Spectral Transformer Pipeline** (`mesie.ai.transformer_pipeline`)
  - `SpectralTransformerPipeline` — end-to-end transformer encoder for spectral sequences
  - `TransformerConfig` — configurable architecture (d_model, n_heads, n_layers, feedforward dim, pooling)
  - `SpectralTokenizer` — converts continuous spectra to discrete tokens (frequency bins, wavelets, patches)
  - `PositionalEncoder` — sinusoidal and learnable positional encodings for spectral sequences
  - `MultiHeadSpectralAttention` — scaled dot-product multi-head attention optimized for frequency data
  - `TransformerEncoderLayer` — full encoder block with attention, feed-forward, residual connections, and layer norm
  - `TransformerOutput` — structured output with embeddings, pooled vectors, and attention maps

- New install extras: `[intelligence]` for full AI protocol + transformer stack
- Added `transformers>=4.30` and `torch>=2.0` as optional dependencies
- Tests for intelligence protocols and transformer pipeline

### Changed
- Bumped version from 0.1.0 to 0.2.0
- Updated `.zenodo.json` with full Zenodo release metadata including references, subjects, and related identifiers
- Updated `CITATION.cff` with new version and expanded keywords
- Updated `pyproject.toml` description and keywords to reflect transformer and intelligence capabilities
- Extended `[full]` and `[ai]` optional dependency groups to include transformers and torch

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
