# MESIE Monte Carlo Enterprise Report

*Generated 2026-06-07T03:23:02Z — 2,000 trials across 10 enterprise use cases*

## Executive summary

- **Overall success rate:** 100.0%
- **Enterprise grade (≥85%):** PASS
- **Total runtime:** 1.83 s
- **Trials per use case:** 200

## 10 enterprise use cases

| # | Industry | Use case | Success % | Mean ms | P95 ms | Mean score |
|---|----------|----------|-----------|---------|--------|------------|
| 1 | Manufacturing | Predictive Maintenance | 100.0% | 0.77 | 0.91 | 0.604 |
| 2 | Energy | Grid & Power Monitoring | 100.0% | 0.82 | 1.09 | 0.708 |
| 3 | Aerospace | Satellite Ops & Orbital | 100.0% | 0.72 | 1.17 | 0.762 |
| 4 | Insurance | Catastrophe / Seismic Risk | 100.0% | 1.21 | 1.38 | 0.767 |
| 5 | Construction | Structural / Civil Engineering | 100.0% | 0.86 | 0.88 | 0.690 |
| 6 | Healthcare | Medical Device Monitoring | 100.0% | 0.73 | 0.88 | 0.710 |
| 7 | Robotics | Autonomous Robotics Fleet | 100.0% | 1.41 | 1.21 | 0.601 |
| 8 | Telecom | Telecom Spectrum Compliance | 100.0% | 0.91 | 1.01 | 0.749 |
| 9 | Research | R&D Spectral Lab | 100.0% | 0.81 | 0.91 | 0.769 |
| 10 | Enterprise AI | AI Agent Spectral Memory | 100.0% | 0.87 | 0.73 | 0.763 |

## Per-use-case detail

### Predictive Maintenance (Manufacturing)

Detect pump/machine drift from vibration spectra.

- Success metric: `top_match_sim >= 0.5`
- Success rate: **100.0%** (200/200)
- Latency: mean 0.77 ms, std 1.11, p95 0.91
- Score: mean 0.6042, std 0.0274, p5 0.5545

### Grid & Power Monitoring (Energy)

Schumann/EM band fingerprint stability under noise.

- Success metric: `validation_level >= 4`
- Success rate: **100.0%** (200/200)
- Latency: mean 0.82 ms, std 1.34, p95 1.09
- Score: mean 0.7078, std 0.0094, p5 0.6875

### Satellite Ops & Orbital (Aerospace)

Orbital-edge style spectral gate + seismic anchor coupling.

- Success metric: `match_score >= 0.6`
- Success rate: **100.0%** (200/200)
- Latency: mean 0.72 ms, std 0.38, p95 1.17
- Score: mean 0.7619, std 0.0172, p5 0.7310

### Catastrophe / Seismic Risk (Insurance)

Cross-match earthquake vs structural references.

- Success metric: `match_score >= 0.55`
- Success rate: **100.0%** (200/200)
- Latency: mean 1.21 ms, std 2.73, p95 1.38
- Score: mean 0.7669, std 0.0153, p5 0.7293

### Structural / Civil Engineering (Construction)

FAS structural spectrum ranking under perturbation.

- Success metric: `rank_top3_self_or_structural`
- Success rate: **100.0%** (200/200)
- Latency: mean 0.86 ms, std 1.97, p95 0.88
- Score: mean 0.6898, std 0.0128, p5 0.6664

### Medical Device Monitoring (Healthcare)

Anomaly separation on biosignal-like spectra.

- Success metric: `anomaly_detects_outlier`
- Success rate: **100.0%** (200/200)
- Latency: mean 0.73 ms, std 0.55, p95 0.88
- Score: mean 0.7098, std 0.0079, p5 0.6990

### Autonomous Robotics Fleet (Robotics)

Fast ANN neighbor lookup for fleet state.

- Success metric: `query_ms < 50 and sim > 0.4`
- Success rate: **100.0%** (200/200)
- Latency: mean 1.41 ms, std 4.28, p95 1.21
- Score: mean 0.6010, std 0.0319, p5 0.5365

### Telecom Spectrum Compliance (Telecom)

EM band library embedding + research hit.

- Success metric: `research_hit_found`
- Success rate: **100.0%** (200/200)
- Latency: mean 0.91 ms, std 2.46, p95 1.01
- Score: mean 0.7485, std 0.0024, p5 0.7458

### R&D Spectral Lab (Research)

Benchmark sample classification via ranking.

- Success metric: `rank_score >= 0.45`
- Success rate: **100.0%** (200/200)
- Latency: mean 0.81 ms, std 1.29, p95 0.91
- Score: mean 0.7687, std 0.0130, p5 0.7354

### AI Agent Spectral Memory (Enterprise AI)

MAESI query with knowledge + fingerprint ANN.

- Success metric: `neighbors >= 1 and latency < 100ms`
- Success rate: **100.0%** (200/200)
- Latency: mean 0.87 ms, std 1.74, p95 0.73
- Score: mean 0.7628, std 0.0161, p5 0.7310

## How to re-run

```bash
python scripts/monte_carlo_enterprise_benchmark.py
python scripts/monte_carlo_enterprise_benchmark.py --trials 500
```
