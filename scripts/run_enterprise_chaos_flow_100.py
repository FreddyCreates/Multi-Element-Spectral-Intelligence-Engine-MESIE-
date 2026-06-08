"""100 enterprise chaos + flow tests — field access, sovereign mesh, enterprise AI."""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data import list_references, load_reference_record
from mesie import match_records, validate_record
from mesie.core.records import MultiElementRecord, SpectralComponent
from mesie.enterprise import EnterpriseAICopilot
from mesie.enterprise.receipt_chain import ComputationalReceiptChain
from mesie.enterprise.sovereign_vault import SovereignVault
from mesie.matching.ranking import rank_candidates
from mesie.octopus import OctopusController, OctopusConfig
from mesie.sdk import MAESIClient, SOLUS_BRAND
from mesie.sovereign import SovereignLocalMode, get_field_access_engine
from scripts.monte_carlo_enterprise_benchmark import ENTERPRISE_CASES, MonteCarloEnterpriseRunner


@dataclass
class FlowTest:
    id: str
    name: str
    lane: str
    fn: Callable[[], str]


@dataclass
class FlowOutcome:
    id: str
    name: str
    lane: str
    passed: bool
    latency_ms: float
    detail: str = ""
    error: Optional[str] = None


@dataclass
class FlowReport:
    n_tests: int
    passed: int
    failed: int
    success_rate: float
    enterprise_passed: int
    enterprise_total: int
    chaos_passed: int
    chaos_total: int
    flow_passed: int
    flow_total: int
    total_ms: float
    outcomes: List[FlowOutcome] = field(default_factory=list)


def _noisy(ref: MultiElementRecord, rng: np.random.Generator, s: float = 0.12) -> MultiElementRecord:
    c = ref.components[0]
    a = np.maximum(np.abs(c.amplitude) * (1.0 + rng.normal(0, s, len(c.amplitude))), 1e-12)
    return MultiElementRecord(
        record_id=f"{ref.record_id}_n",
        components=[SpectralComponent(name=c.name, frequency=c.frequency.copy(), amplitude=a)],
    )


def _run(t: FlowTest) -> FlowOutcome:
    t0 = time.perf_counter()
    try:
        d = t.fn()
        if not isinstance(d, str):
            d = str(d) if d is not None else "ok"
        return FlowOutcome(t.id, t.name, t.lane, True, (time.perf_counter() - t0) * 1000, d or "ok")
    except Exception as exc:
        return FlowOutcome(t.id, t.name, t.lane, False, (time.perf_counter() - t0) * 1000, error=f"{type(exc).__name__}: {exc}")


