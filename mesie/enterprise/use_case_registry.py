"""MESIE use-case registry — child branch repos (entire GitHub-ready repos per use case)."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

MESIE_VERSION = "1.2.0"
PROTOCOL = "MESIE-USE-CASE-CHILD-BRANCH/1.0"


@dataclass(frozen=True)
class UseCaseSpec:
    use_case_id: str
    github_repo: str
    title: str
    tagline: str
    category: str
    parent_business: str
    processor_ops: List[str]
    start_script: str
    mcp_tools: List[str]
    dataset_path: Optional[str] = None
    research_pack: Optional[str] = None
    proof_key: Optional[str] = None


# Industry + platform use cases — each maps to a standalone child repo
USE_CASES: List[UseCaseSpec] = [
    UseCaseSpec(
        "cybersecurity_ai",
        "mesie-usecase-cybersecurity-ai",
        "Cybersecurity AI",
        "Tunnel hardening, process guardian, 61/71 remediation — ItsNotAILabs branch",
        "Cybersecurity / Edge Exposure",
        "biz-02",
        ["POST /processor/read-signal", "GET /processor/autonomous"],
        "scripts/heal_mesie_stack.ps1",
        ["cyber_scan", "guardian_status", "remediation_playbook", "tunnel_checklist"],
        research_pack="deliverables/research/packs/06_CYBERSECURITY_AI_RESEARCH_PACK.md",
        proof_key="cybersecurity",
    ),
    UseCaseSpec(
        "autonomous_runtime",
        "mesie-usecase-autonomous-runtime",
        "Autonomous Self-Executing Runtime",
        "Platform executes itself — guardian, coherence, NOVA spawn, research forge",
        "Platform / AI Runtime",
        "biz-01",
        ["GET /processor/autonomous", "GET /processor/nova-runtime"],
        "Start-MESIE-Autonomous.ps1",
        ["autonomous_pulse", "coherence_weights", "nova_ensure", "heal_stack"],
        research_pack="deliverables/research/packs/07_SELF_EXECUTING_RUNTIME_RESEARCH_PACK.md",
    ),
    UseCaseSpec(
        "universal_signals",
        "mesie-usecase-universal-signals",
        "Universal Signal Plane",
        "Everything is a signal — text, JSON, events, files → fingerprint + analyst text",
        "Signals / L0 Plane",
        "biz-01",
        ["POST /processor/read-signal", "POST /processor/generate-text"],
        "python -m mesie.processor --serve",
        ["read_signal", "generate_text", "signal_fingerprint", "architecture_map"],
    ),
    UseCaseSpec(
        "nova_swarm",
        "mesie-usecase-nova-swarm",
        "NOVA 70-Career Swarm",
        "IT/infrastructure org — laws, protocols, library, release gates, never-stop",
        "NOVA / Micro Fleet",
        "biz-04",
        ["GET /processor/nova-runtime", "POST /processor/robotics-pulse"],
        "Start-NovaRuntime.ps1",
        ["nova_status", "career_pulse", "robotics_pulse", "showcase_proof"],
    ),
    UseCaseSpec(
        "drone_swarm",
        "mesie-usecase-drone-swarm",
        "Decentralized Drone Swarm",
        "Gossip consensus, field routing, jamming failover — 10K scale doctrine",
        "Defense / Robotics",
        "biz-01",
        ["POST /processor/mesh/pulse", "POST /processor/robotics-pulse"],
        "scripts/run_drone_swarm_suite.py",
        ["swarm_status", "mesh_pulse", "gossip_route", "jamming_failover"],
    ),
    UseCaseSpec(
        "sovereign_cloud",
        "mesie-usecase-sovereign-cloud",
        "Sovereign Cloud ICP",
        "Airgap local :4943, capsula deploy, dual-chain tokens, bridge standby",
        "Sovereign / ICP",
        "biz-05",
        ["GET /processor/status"],
        "Start-SovereignColony.ps1",
        ["airgap_enable", "capsula_build", "bridge_standby", "colony_sync"],
    ),
    UseCaseSpec(
        "enterprise_ai_sovereign",
        "mesie-usecase-enterprise-ai",
        "Enterprise AI Sovereign Memory",
        "Agent memory, receipt chain, sovereign vault, copilot without third-party inference",
        "Enterprise AI",
        "biz-01",
        ["POST /processor/exec", "GET /processor/architecture"],
        "Start-MESIEProduction.ps1",
        ["agent_memory", "receipt_chain", "vault_status", "enterprise_run"],
    ),
    UseCaseSpec(
        "mfg_predictive",
        "mesie-usecase-mfg-predictive",
        "Manufacturing Predictive Maintenance",
        "Spectral machinery classification — Monte Carlo enterprise slice",
        "Industrial / MFG",
        "biz-01",
        ["POST /processor/match", "POST /processor/embed"],
        "scripts/run_multi_enterprise_20.py",
        ["match_spectrum", "benchmark_slice", "monte_carlo"],
        dataset_path="data/benchmarks/enterprise_use_cases_benchmark.json",
    ),
    UseCaseSpec(
        "energy_grid",
        "mesie-usecase-energy-grid",
        "Energy Grid Stability",
        "Grid spectral monitoring, anomaly routing, phi-weighted alerts",
        "Energy / Utilities",
        "biz-01",
        ["POST /processor/read-signal", "POST /processor/match"],
        "scripts/run_enterprise_ai_suite.py",
        ["grid_signal", "anomaly_route", "stability_score"],
        dataset_path="data/benchmarks/enterprise_use_cases_benchmark.json",
    ),
    UseCaseSpec(
        "robotics_fleet",
        "mesie-usecase-robotics-fleet",
        "Robotics Fleet Edge",
        "Fusion dims 256, threat_p50 sub-ms, LRC per pulse",
        "Robotics / Edge",
        "biz-01",
        ["POST /processor/robotics-pulse", "POST /processor/benchmark"],
        "scripts/run_nova_showcase.py",
        ["robotics_pulse", "fusion_status", "threat_benchmark"],
    ),
    UseCaseSpec(
        "seismic_insurance",
        "mesie-usecase-seismic-insurance",
        "Seismic Insurance Risk",
        "Insurance + seismic domain suites, structural civil correlation",
        "Insurance / Seismic",
        "biz-01",
        ["POST /processor/match", "POST /processor/read-signal"],
        "scripts/run_multi_domain_suites.py",
        ["seismic_match", "risk_score", "domain_suite"],
        dataset_path="data/benchmarks/enterprise_use_cases_benchmark.json",
    ),
    UseCaseSpec(
        "native_ai_transformer",
        "mesie-usecase-native-ai",
        "Native AI Transformer Forge",
        "NOVA 50B virtual, ST-φ forge, ORO producer, auto-training corpus",
        "Native AI / Models",
        "biz-02",
        ["GET /processor/architecture"],
        "python -m mesie.mcp.native_config --write",
        ["transformer_forge", "oro_produce", "native_models", "producer_cycle"],
    ),
    UseCaseSpec(
        "career_workforce",
        "mesie-usecase-career-workforce",
        "1000-Career AI Workforce",
        "5 pillars × 200 careers — triple protocol Loom+MCP+Bridge",
        "Workforce / Careers",
        "biz-03",
        ["GET http://127.0.0.1:8767/health"],
        "Start-CareerMCPStack.ps1",
        ["career_list", "career_invoke", "pillar_route", "triple_protocol"],
    ),
    UseCaseSpec(
        "universal_mcp_federation",
        "mesie-usecase-universal-mcp",
        "Universal MCP Federation",
        "12 super tools, federated envelopes, any AI client :8765",
        "MCP / Federation",
        "biz-02",
        ["GET http://127.0.0.1:8765/health"],
        "Start-UniversalStack.ps1",
        ["super_invoke", "federation_status", "ml_forge", "envelope_seal"],
    ),
    UseCaseSpec(
        "interior_datacenter",
        "mesie-usecase-interior-dc",
        "Interior Data Center Edge",
        "LAN gossip, interior DC manifest, cluster edge without cloud-first",
        "Infrastructure / DC",
        "biz-05",
        ["POST /processor/mesh/soak", "GET /processor/mesh"],
        "scripts/run_interior_datacenter.py",
        ["mesh_soak", "cluster_status", "lan_gossip"],
    ),
    UseCaseSpec(
        "neuroswarm_audit",
        "mesie-usecase-neuroswarm-audit",
        "NeuroSwarm Claims Audit",
        "Maps external audit critique to measured SDK evidence",
        "Audit / Claims",
        "biz-01",
        ["POST /processor/benchmark"],
        "scripts/run_neuroswarm_audit.py",
        ["audit_claims", "evidence_map", "latency_proof"],
    ),
    UseCaseSpec(
        "dual_chain_tokens",
        "mesie-usecase-dual-chain",
        "Dual-Chain Token Bridge",
        "MESIE-LRC internal + ETH/ICP external anchors",
        "Tokens / Web3",
        "biz-04",
        ["GET /processor/tokens/manifest", "POST /processor/tokens/mint"],
        "Start-MarketPush.ps1",
        ["token_manifest", "mint_lrc", "anchor_eth", "anchor_icp"],
        research_pack="deliverables/research/packs/04_DUAL_CHAIN_TOKEN_RESEARCH_PACK.md",
    ),
    UseCaseSpec(
        "virtual_processor_devkit",
        "mesie-usecase-virtual-processor",
        "Virtual Processor DevKit",
        "Shippable devkit zip — showcase proof, market research, quickstart",
        "Developer Kit",
        "biz-01",
        ["GET /processor/status", "GET /processor/market-research"],
        "python scripts/package_processor_devkit.py --light",
        ["devkit_package", "release_status", "showcase_proof", "market_story"],
    ),
]

HUB_REPO = "mesie-usecase-universal"


def use_case_by_id(uid: str) -> Optional[UseCaseSpec]:
    for uc in USE_CASES:
        if uc.use_case_id == uid:
            return uc
    return None


def registry_manifest() -> Dict[str, Any]:
    return {
        "protocol": PROTOCOL,
        "mesie_version": MESIE_VERSION,
        "use_case_count": len(USE_CASES),
        "hub_repo": HUB_REPO,
        "child_repos": [uc.github_repo for uc in USE_CASES],
        "use_cases": [
            {
                "use_case_id": uc.use_case_id,
                "github_repo": uc.github_repo,
                "title": uc.title,
                "category": uc.category,
                "parent_business": uc.parent_business,
                "start_script": uc.start_script,
                "mcp_tools": uc.mcp_tools,
                "processor_ops": uc.processor_ops,
                "dataset_path": uc.dataset_path,
                "research_pack": uc.research_pack,
            }
            for uc in USE_CASES
        ],
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }