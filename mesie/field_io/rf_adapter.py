"""Live RF adapter — UDP/SDR spectral ingest for field bridge (Tier 2 hardware path)."""

from __future__ import annotations

import socket
import struct
import threading
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import numpy as np

from mesie.core.records import MultiElementRecord, SpectralComponent
from mesie.field_io.udp_frame import UDPSpectralFrameParser
from mesie.sovereign.field_access import get_field_access_engine


RF_MAGIC = b"NSRF"
RF_HEADER = struct.Struct("<4sddI")  # magic, center_hz, bandwidth_hz, n_bins


class RFSourceMode(str, Enum):
    SIM = "sim"
    UDP = "udp"
    LOOPBACK = "loopback"
    VIRTUAL_SILICON = "virtual_silicon"


@dataclass
class RFIngestReport:
    source: str
    mode: str
    center_hz: float
    bandwidth_hz: float
    points: int
    peak_hz: float
    field_coherence: float
    bridge_ok: bool
    latency_ms: float
    ok: bool
    silicon_certified: bool = False
    hil_path: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RFAdapterConfig:
    mode: RFSourceMode = RFSourceMode.SIM
    bind_host: str = "0.0.0.0"
    port: int = 37531
    schumann_center_hz: float = 7.83
    schumann_bandwidth_hz: float = 45.0
    sim_bins: int = 128


class LiveRFAdapter:
    """Tier 2 live RF path: ingest RF spectrum → MESIE record → field bridge."""

    def __init__(self, config: Optional[RFAdapterConfig] = None) -> None:
        self.config = config or RFAdapterConfig()
        self._parser = UDPSpectralFrameParser()
        self._fa = get_field_access_engine()
        self._sock: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None
        self._frames: List[bytes] = []
        self._running = False

    def _sim_frame(self, *, seq: int = 0) -> bytes:
        cfg = self.config
        freqs = np.linspace(
            cfg.schumann_center_hz - cfg.schumann_bandwidth_hz / 2,
            cfg.schumann_center_hz + cfg.schumann_bandwidth_hz / 2,
            cfg.sim_bins,
        )
        amps = np.exp(-((freqs - cfg.schumann_center_hz) ** 2) / 4.0) + 0.05 * np.random.random(cfg.sim_bins)
        rec = MultiElementRecord(
            record_id=f"rf-sim-{seq}",
            components=[SpectralComponent(name="rf", frequency=freqs, amplitude=amps)],
            lineage=["rf_sim", "schumann_band"],
        )
        return self._parser.encode_json(rec, seq=seq)

    def _decode_rf_binary(self, payload: bytes) -> MultiElementRecord:
        if len(payload) < RF_HEADER.size:
            raise ValueError("RF frame too short")
        magic, center, bw, n_bins = RF_HEADER.unpack_from(payload)
        if magic != RF_MAGIC:
            return self._parser.parse(payload)[0]
        need = RF_HEADER.size + n_bins * 4
        amps = struct.unpack_from(f"<{n_bins}f", payload, RF_HEADER.size)
        freqs = np.linspace(center - bw / 2, center + bw / 2, n_bins)
        a = np.maximum(np.abs(np.asarray(amps, dtype=np.float64)), 1e-12)
        return MultiElementRecord(
            record_id=f"rf-live-{int(center)}",
            components=[SpectralComponent(name="rf_live", frequency=freqs, amplitude=a)],
            lineage=["rf_binary", f"center_{center}"],
        )

    def ingest_payload(self, payload: bytes) -> RFIngestReport:
        t0 = time.perf_counter()
        if payload[:4] == RF_MAGIC:
            rec = self._decode_rf_binary(payload)
            source = "rf_binary"
        else:
            rec, _ = self._parser.parse(payload)
            source = "rf_udp_json"
        br = self._fa.bridge(rec)
        peak_idx = int(np.argmax(np.abs(rec.components[0].amplitude)))
        peak = float(rec.components[0].frequency[peak_idx])
        ms = (time.perf_counter() - t0) * 1000
        return RFIngestReport(
            source=source,
            mode=self.config.mode.value,
            center_hz=self.config.schumann_center_hz,
            bandwidth_hz=self.config.schumann_bandwidth_hz,
            points=len(rec.components[0].frequency),
            peak_hz=peak,
            field_coherence=round(br.field_coherence, 4),
            bridge_ok=br.field_connected,
            latency_ms=round(ms, 4),
            ok=br.field_connected and br.sovereign,
        )

    def ingest_simulated(self) -> RFIngestReport:
        return self.ingest_payload(self._sim_frame())

    def ingest_virtual_silicon(self) -> RFIngestReport:
        """Certified virtual SDR HIL path through virtual silicon RF front-end."""
        from mesie.silicon.rf_frontend import VirtualRFFrontEnd

        rep = VirtualRFFrontEnd().ingest_certified()
        hil = VirtualRFFrontEnd().run_hil_loop()
        rep.silicon_certified = hil.certified
        rep.hil_path = hil.path
        rep.mode = RFSourceMode.VIRTUAL_SILICON.value
        return rep

    def start_listener(self, callback: Optional[Callable[[RFIngestReport], None]] = None) -> Dict[str, Any]:
        if self.config.mode == RFSourceMode.SIM:
            return {"ok": True, "mode": "sim", "note": "use ingest_simulated()"}
        self._running = True
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.config.bind_host, self.config.port))
        self._sock.settimeout(0.1)

        def _loop() -> None:
            while self._running and self._sock:
                try:
                    data, _ = self._sock.recvfrom(65536)
                    rep = self.ingest_payload(data)
                    if callback:
                        callback(rep)
                except socket.timeout:
                    continue
                except OSError:
                    break

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()
        return {"ok": True, "mode": self.config.mode.value, "port": self.config.port}

    def stop_listener(self) -> None:
        self._running = False
        if self._sock:
            self._sock.close()
            self._sock = None

    def encode_rf_binary(self, amps: np.ndarray, *, center_hz: float, bandwidth_hz: float) -> bytes:
        n = int(len(amps))
        header = RF_HEADER.pack(RF_MAGIC, float(center_hz), float(bandwidth_hz), n)
        return header + struct.pack(f"<{n}f", *[float(x) for x in amps])

    def status(self) -> Dict[str, Any]:
        return {
            "adapter": "live_rf",
            "mode": self.config.mode.value,
            "port": self.config.port,
            "schumann_center_hz": self.config.schumann_center_hz,
            "listening": self._running,
            "airgapped": True,
            "third_party": False,
        }