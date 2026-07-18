"""Frozen feature extractors used in the external comparison."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

import numpy as np


def _z_normalize_rows(values: np.ndarray) -> np.ndarray:
    mean = values.mean(axis=1, keepdims=True)
    std = values.std(axis=1, keepdims=True)
    return (values - mean) / np.maximum(std, 1e-12)


def statistical_features(values: np.ndarray) -> np.ndarray:
    x = _z_normalize_rows(np.asarray(values, dtype=np.float64))
    diffs = np.diff(x, axis=1)
    zero_crossings = np.mean(x[:, :-1] * x[:, 1:] < 0, axis=1)
    return np.column_stack([
        x.mean(axis=1),
        x.std(axis=1),
        x.min(axis=1),
        x.max(axis=1),
        np.median(x, axis=1),
        np.mean(np.abs(diffs), axis=1),
        np.std(diffs, axis=1),
        zero_crossings,
    ])


def fft_features(values: np.ndarray, bins: int = 32) -> np.ndarray:
    x = _z_normalize_rows(np.asarray(values, dtype=np.float64))
    spectrum = np.abs(np.fft.rfft(x, axis=1))[:, 1:]
    spectrum = np.log1p(spectrum)
    if spectrum.shape[1] >= bins:
        edges = np.linspace(0, spectrum.shape[1], bins + 1, dtype=int)
        features = np.column_stack([
            spectrum[:, edges[i]:edges[i + 1]].mean(axis=1)
            for i in range(bins)
        ])
    else:
        features = np.pad(spectrum, ((0, 0), (0, bins - spectrum.shape[1])))
    return features / np.maximum(np.linalg.norm(features, axis=1, keepdims=True), 1e-12)


def temporal_paa_features(values: np.ndarray, bins: int = 32) -> np.ndarray:
    """Piecewise temporal shape retained alongside order-invariant spectral features."""
    x = _z_normalize_rows(np.asarray(values, dtype=np.float64))
    edges = np.linspace(0, x.shape[1], min(bins, x.shape[1]) + 1, dtype=int)
    features = np.column_stack([
        x[:, edges[i]:edges[i + 1]].mean(axis=1)
        for i in range(len(edges) - 1)
    ])
    if features.shape[1] < bins:
        features = np.pad(features, ((0, 0), (0, bins - features.shape[1])))
    return features


def mesie_features(values: np.ndarray, mesie_root: Path, n_bands: int = 8) -> np.ndarray:
    root = str(mesie_root.resolve())
    if root not in sys.path:
        sys.path.insert(0, root)
    try:
        from mesie.sdk import SpectralIntelligenceSDK
    except ImportError as exc:
        raise RuntimeError(f"Unable to import MESIE from {mesie_root}") from exc

    x = _z_normalize_rows(np.asarray(values, dtype=np.float64))
    sdk = SpectralIntelligenceSDK(n_bands=n_bands)
    records = []
    for index, series in enumerate(x):
        amplitude = np.abs(np.fft.rfft(series))[1:]
        frequency = np.fft.rfftfreq(series.size, d=1.0)[1:]
        records.append({
            "record_id": f"external-{index}",
            "components": [{
                "name": "rfft",
                "frequency": frequency.tolist(),
                "amplitude": amplitude.tolist(),
            }],
            "metadata": {"source": "external_validation", "transform": "z_norm+rfft"},
        })
    return np.asarray(sdk.embed(records), dtype=np.float64)


def mesie_temporal_spectral_features(values: np.ndarray, mesie_root: Path) -> np.ndarray:
    """Experimental v2 adapter: MESIE semantics plus frequency and temporal detail.

    MESIE's 17-value vector deliberately compresses a spectrum. External results showed
    that compression discarded class information on short ECG and demand sequences.
    This adapter keeps the public MESIE vector while adding frozen multi-resolution
    residual channels instead of changing MESIE internals without evidence.
    """
    x = np.asarray(values, dtype=np.float64)
    mesie = mesie_features(x, mesie_root, n_bands=8)
    spectrum = fft_features(x, bins=32)
    temporal = temporal_paa_features(x, bins=32)
    derivative_spectrum = fft_features(np.diff(x, axis=1), bins=16)
    return np.column_stack([mesie, spectrum, temporal, derivative_spectrum])


FeatureFn = Callable[[np.ndarray], np.ndarray]
