# MESIE — Multi-Element Spectral Intelligence Engine

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://img.shields.io/badge/DOI-pending-lightgrey.svg)](https://zenodo.org)
[![CI](https://github.com/FreddyCreates/Multi-Element-Spectral-Intelligence-Engine-MESIE-/actions/workflows/ci.yml/badge.svg)](https://github.com/FreddyCreates/Multi-Element-Spectral-Intelligence-Engine-MESIE-/actions/workflows/ci.yml)
[![Version](https://img.shields.io/badge/version-0.3.0-green.svg)](https://github.com/FreddyCreates/Multi-Element-Spectral-Intelligence-Engine-MESIE-)
[![Monte Carlo](https://img.shields.io/badge/Monte_Carlo-5%2C000_trials_100%25_pass-brightgreen.svg)](deliverables/MESIE_Monte_Carlo_Enterprise_Report.md)
[![Enterprise Grade](https://img.shields.io/badge/Enterprise_Grade-PASS_%E2%89%A585%25-blue.svg)](deliverables/MESIE_Monte_Carlo_Enterprise_Report.md)

MESIE is an open-source Python framework for multi-component spectral matching, signal generation, resonance-aware embeddings, transformer-based intelligence protocols, and AI-native spectral representation.

It supports:

- Single-component spectral records
- Multi-component records
- RotDnn-style workflows
- PSD-compatible generation
- FAS-compatible generation
- Spectral validation (6 levels)
- Spectral feature extraction
- Frequency-domain matching
- Resonance/coherence scoring
- Embedding generation for AI and cognitive systems
- **Intelligence protocols with autonomous reasoning** *(new in v0.2.0)*
- **Transformer-based spectral pipelines** *(new in v0.2.0)*
- **Helix vector encoding and retrieval** *(new in v0.2.0)*
- **Spectral data protocols and streaming** *(new in v0.2.0)*
- **AI system integration and pipeline orchestration** *(new in v0.2.0)*
- **Foundation pretraining** — Masked Spectral Modeling, InfoNCE Contrastive Learning, Temporal Prediction
- **3D connectome brain environment** — 44 brain regions, 68 biologically-inspired connections, neural simulation
- **Miniverse nesting** — recursive containment, scale-bridging, and downward attention for cognitive architectures

## Why MESIE?

Most spectral tools treat spectra as arrays. MESIE treats spectra as **structured computational objects** with components, metadata, lineage, derived features, and embedding-ready representations.

This makes MESIE useful for:

- Earthquake engineering
- Structural monitoring
- Vibration analysis
- Robotics
- Biosignal analysis
- Digital twins
- Artificial intelligence
- Autonomous systems
- Cognitive architectures

## Core Idea

A spectral record can become more than a plotted curve. It can become a reusable memory object, a search vector, a state signature, or a reasoning primitive inside an intelligent system.

## Installation

```bash
pip install mesie
```

For full scientific stack (scipy, pandas, scikit-learn, networkx):

```bash
pip install mesie[full]
```

For ML extras (transformers; torch on x64/Linux/macOS — skipped on Windows ARM64):

```bash
pip install mesie[ml]
```

For AI/intelligence protocols:

```bash
pip install mesie[intelligence]
```

For development:

```bash
pip install -e ".[dev,full]"
```

## Desktop Application (Electron)

MESIE includes a cross-platform desktop UX with spectral visualization, real-time validation, and Monte Carlo benchmarking:

```bash
cd mesie-desktop && npm install && npm start
```

Development mode with DevTools:
```bash
npm run dev
```

Build distributable: `npm run build:win` | `npm run build:mac` | `npm run build:linux`

See [mesie-desktop/README.md](mesie-desktop/README.md) for full documentation.

## PowerShell Module

Cross-platform PowerShell wrapper (Windows PowerShell 5.1+ / PowerShell Core 7+):

```powershell
# Import the module
Import-Module ./scripts/MESIE.psm1

# Verify installation
Test-MESIEInstall

# Validate a record
Invoke-MESIEValidate -RecordPath "data/reference/vibration_monitoring_reference.json"

# Generate a spectrum
Invoke-MESIEGenerate -Type psd -Seed 42

# Run Monte Carlo benchmark
Invoke-MESIEMonteCarlo -Trials 500

# Search research catalog
Search-MESIEResearch -Query "spectral analysis" -TopK 5

# Launch desktop app
Start-MESIEDesktop -Dev
```

## Cloudflare Worker API

Edge validate/match API: [workers/mesie-api](workers/mesie-api/README.md). Deploy with `npx wrangler deploy` (local `wrangler dev` needs x64 — use WSL or deploy from CI on Windows ARM).

```bash
cd workers/mesie-api && npm install && npx wrangler login && npm run deploy
```

## Basic Usage

```python
from mesie import load_record, validate_record, match_records

reference = load_record("reference.json")
candidate = load_record("candidate.json")

report = validate_record(reference)
result = match_records(reference, candidate)

print(result.composite_score)
print(result.metric_breakdown)
```

## Generate PSD/FAS

```python
from mesie import generate_psd, generate_fas
from mesie.core.config import GenerationConfig

config = GenerationConfig(seed=42, amplitude_shape="power_law")
psd = generate_psd(config)
fas = generate_fas(config)
```

## Create Spectral Embeddings

```python
from mesie.embeddings import SpectralVectorizer

vectorizer = SpectralVectorizer()
embedding = vectorizer.fit_transform(record)
```

## Intelligence Protocols — Autonomous Spectral Reasoning

MESIE v0.2.0 introduces **Intelligence Protocols** — an orchestration layer for autonomous spectral reasoning with configurable intelligence levels:

```python
from mesie import IntelligenceProtocol, IntelligenceConfig, IntelligenceLevel, ReasoningStrategy
import numpy as np

# Configure intelligence behavior
config = IntelligenceConfig(
    level=IntelligenceLevel.ADAPTIVE,
    memory_capacity=500,
    attention_heads=8,
)

# Create protocol instance
protocol = IntelligenceProtocol(config)

# Autonomous reasoning over spectral data
spectrum = np.random.randn(256)
result = protocol.reason(spectrum, strategy=ReasoningStrategy.ENSEMBLE)
print(f"Conclusion: {result.conclusion}")
print(f"Confidence: {result.confidence:.3f}")
print(f"Evidence: {result.evidence}")
print(f"Recommended actions: {result.recommended_actions}")
```

### Intelligence Levels

| Level | Behavior |
|-------|----------|
| Passive | Observe and record only |
| Reactive | Respond to detected anomalies |
| Adaptive | Learn from patterns and adjust |
| Predictive | Anticipate future spectral states |
| Autonomous | Full self-directed reasoning |

## Spectral Transformer Pipeline

End-to-end transformer encoder architecture optimized for spectral sequences:

```python
from mesie import SpectralTransformerPipeline, TransformerConfig, SpectralTokenizer
import numpy as np

# Configure and build pipeline
config = TransformerConfig(d_model=128, n_heads=8, n_layers=6, pooling="mean")
pipeline = SpectralTransformerPipeline(config)

# Process spectral data
spectrum = np.random.randn(512)
output = pipeline.forward(spectrum)
print(f"Embedding shape: {output.embedding.shape}")
print(f"Attention maps: {len(output.attention_maps)} layers")

# Tokenization strategies
tokenizer = SpectralTokenizer(method="frequency_bins", n_tokens=64)
tokens = tokenizer.tokenize(spectrum)
```

## Helix Vector Encoding

Hierarchical spectral encoding using helical geometry for efficient retrieval:

```python
from mesie import VectorHelix, HelixConfig, HelixEncoder, HelixRetriever
import numpy as np

# Encode spectra into helix space
config = HelixConfig(dimensions=64, turns=8)
helix = VectorHelix(config)
encoded = helix.encode(np.random.randn(256))

# Retrieval over helix-encoded vectors
retriever = HelixRetriever()
results = retriever.search(query=encoded, top_k=10)
```

## Protocols and Streaming

Standardized spectral data protocols for interoperability and real-time streaming:

```python
from mesie import SpectralDataProtocol, StreamingProtocol, SpectralSerializer, SerializationFormat

# Define and send protocol messages
protocol = SpectralDataProtocol()
message = protocol.create_message(record, metadata={"source": "sensor_array_1"})

# Stream spectral data in real-time
stream = StreamingProtocol(buffer_size=1024)
stream.push(spectrum_chunk)

# Serialize in multiple formats
serializer = SpectralSerializer(format=SerializationFormat.MSGPACK)
payload = serializer.encode(record)
```

## AI System Integration

Connect MESIE to external AI systems and orchestrate complex pipelines:

```python
from mesie import AISystemConnector, ConnectorConfig, PipelineOrchestrator, OrchestratorConfig

# Connect to AI systems
connector = AISystemConnector(ConnectorConfig(endpoint="local", batch_size=32))
predictions = connector.predict(embeddings)

# Orchestrate multi-stage pipelines
orchestrator = PipelineOrchestrator(OrchestratorConfig(
    stages=["validate", "extract", "embed", "reason"],
    parallel=True,
))
result = orchestrator.run(records)
```

## Cognitive Architecture Integration

```python
from mesie.cognitive import SpectralMemoryAdapter

adapter = SpectralMemoryAdapter()
memory_object = adapter.to_memory_object(record)
# Returns: {semantic_id, spectral_embedding, resonance_signature, coherence_signature, ...}
```

## TAURUS Memory System

TAURUS (Temporal Adaptive Retrieval and Unified Storage) provides persistent, attention-weighted spectral memory for cognitive architectures:

```python
from mesie.cognitive import TaurusMemoryStore, TaurusWorkingMemory
import numpy as np

# Long-term memory with temporal decay and attention-weighted retrieval
store = TaurusMemoryStore(capacity=1000)
store.store(embedding=np.random.randn(128), context={"source": "sensor_A"}, importance=0.9)

# Retrieve by similarity with attention weighting
results = store.retrieve(query=np.random.randn(128), top_k=5)

# Working memory with automatic promotion to long-term storage
working = TaurusWorkingMemory(capacity=7, long_term_store=store)
working.hold(embedding=np.random.randn(128), semantic_tag="transient")
```

## NeuroCores — Spectral Neural Processing

NeuroCores are self-contained neural processing units combining attention, memory (TAURUS), and multi-scale analysis:

```python
from mesie.cognitive import SpectralNeuroCore, NeuroCoreCluster, NeuroCoreConfig
import numpy as np

# Single core with full pipeline
core = SpectralNeuroCore(NeuroCoreConfig(d_model=128, n_attention_heads=8))
result = core.process(np.random.randn(256))

# Access attention analysis for interpretability
analysis = core.get_attention_analysis()
# Returns: {mean_entropy, mean_max_attention, mean_sparsity, memory_analysis, ...}

# Multi-core cluster for ensemble processing
cluster = NeuroCoreCluster(n_cores=4)
ensemble_embedding = cluster.get_ensemble_embedding(np.random.randn(256))
```

## Attention Analysis

The pipeline provides interpretability through `get_attention_analysis()`:

- **Attention entropy**: How distributed vs. focused the attention is
- **Maximum attention**: Strength of the strongest attended-to token
- **Attention sparsity**: Fraction of near-zero attention weights

This enables understanding of what the model focuses on — critical for scientific applications where interpretability is required.

```python
from mesie import SpectralTransformerPipeline, TransformerConfig
import numpy as np

pipeline = SpectralTransformerPipeline(TransformerConfig(d_model=64, n_heads=4))
analysis = pipeline.get_attention_analysis(np.random.randn(128))
# {'n_layers': 4, 'layer_analyses': [{layer, attention_entropy, max_attention, attention_sparsity}, ...]}
```

### What This Enables for AI Systems

1. **Spectral understanding**: Models that truly "understand" spectral structure, not just memorize patterns
2. **Long-range dependency capture**: Detection of harmonics, resonances, and cross-band relationships
3. **Multi-scale analysis**: Simultaneous processing at multiple frequency resolutions
4. **Transfer learning ready**: Pre-trained spectral transformers that transfer across domains
5. **Interpretable attention**: Visualization of model focus for scientific validation
6. **Efficient inference**: Fixed-size embeddings from variable-length spectra
7. **Foundation model potential**: Architecture suitable for large-scale pre-training on diverse spectral data

## Architecture

```mermaid
flowchart TD
    A[Input Spectral Records] --> B[Validation Layer]
    B --> C[Normalization + Interpolation]
    C --> D[Feature Extraction]
    D --> E[Electro-Spectral Feature Layer]
    D --> F[Node Topology Mapping]
    E --> G[Spectral Matcher]
    F --> G
    G --> H[Match Scores + Rankings]
    D --> I[Spectral Generator]
    I --> J[Single / RotDnn / PSD / FAS Outputs]
    D --> K[Spectral Embedding Encoder]
    K --> L[AI Retrieval + Cognitive Memory]
    D --> M[Transformer Pipeline]
    M --> N[Intelligence Protocols]
    N --> O[Autonomous Reasoning + Actions]
    K --> P[Helix Vector Encoding]
    P --> Q[Helix Retrieval]
    L --> R[Protocol Streaming + Serialization]
    O --> R
```

## Project Structure

```
mesie/
├── core/          — Data structures and configuration
├── io/            — Loading and exporting records
├── processing/    — Normalization, interpolation, smoothing
├── matching/      — Spectral comparison and scoring
├── generation/    — PSD, FAS, RotDnn, single-component generation
├── features/      — Electro-spectral features, resonance, coherence
├── topology/      — Node mapping and lineage tracking
├── embeddings/    — Spectral vectorization and retrieval
├── cognitive/     — TAURUS memory, NeuroCores, attention, agent-state adapters
├── ai/            — Transformer pipeline, intelligence protocols, training, inference, transfer
├── protocols/     — Spectral data protocols, streaming, serialization
├── integration/   — AI system connectors, library bridges, pipeline orchestration
├── helix/         — Helix vector encoding, projection, and retrieval
├── validation/    — Multi-level validation
└── visualization/ — Plotting and diagrams
```

## Research Direction

MESIE is designed to support **spectral intelligence**: the use of spectral structures as embeddings, memory objects, retrieval objects, and state signatures in AI systems.

See [docs/research_program.md](docs/research_program.md) for the full research program.

## Citation

If you use MESIE in your research, please cite:

```bibtex
@software{medina2024mesie,
  author = {Medina, Alfredo},
  title = {MESIE: Multi-Element Spectral Intelligence Engine},
  version = {0.2.0},
  year = {2024},
  url = {https://github.com/FreddyCreates/Multi-Element-Spectral-Intelligence-Engine-MESIE-}
}
```

## Cross-Domain Spectral Transfer

MESIE implements a **cross-domain spectral brain** — a foundation-model-style system that generalizes across wildly different spectral domains.

### Multi-Domain Spectral Corpora

Because MESIE uses:
- **CORAL** (CORrelation ALignment) — aligns second-order statistics between domains
- **MMD** (Maximum Mean Discrepancy) — minimizes distribution distance in kernel space
- **Domain-invariant normalization** — whitening transforms that factor out domain-specific characteristics

...it can learn shared structure across wildly different spectral domains.

This is the spectral equivalent of:
- text → code transfer
- image → video transfer
- audio → language transfer

### Supported Transfer Paths

| Source Domain | Target Domain | Transfer Type |
|--------------|---------------|---------------|
| Earthquake Harmonics | Bridge Vibration Anomalies | Seismic → Structural |
| EEG Oscillations | Audio Resonance Detection | Neural → Acoustic |
| Electromagnetic/RF | Optical Spectroscopy | EM → Optical |
| Climate Atmospheric | Financial Time Series | Cyclic → Market |

### Usage

```python
from mesie.cognitive import (
    SpectralDomainGenerator,
    TransferLearningPipeline,
    SpectralDomain,
    CORALTransfer,
    MMDTransfer,
    CrossDomainTransferEngine,
)

# Initialize with multi-domain synthetic corpora
pipeline = TransferLearningPipeline(shared_dim=64)
pipeline.initialize_with_synthetic(n_samples=1000, n_features=256)

# Transfer: earthquake harmonics → bridge vibration anomalies
result = pipeline.evaluate_transfer(
    SpectralDomain.SEISMIC,
    SpectralDomain.STRUCTURAL_VIBRATION,
    method="coral"
)
print(f"Transfer efficiency: {result['transfer_efficiency']:.3f}")
print(f"MMD reduction: {result['mmd_before']:.4f} → {result['mmd_after']:.4f}")

# Transfer: EEG oscillations → audio resonance detection
result = pipeline.evaluate_transfer(
    SpectralDomain.EEG_NEURAL,
    SpectralDomain.AUDIO_ACOUSTIC,
    method="combined"  # CORAL + MMD refinement
)

# Find optimal transfer strategy automatically
strategy = pipeline.find_optimal_transfer_strategy(
    SpectralDomain.ELECTROMAGNETIC,
    SpectralDomain.AUDIO_ACOUSTIC
)
print(f"Best method: {strategy['best_method']}")
```

### What Makes This a Foundation Model

1. **Generalization across domains** — a model trained on earthquake harmonics transfers to bridge vibration anomalies
2. **Shared spectral representations** — domain-invariant encoding learns universal spectral structure
3. **Multi-hop transfer** — distant domains connected through intermediate spectral spaces
4. **Automatic domain discovery** — the system identifies compatible domains via similarity graphs

## Experiment Management

MESIE provides comprehensive experiment tracking and hyperparameter optimization:

```python
from mesie.cognitive import (
    ExperimentPipeline,
    ExperimentConfig,
    SpectralBenchmark,
    DataAugmentation,
    CrossValidationEngine,
    StatisticalTestSuite,
)

# Run optimized experiments with cross-validation
pipeline = ExperimentPipeline(
    name="spectral_classification",
    search_space={
        "lr": {"type": "float", "range": [0.001, 0.1], "log": True},
        "layers": {"type": "int", "range": [1, 8]},
    }
)
result = pipeline.optimize(data, labels, n_trials=50)

# Benchmark with statistical rigor
stats = StatisticalTestSuite()
ci = stats.bootstrap_ci(scores, n_bootstrap=1000)
comparison = stats.paired_t_test(method_a_scores, method_b_scores)
```

## Monte Carlo Enterprise Benchmark

MESIE is validated across **10 enterprise verticals** with **5,000 stochastic trials** (500 per use case):

| # | Industry | Use Case | Success |
|---|----------|----------|---------|
| 1 | Manufacturing | Predictive maintenance (vibration drift) | 100% |
| 2 | Energy | Grid & power (Schumann/EM under noise) | 100% |
| 3 | Aerospace | Satellite / orbital edge + seismic anchor | 100% |
| 4 | Insurance | Catastrophe / seismic risk cross-match | 100% |
| 5 | Construction | Structural FAS ranking under perturbation | 100% |
| 6 | Healthcare | Device monitoring (anomaly vs baseline) | 100% |
| 7 | Robotics | Fleet ANN state lookup | 100% |
| 8 | Telecom | Spectrum compliance (research + EM libs) | 100% |
| 9 | Research | R&D lab benchmark classification | 100% |
| 10 | Enterprise AI | Agent spectral memory (MAESI + fingerprint) | 100% |

**Overall: 100% success rate | Enterprise grade (≥85%): PASS | Runtime: ~8s for 5,000 trials**

Run the benchmark:

```bash
# Quick (2,000 trials)
python scripts/monte_carlo_enterprise_benchmark.py --trials 200

# Full enterprise (5,000 trials)
python scripts/monte_carlo_enterprise_benchmark.py --trials 500

# Or run as pytest (includes long workflow patterns)
pytest tests/test_enterprise_workflows.py -v
```

Full report: [deliverables/MESIE_Monte_Carlo_Enterprise_Report.md](deliverables/MESIE_Monte_Carlo_Enterprise_Report.md)

## License

Apache-2.0 — See [LICENSE](LICENSE) for details.

