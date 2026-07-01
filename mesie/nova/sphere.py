"""NOVA Sphere — adaptive cognitive linguistic translator shell around MESIE."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from mesie.agentic.micro import MicroCareer, MicroOrchestrator
from mesie.nova.cognitive import AdaptiveCognitiveEngine
from mesie.nova.linguistic import LinguisticEngine
from mesie.nova.translator import TranslatorEngine

try:
    from mesie.version_info import MESIE_VERSION, NOVA_VERSION
except ImportError:
    MESIE_VERSION = "0.4.0"
    NOVA_VERSION = "1.0.0"


@dataclass
class NovaResponse:
    spoken_summary: str
    cognitive: Dict[str, Any]
    linguistic: Dict[str, Any]
    translated: Dict[str, Any]
    mesie_routes: List[str]
    micro_fleet: Dict[str, Any]
    latency_ms: float
    nova_version: str = NOVA_VERSION
    mesie_version: str = MESIE_VERSION
    sovereign: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spoken_summary": self.spoken_summary,
            "cognitive": self.cognitive,
            "linguistic": self.linguistic,
            "translated": self.translated,
            "mesie_routes": self.mesie_routes,
            "micro_fleet": self.micro_fleet,
            "latency_ms": self.latency_ms,
            "nova_version": self.nova_version,
            "mesie_version": self.mesie_version,
            "sovereign": self.sovereign,
        }


@dataclass
class NovaSphere:
    """Full NOVA intelligence sphere wrapping MESIE core."""

    session_id: str = field(default_factory=lambda: f"nova-{uuid.uuid4().hex[:10]}")
    cognitive: AdaptiveCognitiveEngine = field(default_factory=AdaptiveCognitiveEngine)
    linguistic: LinguisticEngine = field(default_factory=LinguisticEngine)
    translator: TranslatorEngine = field(default_factory=TranslatorEngine)
    micro: MicroOrchestrator = field(default_factory=MicroOrchestrator)
    _mesie_lm: Any = field(default=None, init=False)

    def __post_init__(self) -> None:
        self._boot_micro_agents()
        self._mesie_lm = self._load_mesie_lm()

    def _load_mesie_lm(self) -> Optional[Any]:
        try:
            from mesie.neuroai.auro.native_lm import AuroNativeLanguageModel
            return AuroNativeLanguageModel(session_id=self.session_id)
        except ImportError:
            return None

    def _boot_micro_agents(self) -> None:
        from mesie.agentic.micro.organization import boot_nova_organization

        boot_nova_organization(self.micro, satellite=False)

    def process(self, text: str, *, context: Optional[Dict[str, Any]] = None) -> NovaResponse:
        t0 = time.perf_counter()
        cog = self.cognitive.adapt(text, context)
        ling = self.linguistic.analyze(text)
        trans = self.translator.translate(text)
        micro_results = self.micro.run_all_once()

        summary = self._compose_summary(text, cog, ling)
        if self._mesie_lm:
            try:
                lm_out = self._mesie_lm.generate(text[:2000])
                summary = lm_out.spoken
            except Exception:
                pass

        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        return NovaResponse(
            spoken_summary=summary,
            cognitive=cog.to_dict(),
            linguistic=ling.to_dict(),
            translated=trans.to_dict(),
            mesie_routes=cog.routes,
            micro_fleet={"pulse": micro_results, "status": self.micro.fleet_status()},
            latency_ms=elapsed,
        )

    @staticmethod
    def _compose_summary(text: str, cog: Any, ling: Any) -> str:
        return (
            f"NOVA sphere — domain={cog.domain}, policy={cog.policy}, "
            f"coherence={ling.coherence:.3f}. Routes: {', '.join(cog.routes)}. "
            f"Input: {text[:120]}{'…' if len(text) > 120 else ''}"
        )

    def activate_satellites(self, careers: Optional[List[MicroCareer]] = None) -> None:
        """Activate full NOVA organization — 55 careers on production timers."""
        from mesie.agentic.micro.organization import activate_nova_organization

        activate_nova_organization(self.micro, careers=careers)

    def stop_satellites(self) -> None:
        self.micro.stop_all()

    def status(self) -> Dict[str, Any]:
        return {
            "product": "NOVA",
            "nova_version": NOVA_VERSION,
            "mesie_version": MESIE_VERSION,
            "session_id": self.session_id,
            "layers": ["cognitive", "linguistic", "translator", "mesie_core", "micro_fleet"],
            "mesie_lm": self._mesie_lm.status() if self._mesie_lm else None,
            "micro_fleet": self._org_status(),
            "sovereign": True,
            "third_party_inference": False,
        }

    def _org_status(self) -> Dict[str, Any]:
        from mesie.agentic.micro.organization import organization_status

        return organization_status(self.micro)