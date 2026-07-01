"""Read any modality as a unified MESIE signal — text, state, events, files, spectra."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np

from mesie.nova.translator import TranslatorEngine


class SignalModality(str, Enum):
    TEXT = "text"
    SPECTRAL = "spectral"
    JSON = "json"
    STATE = "state"
    EVENT = "event"
    NUMERIC = "numeric"
    FILE = "file"
    MIXED = "mixed"


@dataclass
class SignalReadResult:
    modality: SignalModality
    text: str
    spectral_signature: List[float]
    fingerprint: str
    record_id: str
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "modality": self.modality.value,
            "text": self.text[:2000],
            "spectral_signature": self.spectral_signature[:32],
            "fingerprint": self.fingerprint,
            "record_id": self.record_id,
            "meta": self.meta,
        }


class UniversalSignalReader:
    """Ingest text, JSON state, logs, files, and spectra into one signal envelope."""

    def __init__(self) -> None:
        self._translator = TranslatorEngine()

    def read(
        self,
        payload: Union[str, Dict[str, Any], List[Any], Path],
        *,
        hint: Optional[str] = None,
        source_id: Optional[str] = None,
    ) -> SignalReadResult:
        if isinstance(payload, (str, Path)) and Path(payload).is_file():
            return self.read_file(payload)
        modality, normalized = self._classify(payload, hint=hint)
        translated = self._translator.translate(normalized, source_modality=modality.value)
        text = self._extract_text(normalized, translated.text)
        record_id = source_id or translated.fingerprint[:16]
        meta = {
            "dims": len(translated.spectral_signature),
            "hint": hint,
            "chars": len(text),
            "keys": list(normalized.keys()) if isinstance(normalized, dict) else None,
        }
        if modality == SignalModality.FILE and isinstance(payload, (str, Path)):
            meta["path"] = str(payload)
        return SignalReadResult(
            modality=modality,
            text=text,
            spectral_signature=translated.spectral_signature,
            fingerprint=translated.fingerprint,
            record_id=record_id,
            meta=meta,
        )

    def read_file(self, path: Union[str, Path]) -> SignalReadResult:
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"signal file not found: {p}")
        suffix = p.suffix.lower()
        if suffix == ".json":
            data = json.loads(p.read_text(encoding="utf-8"))
            return self.read(data, hint="json", source_id=p.stem)
        if suffix in {".txt", ".md", ".log", ".jsonl"}:
            return self.read(p.read_text(encoding="utf-8", errors="replace"), hint="text", source_id=p.stem)
        return self.read(p.read_bytes().decode("utf-8", errors="replace"), hint="text", source_id=p.stem)

    def _classify(
        self,
        payload: Union[str, Dict[str, Any], List[Any], Path],
        *,
        hint: Optional[str],
    ) -> tuple[SignalModality, Any]:
        if hint == "spectral" or hint == "numeric":
            return SignalModality.SPECTRAL, payload

        if isinstance(payload, dict):
            if "components" in payload or "amplitude" in payload or "spectrum" in payload:
                return SignalModality.SPECTRAL, payload
            if payload.get("event") or payload.get("type") == "event":
                return SignalModality.EVENT, payload
            return SignalModality.JSON if "record_id" in payload else SignalModality.STATE, payload

        if isinstance(payload, list):
            if payload and isinstance(payload[0], (int, float)):
                return SignalModality.NUMERIC, payload
            return SignalModality.MIXED, payload

        if isinstance(payload, str):
            stripped = payload.strip()
            if stripped.startswith("{") or stripped.startswith("["):
                try:
                    parsed = json.loads(stripped)
                    return self._classify(parsed, hint=hint)
                except json.JSONDecodeError:
                    pass
            if self._looks_like_log(stripped):
                return SignalModality.EVENT, {"event": "log_line", "text": stripped}
            return SignalModality.TEXT, stripped

        return SignalModality.MIXED, payload

    @staticmethod
    def _extract_text(normalized: Any, fallback: str) -> str:
        if isinstance(normalized, str):
            return normalized
        if isinstance(normalized, dict):
            for key in ("text", "content", "message", "body", "summary", "conclusion"):
                val = normalized.get(key)
                if isinstance(val, str) and val.strip():
                    return val
            return json.dumps(normalized, ensure_ascii=False)[:4000]
        if isinstance(normalized, list):
            if normalized and isinstance(normalized[0], (int, float)):
                return f"[numeric_signal len={len(normalized)} mean={float(np.mean(normalized)):.4f}]"
            return json.dumps(normalized, ensure_ascii=False)[:4000]
        return fallback

    @staticmethod
    def _looks_like_log(text: str) -> bool:
        return bool(re.match(r"^\d{4}-\d{2}-\d{2}|^\[|^{", text[:24]))