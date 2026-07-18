"""Deterministic nearest-neighbor evaluation and metrics."""

from __future__ import annotations

import time
from typing import Any

import numpy as np


def _standardize(train: np.ndarray, test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = train.mean(axis=0, keepdims=True)
    std = train.std(axis=0, keepdims=True)
    return (train - mean) / np.maximum(std, 1e-12), (test - mean) / np.maximum(std, 1e-12)


def _predict_1nn(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    train_norm = np.maximum(np.linalg.norm(train_x, axis=1), 1e-12)
    test_norm = np.maximum(np.linalg.norm(test_x, axis=1), 1e-12)
    similarity = (test_x @ train_x.T) / (test_norm[:, None] * train_norm[None, :])
    return train_y[np.argmax(similarity, axis=1)]


def _macro_f1(actual: np.ndarray, predicted: np.ndarray) -> float:
    scores = []
    for label in sorted(set(actual.tolist())):
        tp = np.sum((actual == label) & (predicted == label))
        fp = np.sum((actual != label) & (predicted == label))
        fn = np.sum((actual == label) & (predicted != label))
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        scores.append(2 * precision * recall / max(precision + recall, 1e-12))
    return float(np.mean(scores))


def evaluate_feature_set(
    name: str,
    train_values: np.ndarray,
    train_labels: np.ndarray,
    test_values: np.ndarray,
    test_labels: np.ndarray,
    extractor,
) -> dict[str, Any]:
    started = time.perf_counter()
    train_features = np.asarray(extractor(train_values), dtype=np.float64)
    test_features = np.asarray(extractor(test_values), dtype=np.float64)
    feature_ms = (time.perf_counter() - started) * 1000
    train_features, test_features = _standardize(train_features, test_features)

    query_started = time.perf_counter()
    predicted = _predict_1nn(train_features, train_labels, test_features)
    query_ms = (time.perf_counter() - query_started) * 1000
    accuracy = float(np.mean(predicted == test_labels))
    return {
        "feature_set": name,
        "embedding_dim": int(train_features.shape[1]),
        "accuracy": accuracy,
        "macro_f1": _macro_f1(test_labels, predicted),
        "feature_total_ms": round(feature_ms, 4),
        "feature_ms_per_sample": round(feature_ms / (len(train_values) + len(test_values)), 6),
        "query_total_ms": round(query_ms, 4),
        "query_ms_per_sample": round(query_ms / len(test_values), 6),
        "correct": int(np.sum(predicted == test_labels)),
        "total": int(len(test_labels)),
    }
