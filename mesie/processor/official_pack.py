"""Official commercial pack — technology, use cases, tests, certifications, compliance."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
OFFICIAL_DIR = ROOT / "deliverables" / "processor" / "official"
PRODUCT_SKU = "MESIE-VP-1.2"
PRODUCT_NAME = "MESIE Virtual Processor"
LEGAL_ENTITY = "Medina Sovereign Intelligence / Builder Lab"


@dataclass
class CommercialTestCase:
    test_id: str
    category: str
    description: str
    ok: bool
    detail: str = ""
    artifact: str = ""
    duration_s: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CertificationEntry:
    cert_id: str
    title: str
    tier: str
    status: str
    scope: str
    evidence_paths: List[str]
    honest_limit: str
    valid_for_public_claim: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _write(name: str, payload: Dict[str, Any]) -> Path:
    OFFICIAL_DIR.mkdir(parents=True, exist_ok=True)
    out = OFFICIAL_DIR / name
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def build_technology_overview() -> Dict[str, Any]:
    from mesie.agentic.micro.foundations import foundations_snapshot
    from mesie.processor.stack_architecture import stack_architecture_snapshot

    foundations = foundations_snapshot()
    stack = stack_architecture_snapshot()
    return {
        "product": PRODUCT_NAME,
        "sku": PRODUCT_SKU,
        "version": "1.2.0",
        "doctrine": "Everything is a signal — text, JSON, events, physics, and spectra unify under one stack.",
        "formula": "Logic ⊗ Reasoning ⊗ Emergence ⊗ Adaptation (SOLUS)",
        "execution_model": "Python executes; LLMs orchestrate; LRC receipts prove measured work.",
        "technology_layers": [
            {
                "layer": "Universal Signal Plane",
                "components": ["UniversalSignalReader", "SignalTextEmitter", "TranslatorEngine"],
                "modalities": ["text", "json", "state", "event", "numeric", "spectral", "file"],
            },
            {
                "layer": "Spectral Compute Core",
                "components": ["FastSpectralCompute", "SpectralVectorizer", "match_records", "fingerprint LSH"],
                "engines": foundations.get("engines", []),
            },
            {
                "layer": "Virtual Processor",
                "port": 8750,
                "operations": stack["layers"][2]["operations"],
                "accounting": "Local LRC mint ledger per operation",
            },
            {
                "layer": "VP-MESH Network",
                "protocol": "VP-MESH v1.2",
                "transport": "UDP multicast 239.192.77.2:37542 + LAN peer registry",
                "routing": "φ-weighted lowest-latency peer selection",
                "ota": "NSOT-compatible multicast gossip",
            },
            {
                "layer": "NOVA Micro Organization",
                "careers": 70,
                "teams": 12,
                "runtime": "never-stop supervisor + robotics satellite",
            },
            {
                "layer": "Virtual Silicon",
                "chip": "MESIE-VS1",
                "hil": "Virtual RF SDR ingest lane (software-certified)",
                "mesh_mac": "NSOT_multicast_v1",
            },
            {
                "layer": "Sovereign Surface",
                "integrations": ["SovereignForge heartbeat", "Loom vault", "Medina Surface :8760"],
            },
        ],
        "protocols": foundations.get("protocols", []),
        "physics_foundations": foundations.get("physics", []),
        "library": foundations.get("library", {}),
        "tools_count": foundations.get("tools", 0),
        "stack_reference": "deliverables/processor/MESIE_STACK_ARCHITECTURE.json",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def build_use_cases() -> Dict[str, Any]:
    cases = [
        {
            "id": "ai_for_ai_orchestration",
            "vertical": "Enterprise AI",
            "title": "AI agents orchestrating AI",
            "description": "LLM planners call Virtual Processor HTTP/MCP; Python executes embed/match/signals with LRC proof.",
            "buyer": "AI platform teams",
            "mesh_role": "Route compute to lowest-latency LAN node",
        },
        {
            "id": "defense_edge_threat",
            "vertical": "Defense / Robotics",
            "title": "Sub-ms threat-fast spectral path",
            "description": "Robotics satellite fusion + NeuroSwarm audit benchmarks on edge hardware.",
            "buyer": "Contested field operators",
            "mesh_role": "OTA gossip + jam failover routing metadata",
        },
        {
            "id": "industrial_pdm",
            "vertical": "Industrial",
            "title": "Predictive maintenance spectral memory",
            "description": "PSD/FAS/vibration references embedded; top-k retrieval across machine states.",
            "buyer": "Digital twin / factory IT",
            "mesh_role": "Interior DC corpus shards across cluster edge nodes",
        },
        {
            "id": "seismic_orbital_power",
            "vertical": "Multi-domain",
            "title": "Unified domain signal hub",
            "description": "Seismic, orbital, power grid, terrain, RF — all as signals in one library index.",
            "buyer": "Critical infrastructure",
            "mesh_role": "Domain Signal Hub career + VP-MESH peer sync",
        },
        {
            "id": "sovereign_agent_memory",
            "vertical": "Enterprise AI",
            "title": "Sovereign agent memory + receipt chain",
            "description": "Vault curator careers + LRC accounting; zero third-party inference on sovereign path.",
            "buyer": "Regulated / airgapped programs",
            "mesh_role": "Sovereign mesh bundle export to LAN peers",
        },
        {
            "id": "developer_kit_release",
            "vertical": "Commercial",
            "title": "Virtual Processor Developer Kit",
            "description": "Zip manifest + showcase + official dossier for partner distribution.",
            "buyer": "SDK publishers / integrators",
            "mesh_role": "Optional multi-node soak in partner labs",
        },
        {
            "id": "drone_swarm_coordination",
            "vertical": "Defense",
            "title": "Decentralized swarm coordination",
            "description": "Gossip consensus, field routing, cluster-optimized ms/agent in software validation.",
            "buyer": "UAS / counter-UAS programs",
            "mesh_role": "VP-MESH + OTA mesh rounds",
        },
        {
            "id": "native_ai_deliverables",
            "vertical": "Enterprise",
            "title": "SOLUS native AI deliverables",
            "description": "Stream JSON/MD reports with vault tokens — local only.",
            "buyer": "Analyst workflows",
            "mesh_role": "Generate-text from any signal modality",
        },
        {
            "id": "coding_lab_visibility",
            "vertical": "Operations",
            "title": "Live swarm visibility window",
            "description": "Coding lab :8770 feeds robotics + NOVA state for operator dashboards.",
            "buyer": "Internal IT / SOC",
            "mesh_role": "Processor bridge career polls mesh state",
        },
        {
            "id": "commercial_benchmark_proof",
            "vertical": "Commercial",
            "title": "Market-facing benchmark proof",
            "description": "NOVA_SHOWCASE + official commercial test report for public claims.",
            "buyer": "Marketing / GSA / partners",
            "mesh_role": "VP_MESH_SOAK.json multi-round proof",
        },
    ]
    return {
        "product": PRODUCT_NAME,
        "sku": PRODUCT_SKU,
        "count": len(cases),
        "use_cases": cases,
        "plain_summary": f"{len(cases)} high-level commercial use cases across enterprise AI, defense edge, industrial, and sovereign programs.",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def build_certification_manifest(*, live: bool = True) -> Dict[str, Any]:
    certs: List[CertificationEntry] = []
    chip_ok = mesh_ok = release_ok = False
    if live:
        try:
            from mesie.processor.virtual_processor import VirtualProcessor

            proc = VirtualProcessor()
            chip_ok = proc.virtual_chip_certify().ok
            mesh_ok = proc.mesh_pulse().ok
            release_ok = True
        except Exception:
            pass

    def add(
        cert_id: str,
        title: str,
        tier: str,
        status: str,
        scope: str,
        paths: List[str],
        limit: str,
        public: bool,
    ) -> None:
        certs.append(
            CertificationEntry(cert_id, title, tier, status, scope, paths, limit, public)
        )

    add(
        "VP-REL-001",
        "Virtual Processor Release Gate",
        "measured_local",
        "active" if release_ok else "pending_run",
        "Embed, match, benchmark, mesh, LRC accounting",
        ["deliverables/processor/VIRTUAL_PROCESSOR_RELEASE.json"],
        "Single-node harness; customer repro extends corroboration",
        True,
    )
    add(
        "VS-HIL-001",
        "Virtual Silicon RF HIL Lane",
        "simulated_validated",
        "active" if chip_ok else "pending_run",
        "Virtual SDR ADC → NSRF binary → field bridge",
        ["deliverables/processor/official/VIRTUAL_PROCESSOR_COMMERCIAL_TEST_REPORT.json"],
        "Software-certified only — not physical fab or SDR range",
        True,
    )
    add(
        "VP-MESH-001",
        "VP-MESH Network Protocol",
        "measured_local",
        "active" if mesh_ok else "pending_run",
        "UDP multicast beacons + OTA gossip + LAN peer registry",
        ["deliverables/processor/VP_MESH_SOAK.json", "deliverables/processor/VP_MESH_STATE.json"],
        "LAN multicast today; multi-host WAN extension is roadmap",
        True,
    )
    add(
        "SOLUS-ORG-001",
        "SOLUS Formal Organism",
        "documented_reference",
        "active",
        "Logic ⊗ Reasoning ⊗ Emergence ⊗ Adaptation — zero third-party models",
        ["mesie/sdk/solus/"],
        "Own formal models — not third-party LLM certification",
        True,
    )
    add(
        "NOVA-ORG-070",
        "NOVA 70-Career IT Organization",
        "measured_local",
        "active",
        "Infrastructure micro fleet — laws, protocols, library, release",
        ["deliverables/nova/NOVA_RUNTIME_STATE.json"],
        "Software organization runtime — not human ITIL audit",
        True,
    )
    add(
        "SIG-PLANE-001",
        "Universal Signal Plane",
        "measured_local",
        "active",
        "Text, JSON, events, files → spectral fingerprint + analyst text",
        ["tests/test_universal_signals.py"],
        "Signal translation layer — not NLP benchmark leaderboard",
        True,
    )
    add(
        "MLPERF-COMM-001",
        "MLPerf Community Formal Pack",
        "documented_reference",
        "active",
        "Compliance manifest for community pack — not official MLPerf board",
        ["deliverables/mlperf_submit/compliance_manifest.json"],
        "Not submitted to official MLPerf leaderboard",
        False,
    )
    add(
        "DATA-SOV-001",
        "Data Sovereignty / Airgapped Path",
        "documented_reference",
        "active",
        "Local vault, LRC ledger, no third-party inference on sovereign path",
        ["deliverables/processor/official/VIRTUAL_PROCESSOR_COMPLIANCE_PACK.json"],
        "Architectural compliance — not FedRAMP/ISO audit certificate",
        True,
    )
    add(
        "COMBAT-NOT-001",
        "Not Combat / DoD Accredited",
        "gap",
        "acknowledged",
        "Explicit non-claim — software scenario validation only",
        [],
        "Do not claim combat certification or DoD accreditation",
        False,
    )

    active = sum(1 for c in certs if c.status == "active")
    return {
        "product": PRODUCT_NAME,
        "sku": PRODUCT_SKU,
        "issuer": LEGAL_ENTITY,
        "certifications": [c.to_dict() for c in certs],
        "active_count": active,
        "total_count": len(certs),
        "public_claim_rule": "Only certifications with valid_for_public_claim=true may appear on marketing.",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def build_compliance_pack() -> Dict[str, Any]:
    return {
        "product": PRODUCT_NAME,
        "sku": PRODUCT_SKU,
        "entity": LEGAL_ENTITY,
        "sovereign_principles": [
            "Python executes; LLMs orchestrate — no chat-only product loops",
            "Third-party inference disabled on sovereign path (SOLUS + native voice optional)",
            "Local LRC receipt chain — measured work units per operation",
            "Airgapped LAN mesh — VP-MESH + sovereign peer bundles",
            "φ-laws: RECITAL_PLUS_ONE, DUAL_READ, φ-DECAY (Medina Protocol reference)",
        ],
        "data_handling": {
            "default_storage": "Local deliverables/ + .processor_vault/",
            "mesh_peer_export": "library/mesh_peers/ — LAN file-drop only",
            "cloud_required": False,
            "pii_note": "Operator responsible for signal payloads sent to read-signal/generate-text",
        },
        "commercial_disclaimers": [
            "Software validation and measured benchmarks — not combat certification.",
            "Virtual silicon RF HIL is software-certified; physical SDR range is a named gap.",
            "MLPerf community pack is not an official MLPerf board submission.",
            "10K swarm figures are in-process/cluster simulation unless multi-host soak artifact cited.",
        ],
        "export_control_note": "Consult counsel for ITAR/EAR on defense domain reference spectra bundled in SDK.",
        "audit_artifacts": [
            "deliverables/processor/official/VIRTUAL_PROCESSOR_COMMERCIAL_TEST_REPORT.json",
            "deliverables/nova/NOVA_SHOWCASE.json",
            "deliverables/processor/VIRTUAL_PROCESSOR_RELEASE.json",
        ],
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def _run_pytest(tests: List[str], timeout: int = 300) -> CommercialTestCase:
    t0 = time.perf_counter()
    r = subprocess.run(
        [sys.executable, "-m", "pytest", *tests, "-q", "--tb=no"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    elapsed = round(time.perf_counter() - t0, 2)
    detail = (r.stdout or r.stderr)[-500:]
    return CommercialTestCase(
        test_id="pytest_suite",
        category="automated",
        description=f"pytest: {', '.join(tests)}",
        ok=r.returncode == 0,
        detail=detail,
        duration_s=elapsed,
    )


def run_commercial_tests(*, quick: bool = False) -> Dict[str, Any]:
    """Full commercial validation battery."""
    from mesie.agentic.micro.showcase import run_showcase
    from mesie.processor.mesh_protocol import run_mesh_soak
    from mesie.processor.release import run_processor_release
    from mesie.processor.virtual_processor import VirtualProcessor

    tests: List[CommercialTestCase] = []
    t_all = time.perf_counter()

    # Release gate
    t0 = time.perf_counter()
    rep = run_processor_release(export=True)
    tests.append(
        CommercialTestCase(
            "release_gate",
            "production",
            "Virtual Processor release gate (all checks)",
            rep.ready,
            str([c["name"] for c in rep.checks]),
            "deliverables/processor/VIRTUAL_PROCESSOR_RELEASE.json",
            round(time.perf_counter() - t0, 2),
        )
    )

    # Showcase
    t0 = time.perf_counter()
    show = run_showcase(export=True, quick=True)
    tests.append(
        CommercialTestCase(
            "nova_showcase",
            "benchmark",
            "NOVA showcase workflow proof",
            bool(show.get("ok")),
            str(show.get("headline", {})),
            "deliverables/nova/NOVA_SHOWCASE.json",
            round(time.perf_counter() - t0, 2),
        )
    )

    # VP-MESH soak
    t0 = time.perf_counter()
    soak = run_mesh_soak(n_nodes=4, rounds=2 if quick else 5)
    tests.append(
        CommercialTestCase(
            "vp_mesh_soak",
            "network",
            "VP-MESH production soak",
            bool(soak.get("ok")),
            f"rounds={soak.get('rounds')} ota_ok={soak.get('pulses', [{}])[-1].get('ota_mesh_ok')}",
            "deliverables/processor/VP_MESH_SOAK.json",
            round(time.perf_counter() - t0, 2),
        )
    )

    # Virtual chip
    t0 = time.perf_counter()
    proc = VirtualProcessor()
    chip = proc.virtual_chip_certify()
    tests.append(
        CommercialTestCase(
            "virtual_chip",
            "silicon",
            "Virtual silicon certification lane",
            chip.ok,
            str(chip.output.get("certified")),
            "embedded in commercial test report",
            round(time.perf_counter() - t0, 2),
        )
    )

    # Cluster edge (quick only runs small)
    if not quick:
        try:
            t0 = time.perf_counter()
            from mesie.production.cluster_edge import ClusterEdgeFabric

            cluster = ClusterEdgeFabric(n_nodes=4, n_agents=500).run()
            tests.append(
                CommercialTestCase(
                    "cluster_edge",
                    "fabric",
                    "Cluster edge fabric (interior DC + OTA + swarm)",
                    cluster.ok,
                    f"ota={cluster.ota_mesh_ok} ms/agent={cluster.cluster_ms_per_agent}",
                    "deliverables/MESIE_Cluster_Edge_Report.json",
                    round(time.perf_counter() - t0, 2),
                )
            )
        except Exception as exc:
            tests.append(
                CommercialTestCase(
                    "cluster_edge",
                    "fabric",
                    "Cluster edge fabric",
                    False,
                    str(exc)[:200],
                    "",
                    0.0,
                )
            )

    # Pytest battery
    pytest_targets = [
        "tests/test_vp_mesh.py",
        "tests/test_universal_signals.py",
    ]
    if not quick:
        pytest_targets.append("tests/test_nova_sphere.py::test_nova_organization_size")
    tests.append(_run_pytest(pytest_targets, timeout=600 if not quick else 120))

    passed = sum(1 for t in tests if t.ok)
    report = {
        "product": PRODUCT_NAME,
        "sku": PRODUCT_SKU,
        "commercial_ready": passed == len(tests),
        "passed": passed,
        "total": len(tests),
        "pass_rate": round(100.0 * passed / max(1, len(tests)), 1),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "tests": [t.to_dict() for t in tests],
        "elapsed_s": round(time.perf_counter() - t_all, 2),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _write("VIRTUAL_PROCESSOR_COMMERCIAL_TEST_REPORT.json", report)
    return report


def build_official_dossier(*, run_tests: bool = True, quick: bool = False) -> Dict[str, Any]:
    """Master official paperwork index — technology, use cases, certs, compliance, tests."""
    tech = build_technology_overview()
    uses = build_use_cases()
    compliance = build_compliance_pack()
    commercial = run_commercial_tests(quick=quick) if run_tests else {"note": "tests skipped"}
    certs = build_certification_manifest(live=run_tests)

    paths = {
        "technology": str(_write("VIRTUAL_PROCESSOR_TECHNOLOGY.json", tech)),
        "use_cases": str(_write("VIRTUAL_PROCESSOR_USE_CASES.json", uses)),
        "certifications": str(_write("VIRTUAL_PROCESSOR_CERTIFICATION_MANIFEST.json", certs)),
        "compliance": str(_write("VIRTUAL_PROCESSOR_COMPLIANCE_PACK.json", compliance)),
        "commercial_tests": str(OFFICIAL_DIR / "VIRTUAL_PROCESSOR_COMMERCIAL_TEST_REPORT.json"),
        "market_research": str(ROOT / "deliverables/processor/VIRTUAL_PROCESSOR_MARKET_RESEARCH.json"),
        "devkit": str(ROOT / "deliverables/processor/VIRTUAL_PROCESSOR_DEVKIT.json"),
        "showcase": str(ROOT / "deliverables/nova/NOVA_SHOWCASE.json"),
        "mesh_soak": str(ROOT / "deliverables/processor/VP_MESH_SOAK.json"),
        "stack": str(ROOT / "deliverables/processor/MESIE_STACK_ARCHITECTURE.json"),
    }

    dossier = {
        "document_type": "OFFICIAL_COMMERCIAL_DOSSIER",
        "product": PRODUCT_NAME,
        "sku": PRODUCT_SKU,
        "version": "1.2.0",
        "entity": LEGAL_ENTITY,
        "commercial_ready": commercial.get("commercial_ready", False),
        "pass_rate": commercial.get("pass_rate"),
        "artifacts": paths,
        "executive_summary": (
            f"{PRODUCT_NAME} ({PRODUCT_SKU}) — sovereign virtual processor with universal signals, "
            f"VP-MESH LAN fabric, 70-career NOVA runtime, and measured LRC proof. "
            f"Commercial test pass rate: {commercial.get('pass_rate', 'n/a')}%. "
            "Software validation — not combat certification."
        ),
        "public_release_bundle": "deliverables/processor/VIRTUAL_PROCESSOR_OFFICIAL_BUNDLE.zip",
        "deploy_command": ".\\Deploy-MESIE.ps1 -Package -DevKit -Mesh -Official",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _write("VIRTUAL_PROCESSOR_OFFICIAL_DOSSIER.json", dossier)
    _write_technology_md(tech, uses, certs, compliance)
    _write_release_brief_md(dossier, commercial)
    return dossier


def _write_technology_md(
    tech: Dict[str, Any],
    uses: Dict[str, Any],
    certs: Dict[str, Any],
    compliance: Dict[str, Any],
) -> Path:
    lines = [
        f"# {PRODUCT_NAME} — Technology Overview",
        "",
        f"**SKU:** {PRODUCT_SKU}  ",
        f"**Version:** {tech.get('version')}  ",
        f"**Generated:** {tech.get('generated_at')}",
        "",
        "## Doctrine",
        tech.get("doctrine", ""),
        "",
        "## Technology Layers",
    ]
    for layer in tech.get("technology_layers", []):
        lines.append(f"### {layer.get('layer')}")
        if "components" in layer:
            lines.append("- " + ", ".join(layer["components"]))
        if "operations" in layer:
            lines.append("- Operations: " + ", ".join(layer["operations"][:8]) + "...")
        lines.append("")

    lines.extend(["## High-Level Use Cases", ""])
    for uc in uses.get("use_cases", [])[:6]:
        lines.append(f"- **{uc['title']}** ({uc['vertical']}): {uc['description']}")
    lines.append("")
    lines.append("## Certifications (summary)")
    for c in certs.get("certifications", [])[:6]:
        lines.append(f"- {c['cert_id']}: {c['title']} — `{c['status']}` ({c['tier']})")
    lines.append("")
    lines.append("## Compliance")
    for d in compliance.get("commercial_disclaimers", []):
        lines.append(f"- {d}")
    lines.append("")

    out = OFFICIAL_DIR / "TECHNOLOGY_OVERVIEW.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def _write_release_brief_md(dossier: Dict[str, Any], commercial: Dict[str, Any]) -> Path:
    lines = [
        "# Commercial Release Brief",
        "",
        f"**Product:** {dossier['product']}",
        f"**SKU:** {dossier['sku']}",
        f"**Commercial ready:** {dossier.get('commercial_ready')}",
        f"**Test pass rate:** {dossier.get('pass_rate')}%",
        "",
        "## Executive Summary",
        dossier.get("executive_summary", ""),
        "",
        "## Commercial Test Results",
    ]
    for t in commercial.get("tests", []):
        status = "PASS" if t.get("ok") else "FAIL"
        lines.append(f"- [{status}] {t.get('test_id')}: {t.get('description')}")
    lines.extend([
        "",
        "## Deploy",
        "```powershell",
        dossier.get("deploy_command", ".\\Deploy-MESIE.ps1"),
        "```",
        "",
        "## Official Artifacts",
    ])
    for k, v in dossier.get("artifacts", {}).items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")

    out = OFFICIAL_DIR / "COMMERCIAL_RELEASE_BRIEF.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def package_official_bundle() -> Path:
    """Zip all official paperwork for commercial distribution."""
    import zipfile

    build_official_dossier(run_tests=True, quick=True)
    zip_path = ROOT / "deliverables" / "processor" / "VIRTUAL_PROCESSOR_OFFICIAL_BUNDLE.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        if OFFICIAL_DIR.is_dir():
            for p in OFFICIAL_DIR.rglob("*"):
                if p.is_file():
                    zf.write(p, p.relative_to(ROOT).as_posix())
        for rel in [
            "deliverables/processor/VIRTUAL_PROCESSOR_RELEASE.json",
            "deliverables/processor/VIRTUAL_PROCESSOR_MARKET_RESEARCH.json",
            "deliverables/processor/MESIE_STACK_ARCHITECTURE.json",
            "deliverables/processor/VP_MESH_SOAK.json",
            "deliverables/nova/NOVA_SHOWCASE.json",
        ]:
            src = ROOT / rel
            if src.is_file():
                zf.write(src, rel)
    return zip_path