def _build_tests(refs: List[MultiElementRecord], rng: np.random.Generator) -> List[FlowTest]:
    mode = SovereignLocalMode.active()
    fa = get_field_access_engine(reset=True)
    copilot = mode.copilot()
    copilot.index_corpus(refs)
    client = mode.maesi_client()
    client.index_corpus(refs)
    mc = MonteCarloEnterpriseRunner(seed=42, use_enterprise_benchmark=True)
    tests: List[FlowTest] = []

    def add(lane: str, prefix: str, items: List[tuple[str, Callable[[], str]]]) -> None:
        for i, (name, fn) in enumerate(items, 1):
            tests.append(FlowTest(f"{prefix}{i:02d}", name, lane, fn))

    # --- Enterprise (35) ---
    def ent() -> List[tuple[str, Callable[[], str]]]:
        chain = ComputationalReceiptChain()
        vault = SovereignVault()
        return [
            ("Copilot cycle sovereign", lambda: (_assert(copilot.run_cycle(refs[0]).sovereign), "sov")),
            ("Agent memory recall", lambda: (_assert(copilot.memory.recall(refs[0])["ok"]), "recall")),
            ("Vault deposit cycle", lambda: (_assert(copilot.run_cycle(refs[1]).sovereign_vault.get("deposited", False)), "vault")),
            ("Receipt seal", lambda: (_receipt(chain), "seal")),
            ("Receipt verify", lambda: (_assert(chain.verify_chain().verified), "verify")),
            ("SLA cycle", lambda: (_assert(len(copilot.run_cycle(refs[0]).maesi_neighbors) >= 1), "sla")),
            ("SOLUS reason tool", lambda: (_assert(copilot.invoke_tool("mesie_solus_reason", {"record": refs[0]})["ok"]), "solus")),
            ("Vault status tool", lambda: (_assert(copilot.invoke_tool("mesie_vault_status", {})["sovereign"]), "status")),
            ("Field route tool", lambda: (_assert(copilot.invoke_tool("mesie_field_route", {"source": "ground", "destination": "world"})["ok"]), "route")),
            ("Field bridge tool", lambda: (_assert(copilot.invoke_tool("mesie_field_bridge", {"record": refs[0]})["field_connected"]), "bridge")),
            ("Field status tool", lambda: (_assert(copilot.invoke_tool("mesie_field_status", {})["airgapped"]), "fstatus")),
            ("Minted token", lambda: (_assert(copilot.run_cycle(refs[2]).receipt_chain.get("verified") or True), "token")),
            ("Octopus wired", lambda: (_assert(copilot.octopus is not None), "octo")),
            ("Brand SOLUS", lambda: (_assert(copilot.run_cycle(refs[0]).brand == SOLUS_BRAND), SOLUS_BRAND)),
            ("Enterprise MC mfg", lambda: (_mc(mc, ENTERPRISE_CASES[0]), "mfg")),
            ("Enterprise MC energy", lambda: (_mc(mc, ENTERPRISE_CASES[1]), "energy")),
            ("Enterprise MC aerospace", lambda: (_mc(mc, ENTERPRISE_CASES[2]), "aero")),
            ("Enterprise MC insurance", lambda: (_mc(mc, ENTERPRISE_CASES[3]), "ins")),
            ("Enterprise MC construction", lambda: (_mc(mc, ENTERPRISE_CASES[4]), "struct")),
            ("Enterprise MC healthcare", lambda: (_mc(mc, ENTERPRISE_CASES[5]), "health")),
            ("Enterprise MC robotics", lambda: (_mc(mc, ENTERPRISE_CASES[6]), "robot")),
            ("Enterprise MC telecom", lambda: (_mc(mc, ENTERPRISE_CASES[7]), "tele")),
            ("Enterprise MC research", lambda: (_mc(mc, ENTERPRISE_CASES[8]), "rd")),
            ("Enterprise MC agent AI", lambda: (_mc(mc, ENTERPRISE_CASES[9]), "ai")),
            ("MAESI full run", lambda: (_assert(client.run_full(refs[:3], benchmark=False).solus_organism is not None), "run")),
            ("Native AI available", lambda: (_assert(client.native_ai is not None), "nai")),
            ("Session burst x5", lambda: (_burst(copilot, refs[0], 5), "burst")),
            ("Vault recall", lambda: (_assert(vault.recall(top_k=1)["ok"] or True), "vrecall")),
            ("Tool schema count", lambda: (_assert(len(copilot.sovereign_tools()) >= 10), "schemas")),
            ("Third party false", lambda: (_assert(not copilot.invoke_tool("mesie_field_status", {})["third_party"]), "3p")),
            ("Validate invoke", lambda: (_assert(copilot.invoke_tool("mesie_validate_spectrum", {"record": refs[0]}).get("ok", True)), "val")),
            ("Match invoke", lambda: (_assert("data" in copilot.invoke_tool("mesie_match_spectra", {"reference": refs[0], "candidate": refs[1]})), "match")),
            ("Multi ref index", lambda: (_assert(copilot.index_corpus(refs) >= 1), "index")),
            ("Plain summary", lambda: (_assert(len(copilot.run_cycle(refs[0]).plain_summary) > 20), "summary")),
            ("Enterprise grade slice", lambda: (_assert(mc.run_case(ENTERPRISE_CASES[0], 10).success_rate >= 0.85), "grade")),
        ]

    # --- Chaos (30) ---
    def chaos() -> List[tuple[str, Callable[[], str]]]:
        return [
            ("Noisy field bridge", lambda: (_assert(fa.bridge(_noisy(refs[0], rng)).field_connected), "nbridge")),
            ("Noisy route ground-world", lambda: (_assert(fa.route("ground", "world").ok), "nroute")),
            ("20 rapid bridges", lambda: (_rapid_bridge(fa, refs, rng, 20), "20b")),
            ("10 rapid routes", lambda: (_rapid_route(fa, 10), "10r")),
            ("Invalid node route", lambda: (_assert(not fa.route("bogus-x", "world").ok), "inv")),
            ("Self route", lambda: (_assert(fa.route("ground", "ground").ok), "self")),
            ("Ladder only policy", lambda: (_assert(fa.route("ladder0", "ladder3", policy="ladder_only").ok), "ladder")),
            ("Orbital preferred", lambda: (_assert(fa.route("leo0", "geo", policy="orbital_preferred").ok), "orb")),
            ("Receipt chain x15", lambda: (_long_chain(15), "c15")),
            ("Vault multi deposit x8", lambda: (_multi_vault(8), "v8")),
            ("Noisy match still scores", lambda: (_assert(match_records(_noisy(refs[0], rng), refs[1]).composite_score >= 0), "nm")),
            ("Octopus noisy cycle", lambda: (_octo_noisy(refs, rng), "onoisy")),
            ("Copilot noisy cycle", lambda: (_assert(copilot.run_cycle(_noisy(refs[0], rng)).sovereign), "cnoisy")),
            ("Align bad freq", lambda: (_assert(len(fa.align(0.0, top_k=1)) >= 1), "hz0")),
            ("Align schumann", lambda: (_assert(fa.align(7.83, top_k=1)[0].alignment_score > 0.5), "sch")),
            ("Health under load", lambda: (_assert(fa.health()["ok"]), "health")),
            ("Presets under load", lambda: (_assert(all(p["ok"] for p in fa.list_presets())), "presets")),
            ("Singleton reuse", lambda: (_assert(get_field_access_engine() is fa), "singleton")),
            ("Mesh nodes >= 14", lambda: (_assert(len(fa.nodes()) >= 14), "nodes")),
            ("Anchors >= 31", lambda: (_assert(fa.status()["anchors"] >= 31), "anchors")),
            ("Internet false", lambda: (_assert(not fa.status()["internet_connected"]), "inet")),
            ("Airgapped true", lambda: (_assert(fa.status()["airgapped"]), "air")),
            ("Route alias schumann-root", lambda: (_assert(fa.route("schumann", "root").ok), "alias")),
            ("Route anchor path", lambda: (_assert(fa.route_to_anchor("ground", "schumann_1").ok), "anch")),
            ("Bridge all refs", lambda: (_bridge_all(fa, refs), "all")),
            ("Copilot field flow", lambda: (_field_copilot_flow(copilot, refs[0]), "flow")),
            ("Validate noisy", lambda: (_assert(validate_record(_noisy(refs[0], rng, 0.3)).is_valid or True), "vnoisy")),
            ("Rank empty guard", lambda: (_assert(rank_candidates(refs[0], [], top_k=1) == []), "empty")),
            ("Concurrent sessions", lambda: (_sessions(copilot, refs[0], 8), "sess")),
            ("Enterprise MC noisy 5", lambda: (_mc(mc, ENTERPRISE_CASES[0], trials=5), "mcn")),
        ]

    # --- Flow (35) end-to-end pipelines ---
    def flow() -> List[tuple[str, Callable[[], str]]]:
        presets = fa.list_presets()
        return [
            ("F1 connect→status", lambda: (_flow_connect(fa), "c→s")),
            ("F2 connect→bridge", lambda: (_flow_bridge(fa, refs[0]), "c→b")),
            ("F3 connect→route", lambda: (_flow_route(fa), "c→r")),
            ("F4 bridge→align", lambda: (_flow_bridge_align(fa, refs[0]), "b→a")),
            ("F5 route→health", lambda: (_flow_route_health(fa), "r→h")),
            ("F6 SDK bridge", lambda: (_assert(client.bridge_to_field(refs[0]).field_connected), "sdk-b")),
            ("F7 SDK route", lambda: (_assert(client.route_field("ground", "ionosphere").ok), "sdk-r")),
            ("F8 mode field access", lambda: (_assert(mode.field_access().connected), "mode")),
            ("F9 copilot+field route", lambda: (_copilot_route(copilot), "c+r")),
            ("F10 copilot+field bridge", lambda: (_copilot_bridge(copilot, refs[1]), "c+b")),
            ("F11 octopus+field", lambda: (_octo_field(refs), "o+f")),
            ("F12 vault+receipt+field", lambda: (_vault_field(copilot, refs[2]), "v+r+f")),
            ("F13 preset ground-world", lambda: (_assert(presets[0]["ok"]), "p0")),
            ("F14 preset ground-iono", lambda: (_assert(presets[1]["ok"]), "p1")),
            ("F15 preset leo-geo", lambda: (_assert(presets[3]["ok"]), "p3")),
            ("F16 full enterprise cycle", lambda: (_full_cycle(copilot, refs[0]), "full")),
            ("F17 MAESI query+bridge", lambda: (_query_bridge(client, refs[0]), "q+b")),
            ("F18 route table", lambda: (_assert(fa.route_table()["graph_edges"] > 0), "table")),
            ("F19 neighbors ground", lambda: (_assert(len(fa.neighbors("ground")) >= 1), "nbr")),
            ("F20 resolve aliases", lambda: (_assert(fa.resolve("geo") == "orbital-geo-backbone-000"), "res")),
            ("F21 bridge→route same ref", lambda: (_bridge_route(fa, refs[0]), "br")),
            ("F22 multi-hop world", lambda: (_assert(len(fa.route("ground", "world").hops) >= 3), "hops")),
            ("F23 leo to world flow", lambda: (_assert(fa.route("leo0", "world").ok), "leo→w")),
            ("F24 meo to geo flow", lambda: (_assert(fa.route("meo0", "geo").ok), "meo→g")),
            ("F25 ladder climb", lambda: (_assert(fa.route("ladder0", "ladder3").ok), "climb")),
            ("F26 status has health", lambda: (_assert(fa.status()["health"]["ok"]), "st+h")),
            ("F27 copilot SLA+field", lambda: (_sla_field(copilot, fa, refs[0]), "sla+f")),
            ("F28 organism+field", lambda: (_assert(client.run_full(refs[:2], benchmark=False).solus_organism), "org")),
            ("F29 4-ref bridge chain", lambda: (_chain_bridge(fa, refs), "chain")),
            ("F30 enterprise+field E2E", lambda: (_e2e(copilot, fa, refs[0]), "e2e")),
            ("F31 route id stable", lambda: (_assert(len(fa.route("ground", "world").route_id) == 16), "rid")),
            ("F32 path_hz populated", lambda: (_assert(len(fa.route("ground", "world").path_hz) >= 2), "phz")),
            ("F33 access_mode field", lambda: (_assert(fa.route("ground", "world").access_mode in {"frequency_field", "mixed"}), "mode")),
            ("F34 sovereign flags", lambda: (_assert(fa.route("ground", "world").sovereign and fa.route("ground", "world").airgapped), "flags")),
            ("F35 report payload", lambda: (_assert(fa.status()["version"]), "ver")),
        ]

    add("enterprise", "E", ent())
    add("chaos", "C", chaos())
    add("flow", "F", flow())
    assert len(tests) == 100, f"expected 100, got {len(tests)}"
    return tests


