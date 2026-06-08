"""UDP spectral frame parser — binary + JSON line formats for edge ingest."""

from __future__ import annotations

import json
import struct
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from mesie.core.records import MultiElementRecord, SpectralComponent


@dataclass
class UDPFrameReport:
    format: str
    points: int
    record_id: str
    seq: int
    ok: bool
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class UDPSpectralFrameParser:
    """Parse UDP payloads: JSON `{"freq":[],"amp":[],"id":"","seq":0}` or binary LE doubles."""

    MAGIC = b"MSIE"
    HEADER = struct.Struct("<4sIId")  # magic, seq, n_points, sample_rate

    def parse(self, payload: bytes) -> Tuple[MultiElementRecord, UDPFrameReport]:
        if not payload:
            raise ValueError("empty UDP payload")
        if payload[:1] == b"{":
            return self._parse_json(payload)
        if payload[:4] == self.MAGIC:
            return self._parse_binary(payload)
        return self._parse_json(payload)

    def _parse_json(self, payload: bytes) -> Tuple[MultiElementRecord, UDPFrameReport]:
        try:
            data = json.loads(payload.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            rep = UDPFrameReport("json", 0, "", 0, False, str(exc))
            raise ValueError(rep.error) from exc
        freqs = data.get("freq") or data.get("frequencies") or data.get("frequency")
        amps = data.get("amp") or data.get("amplitudes") or data.get("amplitude")
        if not freqs or not amps:
            raise ValueError("JSON frame needs freq and amp arrays")
        f = np.asarray(freqs, dtype=np.float64)
        a = np.maximum(np.abs(np.asarray(amps, dtype=np.float64)), 1e-12)
        rid = str(data.get("id") or data.get("record_id") or "udp-frame")
        seq = int(data.get("seq", 0))
        rec = MultiElementRecord(
            record_id=rid,
            components=[SpectralComponent(name="udp", frequency=f, amplitude=a)],
            representation="psd",
            lineage=["udp_json"],
        )
        return rec, UDPFrameReport("json", len(f), rid, seq, True)

    def _parse_binary(self, payload: bytes) -> Tuple[MultiElementRecord, UDPFrameReport]:
        if len(payload) < self.HEADER.size:
            raise ValueError("binary frame too short")
        magic, seq, n_pts, _sr = self.HEADER.unpack_from(payload)
        if magic != self.MAGIC:
            raise ValueError("invalid magic")
        need = self.HEADER.size + n_pts * 16
        if len(payload) < need:
            raise ValueError("binary frame truncated")
        freqs, amps = [], []
        off = self.HEADER.size
        for _ in range(n_pts):
            fv, av = struct.unpack_from("<dd", payload, off)
            freqs.append(fv)
            amps.append(av)
            off += 16
        f = np.asarray(freqs, dtype=np.float64)
        a = np.maximum(np.abs(np.asarray(amps, dtype=np.float64)), 1e-12)
        rid = f"udp-bin-{seq}"
        rec = MultiElementRecord(
            record_id=rid,
            components=[SpectralComponent(name="udp", frequency=f, amplitude=a)],
            representation="psd",
            lineage=["udp_binary"],
        )
        return rec, UDPFrameReport("binary", n_pts, rid, seq, True)

    def encode_json(self, record: MultiElementRecord, *, seq: int = 0) -> bytes:
        c = record.components[0]
        body = {
            "id": record.record_id,
            "seq": seq,
            "freq": c.frequency.tolist(),
            "amp": c.amplitude.tolist(),
        }
        return json.dumps(body).encode("utf-8")


def parse_udp_spectral_frame(payload: bytes) -> MultiElementRecord:
    rec, _ = UDPSpectralFrameParser().parse(payload)
    return rec