# MESIE External Dataset Validation Report

**Run ID:** `mesie-external-20260718T064805Z`
**Generated:** 2026-07-18T06:48:05.879456+00:00
**Configuration SHA-256:** `89c46dec17cf4515cf3fb5fdf5b685163b83833b5831ca54a65e69772db2c819`

## Executive result

MESIE met the frozen external-support rule on 3/3 public datasets. This result measures reproducible classification utility; it does not establish universal cross-domain semantics or production readiness.

## Benchmark results

| Dataset | Domain | Feature set | Accuracy | Macro F1 | Feature ms/sample | Query ms/sample |
|---|---|---|---:|---:|---:|---:|
| GunPoint | human-motion | statistics | 0.8400 | 0.8400 | 0.211714 | 0.000641 |
| GunPoint | human-motion | fft-32 | 0.8667 | 0.8666 | 0.021859 | 0.001003 |
| GunPoint | human-motion | mesie | 0.8800 | 0.8798 | 21.333450 | 0.000933 |
| GunPoint | human-motion | mesie-temporal-spectral-v2 | 0.8800 | 0.8795 | 0.194178 | 0.017297 |
| ECG200 | biomedical-ecg | statistics | 0.7800 | 0.7613 | 0.005786 | 0.001053 |
| ECG200 | biomedical-ecg | fft-32 | 0.8900 | 0.8799 | 0.005468 | 0.001090 |
| ECG200 | biomedical-ecg | mesie | 0.7600 | 0.7326 | 0.191251 | 0.000680 |
| ECG200 | biomedical-ecg | mesie-temporal-spectral-v2 | 0.8900 | 0.8783 | 0.176000 | 0.003326 |
| ItalyPowerDemand | electrical-demand | statistics | 0.7328 | 0.7328 | 0.001400 | 0.000759 |
| ItalyPowerDemand | electrical-demand | fft-32 | 0.8455 | 0.8455 | 0.000525 | 0.000314 |
| ItalyPowerDemand | electrical-demand | mesie | 0.8047 | 0.8047 | 0.175496 | 0.000347 |
| ItalyPowerDemand | electrical-demand | mesie-temporal-spectral-v2 | 0.9184 | 0.9184 | 0.131022 | 0.000764 |

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
mesie-validate-external run --config configs/public_ucr.json
```