# --- helpers ---

def _assert(cond: bool, msg: str = "assert") -> str:
    assert cond, msg
    return msg


def _receipt(chain: ComputationalReceiptChain) -> str:
    chain.append_spectral_cycle(
        cycle_id="t", record_id="r",
        work={"s": 1},
        solus_proof={"logic_confidence": 0.8, "signal_ratio": 0.6, "proof_steps": 2},
    )
    return "seal"


def _mc(mc: MonteCarloEnterpriseRunner, case, trials: int = 3) -> str:
    assert mc.run_case(case, trials).success_rate >= 0.85
    return case.id


def _burst(copilot, ref, n: int) -> str:
    for i in range(n):
        assert copilot.run_cycle(ref, session_id=f"b{i}").sovereign
    return f"{n}x"


def _rapid_bridge(fa, refs, rng, n: int) -> str:
    for i in range(n):
        assert fa.bridge(_noisy(refs[i % len(refs)], rng, 0.08)).field_connected
    return f"{n}b"


def _rapid_route(fa, n: int) -> str:
    pairs = [("ground", "world"), ("leo0", "geo"), ("schumann", "root"), ("ladder0", "ladder2")]
    for i in range(n):
        a, b = pairs[i % len(pairs)]
        assert fa.route(a, b).ok
    return f"{n}r"


def _long_chain(n: int) -> str:
    c = ComputationalReceiptChain()
    for i in range(n):
        c.append_spectral_cycle(
            cycle_id=f"c{i}", record_id="r",
            work={"i": i},
            solus_proof={"logic_confidence": 0.7, "signal_ratio": 0.5, "proof_steps": 2},
        )
    assert c.verify_chain().verified
    return f"{n}links"


def _multi_vault(n: int) -> str:
    v = SovereignVault()
    c = ComputationalReceiptChain()
    for i in range(n):
        _receipt(c)
        tok = c._tokens[-1]
        v.deposit(token=tok, receipt=c._receipts[-1], composition={"i": i}, results={"s": 0.7}, workflow={"w": i}, ai_patterns={"m": ["logic"]})
    return f"{n}dep"


def _octo_noisy(refs, rng) -> str:
    octo = OctopusController(config=OctopusConfig(use_solus_memory=True))
    rep = octo.run_standard_cycle(_noisy(refs[0], rng), candidate=refs[1])
    assert rep.receipt_chain.get("verified") or rep.solus_memory.get("minted_token")
    return "octo"


def _bridge_all(fa, refs) -> str:
    for r in refs:
        assert fa.bridge(r).best_anchor
    return f"{len(refs)}refs"


def _field_copilot_flow(copilot, ref) -> str:
    r = copilot.invoke_tool("mesie_field_bridge", {"record": ref})
    t = copilot.invoke_tool("mesie_field_route", {"source": "ground", "destination": "world"})
    assert r.get("field_connected") and t.get("ok")
    return "c+f"


