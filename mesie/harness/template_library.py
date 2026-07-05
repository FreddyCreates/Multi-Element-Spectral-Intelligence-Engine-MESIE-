"""Interface + build templates — fast product surfaces on native intelligence."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from mesie.version_info import MESIE_VERSION

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = "MESIE-TEMPLATE-LIBRARY/1.0"


@dataclass(frozen=True)
class BuildTemplate:
    template_id: str
    title: str
    interface_type: str
    stack: str
    path: str
    industries: tuple[str, ...]
    hooks: tuple[str, ...]
    description: str


TEMPLATE_LIBRARY: List[BuildTemplate] = [
    BuildTemplate(
        "dashboard_4k",
        "Enterprise 4K Command Center",
        "operations_dashboard",
        "html+css+fetch",
        "websites/enterprise-4k/index.html",
        ("enterprise", "platform", "all"),
        ("GET /processor/status", "GET :8765/health", "GET :8767/health"),
        "3840×2160 ops desk — five businesses, dual-chain tokens, live ping.",
    ),
    BuildTemplate(
        "computing_family",
        "MESIE Computing Family Live",
        "product_dashboard",
        "html+css+fetch",
        "websites/computing-family/index.html",
        ("compute", "all"),
        ("GET /processor/dsl", "GET /processor/depth", "MESIE_COMPUTE_PRODUCTS.json"),
        "8 virtual SKUs, tri-agent squads, latency table — live stats.",
    ),
    BuildTemplate(
        "landing",
        "Product Landing Page",
        "marketing",
        "html+css",
        "websites/mesie-landing/index.html",
        ("all",),
        ("hero", "sku_grid", "cta_start_script"),
        "φ-branded landing — link to processor quickstart.",
    ),
    BuildTemplate(
        "career_portal",
        "1000-Career Workforce Portal",
        "workforce",
        "html+css",
        "websites/career-portal/index.html",
        ("workforce", "careers"),
        ("GET :8767/health", "triple_protocol"),
        "5 pillars × 200 careers — triple protocol routing.",
    ),
    BuildTemplate(
        "market_hub",
        "Market + Fork Portal",
        "commerce",
        "html+css",
        "websites/market-hub/index.html",
        ("commerce", "devkit"),
        ("public-forks", "dual_chain_tokens"),
        "Child repos, zips, GitHub publish flows.",
    ),
    BuildTemplate(
        "api_console",
        "Processor API Console",
        "developer",
        "html+css+fetch",
        "templates/surfaces/api_console.html",
        ("developer", "all"),
        ("POST /processor/dsl/{id}/run", "POST /processor/depth/{id}/envelope"),
        "Invoke any processor op from browser — native DSL + depth.",
    ),
    BuildTemplate(
        "product_sku",
        "Single SKU Product App",
        "product",
        "html+css+fetch",
        "templates/surfaces/product_sku.html",
        ("all_industries",),
        ("MESIE_COMPUTE_PRODUCTS.json", "use_case_spec"),
        "One virtual product — invocations, p50, health, ops list.",
    ),
    BuildTemplate(
        "auto_business_ops",
        "Auto-AI Business Operations",
        "autonomous_business",
        "html+css+fetch+json",
        "templates/surfaces/auto_business_ops.html",
        ("all_industries",),
        ("AUTO_AI_BUSINESS_CATALOG.json", "tri_agent_squads", "receipt_chain"),
        "You + native AI — mission board, squad status, ship gate.",
    ),
    BuildTemplate(
        "native_dsl_ide",
        "Native DSL Playground",
        "language",
        "html+css+fetch",
        "templates/surfaces/native_dsl_ide.html",
        ("signals", "mcp", "workflow"),
        ("POST /processor/dsl/{id}/compile", "POST /processor/dsl/{id}/run"),
        "8 languages — compile + run in browser against :8750.",
    ),
    BuildTemplate(
        "depth_explorer",
        "Depth Pillar Explorer",
        "polyglot_depth",
        "html+css+fetch",
        "templates/surfaces/depth_explorer.html",
        ("all_industries",),
        ("GET /processor/depth", "GET /processor/depth/{id}"),
        "18 pillars — LOC, engines, envelope invoke.",
    ),
    BuildTemplate(
        "research_paper",
        "Latin Research Paper Viewer",
        "research",
        "markdown+html",
        "docs/papers/",
        ("research", "all"),
        ("NATIVE_RELEASE_MANIFEST.json",),
        "Opera Spectralia I–XIII — release capstone papers.",
    ),
    BuildTemplate(
        "acoustic_demo",
        "Domain Demo (Acoustic Metamaterial)",
        "domain_proof",
        "html+css",
        "demos/acoustic-metamaterial.html",
        ("materials", "seismic", "defense"),
        ("acoustic_metamaterial_agent",),
        "Single-domain interactive proof page pattern.",
    ),
]


def template_manifest() -> Dict[str, Any]:
    return {
        "protocol": PROTOCOL,
        "mesie_version": MESIE_VERSION,
        "template_count": len(TEMPLATE_LIBRARY),
        "design_system": "websites/shared/mesie.css",
        "design_tokens": ["--bg", "--card", "--accent", "--phi", "--ok", "--mono"],
        "templates": [
            {
                "template_id": t.template_id,
                "title": t.title,
                "interface_type": t.interface_type,
                "stack": t.stack,
                "path": t.path,
                "industries": list(t.industries),
                "hooks": list(t.hooks),
                "description": t.description,
            }
            for t in TEMPLATE_LIBRARY
        ],
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }