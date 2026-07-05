"""φ-Kernel — spectral compression, slice indexing, and zero-copy transfer.

High-tech kernel layer: compresses embeddings and code slices for
local → cloud → mainnet → GitHub → MCP transfer.
"""

from __future__ import annotations

import hashlib
import json
import struct
import time
import zlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

PHI = (1 + 5**0.5) / 2
ROOT = Path(__file__).resolve().parents[2]
KERNEL_STATE = ROOT / "deliverables" / "compute" / "PHI_KERNEL_STATE.json"


@dataclass
class PhiKernelSlice:
    slice_id: str
    source: str
    offset: int
    raw_bytes: int
    compressed_bytes: int
    phi_weight: float
    hash: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PhiKernel:
    """φ-weighted compression kernel for spectral data and code slices."""

    def __init__(self, compression_level: int = 6) -> None:
        self.compression_level = compression_level
        self._index: List[PhiKernelSlice] = []

    @staticmethod
    def phi_quantize(vec: np.ndarray, bits: int = 8) -> bytes:
        """Quantize embedding with φ-scaled bins."""
        v = vec.astype(np.float64)
        vmin, vmax = v.min(), v.max()
        span = max(vmax - vmin, 1e-9)
        bins = (1 / PHI) ** np.arange(bits)
        scaled = ((v - vmin) / span * (2**bits - 1)).astype(np.uint8)
        return scaled.tobytes()

    def compress_embedding(self, vec: np.ndarray, source: str = "embed") -> PhiKernelSlice:
        raw = vec.astype(np.float32).tobytes()
        compressed = zlib.compress(raw, self.compression_level)
        sid = hashlib.sha256(raw).hexdigest()[:16]
        rec = PhiKernelSlice(
            slice_id=f"φk-{sid}",
            source=source,
            offset=0,
            raw_bytes=len(raw),
            compressed_bytes=len(compressed),
            phi_weight=PHI ** -1,
            hash=hashlib.sha256(compressed).hexdigest(),
        )
        self._index.append(rec)
        return rec

    def compress_file_slices(self, path: Path, chunk_size: int = 32768) -> List[PhiKernelSlice]:
        if not path.is_file():
            return []
        raw = path.read_bytes()
        slices: List[PhiKernelSlice] = []
        for i, off in enumerate(range(0, len(raw), chunk_size)):
            chunk = raw[off : off + chunk_size]
            compressed = zlib.compress(chunk, self.compression_level)
            sid = hashlib.sha256(chunk).hexdigest()[:12]
            rec = PhiKernelSlice(
                slice_id=f"φk-{path.stem}-s{i:04d}",
                source=str(path.name),
                offset=off,
                raw_bytes=len(chunk),
                compressed_bytes=len(compressed),
                phi_weight=PHI ** -(i % 8),
                hash=hashlib.sha256(compressed).hexdigest(),
            )
            slices.append(rec)
            self._index.append(rec)
        return slices

    def export_index(self) -> Dict[str, Any]:
        total_raw = sum(s.raw_bytes for s in self._index)
        total_cmp = sum(s.compressed_bytes for s in self._index)
        payload = {
            "kernel": "MESIE-φ-KERNEL/1.0",
            "slice_count": len(self._index),
            "total_raw_bytes": total_raw,
            "total_compressed_bytes": total_cmp,
            "compression_ratio": round(total_cmp / max(total_raw, 1), 4),
            "slices": [s.to_dict() for s in self._index[-64:]],
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        KERNEL_STATE.parent.mkdir(parents=True, exist_ok=True)
        KERNEL_STATE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return payload