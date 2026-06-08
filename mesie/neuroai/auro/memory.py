"""Auro voice-memory — commitments, corrections, long-horizon continuity."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class VoiceMemoryTurn:
    turn_id: int
    user_text: str
    speech_act: str
    role: str
    affect: str
    claim_posture: str
    commitments: List[str]
    corrections: List[str]
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "turn_id": self.turn_id,
            "user_text": self.user_text[:200],
            "speech_act": self.speech_act[:400],
            "role": self.role,
            "affect": self.affect,
            "claim_posture": self.claim_posture,
            "commitments": self.commitments,
            "corrections": self.corrections,
            "timestamp": self.timestamp,
        }


@dataclass
class AuroVoiceMemory:
    """Native voice memory — not canonical THESIS proof store."""

    session_id: str
    max_turns: int = 256
    _turns: List[VoiceMemoryTurn] = field(default_factory=list)
    _commitments: List[str] = field(default_factory=list)
    _corrections: List[str] = field(default_factory=list)

    def store(
        self,
        user_text: str,
        speech_act: str,
        *,
        role: str,
        affect: str,
        claim_posture: str,
        commitments: Optional[List[str]] = None,
    ) -> VoiceMemoryTurn:
        if user_text.lower().startswith("actually") or "correction" in user_text.lower():
            self._corrections.append(user_text[:240])

        new_commitments = commitments or []
        for c in new_commitments:
            if c not in self._commitments:
                self._commitments.append(c)

        turn = VoiceMemoryTurn(
            turn_id=len(self._turns),
            user_text=user_text,
            speech_act=speech_act,
            role=role,
            affect=affect,
            claim_posture=claim_posture,
            commitments=list(new_commitments),
            corrections=list(self._corrections[-3:]),
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )
        self._turns.append(turn)
        if len(self._turns) > self.max_turns:
            self._turns = self._turns[-self.max_turns :]
        return turn

    def recall(self, query: str, *, top_k: int = 5) -> Dict[str, Any]:
        """Spectral-hash recall over prior voice turns."""
        q_sig = _text_signature(query)
        scored: List[tuple[float, VoiceMemoryTurn]] = []
        for turn in self._turns:
            sig = _text_signature(turn.user_text + " " + turn.speech_act)
            overlap = _sig_overlap(q_sig, sig)
            scored.append((overlap, turn))
        scored.sort(key=lambda x: -x[0])
        hits = [t.to_dict() for _, t in scored[:top_k] if _ > 0]
        return {
            "session_id": self.session_id,
            "turn_count": len(self._turns),
            "commitments": self._commitments[-10:],
            "corrections": self._corrections[-5:],
            "hits": hits,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "turn_count": len(self._turns),
            "commitments": self._commitments,
            "corrections": self._corrections,
            "turns": [t.to_dict() for t in self._turns[-20:]],
        }


def _text_signature(text: str) -> List[int]:
    tokens = [t for t in text.lower().split() if len(t) > 2][:64]
    sig = []
    for tok in tokens:
        h = int(hashlib.sha256(tok.encode()).hexdigest()[:8], 16)
        sig.append(h % 997)
    return sig or [0]


def _sig_overlap(a: List[int], b: List[int]) -> float:
    if not a or not b:
        return 0.0
    sa, sb = set(a), set(b)
    return len(sa & sb) / max(len(sa | sb), 1)