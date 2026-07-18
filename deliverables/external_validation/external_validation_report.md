# MESIE External Dataset Validation Report

**Run ID:** `mesie-external-20260718T165257Z`
**Generated:** 2026-07-18T16:52:57.104656+00:00
**Configuration SHA-256:** `89c46dec17cf4515cf3fb5fdf5b685163b83833b5831ca54a65e69772db2c819`

## Executive result

MESIE met the frozen external-support rule on 3/3 public datasets. This result measures reproducible classification utility; it does not establish universal cross-domain semantics or production readiness.

## Sovereign binding

- Contract: `freddycreates.sovereign.training.v1`
- Repository: `FreddyCreates/sovereign`
- Commit: `9d14a7b57260a2b08ecb9e7b4952a00fdc7ef739`
- Bound records: 85
- Receipt SHA-256: `6df2138520d1af5c857d5f151faeacb69dd8b3a4770eb1e308bebd885a226f2b`

## Benchmark results

| Dataset | Domain | Feature set | Accuracy | Macro F1 | Feature ms/sample | Query ms/sample |
|---|---|---|---:|---:|---:|---:|
| GunPoint | human-motion | statistics | 0.8400 | 0.8400 | 0.084630 | 0.009205 |
| GunPoint | human-motion | fft-32 | 0.8667 | 0.8666 | 0.113196 | 0.000437 |
| GunPoint | human-motion | mesie | 0.8800 | 0.8798 | 29.224424 | 0.000563 |
| GunPoint | human-motion | mesie-temporal-spectral-v2 | 0.8800 | 0.8795 | 0.154275 | 0.018067 |
| ECG200 | biomedical-ecg | statistics | 0.7800 | 0.7613 | 0.002807 | 0.000587 |
| ECG200 | biomedical-ecg | fft-32 | 0.8900 | 0.8799 | 0.002540 | 0.000501 |
| ECG200 | biomedical-ecg | mesie | 0.7600 | 0.7326 | 0.118011 | 0.000646 |
| ECG200 | biomedical-ecg | mesie-temporal-spectral-v2 | 0.8900 | 0.8783 | 0.155655 | 0.001408 |
| ItalyPowerDemand | electrical-demand | statistics | 0.7328 | 0.7328 | 0.000725 | 0.000665 |
| ItalyPowerDemand | electrical-demand | fft-32 | 0.8455 | 0.8455 | 0.000535 | 0.000312 |
| ItalyPowerDemand | electrical-demand | mesie | 0.8047 | 0.8047 | 0.139236 | 0.000742 |
| ItalyPowerDemand | electrical-demand | mesie-temporal-spectral-v2 | 0.9184 | 0.9184 | 0.114471 | 0.000660 |

## Provenance

### GunPoint

- Source: https://www.timeseriesclassification.com/aeon-toolkit/GunPoint.zip
- Archive SHA-256: `d7513cfe222418fabfdb5a6434ffb21ac3de4923e637971e9388ebc857816803`
- Train/test samples: 50/150
- Series length: 150
- Classes: 1, 2

### ECG200

- Source: https://www.timeseriesclassification.com/aeon-toolkit/ECG200.zip
- Archive SHA-256: `755937ea37849346ea20033666b19d17345bb039971e8fa33458b16b62c09380`
- Train/test samples: 100/100
- Series length: 96
- Classes: -1, 1

### ItalyPowerDemand

- Source: https://www.timeseriesclassification.com/aeon-toolkit/ItalyPowerDemand.zip
- Archive SHA-256: `4b68635dc79855fbdb7787d5dff5bac978fd0448afaa8eb7811dae52d43e5e46`
- Train/test samples: 67/1029
- Series length: 24
- Classes: 1, 2

## Interpretation rules

- Results are comparisons on official train/test splits; they are not claims of state-of-the-art performance.
- `fft-32` is the frozen frequency-domain baseline.
- `statistics` is a small non-spectral control baseline.
- `mesie` uses z-normalized real-FFT amplitudes converted into MESIE records and embedded with the MESIE SDK.
- `mesie-temporal-spectral-v2` preserves the MESIE embedding and adds frozen FFT, temporal-shape, and derivative-spectrum residual channels.
- MESIE v2 is considered externally supported when it meets or exceeds the stronger baseline by the configured margin.
- Dataset archives are identified by SHA-256 so later runs can detect source drift.

## Reproduction

```powershell
mesie-validate-external run --config configs/public_ucr.json --sovereign-root ../sovereign
```
