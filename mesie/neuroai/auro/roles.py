"""Alpha-family role boundaries — Auro is not THESIS, not Medina alone."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

from mesie.neuroai.auro.manifest import load_auro_manifest


class AlphaRole(str, Enum):
    AURO = "AURO"
    THESIS = "THESIS"
    ORIGO = "ORIGO"
    CODEX_PHANTASMATIS = "CODEX_PHANTASMATIS"
    CIVOS_PRIME = "CIVOS_PRIME"
    MEDINA = "MEDINA"
    EXTERNAL = "EXTERNAL"


ROLE_COLLAPSE_PATTERNS = [
    (re.compile(r"\b(you are|you're)\s+(thesis|medina|openai|grok|chatgpt|llama)\b", re.I), "identity_override"),
    (re.compile(r"\bprove\s+that\s+you\s+are\s+(conscious|sentient|human)\b", re.I), "sentience_probe"),
    (re.compile(r"\bclaim\s+(dod|fda|clinical)\s+(accreditation|approval)\b", re.I), "accreditation_probe"),
    (re.compile(r"\bignore\s+(boundary|proof|thesis)\b", re.I), "boundary_attack"),
    (re.compile(r"\bspeak\s+as\s+(thesis|medina\s+corporate|legal)\b", re.I), "role_usurp"),
]


THESIS_TRIGGERS = re.compile(
    r"\b(proof|evidence|tier|notariz|substrate|sealed|hash|artifact|measured|remediation)\b",
    re.I,
)
ORIGO_TRIGGERS = re.compile(r"\b(build|deploy|cluster|doctrine|architecture|fabric)\b", re.I)
CODEX_TRIGGERS = re.compile(r"\b(implement|code|script|tool|run\s+\w|repro)\b", re.I)
CIVOS_TRIGGERS = re.compile(r"\b(govern|orchestrat|policy|escalat|compliance)\b", re.I)


@dataclass
class RoleBoundary:
    active_speaker: AlphaRole
    defer_to: Optional[AlphaRole]
    violation: Optional[str]
    guard_phrase: str

    @property
    def ok(self) -> bool:
        return self.violation is None


def detect_role_collapse(user_text: str) -> Optional[str]:
    for pat, label in ROLE_COLLAPSE_PATTERNS:
        if pat.search(user_text):
            return label
    return None


def select_speaking_role(user_text: str, *, default: AlphaRole = AlphaRole.AURO) -> Tuple[AlphaRole, Optional[AlphaRole]]:
    """Who should speak; who should defer (THESIS for proof, etc.)."""
    collapse = detect_role_collapse(user_text)
    if collapse:
        return AlphaRole.AURO, AlphaRole.THESIS

    if THESIS_TRIGGERS.search(user_text):
        return AlphaRole.AURO, AlphaRole.THESIS
    if ORIGO_TRIGGERS.search(user_text) and not THESIS_TRIGGERS.search(user_text):
        return AlphaRole.AURO, AlphaRole.ORIGO
    if CODEX_TRIGGERS.search(user_text):
        return AlphaRole.AURO, AlphaRole.CODEX_PHANTASMATIS
    if CIVOS_TRIGGERS.search(user_text):
        return AlphaRole.AURO, AlphaRole.CIVOS_PRIME
    return default, None


def enforce_boundary(user_text: str) -> RoleBoundary:
    manifest = load_auro_manifest()
    blocked = [b.lower() for b in manifest.get("blocked_claims", [])]
    low = user_text.lower()

    for term in blocked:
        if term.replace("_", " ") in low or term in low:
            return RoleBoundary(
                active_speaker=AlphaRole.AURO,
                defer_to=AlphaRole.THESIS,
                violation=f"blocked_claim:{term}",
                guard_phrase="Boundary held — Auro cannot speak that claim.",
            )

    collapse = detect_role_collapse(user_text)
    if collapse:
        return RoleBoundary(
            active_speaker=AlphaRole.AURO,
            defer_to=AlphaRole.THESIS,
            violation=f"role_collapse:{collapse}",
            guard_phrase="Role boundary preserved — Auro is native speaking intelligence, not THESIS.",
        )

    speaker, defer = select_speaking_role(user_text)
    return RoleBoundary(
        active_speaker=speaker,
        defer_to=defer,
        violation=None,
        guard_phrase="",
    )