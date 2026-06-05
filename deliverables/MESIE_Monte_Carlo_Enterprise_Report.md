# MESIE Monte Carlo Enterprise Report

*Generated 2026-06-05T22:54:03Z — 2,000 trials across 10 enterprise use cases*

## Executive summary

- **Overall success rate:** 100.0%
- **Enterprise grade (≥85%):** PASS
- **Total runtime:** 1.18 s
- **Trials per use case:** 200

## 10 enterprise use cases

| # | Industry | Use case | Success % | Mean ms | P95 ms | Mean score |
|---|----------|----------|-----------|---------|--------|------------|
| 1 | Manufacturing | Predictive Maintenance | 100.0% | 0.14 | 0.14 | 0.978 |
| 2 | Energy | Grid & Power Monitoring | 100.0% | 0.14 | 0.16 | 6.000 |
| 3 | Aerospace | Satellite Ops & Orbital | 100.0% | 0.18 | 0.19 | 0.859 |
| 4 | Insurance | Catastrophe / Seismic Risk | 100.0% | 0.16 | 0.19 | 0.635 |
| 5 | Construction | Structural / Civil Engineering | 100.0% | 0.67 | 0.80 | 0.846 |
| 6 | Healthcare | Medical Device Monitoring | 100.0% | 0.26 | 0.34 | 74.607 |
| 7 | Robotics | Autonomous Robotics Fleet | 100.0% | 0.10 | 0.10 | 0.958 |
| 8 | Telecom | Telecom Spectrum Compliance | 100.0% | 0.02 | 0.02 | 2.000 |
| 9 | Research | R&D Spectral Lab | 100.0% | 0.66 | 0.79 | 0.739 |
| 10 | Enterprise AI | AI Agent Spectral Memory | 100.0% | 3.56 | 4.35 | 1.000 |

## Per-use-case detail

### Predictive Maintenance (Manufacturing)

Detect pump/machine drift from vibration spectra.

- Success metric: `top_match_sim >= 0.5`
- Success rate: **100.0%** (200/200)
- Latency: mean 0.14 ms, std 0.56, p95 0.14
- Score: mean 0.9779, std 0.0484, p5 0.8993

### Grid & Power Monitoring (Energy)

Schumann/EM band fingerprint stability under noise.

- Success metric: `validation_level >= 4`
- Success rate: **100.0%** (200/200)
- Latency: mean 0.14 ms, std 0.16, p95 0.16
- Score: mean 6.0000, std 0.0000, p5 6.0000

### Satellite Ops & Orbital (Aerospace)

Orbital-edge style spectral gate + seismic anchor coupling.

- Success metric: `match_score >= 0.6`
- Success rate: **100.0%** (200/200)
- Latency: mean 0.18 ms, std 0.12, p95 0.19
- Score: mean 0.8589, std 0.0226, p5 0.7950

### Catastrophe / Seismic Risk (Insurance)

Cross-match earthquake vs structural references.

- Success metric: `match_score >= 0.55`
- Success rate: **100.0%** (200/200)
- Latency: mean 0.16 ms, std 0.02, p95 0.19
- Score: mean 0.6352, std 0.0019, p5 0.6318

### Structural / Civil Engineering (Construction)

FAS structural spectrum ranking under perturbation.

- Success metric: `rank_top3_self_or_structural`
- Success rate: **100.0%** (200/200)
- Latency: mean 0.67 ms, std 0.16, p95 0.80
- Score: mean 0.8459, std 0.0023, p5 0.8419

### Medical Device Monitoring (Healthcare)

Anomaly separation on biosignal-like spectra.

- Success metric: `anomaly_detects_outlier`
- Success rate: **100.0%** (200/200)
- Latency: mean 0.26 ms, std 0.06, p95 0.34
- Score: mean 74.6074, std 6.1115, p5 51.7212

### Autonomous Robotics Fleet (Robotics)

Fast ANN neighbor lookup for fleet state.

- Success metric: `query_ms < 50 and sim > 0.4`
- Success rate: **100.0%** (200/200)
- Latency: mean 0.10 ms, std 0.08, p95 0.10
- Score: mean 0.9578, std 0.0694, p5 0.8287

### Telecom Spectrum Compliance (Telecom)

EM band library embedding + research hit.

- Success metric: `research_hit_found`
- Success rate: **100.0%** (200/200)
- Latency: mean 0.02 ms, std 0.09, p95 0.02
- Score: mean 2.0000, std 0.0000, p5 2.0000

### R&D Spectral Lab (Research)

Benchmark sample classification via ranking.

- Success metric: `rank_score >= 0.45`
- Success rate: **100.0%** (200/200)
- Latency: mean 0.66 ms, std 0.13, p95 0.79
- Score: mean 0.7388, std 0.0406, p5 0.6760

### AI Agent Spectral Memory (Enterprise AI)

MAESI query with knowledge + fingerprint ANN.

- Success metric: `neighbors >= 1 and latency < 100ms`
- Success rate: **100.0%** (200/200)
- Latency: mean 3.56 ms, std 1.88, p95 4.35
- Score: mean 1.0000, std 0.0000, p5 1.0000

## How to re-run

```bash
python scripts/monte_carlo_enterprise_benchmark.py
python scripts/monte_carlo_enterprise_benchmark.py --trials 500
```
