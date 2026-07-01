"""MININOVA Sphere — mini adaptive cognitive linguistic shell on NOVAMINI."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.agentic.micro import MicroCareer, MicroOrchestrator
from mesie.nova.linguistic import LinguisticEngine
from mesie.nova.translator import TranslatorEngine
from mesie.novamini.runtime import NovaMiniRuntime

try:
    from mesie.version_info import MESIE_VERSION, MININOVA_VERSION
except ImportError:
    MESIE_VERSION = "0.4.0"
    MININOVA_VERSION = "1.0.0"


@dataclass
class MiniNovaResponse:
    spoken: str
    role: str
    linguistic: Dict[str, Any]
    translated: Dict[str, Any]
    memory_hits: List[Dict[str, Any]]
    micro_fleet: Dict[str, Any]
    latency_ms: float
    mininova_version: str = MININOVA_VERSION
    mesie_version: str = MESIE_VERSION
    sovereign: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spoken": self.spoken,
            "role": self.role,
            "linguistic": self.linguistic,
            "translated": self.translated,
            "memory_hits": self.memory_hits,
            "micro_fleet": self.micro_fleet,
            "latency_ms": self.latency_ms,
            "mininova_version": self.mininova_version,
            "mesie_version": self.mesie_version,
            "sovereign": self.sovereign,
        }


@dataclass
class MiniNovaSphere:
    """MININOVA — NOVAMINI runtime + linguistic/translator micro fleet."""

    session_id: str = field(default_factory=lambda: f"mininova-{uuid.uuid4().hex[:10]}")
    vault_root: Optional[Path] = None
    linguistic: LinguisticEngine = field(default_factory=LinguisticEngine)
    translator: TranslatorEngine = field(default_factory=TranslatorEngine)
    micro: MicroOrchestrator = field(default_factory=MicroOrchestrator)
    _runtime: NovaMiniRuntime = field(init=False)

    def __post_init__(self) -> None:
        self._runtime = NovaMiniRuntime(
            session_id=self.session_id,
            vault_root=self.vault_root,
        )
        from mesie.agentic.micro.tasks import register_production_tasks

        register_production_tasks(self.micro)
        for career in (MicroCareer.LINGUIST, MicroCareer.TRANSLATOR):
            self.micro.spawn(career, satellite=False)

    def process(self, text: str) -> MiniNovaResponse:
        t0 = time.perf_counter()
        ling = self.linguistic.analyze(text)
        trans = self.translator.translate(text)
        chat = self._runtime.chat(text)
        micro_results = self.micro.run_all_once()
        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        return MiniNovaResponse(
            spoken=chat.spoken,
            role=chat.role,
            linguistic=ling.to_dict(),
            translated=trans.to_dict(),
            memory_hits=chat.memory_hits,
            micro_fleet={"pulse": micro_results, "status": self.micro.fleet_status()},
            latency_ms=elapsed,
        )

    def activate_satellites(self) -> None:
        from mesie.agentic.micro.tasks import register_production_tasks

        register_production_tasks(self.micro)
        for career in (MicroCareer.LINGUIST, MicroCareer.TRANSLATOR):
            self.micro.ensure_satellite(career)

    def stop_satellites(self) -> None:
        self.micro.stop_all()

    def status(self) -> Dict[str, Any]:
        return {
            "product": "MININOVA",
            "mininova_version": MININOVA_VERSION,
            "mesie_version": MESIE_VERSION,
            "session_id": self.session_id,
            "layers": ["novamini", "linguistic", "translator", "micro_fleet"],
            "novamini": self._runtime.status(),
            "micro_fleet": self.micro.fleet_status(),
            "sovereign": True,
            "third_party_inference": False,
        }