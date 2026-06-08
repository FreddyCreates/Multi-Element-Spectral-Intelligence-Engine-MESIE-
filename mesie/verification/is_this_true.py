"""Is This True? — Grok/X-style honest responder (not marketing yes)."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.verification.claim_registry import ClaimEntry, default_claim_registry
from mesie.verification.evidence_tiers import EvidenceTier, public_answer_for_tier, tier_summary

DELIVERABLES = Path(__file__).resolve().parents[2] / "deliverables"


@dataclass
class TruthResponse:
    question: str
    short_answer: str
    verdict: str
    confidence: str
    claims_addressed: List[Dict[str, Any]]
    grok_critique_mapping: List[Dict[str, str]]
    what_is_proven: List[str]
    what_is_not_proven: List[str]
    how_to_verify_yourself: List[str]
    generated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class IsThisTrueEngine:
    """Answer 'is this true?' the way Grok should — evidence tiers, not hype."""

    GROK_CRITIQUE_POINTS = [
        ("self_reported_only", "Anyone can run local Python suites and post passing results"),
        ("no_drone_hw", "Real drone hardware integration not independently confirmed"),
        ("no_physical_jam", "Actual jammed/denied environment with physical assets unproven"),
        ("sim_vs_real_10k", "10K scalability is simulation unless multi-host evidence published"),
        ("no_external_audit", "No independent corroboration on chimeradefense.com / public web"),
        ("mission_critical_overclaim", "100/100 mission-critical defense is not publicly accredited"),
    ]

    def __init__(self) -> None:
        self.registry = default_claim_registry()

    def _map_critique(self) -> List[Dict[str, str]]:
        mapping = []
        for cid, critique in self.GROK_CRITIQUE_POINTS:
            related = [c for c in self.registry if critique.split()[0].lower() in c.honest_limit.lower()
                       or cid in c.claim_id or critique[:20].lower() in c.critique_source.lower()]
            if not related:
                related = [c for c in self.registry if c.tier in (EvidenceTier.GAP, EvidenceTier.SIMULATED_VALIDATED)][:2]
            entry = related[0] if related else self.registry[0]
            mapping.append({
                "critique": critique,
                "our_response": public_answer_for_tier(entry.tier),
                "claim_id": entry.claim_id,
                "remediation": entry.remediation,
            })
        return mapping

    def answer(self, question: str = "Is NeuroSwarm/MESIE drone defense true?") -> TruthResponse:
        proven = []
        not_proven = []
        for c in self.registry:
            if c.tier in (EvidenceTier.MEASURED_LOCAL, EvidenceTier.DOCUMENTED_REFERENCE):
                proven.append(f"{c.public_claim}: {c.measured_summary}")
            elif c.tier == EvidenceTier.SIMULATED_VALIDATED:
                proven.append(f"[SIM] {c.public_claim}: {c.measured_summary}")
                not_proven.append(c.honest_limit)
            else:
                not_proven.append(f"{c.public_claim}: {c.honest_limit}")

        short = (
            "Partially true as software — locally measured spectral/swarm performance is real on dev hardware. "
            "Not fully true as deployed defense system — physical drones, live EW, independent audit, and "
            "public corroboration remain gaps. Do not equate laptop benchmarks with combat validation."
        )
        gaps = sum(1 for c in self.registry if c.tier == EvidenceTier.GAP)
        sim = sum(1 for c in self.registry if c.tier == EvidenceTier.SIMULATED_VALIDATED)
        measured = sum(1 for c in self.registry if c.tier == EvidenceTier.MEASURED_LOCAL)

        return TruthResponse(
            question=question,
            short_answer=short,
            verdict="partially_true_software_substrate",
            confidence="high_on_local_harness_low_on_field_deployment",
            claims_addressed=[c.to_dict() for c in self.registry],
            grok_critique_mapping=self._map_critique(),
            what_is_proven=proven,
            what_is_not_proven=list(dict.fromkeys(not_proven)),
            how_to_verify_yourself=[
                "python scripts/run_is_this_true.py",
                "python scripts/run_sdk_major_benchmarks.py --agents 10000",
                "python scripts/run_mission_world_week.py --days 7",
                "Inspect deliverables/*.json artifact hashes and hardware profile",
            ],
            generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    def export(self, path: Optional[Path] = None) -> Path:
        resp = self.answer()
        out = path or DELIVERABLES / "Is_This_True_Response.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = resp.to_dict()
        payload["summary"] = {
            "measured_claims": sum(1 for c in self.registry if c.tier == EvidenceTier.MEASURED_LOCAL),
            "simulated_claims": sum(1 for c in self.registry if c.tier == EvidenceTier.SIMULATED_VALIDATED),
            "gap_claims": sum(1 for c in self.registry if c.tier == EvidenceTier.GAP),
        }
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        md = DELIVERABLES / "Is_This_True_Response.md"
        md.write_text(self._to_md(resp), encoding="utf-8")
        return out

    def _to_md(self, resp: TruthResponse) -> str:
        lines = [
            "# Is This True? — Honest Verification Response",
            "",
            f"**Question:** {resp.question}",
            "",
            f"**Short answer:** {resp.short_answer}",
            "",
            f"**Verdict:** `{resp.verdict}` | **Confidence:** `{resp.confidence}`",
            "",
            "## What IS proven (with artifacts)",
            "",
        ]
        for p in resp.what_is_proven:
            lines.append(f"- {p}")
        lines.extend(["", "## What is NOT proven", ""])
        for n in resp.what_is_not_proven:
            lines.append(f"- {n}")
        lines.extend(["", "## Grok/X critique mapping", ""])
        for m in resp.grok_critique_mapping:
            lines.append(f"- **Critique:** {m['critique']}")
            lines.append(f"  - **Response:** {m['our_response']}")
            lines.append(f"  - **Remediation:** {m['remediation']}")
        lines.extend(["", "## Verify yourself", ""])
        for h in resp.how_to_verify_yourself:
            lines.append(f"- `{h}`")
        return "\n".join(lines)