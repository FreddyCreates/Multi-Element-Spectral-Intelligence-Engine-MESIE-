"""Auto-AI business catalog — native intelligence runs ops; human + Grok ship."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from mesie.enterprise.use_case_registry import USE_CASES, MESIE_VERSION
from mesie.harness.template_library import TEMPLATE_LIBRARY

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = "MESIE-AUTO-AI-BUSINESS/1.0"

_SURFACE_BY_CATEGORY = {
    "Cybersecurity": "dashboard_4k",
    "Platform": "computing_family",
    "Signals": "native_dsl_ide",
    "NOVA": "career_portal",
    "Defense": "dashboard_4k",
    "Sovereign": "auto_business_ops",
    "Enterprise": "dashboard_4k",
    "Industrial": "product_sku",
    "Energy": "product_sku",
    "Robotics": "computing_family",
    "Insurance": "product_sku",
    "Native": "native_dsl_ide",
    "Workforce": "career_portal",
    "MCP": "api_console",
    "Infrastructure": "dashboard_4k",
    "Audit": "research_paper",
    "Tokens": "market_hub",
    "Developer": "market_hub",
}


@dataclass(frozen=True)
class AutoAIBusiness:
    business_id: str
    title: str
    industry: str
    parent_business: str
    github_repo: str
    template_id: str
    harness_ids: tuple[str, ...]
    intelligence: str
    operators: tuple[str, ...]
    processor_ops: tuple[str, ...]


def _template_for(category: str) -> str:
    for key, tpl in _SURFACE_BY_CATEGORY.items():
        if key.lower() in category.lower():
            return tpl
    return "product_sku"


def build_auto_businesses() -> List[AutoAIBusiness]:
    rows: List[AutoAIBusiness] = []
    for uc in USE_CASES:
        rows.append(
            AutoAIBusiness(
                business_id=uc.use_case_id,
                title=uc.title,
                industry=uc.category.split("/")[0].strip(),
                parent_business=uc.parent_business,
                github_repo=uc.github_repo,
                template_id=_template_for(uc.category),
                harness_ids=("use_case_child_repo", "tri_agent_squad", "auto_ai_business_shell"),
                intelligence="SOLUS + MESIE native — embed, match, logic, workflow (no third-party inference)",
                operators=("human:Medin", "executor:Grok-Build", "fleet:NOVA-70"),
                processor_ops=tuple(uc.processor_ops),
            )
        )
    return rows


AUTO_AI_BUSINESSES: List[AutoAIBusiness] = build_auto_businesses()


def auto_business_catalog() -> Dict[str, Any]:
    return {
        "protocol": PROTOCOL,
        "mesie_version": MESIE_VERSION,
        "business_count": len(AUTO_AI_BUSINESSES),
        "model": {
            "intelligence": "native SOLUS + MESIE engines on :8750",
            "not_used": ["OpenAI API", "Anthropic API", "HuggingFace inference"],
            "operators": ["human approves ship", "Grok Build executes DAG", "NOVA careers maintain uptime"],
            "proof": ["receipt_chain", "LRC mint", "benchmark_manifest"],
        },
        "template_library": len(TEMPLATE_LIBRARY),
        "businesses": [
            {
                "business_id": b.business_id,
                "title": b.title,
                "industry": b.industry,
                "parent_business": b.parent_business,
                "github_repo": b.github_repo,
                "template_id": b.template_id,
                "harness_ids": list(b.harness_ids),
                "intelligence": b.intelligence,
                "operators": list(b.operators),
                "processor_ops": list(b.processor_ops),
                "scaffold": f"templates/businesses/{b.business_id}/",
            }
            for b in AUTO_AI_BUSINESSES
        ],
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }