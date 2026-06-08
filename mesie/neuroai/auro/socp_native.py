"""PROTO-183 SOCP — Python bridge to GPTREPO Sovereign Offline Cognition (native LM)."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from mesie.neuroai.auro.substrate_loader import load_paper_iv, substrate_status

PHI = 1.618033988749895
HEARTBEAT = 873
SOLUS_KNOWLEDGE_CAPACITY = 1000


@dataclass
class SolusKnowledgeEntry:
    domain: str
    key: str
    content: str
    entry_id: str = ""

    def score(self, words: List[str]) -> float:
        blob = (self.content + " " + self.key).lower()
        hits = sum(1 for w in words if w in blob)
        return hits / max(len(words), 1)


@dataclass
class SolusRule:
    pattern: re.Pattern[str]
    response: str


@dataclass
class SovereignOfflineCognition:
    """Faithful Python port of GPTREPO protocols/sovereign-offline-cognition-protocol.js."""

    solus_mode: bool = True
    solus_knowledge: List[SolusKnowledgeEntry] = field(default_factory=list)
    solus_rules: List[SolusRule] = field(default_factory=list)
    metrics: Dict[str, int] = field(default_factory=lambda: {
        "solus_activations": 0,
        "offline_queries": 0,
        "knowledge_hits": 0,
        "rule_applications": 0,
    })

    def __post_init__(self) -> None:
        self._seed_knowledge()
        self._absorb_paper_iv()
        self.metrics["solus_activations"] = 1

    def _seed_knowledge(self) -> None:
        seed = [
            ("math", "phi", "φ = (1+√5)/2 ≈ 1.618 — golden ratio, harmonic basis of all AURO computations"),
            ("math", "fibonacci", "Fibonacci sequence: each term = sum of two preceding — F(n) = F(n-1)+F(n-2)"),
            ("math", "phi_decay", "φ-decay: 1/φⁿ ≈ 0.618ⁿ — exponential decay toward the golden mean"),
            ("protocol", "heartbeat", "AURO heartbeat = 873ms — φ-locked interval governing all background ticks"),
            ("protocol", "srp", "PROTO-001 SRP: Sovereign Routing Protocol — reputation-weighted adaptive model routing"),
            ("protocol", "eit", "PROTO-002 EIT: Encrypted Intelligence Transport — zero-knowledge communication"),
            ("security", "guardian", "Guardian Worker — computational immune system with Hebbian threat learning"),
            ("security", "threat_score", "Threat severity = φⁿ where n ∈ {1,2,3,4,5} for low/medium/high/critical/sovereign"),
            ("memory", "mlep", "PROTO-182 MLEP: spatial memory with phi-decay, LRU cache, and lineage graphs"),
            ("governance", "auro_charter", "AURO Charter (ORO-CHARTER-001): official founding document, effective 2026-04-27"),
            ("code", "pse", "PatternSynthesisEngine: 40 primitives across 8 domains — synthesizes knowledge patterns"),
            ("science", "hebbian", "Hebbian learning: neurons that fire together wire together — dW = lr*(1-W)*input"),
            ("philosophy", "autonomia", "Autonomia Perpetua: computational organism that heals itself and runs forever"),
            ("governance", "oro_systems", "ORO Systems: Organism Reasoning Operations — owners of the AURO intelligence wire"),
            ("governance", "alpha_family", "Alpha-family: AURO speaks, THESIS proves, ORIGO builds, Codex implements, CIVOS-PRIME governs"),
            ("governance", "thesis", "THESIS Alpha: research, IP, proof, publication, notarization — not the speaking voice"),
            ("governance", "medina", "Medina is sovereign intelligence infrastructure; Auro is native speaking intelligence"),
            ("governance", "speaking_loop", "Speaking loop: perception, memory, role, affect, claims, speech, response, state update"),
        ]
        for domain, key, content in seed:
            self._add_knowledge(domain, key, content)

        rules = [
            (r"what is phi", "φ = (1+√5)/2 ≈ 1.6180339887 — the golden ratio. AURO uses it as the harmonic basis for all computations."),
            (r"what is auro", "AURO (Autonomous Universal Reasoning Oracle) is Medina's native speaking intelligence — sovereign, repo-native, PROTO-183 SOCP."),
            (r"what is oro", "ORO Systems (Organism Reasoning Operations) maintains AURO's protocol stack and intelligence wire."),
            (r"heartbeat", "The AURO heartbeat is 873ms — φ-locked to maintain harmonic resonance across all background processes."),
            (r"guardian", "The Guardian Worker is AURO's computational immune system (PROTO-181 AGIP)."),
            (r"memory", "AURO memory: spatial memory with phi-decay, lineage graphs (PROTO-182 MLEP)."),
            (r"charter", "The AURO Charter (ORO-CHARTER-001) is the official founding document, ratified 2026-04-27."),
            (r"solus|offline", "Solus mode: AURO operates fully offline using embedded knowledge and reasoning rules — no network."),
            (r"thesis|proof|evidence", "THESIS owns proof authority. Auro speaks orientation; run proof-substrate for sealed evidence."),
            (r"alpha.?family|origo|civos|codex", "Alpha-family role separation: Auro speaks, THESIS proves, ORIGO builds, Codex implements, CIVOS governs."),
        ]
        for pat, resp in rules:
            self.solus_rules.append(SolusRule(re.compile(pat, re.I), resp))

    def _absorb_paper_iv(self) -> None:
        """PROTO-185-style absorption of NeuroAI Paper IV into offline knowledge."""
        paper = load_paper_iv()
        if not paper:
            return
        chunks = []
        for section in paper.split("\n## "):
            section = section.strip()
            if len(section) < 80:
                continue
            title = section.split("\n", 1)[0][:80]
            body = section[:1200]
            chunks.append((title, body))
        for i, (title, body) in enumerate(chunks[:24]):
            self._add_knowledge("philosophy", f"paper_iv_{i}", f"[Paper IV — {title}] {body}")

    def _add_knowledge(self, domain: str, key: str, content: str) -> None:
        entry = SolusKnowledgeEntry(domain=domain, key=key, content=content, entry_id=f"solus-{len(self.solus_knowledge)}")
        self.solus_knowledge.append(entry)
        if len(self.solus_knowledge) > SOLUS_KNOWLEDGE_CAPACITY:
            self.solus_knowledge.pop(0)

    def query(self, text: str) -> Dict[str, Any]:
        self.metrics["offline_queries"] += 1
        for rule in self.solus_rules:
            if rule.pattern.search(text):
                self.metrics["rule_applications"] += 1
                return {
                    "response": rule.response,
                    "confidence": PHI / (PHI + 1),
                    "source": "solus_rules",
                    "protocol": "PROTO-183-SOCP",
                }

        words = [w.lower() for w in re.split(r"\W+", text) if len(w) > 2]
        scored = [(k.score(words), k) for k in self.solus_knowledge]
        hits = [(s, k) for s, k in scored if s > 0]
        hits.sort(key=lambda x: -x[0])
        if hits:
            self.metrics["knowledge_hits"] += 1
            top = hits[:3]
            return {
                "response": " | ".join(k.content for _, k in top),
                "confidence": top[0][0],
                "source": "solus_knowledge",
                "hits": len(top),
                "protocol": "PROTO-183-SOCP",
            }

        snippet = " ".join(text.split()[:5])
        return {
            "response": (
                f'AURO Solus: Query "{snippet}" processed through embedded knowledge substrate '
                f"(GPTREPO PROTO-183). φ = {PHI:.6f}. Voice carries the boundary."
            ),
            "confidence": 1 / PHI,
            "source": "solus_generative",
            "protocol": "PROTO-183-SOCP",
        }

    def status(self) -> Dict[str, Any]:
        st = substrate_status()
        return {
            "protocol": "PROTO-183-SOCP",
            "ring": "Sovereign Ring",
            "solus_mode": self.solus_mode,
            "knowledge_entries": len(self.solus_knowledge),
            "reasoning_rules": len(self.solus_rules),
            "metrics": dict(self.metrics),
            "phi": PHI,
            "heartbeat": HEARTBEAT,
            "gptrepo_socp_source": st.get("socp_protocol"),
            "gptrepo_present": st.get("gptrepo_present"),
        }