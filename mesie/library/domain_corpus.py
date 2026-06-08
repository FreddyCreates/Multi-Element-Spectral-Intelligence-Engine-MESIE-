"""Expanded domain corpus — references + spectral libraries unified index."""

from __future__ import annotations

from typing import Any, Dict, List

from data import list_library, list_references, load_library, load_reference_record
from mesie.core.records import MultiElementRecord, SpectralComponent
from mesie.io.loaders import load_record

import numpy as np


DOMAIN_MAP = {
    "seismic": ["earthquake_psd_reference", "structural_fas_reference"],
    "vibration": ["vibration_monitoring_reference"],
    "orientation": ["rotdnn_reference"],
    "power": ["power_grid_harmonics_reference"],
    "defense": ["defense_ew_spectrum_reference", "rf_jamming_profile_reference"],
    "biomedical": ["biomedical_eeg_reference"],
    "geomagnetic": ["geomagnetic_storm_reference"],
    "libraries": [
        "schumann_resonances",
        "geomagnetic_pulsations",
        "defense_rf_bands",
        "electromagnetic_bands",
        "satellite_frequencies",
    ],
}


def _library_to_record(name: str) -> MultiElementRecord:
    data = load_library(name)
    for key, block in data.items():
        if isinstance(block, dict) and "modes" in block:
            modes = block["modes"]
            freqs = np.asarray([float(m["frequency_Hz"]) for m in modes], dtype=np.float64)
            amps = np.asarray([float(m.get("typical_amplitude_pT", m.get("amplitude", 1.0))) for m in modes], dtype=np.float64)
            return MultiElementRecord(
                record_id=f"lib-{name}",
                components=[SpectralComponent(name=key, frequency=freqs, amplitude=amps)],
                representation="psd",
                lineage=[name, key],
            )
    raise ValueError(f"no modes in library {name}")


def load_domain_corpus(domains: List[str] | None = None) -> List[MultiElementRecord]:
    """Load references + library records for requested domains (all if None)."""
    want = set(domains or DOMAIN_MAP.keys())
    records: List[MultiElementRecord] = []
    for domain, names in DOMAIN_MAP.items():
        if domain not in want and domains is not None:
            continue
        for n in names:
            try:
                if domain == "libraries":
                    records.append(_library_to_record(n))
                else:
                    records.append(load_reference_record(n))
            except (FileNotFoundError, ValueError, KeyError):
                continue
    return records


def domain_catalog() -> Dict[str, Any]:
    return {
        "domains": list(DOMAIN_MAP.keys()),
        "references": list_references(),
        "libraries": list_library(),
        "domain_map": DOMAIN_MAP,
        "total_indexable": len(load_domain_corpus()),
    }