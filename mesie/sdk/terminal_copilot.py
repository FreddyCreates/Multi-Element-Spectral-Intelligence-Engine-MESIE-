"""Terminal copilot — sovereign AI + Sam.gov edition + Grok/Llama research tier."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from data import list_references, load_reference_record
from mesie.sdk.llm_bridge import LLMBridge
from mesie.sdk.terminal import ROOT, TerminalSession, default_session
from mesie.tools.registry import TOOLS, tool_by_id


class CopilotTier(str, Enum):
    SOVEREIGN = "sovereign"
    SAMGOV = "samgov"
    RESEARCH = "research"


TIER_LABELS = {
    CopilotTier.SOVEREIGN: "SOLUS native local AI — own models, vault, receipts (default)",
    CopilotTier.SAMGOV: "Sam.gov / GSA contractor — proof, readiness, opportunity alignment",
    CopilotTier.RESEARCH: "Research/startup — Grok or Llama/Ollama + MESIE tools",
}


@dataclass
class TerminalCopilot:
    """AI copilot embedded in MESIE terminal — does tool routing like an agent assistant."""

    tier: CopilotTier = CopilotTier.SOVEREIGN
    session: TerminalSession = field(default_factory=default_session)
    history: List[Dict[str, str]] = field(default_factory=list)
    _client: Any = field(default=None, init=False)
    _samgov: Any = field(default=None, init=False)
    _llm: Optional[LLMBridge] = field(default=None, init=False)

    def _maesi(self):
        if self._client is None:
            from mesie.sdk import MAESIClient

            self._client = MAESIClient()
        return self._client

    def _sam(self):
        if self._samgov is None:
            from mesie.enterprise.samgov_suite import SamGovSuite

            self._samgov = SamGovSuite()
        return self._samgov

    def _bridge(self) -> LLMBridge:
        if self._llm is None:
            tool_ids = ", ".join(t.id for t in TOOLS[:20])
            self._llm = LLMBridge(
                system_tools_context=(
                    "You assist inside MESIE/MAESI spectral intelligence SDK. "
                    f"Native tools include: {tool_ids}, ... "
                    "User can 'run <tool-id>' in terminal. Be concise. Sovereign edge deploy."
                )
            )
        return self._llm

    def status(self) -> Dict[str, Any]:
        import mesie
        from mesie.sdk import __sdk_version__

        st: Dict[str, Any] = {
            "tier": self.tier.value,
            "tier_label": TIER_LABELS[self.tier],
            "mesie_version": mesie.__version__,
            "sdk_version": __sdk_version__,
            "terminal": self.session.status(),
            "tool_count": len(TOOLS),
        }
        if self.tier == CopilotTier.RESEARCH:
            st["llm"] = self._bridge().available()
        if self.tier == CopilotTier.SAMGOV:
            st["samgov_edition"] = self._sam().EDITION
        return st

    def handle(self, line: str) -> str:
        """Process one copilot input line."""
        text = line.strip()
        if not text:
            return ""

        low = text.lower()
        if low in ("help", "?"):
            return self._help()
        if low == "status":
            return json.dumps(self.status(), indent=2)
        if low == "tiers":
            return "\n".join(f"  {k.value}: {v}" for k, v in TIER_LABELS.items())
        if low.startswith("tier "):
            try:
                self.tier = CopilotTier(low.split(maxsplit=1)[1].strip())
                return f"Switched to tier: {self.tier.value}"
            except ValueError:
                return "Tiers: sovereign | samgov | research"
        if low == "list":
            return "\n".join(f"  {t.id:22} {t.name}" for t in TOOLS[:30]) + f"\n  ... ({len(TOOLS)} total)"
        if low.startswith("run "):
            parts = text[4:].strip().split(maxsplit=1)
            tid = parts[0]
            extra = parts[1] if len(parts) > 1 else ""
            try:
                rc = self.session.run_tool(tid, extra)
                return f"Tool '{tid}' finished (exit {rc})"
            except ValueError as e:
                return str(e)
        if low.startswith("workflows") and self.tier == CopilotTier.SAMGOV:
            rep = self._sam().build_report()
            return "\n".join(f"  {w.workflow_id}: {w.title}" for w in rep.workflows)

        self.history.append({"role": "user", "content": text})
        reply = self._think(text)
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def _think(self, text: str) -> str:
        if self.tier == CopilotTier.SAMGOV:
            return self._sam().answer(text)

        if self.tier == CopilotTier.RESEARCH:
            bridge = self._bridge()
            avail = bridge.available()
            if avail.get("ollama") or avail.get("grok"):
                resp = bridge.chat(self.history[-6:])
                if resp.get("ok"):
                    return resp.get("content", "")
                return f"LLM bridge error: {resp.get('error')} — falling back to sovereign."
            return self._sovereign_reply(text) + "\n(Tip: start Ollama or set XAI_API_KEY for Grok.)"

        return self._sovereign_reply(text)

    def _sovereign_reply(self, text: str) -> str:
        client = self._maesi()
        low = text.lower()
        if "tool" in low or "run" in low:
            return (
                "Sovereign copilot: use 'run <tool-id>' — e.g. run proof-substrate, "
                "run interior-datacenter, run cluster-edge. 'list' for tools."
            )
        if "proof" in low or "evidence" in low:
            return "Run proof-substrate or neuroswarm-readiness. PowerShell: Invoke-MESIEProofSubstrate"
        if "swarm" in low or "drone" in low:
            return "Run drone-swarm or cluster-edge. Edge contested — PowerShell primary."
        if "match" in low or "spectral" in low:
            try:
                refs = list_references()
                if refs:
                    q = load_reference_record(refs[0])
                    rep = client.query(q)
                    return (
                        f"Sovereign query on {rep.record_id}: "
                        f"{len(rep.neighbors)} neighbors, {rep.elapsed_ms:.2f} ms. "
                        f"Tech hits: {rep.technical_hits[:2]}"
                    )
            except Exception as exc:
                return f"Spectral query error: {exc}"
        if "native" in low or "solus" in low:
            return (
                f"Native AI online — {client.native_ai.session_id}. "
                "stream_native_ai(records) for full deliverable pipeline."
            )
        return (
            "MESIE sovereign copilot — 'list', 'run <tool>', 'tier samgov|research', 'status'. "
            "Your edge terminal is the product."
        )

    def _help(self) -> str:
        lines = [
            "MAESI Terminal Copilot",
            f"  tier: {self.tier.value} — {TIER_LABELS[self.tier]}",
            "",
            "Commands:",
            "  help | status | tiers | tier <sovereign|samgov|research>",
            "  list              — native tools",
            "  run <tool-id>     — execute registry tool",
            "  workflows         — Sam.gov workflows (samgov tier)",
            "  exit              — leave shell",
            "",
            "Tiers:",
            "  sovereign  — SOLUS native AI (default, zero third-party)",
            "  samgov     — GSA contractor proof + readiness edition",
            "  research   — Grok or Llama/Ollama + MESIE tools",
        ]
        return "\n".join(lines)


def run_copilot_terminal(*, tier: Optional[str] = None) -> int:
    """Interactive terminal with embedded AI copilot."""
    from mesie.release.bootstrap import ensure_bootstrapped

    boot = ensure_bootstrapped(quiet=True)

    copilot = TerminalCopilot()
    if tier:
        try:
            copilot.tier = CopilotTier(tier)
        except ValueError:
            print(f"Unknown tier: {tier}", file=sys.stderr)

    mode = boot.get("install_mode", "dev")
    print(copilot._help())
    print(
        f"\nMESIE {boot.get('mesie_version', '?')} | mode={mode} | "
        f"config={boot.get('config_dir', '')}"
    )
    print(f"[{copilot.session.profile.kind.value}] mesie-ai> ", end="", flush=True)

    while True:
        try:
            line = input()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if line.strip().lower() in ("exit", "quit"):
            return 0
        out = copilot.handle(line)
        if out:
            print(out)
        print(f"\n[{copilot.session.profile.kind.value}] mesie-ai> ", end="", flush=True)