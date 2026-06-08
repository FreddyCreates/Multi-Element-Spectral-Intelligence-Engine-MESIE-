"""AuroSpeakingEngine — Medina's native speaking intelligence for government / Sam.gov tier."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.neuroai.auro.manifest import AURO_EDITION, AURO_PACKET_ID, load_auro_manifest
from mesie.neuroai.auro.memory import AuroVoiceMemory
from mesie.neuroai.auro.speaking_loop import SpeakingIntelligenceLoop
from mesie.sdk.solus import SDKSolusOrganism
from mesie.sdk.solus.constants import SOLUS_BRAND

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

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AuroSpeakingEngine:
    """Repo-native speaking intelligence — SOLUS reasoning + native lexicon composer."""

    session_id: str = "auro-gov-default"
    edition: str = AURO_EDITION
    packet_id: str = AURO_PACKET_ID
    memory: AuroVoiceMemory = field(default_factory=lambda: AuroVoiceMemory("auro-gov-default"))
    organism: SDKSolusOrganism = field(default_factory=SDKSolusOrganism)
    _loop: Optional[SpeakingIntelligenceLoop] = field(default=None, init=False)
    _samgov: Any = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.memory.session_id = self.session_id
        self._loop = SpeakingIntelligenceLoop(self.memory)

    def _sam(self):
        if self._samgov is None:
            from mesie.enterprise.samgov_suite import SamGovSuite

            self._samgov = SamGovSuite()
        return self._samgov

    def status(self) -> Dict[str, Any]:
        import mesie
        from mesie.sdk import __sdk_version__

        manifest = load_auro_manifest()
        return {
            "identity": "Auro — Medina native speaking intelligence",
            "edition": self.edition,
            "packet_id": self.packet_id,
            "mesie_version": mesie.__version__,
            "sdk_version": __sdk_version__,
            "native_model": "AuroNativeComposer-v1",
            "solus_brand": SOLUS_BRAND,
            "sovereign": True,
            "third_party_inference": False,
            "alpha_family": list(manifest.get("alpha_family", {}).keys()),
            "voice_memory_turns": len(self.memory._turns),
            "speaking_loop": manifest.get("speaking_loop", []),
            "blocked_claims": manifest.get("blocked_claims", []),
        }

    def _solus_reason(self, text: str) -> str:
        """Native SOLUS caretaker reasoning — not external LLM."""
        try:
            sig = [float(ord(c) % 97) for c in text[:128]]
            if len(sig) < 8:
                sig = sig + [1.0] * (8 - len(sig))
            freqs = list(range(len(sig)))
            analysis = self.organism.analyze_spectrum(freqs, sig)
            ratio = analysis.get("xray", {}).get("signal_ratio", 0.0)
            logic = self.organism.logic_action(
                "prove",
                theorem=f"auro_session_{self.session_id}: bounded speech preserves proof posture",
            )
            conf = logic.brain.get("confidence", 0.0)
            return (
                f"signal_ratio={ratio:.3f}, logic_confidence={conf:.3f} — "
                f"voice carries boundary; THESIS owns sealed proof."
            )
        except Exception as exc:
            return f"solus_local_reasoning={exc}"

    def _samgov_context(self, text: str) -> str:
        low = text.lower()
        if not any(k in low for k in ("sam", "gsa", "contractor", "opportunit", "proposal")):
            return ""
        rep = self._sam().build_report()
        return f"workflows={len(rep.workflows)}, opportunities={len(rep.opportunity_refs)}"

    def speak(self, user_text: str) -> AuroSpeechAct:
        """Full speaking loop — native compose, no Grok/Llama/OpenAI."""
        solus = self._solus_reason(user_text)
        sam_ctx = self._samgov_context(user_text)
        state = self._loop.run(user_text, solus_conclusion=solus, samgov_context=sam_ctx)
        utterance = state.utterance
        spoken = utterance.format_spoken() if utterance else "Auro online."

        if state.claims.thesis_defer and state.claims.proof_artifacts:
            spoken += f"\nTHESIS artifacts: {', '.join(state.claims.proof_artifacts[:2])}"

        return AuroSpeechAct(
            spoken=spoken,
            loop_state=state.to_dict(),
            native_model=utterance.native_model if utterance else "AuroNativeComposer-v1",
            edition=self.edition,
            packet_id=self.packet_id,
            sovereign=True,
            thesis_defer=state.claims.thesis_defer,
            session_id=self.session_id,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    def answer(self, question: str) -> str:
        """Terminal copilot interface."""
        return self.speak(question).spoken

    def export_session(self, path: Optional[Path] = None) -> Path:
        out = path or DELIVERABLES / "Auro_Voice_Session.json"
        payload = {
            "edition": self.edition,
            "packet_id": self.packet_id,
            "status": self.status(),
            "memory": self.memory.to_dict(),
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return out