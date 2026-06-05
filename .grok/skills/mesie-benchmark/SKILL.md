---
name: mesie-benchmark
description: >
  Determinism and match/embed throughput. Triggers: benchmark, determinism, speed. Use for /mesie-benchmark or MESIE/MAESI/NeuroAIX tasks.
---

# mesie-benchmark

Native MESIE / MAESI / NeuroAIX skill — **Quality Assurance & Benchmarks**.

## When to use

- Determinism and match/embed throughput.

## Tools in this skill

### `benchmark` — Speed Benchmark
- Command: `python scripts/determinism_benchmark.py`

## Agent workflow

1. `cd` to repo root: `Multi-Element-Spectral-Intelligence-Engine-MESIE-`
2. Run via unified CLI: `python -m mesie.tools.cli run <tool-id>`
3. Or run the command above directly.
4. Read deliverable path if present; summarize results for the user.
5. On failure: run `python -m mesie.tools.cli run test` to verify environment.

## Repo paths

- Tools registry: `mesie/tools/registry.py`
- CLI: `python -m mesie.tools.cli list`