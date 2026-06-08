"""CSV spectral ingest adapter — first live field I/O primitive."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np

from mesie.core.records import MultiElementRecord, SpectralComponent
from mesie.io.loaders import RecordInput

PathLike = Union[str, Path]


@dataclass
class CSVIngestReport:
    record_id: str
    points: int
    freq_min_hz: float
    freq_max_hz: float
    source_path: str
    columns: List[str]
    ok: bool
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CSVSpectralIngest:
    """Parse frequency,amplitude CSV into MESIE MultiElementRecord."""

    def __init__(
        self,
        *,
        freq_col: str = "frequency",
        amp_col: str = "amplitude",
        delimiter: str = ",",
    ) -> None:
        self.freq_col = freq_col
        self.amp_col = amp_col
        self.delimiter = delimiter

    def ingest(
        self,
        path: PathLike,
        *,
        record_id: Optional[str] = None,
        component_name: str = "csv_channel",
    ) -> tuple[MultiElementRecord, CSVIngestReport]:
        p = Path(path)
        if not p.exists():
            rep = CSVIngestReport("", 0, 0.0, 0.0, str(p), [], False, "file not found")
            raise FileNotFoundError(rep.error)

        freqs: List[float] = []
        amps: List[float] = []
        columns: List[str] = []
        try:
            with p.open(encoding="utf-8", newline="") as fh:
                reader = csv.DictReader(fh, delimiter=self.delimiter)
                columns = list(reader.fieldnames or [])
                fc = self._resolve_col(columns, self.freq_col, ("freq", "frequency_hz", "f"))
                ac = self._resolve_col(columns, self.amp_col, ("amp", "amplitude", "power", "psd"))
                for row in reader:
                    freqs.append(float(row[fc]))
                    amps.append(float(row[ac]))
        except Exception as exc:
            rep = CSVIngestReport(record_id or p.stem, 0, 0.0, 0.0, str(p), columns, False, str(exc))
            raise ValueError(rep.error) from exc

        if len(freqs) < 2:
            raise ValueError("CSV needs at least 2 spectral points")

        f = np.asarray(freqs, dtype=np.float64)
        a = np.maximum(np.abs(np.asarray(amps, dtype=np.float64)), 1e-12)
        order = np.argsort(f)
        f, a = f[order], a[order]
        rid = record_id or f"csv-{p.stem}"
        rec = MultiElementRecord(
            record_id=rid,
            components=[SpectralComponent(name=component_name, frequency=f, amplitude=a)],
            representation="psd",
            lineage=[str(p)],
        )
        rep = CSVIngestReport(
            record_id=rid,
            points=len(f),
            freq_min_hz=float(f[0]),
            freq_max_hz=float(f[-1]),
            source_path=str(p.resolve()),
            columns=columns,
            ok=True,
        )
        return rec, rep

    @staticmethod
    def _resolve_col(columns: List[str], primary: str, aliases: tuple[str, ...]) -> str:
        lower = {c.lower(): c for c in columns}
        for key in (primary, *aliases):
            if key.lower() in lower:
                return lower[key.lower()]
        if len(columns) >= 2:
            return columns[0]
        raise ValueError(f"column not found: {primary}")


def ingest_csv_spectrum(path: PathLike, **kwargs: Any) -> RecordInput:
    rec, _ = CSVSpectralIngest().ingest(path, **kwargs)
    return rec