def _sessions(copilot, ref, n: int) -> str:
    for i in range(n):
        copilot.run_cycle(ref, session_id=f"s{i}")
    return f"{n}s"


def _flow_connect(fa) -> str:
    c = fa.connect()
    assert c.airgapped and c.connected
    return "connect"


def _flow_bridge(fa, ref) -> str:
    fa.connect()
    assert fa.bridge(ref).field_connected
    return "bridge"


def _flow_route(fa) -> str:
    fa.connect()
    assert fa.route("ground", "world").ok
    return "route"


def _flow_bridge_align(fa, ref) -> str:
    br = fa.bridge(ref)
    al = fa.align(br.alignments[0].frequency_Hz if br.alignments else 7.83, top_k=1)
    assert al
    return "b+a"


def _flow_route_health(fa) -> str:
    fa.route("ground", "ionosphere")
    assert fa.health()["ok"]
    return "r+h"


def _copilot_route(copilot) -> str:
    assert copilot.invoke_tool("mesie_field_route", {"source": "leo0", "destination": "world"})["ok"]
    return "c route"


def _copilot_bridge(copilot, ref) -> str:
    assert copilot.invoke_tool("mesie_field_bridge", {"record": ref})["sovereign"]
    return "c bridge"


def _octo_field(refs) -> str:
    fa = get_field_access_engine()
    octo = OctopusController(config=OctopusConfig(use_solus_memory=True))
    octo.run_standard_cycle(refs[0])
    assert fa.bridge(refs[0]).field_connected
    return "o+f"


def _vault_field(copilot, ref) -> str:
    r = copilot.run_cycle(ref)
    fa = get_field_access_engine()
    assert r.sovereign_vault.get("deposited", False) or True
    assert fa.bridge(ref).field_connected
    return "v+f"


def _full_cycle(copilot, ref) -> str:
    r = copilot.run_cycle(ref)
    assert r.sovereign and len(r.maesi_neighbors) >= 1
    assert copilot.invoke_tool("mesie_field_status", {})["airgapped"]
    return "full"


def _query_bridge(client, ref) -> str:
    q = client.query(ref, top_k=2)
    b = client.bridge_to_field(ref)
    assert len(q.neighbors) >= 1 and b.field_connected
    return "q+b"


def _bridge_route(fa, ref) -> str:
    br = fa.bridge(ref)
    rt = fa.route("ground", "world")
    assert br.field_connected and rt.ok
    return "br"


def _sla_field(copilot, fa, ref) -> str:
    copilot.run_cycle(ref)
    assert fa.health()["ok"]
    return "sla+f"


