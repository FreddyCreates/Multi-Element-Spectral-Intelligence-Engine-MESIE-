"""Alpha coding harness registry — MESIE-native build patterns (zero third-party inference)."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.version_info import MESIE_VERSION

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = "MESIE-ALPHA-HARNESS/1.0"


@dataclass(frozen=True)
class AlphaHarness:
    harness_id: str
    title: str
    category: str
    intelligence: str
    entry_command: str
    verify_command: str
    squad: Optional[str]
    industries: tuple[str, ...]
    surfaces: tuple[str, ...]
    description: str


ALPHA_HARNESSES: List[AlphaHarness] = [
    AlphaHarness(
        "tri_agent_squad",
        "Tri-Agent Maintenance Squad",
        "ops_quality_intel",
        "SOLUS + MESIE engines",
        "python -m mesie.compute.tri_agent_squads --all",
        "deliverables/compute/TRI_AGENT_SQUAD_STATE.json",
        "ops-triad",
        ("platform", "enterprise", "defense"),
        ("dashboard_4k", "api_console", "product_sku"),
        "3×3 agent teams — health, benchmark, embed, match, release.",
    ),
    AlphaHarness(
        "computing_family",
        "MESIE Computing Family Benchmark",
        "proof_latency",
        "native ST-φ + Fast ANN",
        "python scripts/run_mesie_computing_family_benchmarks.py",
        "deliverables/compute/MESIE_COMPUTING_FAMILY_RELEASE.json",
        "ops-triad",
        ("all_industries",),
        ("dashboard_4k", "product_sku", "landing"),
        "8 virtual products + industry benchmarks + economic Monte Carlo.",
    ),
    AlphaHarness(
        "swarm_mission_grok",
        "Grok Swarm Mission DAG",
        "long_horizon_build",
        "ST-φ encode + Loom vault",
        "deliverables/swarm_missions/<id>/mission_dag.json",
        "deliverables/swarm_missions/<id>/mission_receipt.json",
        "research-triad",
        ("all_industries",),
        ("auto_business_ops", "api_console"),
        "Seven-phase mission loop — intake, transform, decompose, execute, verify, persist.",
    ),
    AlphaHarness(
        "enterprise_execution",
        "Enterprise Execution Engine",
        "mega_release",
        "NOVA + MESIE + Grok + CloudColony",
        "python -m mesie.enterprise.execution_engine --mission <slug>",
        "deliverables/enterprise/EXECUTION_ENGINE_STATE.json",
        "quality-triad",
        ("enterprise", "sovereign", "platform"),
        ("dashboard_4k", "market_hub"),
        "13-node DAG — unify repos, runtime, ship, persist receipts.",
    ),
    AlphaHarness(
        "native_dsl_forge",
        "Native DSL Suite",
        "sovereign_language",
        "8 domain languages — no OpenAI/HF",
        "python scripts/forge_native_dsl.py",
        "deliverables/native_dsl/NATIVE_DSL_MANIFEST.json",
        "intel-triad",
        ("signals", "mcp", "workflow"),
        ("native_dsl_ide", "api_console"),
        "SpectraScript, EnvelopeLang, DepthLang, WorkflowLang, LogicLang, etc.",
    ),
    AlphaHarness(
        "depth_pillar_forge",
        "Polyglot Depth Pillars",
        "measurable_depth",
        "Python + Julia + Haskell per use case",
        "python scripts/forge_depth_pillars.py --rebuild",
        "deliverables/depth/DEPTH_MANIFEST.json",
        "research-triad",
        ("all_industries",),
        ("depth_explorer", "api_console"),
        "18 pillars × 5k+ LOC — enveloped engines per industry.",
    ),
    AlphaHarness(
        "use_case_child_repo",
        "Use-Case Child Branch Repo",
        "github_ready_business",
        "Federated MCP + processor ops",
        "python scripts/build_use_case_child_repos.py",
        "deliverables/enterprise/USE_CASE_CHILD_BRANCHES.json",
        None,
        ("all_industries",),
        ("landing", "product_sku", "auto_business_ops"),
        "Entire standalone repo per use case — publish to GitHub.",
    ),
    AlphaHarness(
        "nova_runtime",
        "NOVA 70-Career Never-Stop",
        "micro_fleet",
        "70 careers + robotics satellites",
        "python scripts/run_nova_runtime.py",
        "deliverables/nova/NOVA_RUNTIME_STATE.json",
        "ops-triad",
        ("infra", "release", "robotics"),
        ("career_portal", "dashboard_4k"),
        "Always-on micro careers — laws, protocols, release gates.",
    ),
    AlphaHarness(
        "sdk_major_benchmark",
        "SDK Major Industry Benchmarks",
        "third_party_compare",
        "MLPerf-class, vector DB, LLM, swarm",
        "python scripts/run_sdk_major_benchmarks.py --trials 300",
        "deliverables/MAESI_SDK_Major_Benchmarks.json",
        "ops-triad",
        ("all_industries",),
        ("landing", "research_paper"),
        "14 industry baselines — MQTT, Pinecone, GPT-4 tool, FAISS, NeuroSwarm.",
    ),
    AlphaHarness(
        "model_platforms",
        "Model Platform Web Apps",
        "mvp_protocol_bridge",
        "10 services — workers + native models",
        ".\\Start-ModelPlatforms.ps1",
        "deliverables/platform/PLATFORM_MANIFEST.json",
        "intel-triad",
        ("all_industries",),
        ("platform_hub", "model_hub", "solus_console", "auro_studio", "producer_lab", "api_console"),
        "8 web apps wired — platform, models, SOLUS, Auro, producer, compute, reality, enterprise.",
    ),
    AlphaHarness(
        "four_tier_market_ready",
        "4-Tier Market Ready Sleep Loop",
        "market_autonomous",
        "Agent squads × 4 tiers — prove, package, platform, ship",
        ".\\Start-MarketReadySleep.ps1 -Once",
        "deliverables/market/FOUR_TIER_MARKET_READY_STATE.json",
        "ops-triad",
        ("market", "enterprise", "all_industries"),
        ("market_hub", "enterprise_4k", "platform_hub", "hermes_fleet"),
        "Run while you sleep — ops/quality/intel/research triads per tier.",
    ),
    AlphaHarness(
        "auto_ai_business_shell",
        "Auto-AI Business Shell",
        "operator_plus_native_ai",
        "You + Grok + SOLUS — not third-party inference",
        "python scripts/forge_auto_ai_businesses.py",
        "deliverables/harness/AUTO_AI_BUSINESS_CATALOG.json",
        "intel-triad",
        ("all_industries",),
        ("auto_business_ops", "landing", "dashboard_4k", "market_hub"),
        "Business unit scaffold — native intelligence runs ops; you approve ship.",
    ),
]

try:
    from mesie.harness.alpha_extended import ALPHA_EXTENDED

    ALPHA_HARNESSES = ALPHA_HARNESSES + ALPHA_EXTENDED
except ImportError:
    pass


def harness_by_id(harness_id: str) -> Optional[AlphaHarness]:
    for h in ALPHA_HARNESSES:
        if h.harness_id == harness_id:
            return h
    return None


def harness_manifest() -> Dict[str, Any]:
    return {
        "protocol": PROTOCOL,
        "mesie_version": MESIE_VERSION,
        "harness_count": len(ALPHA_HARNESSES),
        "intelligence_model": "SOLUS native + MESIE engines — zero third-party inference for product intelligence",
        "operator_model": "human (Medin) + Grok Build executor + NOVA micro fleet",
        "harnesses": [
            {
                "harness_id": h.harness_id,
                "title": h.title,
                "category": h.category,
                "intelligence": h.intelligence,
                "entry_command": h.entry_command,
                "verify_command": h.verify_command,
                "squad": h.squad,
                "industries": list(h.industries),
                "surfaces": list(h.surfaces),
                "description": h.description,
            }
            for h in ALPHA_HARNESSES
        ],
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }