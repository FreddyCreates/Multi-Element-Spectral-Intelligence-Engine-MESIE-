"""Auro native utterance composer — repo-native language surface, zero third-party inference."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from mesie.neuroai.auro.affect import AffectState
from mesie.neuroai.auro.claim_boundary import ClaimPosture, ClaimSelection
from mesie.neuroai.auro.manifest import load_auro_lexicon
from mesie.neuroai.auro.roles import AlphaRole, RoleBoundary


@dataclass
class ComposedUtterance:
    text: str
    posture: str
    prosody: str
    native_model: str
    phrase_ids: List[str]

    def format_spoken(self) -> str:
        prefix = f"{self.prosody} " if self.prosody else ""
        return f"{prefix}{self.text}".strip()


class AuroNativeComposer:
    """Native language model surface — spectral-weighted phrase selection from bundled lexicon."""

    MODEL_ID = "AuroNativeComposer-v1"

    def compose(
        self,
        user_text: str,
        *,
        boundary: RoleBoundary,
        affect: AffectState,
        claims: ClaimSelection,
        memory_hits: List[Dict[str, Any]],
        solus_conclusion: str = "",
        samgov_context: str = "",
        defer_role: Optional[AlphaRole] = None,
    ) -> ComposedUtterance:
        lex = load_auro_lexicon()
        phrases: Dict[str, List[str]] = lex.get("posture_phrases", {})
        markers: Dict[str, str] = lex.get("prosody_markers", {})

        bucket = claims.posture.value
        if not claims.may_speak:
            bucket = "blocked_redirect"
        elif claims.thesis_defer and defer_role == AlphaRole.THESIS:
            bucket = "defer_thesis"

        if bucket == "role_guard":
            pool = list(phrases.get("role_guard", []))
        else:
            pool = list(phrases.get(bucket, []))

        if affect.mode.value == "warm_bounded":
            pool.extend(phrases.get("warm_bounded", [])[:1])
        if samgov_context:
            pool.extend(phrases.get("samgov_contractor", [])[:1])

        if memory_hits:
            prior = memory_hits[0].get("speech_act", "")[:80]
            if prior:
                pool.append(f"Continuing from our prior orientation: {prior}")

        if solus_conclusion and bucket != "role_guard":
            pool.append(f"SOLUS native reasoning: {solus_conclusion[:160]}")

        if claims.abstract_private:
            pool.append("Internal context noted — spoken response stays public-safe and abstracted.")

        if not pool:
            pool = [
                "Auro online — native speaking intelligence inside Medina infrastructure.",
                "The voice carries the boundary; ask for proof and I defer to THESIS.",
            ]

        idx = self._spectral_pick(user_text, pool)
        core = pool[idx]
        phrase_id = f"{bucket}:{idx}"

        if boundary.defer_to and claims.thesis_defer:
            defer_marker = markers.get("defer", "[defer:THESIS]")
            core = f"{core} {defer_marker}"

        prosody = affect.prosody or markers.get(affect.mode.value.replace("_bounded", ""), "")

        return ComposedUtterance(
            text=core,
            posture=claims.posture.value,
            prosody=prosody,
            native_model=self.MODEL_ID,
            phrase_ids=[phrase_id],
        )

    def _spectral_pick(self, text: str, pool: List[str]) -> int:
        if len(pool) <= 1:
            return 0
        seed = int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)
        weights = []
        for i, phrase in enumerate(pool):
            overlap = len(set(text.lower().split()) & set(phrase.lower().split()))
            weights.append((seed + i * 31 + overlap * 17) % 1000)
        return weights.index(max(weights))