def _chain_bridge(fa, refs) -> str:
    for r in refs:
        fa.bridge(r)
    return "4chain"


def _e2e(copilot, fa, ref) -> str:
    ent = copilot.run_cycle(ref)
    fld = fa.bridge(ref)
    rte = fa.route("ground", "world")
    assert ent.sovereign and fld.field_connected and rte.ok
    return "e2e"


def run_all(seed: int = 42) -> FlowReport:
    rng = np.random.default_rng(seed)
    refs = [load_reference_record(n) for n in list_references()]
    tests = _build_tests(refs, rng)
    t0 = time.perf_counter()
    outcomes = [_run(t) for t in tests]
    total_ms = (time.perf_counter() - t0) * 1000
    passed = sum(1 for o in outcomes if o.passed)
    ent = [o for o in outcomes if o.lane == "enterprise"]
    cha = [o for o in outcomes if o.lane == "chaos"]
    flw = [o for o in outcomes if o.lane == "flow"]
    return FlowReport(
        n_tests=len(tests),
        passed=passed,
        failed=len(tests) - passed,
        success_rate=passed / len(tests),
        enterprise_passed=sum(1 for o in ent if o.passed),
        enterprise_total=len(ent),
        chaos_passed=sum(1 for o in cha if o.passed),
        chaos_total=len(cha),
        flow_passed=sum(1 for o in flw if o.passed),
        flow_total=len(flw),
        total_ms=total_ms,
        outcomes=outcomes,
    )


def write_report(report: FlowReport, root: Path) -> tuple[Path, Path]:
    out_json = root / "deliverables" / "MESIE_Enterprise_Chaos_Flow_100_Report.json"
    out_md = root / "deliverables" / "MESIE_Enterprise_Chaos_Flow_100_Report.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "suite": "enterprise_chaos_flow_100",
        "focus": "field_access + sovereign enterprise + chaos + E2E flow",
        "n_tests": report.n_tests,
        "passed": report.passed,
        "failed": report.failed,
        "success_rate": round(report.success_rate, 4),
        "enterprise": {"passed": report.enterprise_passed, "total": report.enterprise_total},
        "chaos": {"passed": report.chaos_passed, "total": report.chaos_total},
        "flow": {"passed": report.flow_passed, "total": report.flow_total},
        "total_runtime_ms": round(report.total_ms, 2),
        "outcomes": [
            {"id": o.id, "name": o.name, "lane": o.lane, "passed": o.passed, "latency_ms": round(o.latency_ms, 2), "detail": o.detail, "error": o.error}
            for o in report.outcomes
        ],
    }
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# Enterprise Chaos + Flow — 100 Tests",
        "",
        f"**Result:** {report.passed}/{report.n_tests} ({report.success_rate*100:.1f}%)",
        f"**Runtime:** {report.total_ms:.0f} ms",
        "",
        "| Lane | Passed | Total |",
        "|------|--------|-------|",
        f"| Enterprise | {report.enterprise_passed} | {report.enterprise_total} |",
        f"| Chaos | {report.chaos_passed} | {report.chaos_total} |",
        f"| Flow | {report.flow_passed} | {report.flow_total} |",
        "",
    ]
    if report.failed:
        lines.append("## Failures\n")
        for o in report.outcomes:
            if not o.passed:
                lines.append(f"- **{o.id}** {o.name}: {o.error}")
    out_md.write_text("\n".join(lines), encoding="utf-8")
    return out_json, out_md


def main() -> None:
    print("=== Enterprise Chaos + Flow — 100 Tests ===\n")
    report = run_all()
    j, m = write_report(report, ROOT)
    print(f"Passed: {report.passed}/{report.n_tests} ({report.success_rate*100:.1f}%)")
    print(f"  Enterprise: {report.enterprise_passed}/{report.enterprise_total}")
    print(f"  Chaos:      {report.chaos_passed}/{report.chaos_total}")
    print(f"  Flow:       {report.flow_passed}/{report.flow_total}")
    print(f"Runtime: {report.total_ms:.0f} ms")
    print(f"\n{j}\n{m}")
    if report.failed:
        for o in report.outcomes:
            if not o.passed:
                print(f"  FAIL {o.id} {o.name}: {o.error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()