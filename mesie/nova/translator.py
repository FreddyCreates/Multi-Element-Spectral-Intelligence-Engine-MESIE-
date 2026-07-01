"""NOVA translator layer — unify text/spectral/state into MESIE-ready payloads."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

import numpy as np


@dataclass
class TranslatedPayload:
    modality: str
    text: str
    spectral_signature: List[float]
    fingerprint: str
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "modality": self.modality,
            "text": self.text[:500],
            "spectral_signature": self.spectral_signature[:16],
            "fingerprint": self.fingerprint,
            "meta": self.meta,
        }


class TranslatorEngine:
    """Cross-modality translator — adaptive bridge into MESIE spectral records."""

    def translate(
        self,
        payload: Union[str, Dict[str, Any], List[float]],
        *,
        source_modality: str = "text",
    ) -> TranslatedPayload:
        if isinstance(payload, str):
            text = payload
            sig = self._text_spectrum(text)
        elif isinstance(payload, dict):
            text = str(payload.get("text") or payload.get("content") or "")
            if "amplitude" in payload or "spectrum" in payload:
                arr = np.asarray(payload.get("amplitude") or payload.get("spectrum"), dtype=float)
                sig = self._normalize(arr)
                source_modality = "spectral"
            else:
                sig = self._text_spectrum(text or str(payload))
        else:
            arr = np.asarray(payload, dtype=float)
            text = f"[spectral_array len={len(arr)}]"
            sig = self._normalize(arr)
            source_modality = "spectral"

        fp = hashlib.sha256((text + str(sig[:8])).encode()).hexdigest()
        return TranslatedPayload(
            modality=source_modality,
            text=text,
            spectral_signature=sig.tolist(),
            fingerprint=fp,
            meta={"dims": len(sig)},
        )

    @staticmethod
    def _text_spectrum(text: str, n: int = 32) -> np.ndarray:
        sig = np.array([float(ord(c) % 97) for c in text[:n]], dtype=float)
        if len(sig) < n:
            sig = np.pad(sig, (0, n - len(sig)))
        spec = np.abs(np.fft.rfft(sig - np.linspace(sig[0], sig[-1], n)))
        norm = float(np.linalg.norm(spec)) + 1e-12
        return spec / norm

    @staticmethod
    def _normalize(arr: np.ndarray) -> np.ndarray:
        if arr.size == 0:
            return np.zeros(8)
        a = arr.flatten()[:64]
        norm = float(np.linalg.norm(a)) + 1e-12
        return a / norm