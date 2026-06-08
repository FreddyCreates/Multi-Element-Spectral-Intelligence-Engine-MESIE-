"""Tier 1 on-prem production appliance — sovereign spectral copilot."""

from __future__ import annotations

import json
import platform
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.evaluation.major_benchmarks import MajorBenchmarkHarness
from mesie.evaluation.mlperf_submit import MLPerfSubmissionPack
from mesie.library.domain_corpus import load_domain_corpus
from mesie.sdk import MAESIClient, __sdk_version__


from mesie.version_info import APPLIANCE_VERSION
DEFAULT_MANIFEST_PATH = Path(__file__).resolve().parents[2] / "deliverables" / "MESIE_Appliance_Manifest.json"
MAJOR_BENCHMARKS_PATH = Path(__file__).resolve().parents[2] / "deliverables" / "MAESI_SDK_Major_Benchmarks.json"
DEFAULT_NARRATIVE_PATH = Path(__file__).resolve().parents[2] / "deliverables" / "MESIE_Appliance_Narrative.md"


@dataclass
class ApplianceHealth:
    ok: bool
    airgapped: bool
    sovereign: bool
    third_party: bool
    routing_ok: bool
    corpus_size: int
    copilot_tools: int
    threat_fast_sla_ms: float
    enterprise_fast_sla_ms: float
    checks: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ApplianceManifest:
    product: str
    company: str
    appliance_version: str
    sdk_version: str
    mesie_version: str
    tier: str
    airgapped: bool
    sla: Dict[str, Any]
    benchmarks: Dict[str, Any]
    modules: List[str]
    deployment: Dict[str, Any]
    generated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ProductionAppliance:
    """Shippable on-prem unit: copilot + vault + field + swarm + benchmarks."""

    PRODUCT = "MESIE Sovereign Spectral Appliance"
    COMPANY = "NeuroSwarmAI"

    def __init__(self, *, threat_sla_ms: float = 12.0, enterprise_sla_ms: float = 500.0) -> None:
        self.threat_sla_ms = threat_sla_ms
        self.enterprise_sla_ms = enterprise_sla_ms
        self.client = MAESIClient()
        self._corpus = load_domain_corpus()

    def health(self) -> ApplianceHealth:
        from mesie.enterprise import EnterpriseAICopilot

        checks: List[Dict[str, Any]] = []
        swarm_st = self.client.swarm.status()
        checks.append({"name": "swarm_routing", "ok": swarm_st.routing_ok})
        checks.append({"name": "corpus", "ok": swarm_st.corpus_size >= 12, "detail": swarm_st.corpus_size})

        copilot = EnterpriseAICopilot()
        n_tools = len(copilot.sovereign_tools())
        checks.append({"name": "copilot_tools", "ok": n_tools >= 24, "detail": n_tools})

        fa = self.client.field_access.status()
        checks.append({"name": "airgapped", "ok": fa.get("airgapped") and not fa.get("internet_connected")})
        checks.append({"name": "third_party_false", "ok": not fa.get("third_party", True)})

        major = MajorBenchmarkHarness(n_trials=100, corpus_size=1000).run()
        threat = major.latency_summary["threat_fast_p50"]
        ent = major.latency_summary["enterprise_fast_p50"]
        checks.append({"name": "threat_sla", "ok": threat <= self.threat_sla_ms, "p50_ms": threat})
        checks.append({"name": "enterprise_sla", "ok": ent <= self.enterprise_sla_ms, "p50_ms": ent})

        ok = all(c["ok"] for c in checks)
        return ApplianceHealth(
            ok=ok,
            airgapped=bool(fa.get("airgapped")),
            sovereign=True,
            third_party=False,
            routing_ok=swarm_st.routing_ok,
            corpus_size=swarm_st.corpus_size,
            copilot_tools=n_tools,
            threat_fast_sla_ms=threat,
            enterprise_fast_sla_ms=ent,
            checks=checks,
        )

    def _load_major_benchmarks(self) -> Dict[str, Any]:
        if MAJOR_BENCHMARKS_PATH.is_file():
            return json.loads(MAJOR_BENCHMARKS_PATH.read_text(encoding="utf-8"))
        return {}

    def _major_summary(self, *, refresh: bool = False) -> Dict[str, Any]:
        cached = self._load_major_benchmarks()
        if cached.get("major") and not refresh:
            m = cached["major"]
            return {
                "win_rate": m["win_rate"],
                "verdict": m["verdict"],
                "wins": m["wins"],
                "losses": m["losses"],
                "latency_summary": m["latency_summary"],
                "source": str(MAJOR_BENCHMARKS_PATH),
            }
        major = MajorBenchmarkHarness(n_trials=200, corpus_size=10000).run()
        return {
            "win_rate": major.win_rate,
            "verdict": major.verdict,
            "wins": major.wins,
            "losses": major.losses,
            "latency_summary": major.latency_summary,
            "source": "live_harness",
        }

    def build_manifest(self, *, tier: str = "tier1") -> ApplianceManifest:
        import mesie

        health = self.health()
        major = self._major_summary()
        mlperf = MLPerfSubmissionPack().generate()
        lat = major["latency_summary"]

        return ApplianceManifest(
            product=self.PRODUCT,
            company=self.COMPANY,
            appliance_version=APPLIANCE_VERSION,
            sdk_version=__sdk_version__,
            mesie_version=mesie.__version__,
            tier=tier,
            airgapped=True,
            sla={
                "threat_fast_ms": self.threat_sla_ms,
                "enterprise_fast_ms": self.enterprise_sla_ms,
                "measured_threat_p50": lat["threat_fast_p50"],
                "measured_enterprise_p50": lat["enterprise_fast_p50"],
            },
            benchmarks={
                "major_win_rate": major["win_rate"],
                "major_wins": major["wins"],
                "major_losses": major["losses"],
                "major_verdict": major["verdict"],
                "major_benchmarks_path": major["source"],
                "swarm_10k_ms_per_agent": lat.get("swarm_10k_ms_per_agent"),
                "mlperf_submission_id": mlperf["submission_id"],
            },
            modules=[
                "enterprise_copilot", "sovereign_vault", "field_access", "swarm_sdk",
                "virtual_silicon", "rf_adapter", "ota_mesh", "cluster_optimizer", "mlperf_pack",
            ],
            deployment={
                "mode": "on_prem_airgapped",
                "deployment_class": "edge_contested",
                "network": "none_required",
                "cloud_required": False,
                "interior_dc_feed": "MESIE_Interior_DataCenter_Manifest.json",
                "ingest": ["csv", "udp", "rf_sim", "rf_udp", "virtual_silicon_hil", "ota_multicast"],
                "platform": platform.platform(),
                "operator_profiles": ["field_operator", "gsa_drone_contractor", "builder_lab_llc"],
            },
            generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    def export_manifest(self, path: Optional[Path] = None) -> Path:
        manifest = self.build_manifest()
        payload = manifest.to_dict()
        out = path or DEFAULT_MANIFEST_PATH
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return out

    def export_narrative(self, path: Optional[Path] = None) -> Path:
        """Customer-facing Tier 1 on-prem appliance narrative backed by major benchmarks."""
        manifest = self.build_manifest(tier="tier1")
        major = self._load_major_benchmarks()
        m = major.get("major", {})
        rows = m.get("rows", [])
        win_lines = [
            f"- **{r['benchmark']}** ({r['category']}): {r['mesie_ms']} ms vs {r['reference_ms']} ms ref"
            for r in rows[:8]
        ]
        lines = [
            "# MESIE Sovereign Spectral Appliance — Tier 1",
            "",
            f"**Product:** {manifest.product}",
            f"**Company:** {manifest.company}",
            f"**Appliance v{manifest.appliance_version}** | SDK {manifest.sdk_version} | MESIE {manifest.mesie_version}",
            "",
            "## Positioning",
            "",
            "Shippable on-prem, air-gapped spectral intelligence unit for defense and enterprise edge.",
            "Runs on **MESIE Virtual Silicon (VS1)** — a software virtual chip (RF front-end + spectral ALU + OTA MAC).",
            "No cloud dependency. Threat decisions and enterprise agent steps run locally on sovereign hardware.",
            "",
            "## Evidence (MAESI_SDK_Major_Benchmarks.json)",
            "",
            f"- Win rate: **{manifest.benchmarks['major_win_rate']}%** ({manifest.benchmarks.get('major_wins', '?')}/{manifest.benchmarks.get('major_wins', 0) + manifest.benchmarks.get('major_losses', 0)} benchmarks)",
            f"- Verdict: `{manifest.benchmarks['major_verdict']}`",
            f"- Threat-fast p50: **{manifest.sla['measured_threat_p50']} ms** (SLA ≤ {manifest.sla['threat_fast_ms']} ms)",
            f"- Enterprise-fast p50: **{manifest.sla['measured_enterprise_p50']} ms** (SLA ≤ {manifest.sla['enterprise_fast_ms']} ms)",
            f"- Swarm 10K ms/agent: **{manifest.benchmarks.get('swarm_10k_ms_per_agent', 'n/a')}**",
            f"- Source: `{manifest.benchmarks.get('major_benchmarks_path', MAJOR_BENCHMARKS_PATH)}`",
            "",
            "## Headline wins",
            "",
            *win_lines,
            "",
            "## Deployment",
            "",
            f"- Mode: {manifest.deployment['mode']}",
            f"- Network: {manifest.deployment['network']}",
            f"- Ingest: {', '.join(manifest.deployment['ingest'])}",
            f"- Platform: {manifest.deployment['platform']}",
            "",
            "## Modules",
            "",
            *[f"- {mod}" for mod in manifest.modules],
            "",
            f"*Generated {manifest.generated_at}*",
        ]
        out = path or DEFAULT_NARRATIVE_PATH
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines), encoding="utf-8")
        return out

    def run_tier1_validation(self) -> Dict[str, Any]:
        health = self.health()
        manifest = self.build_manifest(tier="tier1")
        return {
            "tier": "tier1",
            "health_ok": health.ok,
            "manifest": manifest.to_dict(),
            "ready_to_ship": health.ok,
        }

    def run_tier2_validation(self) -> Dict[str, Any]:
        from data import load_reference_record
        from mesie.field_io.rf_adapter import LiveRFAdapter, RFAdapterConfig, RFSourceMode
        from mesie.silicon.virtual_chip import VirtualSiliconChip
        from mesie.swarm.cluster_coordinator import ClusterSwarmOptimizer
        from mesie.swarm.drone_coordination import DecentralizedSwarmCoordinator

        q = load_reference_record("defense_ew_spectrum_reference")
        coord = DecentralizedSwarmCoordinator(self._corpus)
        opt = ClusterSwarmOptimizer(coord)
        rep = opt.coordinate_optimized(q, n_agents=10000, jam_ground=True, attrition_rate=0.1)

        vs = VirtualSiliconChip()
        vs_full = vs.certify()
        vs_cert_path = vs.export_certification()
        hil = vs_full.rf_hil
        ota = vs_full.ota_mesh

        rf = LiveRFAdapter(RFAdapterConfig(mode=RFSourceMode.VIRTUAL_SILICON))
        rf_rep = rf.ingest_virtual_silicon()
        mlperf = MLPerfSubmissionPack().generate(n_trials=100)
        mlperf_path = MLPerfSubmissionPack.export(mlperf)

        cluster_win = rep.ms_per_agent < 0.5
        return {
            "tier": "tier2",
            "virtual_silicon_certified": hil.certified,
            "virtual_silicon_cert_path": str(vs_cert_path),
            "cluster_optimized_ms_per_agent": rep.ms_per_agent,
            "cluster_optimized_win": cluster_win,
            "cluster_e2e_p50": rep.e2e_p50_ms,
            "rf_adapter_ok": rf_rep.ok,
            "rf_silicon_certified": rf_rep.silicon_certified,
            "rf_field_coherence": rf_rep.field_coherence,
            "rf_hil_path": rf_rep.hil_path,
            "ota_mesh_ok": ota.ok,
            "ota_frames_received": ota.frames_received,
            "ota_over_the_air": ota.over_the_air,
            "mlperf_submission": mlperf_path,
            "mlperf_credibility_tier": mlperf.get("credibility", {}).get("tier"),
            "mlperf_compliance": mlperf.get("compliance", {}).get("community_formal_pack"),
            "gaps_resolved": vs_full.gaps_resolved,
            "gaps_remaining": vs_full.gaps_remaining,
            "ready": (
                cluster_win and hil.certified and rf_rep.ok
                and ota.ok and mlperf.get("valid")
            ),
        }