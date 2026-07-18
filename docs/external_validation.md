# MESIE External Validation

This package advances MESIE from internally generated demonstrations to reproducible comparisons on public time-series datasets.

It downloads official UCR/TSML dataset archives, records their SHA-256 provenance, evaluates frozen statistical and FFT baselines, evaluates MESIE through its public SDK, and emits paired JSON evidence and a Markdown research report. It also includes an evidence-driven v2 adapter that preserves MESIE's compact embedding while adding temporal, frequency, and derivative residual channels.

## What is measured

- Official train/test classification accuracy
- Macro F1
- Feature-extraction latency
- Nearest-neighbor query latency
- MESIE performance relative to the stronger frozen baseline
- Exact source archive identity and experiment configuration hash

The initial domains are human motion (`GunPoint`), biomedical ECG (`ECG200`), and electrical demand (`ItalyPowerDemand`). These datasets test representation utility across unrelated sources without pretending that their class labels share meaning.

## Run

```powershell
mesie-validate-external run --config configs/public_ucr.json
```

Outputs are written to `deliverables/external_validation/external_validation_results.json` and `deliverables/external_validation/external_validation_report.md`.

## Test

```powershell
python -m pytest
```

## Scientific boundary

This experiment tests whether MESIE embeddings are useful for within-domain classification on several unrelated public datasets. It does not claim that distances between ECG and motion signals have shared physical meaning. A later cross-domain experiment must define a shared task and ground truth before making that claim.
