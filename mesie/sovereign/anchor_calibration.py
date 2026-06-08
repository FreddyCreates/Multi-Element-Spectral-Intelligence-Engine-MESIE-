"""Live anchor calibration — Schumann/geomag reference files → anchor table drift."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from data import DATA_DIR, load_library
from mesie import match_records
from mesie.core.records import MultiElementRecord, SpectralComponent
from mesie.sovereign.field_access import FrequencyFieldBridge, get_field_access_engine


@dataclass
class AnchorCalibrationResult:
    anchor_id: str
    nominal_hz: float
    measured_peak_hz: float
    drift_hz: float
    drift_pct: float
    coherence_before: float
    coherence_after: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CalibrationReport:
    calibrated: int
    mean_drift_pct: float
    mean_coherence_gain: float
    anchors: List[AnchorCalibrationResult]
    reference_sources: List[str]
    ok: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "calibrated": self.calibrated,
            "mean_drift_pct": self.mean_drift_pct,
            "mean_coherence_gain": self.mean_coherence_gain,
            "anchors": [a.to_dict() for a in self.anchors],
            "reference_sources": self.reference_sources,
            "ok": self.ok,
        }


def _library_record(lib_name: str, key: str, modes_key: str = "modes") -> MultiElementRecord:
    data = load_library(lib_name)
    block = data[key]
    modes = block[modes_key]
    freqs = np.asarray([float(m["frequency_Hz"]) for m in modes], dtype=np.float64)
    amps = np.asarray([float(m.get("typical_amplitude_pT", m.get("amplitude", 1.0))) for m in modes], dtype=np.float64)
    return MultiElementRecord(
        record_id=f"cal-{lib_name}-{key}",
        components=[SpectralComponent(name=key, frequency=freqs, amplitude=amps)],
        representation="psd",
        lineage=[lib_name, key],
    )


class AnchorCalibrator:
    """Recalibrate field anchors against bundled Schumann + geomag spectral libraries."""

    def __init__(self, bridge: Optional[FrequencyFieldBridge] = None) -> None:
        self.bridge = bridge or FrequencyFieldBridge()
        self._refs: List[MultiElementRecord] = []

    def load_references(self) -> List[MultiElementRecord]:
        refs: List[MultiElementRecord] = []
        sch = DATA_DIR / "spectral_library" / "schumann_resonances.json"
        if sch.exists():
            refs.append(_library_record("schumann_resonances", "schumann_resonances"))
        geo = DATA_DIR / "spectral_library" / "geomagnetic_pulsations.json"
        if geo.exists():
            refs.append(_library_record("geomagnetic_pulsations", "pulsation_bands"))
        self._refs = refs
        return refs

    def calibrate(self) -> CalibrationReport:
        if not self._refs:
            self.load_references()
        results: List[AnchorCalibrationResult] = []
        for ref in self._refs:
            before = self.bridge.bridge(ref).field_coherence
            peak_idx = int(np.argmax(np.abs(ref.components[0].amplitude)))
            measured = float(ref.components[0].frequency[peak_idx])
            align = self.bridge.nearest_anchors(measured, top_k=1)
            if not align:
                continue
            anchor = align[0]
            nominal = anchor.frequency_Hz
            drift = measured - nominal
            drift_pct = 100.0 * drift / max(abs(nominal), 1e-12)
            after_rec = MultiElementRecord(
                record_id=f"{ref.record_id}_cal",
                components=[
                    SpectralComponent(
                        name="calibrated",
                        frequency=ref.components[0].frequency.copy(),
                        amplitude=ref.components[0].amplitude.copy(),
                        metadata={"anchor_drift_hz": drift},
                    )
                ],
                lineage=ref.lineage + ["anchor_cal"],
            )
            after = self.bridge.bridge(after_rec).field_coherence
            results.append(
                AnchorCalibrationResult(
                    anchor_id=anchor.anchor_id,
                    nominal_hz=nominal,
                    measured_peak_hz=measured,
                    drift_hz=round(drift, 6),
                    drift_pct=round(drift_pct, 4),
                    coherence_before=round(before, 4),
                    coherence_after=round(after, 4),
                )
            )
        gains = [r.coherence_after - r.coherence_before for r in results]
        drifts = [abs(r.drift_pct) for r in results]
        return CalibrationReport(
            calibrated=len(results),
            mean_drift_pct=round(float(np.mean(drifts)) if drifts else 0.0, 4),
            mean_coherence_gain=round(float(np.mean(gains)) if gains else 0.0, 4),
            anchors=results,
            reference_sources=[r.record_id for r in self._refs],
            ok=len(results) > 0,
        )

    def export_calibration(self, path: Path) -> Dict[str, Any]:
        report = self.calibrate()
        payload = report.to_dict()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload


def calibrate_field_anchors() -> CalibrationReport:
    return AnchorCalibrator().calibrate()