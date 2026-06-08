"""AuroSpeakingEngine — Paper IV built native speaking intelligence."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from mesie.neuroai.auro.manifest import AURO_EDITION, AURO_PACKET_ID, load_auro_manifest
from mesie.neuroai.auro.native_lm import AuroNativeLanguageModel, MODEL_ID

ROOT = Path(__file__).resolve().parents[3]
DELIVERABLES = ROOT / "deliverables"


@dataclass
class AuroSpeechAct:
    spoken: str
    loop_state: Dict[str, Any]
    native_model: str
    edition: str
    packet_id: str
    sovereign: bool
    thesis_defer: bool
    session_id: str
    timestamp: str
    trajectory_id: str = ""
    claim_score: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AuroSpeakingEngine:
    """Medina native speaking intelligence — built per Paper IV."""

    session_id: str = "auro-gov-default"
    edition: str = AURO_EDITION
    packet_id: str = AURO_PACKET_ID
    _lm: Optional[AuroNativeLanguageModel] = field(default=None, init=False)
    _samgov: Any = field(default=None, init=False)

    @property
    def lm(self) -> AuroNativeLanguageModel:
        if self._lm is None:
            self._lm = AuroNativeLanguageModel(session_id=self.session_id)
        return self._lm

    def _sam(self):
        if self._samgov is None:
            from mesie.enterprise.samgov_suite import SamGovSuite

            self._samgov = SamGovSuite()
        return self._samgov

    def status(self) -> Dict[str, Any]:
        import mesie
        from mesie.sdk import __sdk_version__

        manifest = load_auro_manifest()
        lm_st = self.lm.status()
        return {
            "identity": "Auro — Medina native speaking intelligence (Paper IV built)",
            "edition": self.edition,
            "packet_id": self.packet_id,
            "mesie_version": mesie.__version__,
            "sdk_version": __sdk_version__,
            "native_model": MODEL_ID,
            "built": True,
            "lm": lm_st,
            "sovereign": True,
            "third_party_inference": False,
            "alpha_family": list(manifest.get("alpha_family", {}).keys()),
            "speaking_loop": manifest.get("speaking_loop", []),
            "trajectory_health": self.lm.trajectory.health,
        }

    def _samgov_context(self, text: str) -> str:
        low = text.lower()
        if not any(k in low for k in ("sam", "gsa", "contractor", "opportunit", "proposal")):
            return ""
        rep = self._sam().build_report()
        return f"SamGov workflows={len(rep.workflows)}, opportunities={len(rep.opportunity_refs)}"

    def speak(self, user_text: str) -> AuroSpeechAct:
        out = self.lm.generate(user_text, samgov_context=self._samgov_context(user_text))
        return AuroSpeechAct(
            spoken=out.spoken,
            loop_state=out.to_dict(),
            native_model=out.native_model,
            edition=self.edition,
            packet_id=self.packet_id,
            sovereign=True,
            thesis_defer=bool(out.defer_to == "THESIS" or out.protocol.get("defer_proof")),
            session_id=self.session_id,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            trajectory_id=out.trajectory_id,
            claim_score=out.claim_score,
        )

    def answer(self, question: str) -> str:
        return self.speak(question).spoken

    def export_session(self, path: Optional[Path] = None) -> Path:
        out = path or DELIVERABLES / "Auro_Voice_Session.json"
        payload = {
            "edition": self.edition,
            "packet_id": self.packet_id,
            "built_model": MODEL_ID,
            "status": self.status(),
            "memory": self.lm.memory.to_dict(),
            "trajectory": self.lm.trajectory.to_dict(),
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return out