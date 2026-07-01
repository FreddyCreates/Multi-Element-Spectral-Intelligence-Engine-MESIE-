"""NOVA cognitive layer — adaptive intent routing around MESIE core."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

PHI_INV = 0.6180339887498949


@dataclass
class CognitiveState:
    intent: str
    domain: str
    salience: float
    policy: str
    routes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "domain": self.domain,
            "salience": round(self.salience, 4),
            "policy": self.policy,
            "routes": self.routes,
        }


class AdaptiveCognitiveEngine:
    """Adaptive cognitive router — selects MESIE engines from natural intent."""

    DOMAIN_PATTERNS = [
        (re.compile(r"embed|vector|fingerprint", re.I), "retrieval", ["embed", "fingerprint", "match"]),
        (re.compile(r"match|similar|rank|compare", re.I), "matching", ["match", "rank"]),
        (re.compile(r"legal|risk|contract|clause", re.I), "legal", ["auro", "validate"]),
        (re.compile(r"swarm|drone|robot", re.I), "robotics", ["robotics", "swarm"]),
        (re.compile(r"proof|theorem|logic", re.I), "logic", ["logic-prover", "pattern-forge"]),
        (re.compile(r"release|ship|ready|production", re.I), "release", ["readiness", "test"]),
    ]

    def adapt(self, text: str, context: Optional[Dict[str, Any]] = None) -> CognitiveState:
        ctx = context or {}
        words = [w for w in re.split(r"\W+", text) if len(w) > 2]
        salience = min(1.0, len(words) / 80.0 * PHI_INV + 0.2)
        domain = "general"
        routes = ["embed", "match"]
        for pat, dom, rts in self.DOMAIN_PATTERNS:
            if pat.search(text):
                domain = dom
                routes = rts
                salience = min(1.0, salience + 0.15)
                break
        if ctx.get("force_domain"):
            domain = str(ctx["force_domain"])
        policy = "sovereign_local" if domain in ("legal", "release") else "spectral_first"
        intent = text[:200].strip() or "ambient_spectral_query"
        return CognitiveState(intent=intent, domain=domain, salience=salience, policy=policy, routes=routes)