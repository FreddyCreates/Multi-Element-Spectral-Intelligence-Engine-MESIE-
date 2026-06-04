# MESIE — Performance & Scale Factsheet

> Plain-language numbers for what MESIE does and how large it is.

---

## Speed (single laptop, single core, no GPU)

> **"MESIE can compare thousands of spectral fingerprints per second on a
> normal laptop — faster than opening a spreadsheet, and far faster than
> waiting on the cloud."**

### Core operation: one match

| Metric | Value |
|--------|-------|
| Single spectral match | ~0.25 ms |
| Throughput | ~4,000 comparisons / sec |
| Rank a handful of candidates | < 1 ms (~1,000 rankings / sec) |
| Generate a synthetic spectrum (fixed seed) | ~0.05 ms (~19,000 / sec) |

### Everyday comparisons

| What people know | Rough time | MESIE equivalent |
|------------------|-----------|------------------|
| Double-clicking open a medium Excel file | ~1–3 seconds | ~4,000–12,000 matches in the same time |
| One round-trip to a typical cloud API (network only) | ~50–200 ms | ~200–800× faster (just local math, no network) |
| An engineer eyeballing a chart | minutes | Millions of times faster |
| Running a heavy ML model inference | 100 ms – seconds | Core path is lightweight math, not a big neural net |

### Determinism

Same inputs + same seed → same answer every time. Good for audits,
demos, and regulated workflows.

---

## Codebase Size (the software itself)

| Metric | Value |
|--------|-------|
| Python modules | ~30 |
| Lines of production code | ~3,000 |
| Test coverage | Core matching, generation, embeddings, validation |
| Install size | Lightweight — NumPy is the only hard dependency |

MESIE is a **compact, modular engine** — not a monolith. The codebase is
intentionally small so it remains auditable, fast to install, and easy to
extend.

---

## Dataset Size (what you bring)

MESIE does **not** ship a built-in spectral library. You connect your own data:

| Scenario | Expected Scale |
|----------|---------------|
| Research prototype | 10–1,000 records |
| Production library | 10,000–1,000,000+ records |
| Real-time stream | Continuous ingestion via `SpectralCorpus` |

Use `SpectralCorpus.from_directory()` or the CLI (`mesie load-corpus /path`)
to point the engine at your spectral library of any size.

---

## What MESIE Does (capabilities)

1. **Spectral Matching** — composite scoring across cosine similarity, RMSE,
   log spectral distance, band-weighted error, electro-spectral alignment,
   and node topology.
2. **Signal Generation** — synthesize PSD, FAS, and RotDnn spectra from
   parametric configurations.
3. **Embeddings** — convert spectral records into fixed-size vectors for ML,
   clustering, and retrieval.
4. **Validation** — automated quality checks on spectral records.
5. **Corpus Management** — load, filter, and iterate large spectral
   libraries from directories of JSON/CSV files.

---

## One-Line Quickstart

```python
from mesie.sdk import SpectralIntelligenceSDK

engine = SpectralIntelligenceSDK()
corpus = engine.load_corpus("/path/to/your/spectral/library")
results = engine.rank(candidate_record, top_k=10)
```

Or from the command line:

```bash
mesie load-corpus /path/to/your/library --list
mesie repl --corpus /path/to/your/library
```

---

## Key Distinction

| Term | Meaning |
|------|---------|
| **Codebase size** | How many lines of Python make up MESIE (~3 k LoC) |
| **Dataset size** | How many spectral records you load into the engine (your data) |

MESIE is small software that processes large data. These are independent
numbers — a 3,000-line engine can match against a million-record library.
