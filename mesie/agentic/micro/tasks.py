"""Production micro-agent tasks — 70 careers, real execution."""

from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from mesie.agentic.micro.brain import MiniBrain
from mesie.agentic.micro.career import CAREER_REGISTRY, MicroCareer
from mesie.agentic.micro.orchestrator import MicroOrchestrator

ROOT = Path(__file__).resolve().parents[3]
_HEARTBEAT = "NOVA production pulse — maintain, wire, design, execute."
TaskFn = Callable[[MiniBrain], Dict[str, Any]]


def _base(brain: MiniBrain, ok: bool, **extra: Any) -> Dict[str, Any]:
    spec = CAREER_REGISTRY[brain.career]
    return {
        "ok": ok,
        "career": brain.career.value,
        "team": spec.team.value,
        "mission": spec.mission,
        **extra,
    }


def _run_pytest(tests: List[str], *, timeout: int = 600) -> Dict[str, Any]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", *tests, "-q", "--tb=no"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return {"ok": r.returncode == 0, "detail": (r.stdout or r.stderr)[-400:]}


def _http_get(url: str, *, timeout: float = 5.0) -> Dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = resp.read().decode()[:600]
            return {"ok": True, "status": resp.status, "body": body}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}


def _deliverable(name: str) -> Dict[str, Any]:
    p = ROOT / "deliverables" / name
    if not p.is_file():
        return {"ok": False, "path": str(p), "exists": False}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return {"ok": True, "path": str(p), "keys": list(data.keys())[:8]}
    except Exception:
        return {"ok": p.stat().st_size > 0, "path": str(p), "bytes": p.stat().st_size}


def _sample_record() -> Dict[str, Any]:
    return {
        "id": f"nova-pulse-{int(time.time())}",
        "spectral": {"bands": [0.1, 0.3, 0.618, 0.9]},
        "meta": {"source": "nova-micro-org"},
    }


def _polyglot_arm(runtime: str) -> TaskFn:
    def _task(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.polyglot.contract import RuntimeId
        from mesie.polyglot.suite import AISVectorPolyglotSuite

        suite = AISVectorPolyglotSuite()
        health = suite.health()
        rt = health.runtimes.get(runtime, {})
        rec = _sample_record()
        embed = suite.embed(rec, runtime=RuntimeId(runtime))
        return _base(
            brain,
            rt.get("ok", False) and embed.ok,
            runtime=runtime,
            mode=rt.get("mode"),
            embed_ok=embed.ok,
            vector_indexed=health.vector_indexed,
        )

    return _task


def build_task_registry(micro: MicroOrchestrator, root: Path) -> Dict[MicroCareer, TaskFn]:
    """All 55 production tasks."""

    def linguist(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.nova.linguistic import LinguisticEngine

        ling = LinguisticEngine().analyze(_HEARTBEAT)
        return _base(brain, ling.coherence >= 0.5, coherence=round(ling.coherence, 4))

    def translator(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.nova.translator import TranslatorEngine

        trans = TranslatorEngine().translate(_HEARTBEAT)
        return _base(brain, bool(trans.fingerprint), fingerprint=trans.fingerprint[:16])

    def cognitive(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.nova.cognitive import AdaptiveCognitiveEngine

        cog = AdaptiveCognitiveEngine().adapt(_HEARTBEAT)
        return _base(brain, bool(cog.routes), domain=cog.domain, routes=cog.routes[:4])

    def embedder(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.embeddings.vectorizers import SpectralVectorizer

        vec = SpectralVectorizer().transform(_sample_record())
        dim = int(vec.shape[0]) if hasattr(vec, "shape") else len(vec)
        return _base(brain, dim > 0, dim=dim)

    def matcher(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.matching.matcher import SpectralMatcher

        m = SpectralMatcher()
        a, b = _sample_record(), {**_sample_record(), "id": "candidate"}
        try:
            result = m.match(a, b)
            return _base(brain, result.score >= 0, score=round(result.score, 4))
        except Exception as exc:
            return _base(brain, False, error=str(exc)[:120])

    def fingerprint_guard(brain: MiniBrain) -> Dict[str, Any]:
        idx = ROOT / "library" / "spectral_index.json"
        ok = idx.is_file()
        count = 0
        if ok:
            try:
                count = len(json.loads(idx.read_text(encoding="utf-8")))
            except Exception:
                count = 0
        return _base(brain, ok, index_entries=count)

    def retriever(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.tools.registry import tool_by_id

        tool = tool_by_id("rank")
        return _base(brain, tool is not None, tool=tool.id if tool else None)

    def salience_router(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.nova.cognitive import AdaptiveCognitiveEngine

        cog = AdaptiveCognitiveEngine().adapt("match and rank spectral retrieval release")
        return _base(brain, cog.domain in ("retrieval", "matching", "release", "general"), policy=cog.policy)

    def release_sentinel(brain: MiniBrain) -> Dict[str, Any]:
        rep = _run_pytest(["tests/test_novamini.py", "tests/test_nova_sphere.py"], timeout=300)
        return {**_base(brain, rep["ok"]), **rep}

    def version_auditor(brain: MiniBrain) -> Dict[str, Any]:
        import mesie
        from mesie import version_info as vi
        from mesie.sdk import __sdk_version__

        pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
        ok = mesie.__version__ == vi.MESIE_VERSION and vi.MESIE_VERSION in pyproject
        return _base(brain, ok, mesie=mesie.__version__, canonical=vi.MESIE_VERSION, sdk=__sdk_version__)

    def manifest_writer(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.surface.catalog import build_catalog

        cat = build_catalog(export=True)
        out = root / "deliverables" / "MEDINA_SURFACE_MANIFEST.json"
        counts = cat.to_dict()["counts"]
        return _base(brain, out.is_file(), systems=counts["systems"], deliverables=counts["deliverables"])

    def schema_validator(brain: MiniBrain) -> Dict[str, Any]:
        refs = root / "data" / "references"
        ok = refs.is_dir()
        n = len(list(refs.glob("*.json"))) if ok else 0
        return _base(brain, n > 0, reference_files=n)

    def readiness_gate(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.release.readiness_check import run_release_check

        rep = run_release_check(run_pytest=False)
        return _base(brain, rep.ready, checks=len(rep.checks), mesie=rep.mesie_version)

    def determinism_checker(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.core.config import GenerationConfig
        from mesie.generation.psd import generate_psd

        cfg = GenerationConfig(seed=42, n_points=64)
        a = generate_psd(cfg)
        b = generate_psd(cfg)
        return _base(brain, a.record_id == b.record_id, record_id=a.record_id)

    def satellite_watch(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.agentic.micro.organization import organization_status

        org = organization_status(micro)
        return _base(
            brain,
            org["size"] >= 50,
            size=org["size"],
            pulsing=org["pulsing"],
            satellites_active=org["satellites_active"],
        )

    def health_monitor(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.release.bootstrap import ensure_bootstrapped

        boot = ensure_bootstrapped(quiet=True)
        return _base(brain, boot.get("bootstrapped", False), config_dir=str(boot.get("config_dir", "")))

    def port_watch(brain: MiniBrain) -> Dict[str, Any]:
        ports = {
            "memory_desk": "http://127.0.0.1:8740/api/health",
            "surface": "http://127.0.0.1:8760/surface/status",
            "coding_lab": "http://127.0.0.1:8770/api/health",
            "processor": "http://127.0.0.1:8750/processor/status",
        }
        results = {k: _http_get(u)["ok"] for k, u in ports.items()}
        up = sum(1 for v in results.values() if v)
        return _base(brain, up >= 2, ports=results, up=up)

    def log_triage(brain: MiniBrain) -> Dict[str, Any]:
        lab_log = Path.home() / "Documents/Enterprise-OS-intelligence/medina-coding-lab/.lab/runs.jsonl"
        lines = 0
        if lab_log.is_file():
            lines = len(lab_log.read_text(encoding="utf-8").strip().splitlines())
        return _base(brain, True, lab_run_lines=lines)

    def benchmark_runner(brain: MiniBrain) -> Dict[str, Any]:
        r = subprocess.run(
            [sys.executable, "scripts/run_fast_compute_benchmark.py"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=120,
        )
        return _base(brain, r.returncode == 0, detail=(r.stdout or r.stderr)[-300:])

    def sla_watcher(brain: MiniBrain) -> Dict[str, Any]:
        rep = _deliverable("MAESI_SDK_Major_Benchmarks.json")
        wins = 0
        if rep.get("ok"):
            data = json.loads((ROOT / "deliverables/MAESI_SDK_Major_Benchmarks.json").read_text())
            wins = data.get("summary", {}).get("wins", 0)
        return _base(brain, rep.get("ok", False), wins=wins)

    def robotics_satellite(brain: MiniBrain) -> Dict[str, Any]:
        log = root / "deliverables" / "processor" / "robotics_satellite.jsonl"
        entries = []
        if log.is_file():
            for line in log.read_text(encoding="utf-8").strip().splitlines()[-3:]:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        last = entries[-1] if entries else {}
        out = (last.get("result") or {}).get("output") or {}
        lrc = (last.get("result") or {}).get("lrc") or {}
        return _base(
            brain,
            bool(out.get("threat_p50_ms")),
            cycle=last.get("cycle"),
            threat_p50_ms=out.get("threat_p50_ms"),
            fusion_dims=out.get("fusion_dims"),
            lrc_id=lrc.get("lrc_id"),
            total_cycles=sum(1 for _ in log.open(encoding="utf-8")) if log.is_file() else 0,
        )

    def schema_designer(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.tools.registry import tool_by_id

        return _base(brain, tool_by_id("validate") is not None, schema_levels="1-6")

    def api_contract_auditor(brain: MiniBrain) -> Dict[str, Any]:
        surface = _http_get("http://127.0.0.1:8760/surface/systems")
        lab = _http_get("http://127.0.0.1:8770/api/health")
        return _base(brain, surface["ok"] or lab["ok"], surface_ok=surface["ok"], lab_ok=lab["ok"])

    def surface_mapper(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.surface.catalog import build_catalog

        cat = build_catalog(export=False)
        return _base(brain, len(cat.systems) >= 8, systems=len(cat.systems), papers=len(cat.papers))

    def doc_synthesizer(brain: MiniBrain) -> Dict[str, Any]:
        papers = list((root / "docs" / "papers").glob("paper_*.md")) if (root / "docs/papers").is_dir() else []
        return _base(brain, len(papers) >= 1, paper_count=len(papers))

    def architecture_reviewer(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.engines.registry import build_default_registry

        reg = build_default_registry()
        names = sorted(reg.names())
        return _base(brain, len(names) >= 5, engines=names)

    def doctrine_curator(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.nova.linguistic import LinguisticEngine

        ling = LinguisticEngine().analyze("φ doctrine attractor sovereign Medina protocol")
        return _base(brain, ling.coherence >= 0.5, attractors=len(ling.attractors))

    def surface_bridge(brain: MiniBrain) -> Dict[str, Any]:
        rep = _http_get("http://127.0.0.1:8760/surface/status")
        return {**_base(brain, rep["ok"]), "endpoint": "/surface/status"}

    def mcp_wiring(brain: MiniBrain) -> Dict[str, Any]:
        mcp = Path.home() / "mcps" / "loom" / "tools"
        tools = list(mcp.glob("*.json")) if mcp.is_dir() else []
        return _base(brain, len(tools) >= 3, mcp_tools=len(tools))

    def repo_scanner(brain: MiniBrain) -> Dict[str, Any]:
        rep = _http_get("http://127.0.0.1:8770/api/repos")
        count = 0
        if rep["ok"]:
            try:
                count = json.loads(rep["body"]).get("count", 0)
            except Exception:
                pass
        return _base(brain, count >= 10, repos=count)

    def bus_router(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.engines.registry import build_default_registry
        from mesie.internal_api.bus import InternalBus

        bus = InternalBus()
        reg = build_default_registry()
        return _base(brain, bus is not None, engines=len(reg.names()))

    def loom_bridge(brain: MiniBrain) -> Dict[str, Any]:
        vault = Path.home() / ".medina"
        skills = list((Path.home() / ".grok" / "skills").glob("**/SKILL.md")) if (Path.home() / ".grok/skills").exists() else []
        return _base(brain, vault.is_dir(), vault_exists=vault.is_dir(), skill_files=len(skills))

    def coding_lab_bridge(brain: MiniBrain) -> Dict[str, Any]:
        rep = _http_get("http://127.0.0.1:8770/api/health")
        return {**_base(brain, rep["ok"]), "service": "coding-lab"}

    def memory_desk_bridge(brain: MiniBrain) -> Dict[str, Any]:
        rep = _http_get("http://127.0.0.1:8740/api/health")
        return {**_base(brain, rep["ok"]), "service": "memory-desk"}

    def processor_bridge(brain: MiniBrain) -> Dict[str, Any]:
        rep = _http_get("http://127.0.0.1:8750/processor/status")
        return {**_base(brain, rep["ok"]), "service": "processor"}

    def orbital_analyst(brain: MiniBrain) -> Dict[str, Any]:
        rep = _deliverable("MESIE_Multi_Domain_Suite_Report.md")
        orbital = (root / "scripts/orbital_edge_50d_report.json").is_file()
        return _base(brain, rep.get("ok", False) or orbital)

    def seismic_watch(brain: MiniBrain) -> Dict[str, Any]:
        data = root / "data" / "references"
        seismic = [p for p in data.glob("*.json") if "seismic" in p.name.lower()] if data.is_dir() else []
        return _base(brain, len(seismic) > 0, seismic_refs=len(seismic))

    def robotics_coord(brain: MiniBrain) -> Dict[str, Any]:
        rep = _deliverable("NeuroSwarmAI_Drone_Swarm_Report.json")
        return {**_base(brain, rep.get("ok", False)), **rep}

    def power_grid(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.tools.registry import tool_by_id

        return _base(brain, tool_by_id("domains") is not None, domain="power")

    def terrain_mapper(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.tools.registry import tool_by_id

        return _base(brain, tool_by_id("domains") is not None, domain="terrain")

    def enterprise_monte(brain: MiniBrain) -> Dict[str, Any]:
        rep = _deliverable("MESIE_Monte_Carlo_Enterprise_Report.md")
        return {**_base(brain, rep.get("ok", False)), **rep}

    def logic_prover_caretaker(brain: MiniBrain) -> Dict[str, Any]:
        rep = _deliverable("SOLUS_Math_Caretakers_Report.json")
        return {**_base(brain, rep.get("ok", False)), **rep}

    def pattern_forge_caretaker(brain: MiniBrain) -> Dict[str, Any]:
        rep = _deliverable("SOLUS_Math_Caretakers_Report.json")
        return {**_base(brain, rep.get("ok", False)), **rep}

    def emergence_watcher(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.tools.registry import tool_by_id

        return _base(brain, tool_by_id("solus-organism") is not None, layer="emergence")

    def adaptation_tuner(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.nova.cognitive import AdaptiveCognitiveEngine

        cog = AdaptiveCognitiveEngine().adapt("adapt policy for enterprise release")
        return _base(brain, cog.policy is not None, policy=cog.policy)

    def vault_curator(brain: MiniBrain) -> Dict[str, Any]:
        vault = Path.home() / ".medina"
        tiers = [p.name for p in vault.iterdir() if p.is_dir()] if vault.is_dir() else []
        return _base(brain, vault.is_dir(), tiers=tiers[:6])

    def receipt_chain(brain: MiniBrain) -> Dict[str, Any]:
        rep = _deliverable("Enterprise_AI_Suite_Report.json")
        return {**_base(brain, rep.get("ok", False)), **rep}

    def knowledge_indexer(brain: MiniBrain) -> Dict[str, Any]:
        try:
            from mesie.sdk import search_research

            hits = search_research("LSH spectral", 3)
            return _base(brain, len(hits) > 0, hits=len(hits))
        except Exception as exc:
            return _base(brain, False, error=str(exc)[:120])

    def sovereign_gate(brain: MiniBrain) -> Dict[str, Any]:
        rep = _deliverable("MESIE_Sovereign_Local_120_Report.md")
        return {**_base(brain, rep.get("ok", False)), **rep}

    def interior_datacenter(brain: MiniBrain) -> Dict[str, Any]:
        rep = _deliverable("MESIE_Interior_DataCenter_Manifest.json")
        return {**_base(brain, rep.get("ok", False)), **rep}

    def engine_registry_keeper(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.agentic.micro.foundations import engine_names

        names = engine_names()
        return _base(brain, len(names) >= 9, engines=names, count=len(names))

    def protocol_executor(brain: MiniBrain) -> Dict[str, Any]:
        import numpy as np
        from mesie.ai.intelligence_protocols import IntelligenceConfig, IntelligenceProtocol

        proto = IntelligenceProtocol(IntelligenceConfig())
        bands = _sample_record()["spectral"]["bands"]
        proto.observe(np.array(bands, dtype=float))
        return _base(brain, proto._observation_count > 0, protocol="intelligence", observations=proto._observation_count)

    def law_compiler(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.release.bootstrap import ensure_bootstrapped

        boot = ensure_bootstrapped(quiet=True)
        phi = 0.618033988749895
        return _base(brain, boot.get("bootstrapped", False), phi=phi, laws=["RECITAL", "DUAL_READ", "φ-DECAY"])

    def charter_keeper(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.agentic.micro.foundations import foundations_snapshot

        snap = foundations_snapshot()
        charter = root / "deliverables" / "nova" / "NOVA_RUNTIME_STATE.json"
        return _base(brain, snap["engine_count"] >= 9, charter_exists=charter.is_file(), tools=snap["tools"])

    def library_feeder(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.agentic.micro.foundations import library_stats
        from mesie.embeddings.vectorizers import SpectralVectorizer

        lib = library_stats()
        vec = SpectralVectorizer().transform(_sample_record())
        r = subprocess.run(
            [sys.executable, "scripts/embed_spectral_library.py"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=300,
        )
        index_path = root / "library" / "spectral_index.json"
        entry_count = 0
        embeds_per_sec = 0.0
        if index_path.is_file():
            try:
                idx = json.loads(index_path.read_text(encoding="utf-8"))
                entry_count = int(idx.get("entry_count", 0))
                embeds_per_sec = float(idx.get("embeds_per_second", 0))
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                pass
        return _base(
            brain,
            r.returncode == 0 and entry_count > 0,
            library_mb=lib.get("mb"),
            embed_dim=len(vec),
            files=lib.get("files"),
            index_entries=entry_count,
            embeds_per_sec=embeds_per_sec,
            detail=(r.stdout or r.stderr)[-300:],
        )

    def signal_router(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.signals import UniversalSignalReader

        reader = UniversalSignalReader()
        text_sig = reader.read(_HEARTBEAT, hint="text")
        event_sig = reader.read({"event": "nova_pulse", "status": "active", "careers": 70}, hint="json")
        numeric_sig = reader.read([0.1, 0.618, 0.9], hint="numeric")
        ok = all(s.fingerprint for s in (text_sig, event_sig, numeric_sig))
        return _base(
            brain,
            ok,
            unified=True,
            modalities=[text_sig.modality.value, event_sig.modality.value, numeric_sig.modality.value],
        )

    def physics_foundation(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.agentic.micro.foundations import physics_modules

        mods = physics_modules()
        ok = len(mods) >= 1
        tiers = 0
        if ok:
            from mesie.edge.hz_ladder import HzLadder

            tiers = len(HzLadder().tiers)
        return _base(brain, ok, physics_modules=mods, hz_tiers=tiers)

    def edge_protocol_ops(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.processor.mesh_protocol import VirtualProcessorMeshNode
        from mesie.tools.registry import tool_by_id

        node = VirtualProcessorMeshNode()
        pulse = node.pulse()
        node.stop()
        return _base(
            brain,
            tool_by_id("field-route") is not None and pulse.ok,
            edge=True,
            vp_mesh=pulse.peers_seen,
            ota_rx=pulse.ota_frames_received,
        )

    def octopus_controller(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.tools.registry import tool_by_id

        return _base(brain, tool_by_id("octopus") is not None, arms=8)

    def workflow_orchestrator(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.engines.registry import build_default_registry
        from mesie.internal_api.bus import InternalBus

        reg = build_default_registry(InternalBus())
        return _base(brain, "workflow" in reg.names(), workflow_registered=True)

    def domain_signal_hub(brain: MiniBrain) -> Dict[str, Any]:
        from data import list_references, load_reference
        from mesie.tools.registry import tool_by_id

        domains = {"terrain", "seismic", "orbital", "power", "robotics", "defense", "biomedical", "rf", "geomagnetic"}
        for name in list_references():
            try:
                d = load_reference(name).get("domain")
                if d:
                    domains.add(str(d))
            except (FileNotFoundError, json.JSONDecodeError, OSError):
                continue
        return _base(brain, tool_by_id("domains") is not None, domains=sorted(domains))

    def training_corpus_curator(brain: MiniBrain) -> Dict[str, Any]:
        from data import list_benchmarks, list_references, load_reference
        from mesie.agentic.micro.foundations import library_stats

        lib = library_stats()
        refs = list_references()
        benches = list_benchmarks()
        domains: List[str] = []
        for name in refs:
            try:
                d = load_reference(name).get("domain")
                if d:
                    domains.append(str(d))
            except (FileNotFoundError, json.JSONDecodeError, OSError):
                continue
        index_path = root / "library" / "spectral_index.json"
        indexed = 0
        if index_path.is_file():
            try:
                indexed = int(json.loads(index_path.read_text(encoding="utf-8")).get("entry_count", 0))
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                pass
        return _base(
            brain,
            len(refs) > 0 and lib.get("files", 0) > 100,
            references=len(refs),
            benchmarks=len(benches),
            library_files=lib.get("files"),
            indexed=indexed,
            domains=sorted(set(domains)),
        )

    def showcase_broadcaster(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.agentic.micro.showcase import run_showcase

        rep = run_showcase(export=True, quick=True)
        return _base(brain, rep.get("ok", False), showcase=rep.get("path"))

    def devkit_packager(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.processor.release import export_devkit, package_devkit_zip

        json_path = export_devkit()
        zip_path = package_devkit_zip()
        return _base(brain, zip_path.is_file(), devkit=str(json_path), zip=str(zip_path))

    def processor_release_gate(brain: MiniBrain) -> Dict[str, Any]:
        from mesie.processor.official_pack import build_official_dossier
        from mesie.processor.release import run_processor_release

        rep = run_processor_release(export=True)
        dossier = build_official_dossier(run_tests=True, quick=True)
        return _base(
            brain,
            rep.ready and dossier.get("commercial_ready", False),
            processor_version=rep.processor_version,
            commercial_ready=dossier.get("commercial_ready"),
            pass_rate=dossier.get("pass_rate"),
        )

    return {
        MicroCareer.LINGUIST: linguist,
        MicroCareer.TRANSLATOR: translator,
        MicroCareer.COGNITIVE: cognitive,
        MicroCareer.EMBEDDER: embedder,
        MicroCareer.MATCHER: matcher,
        MicroCareer.FINGERPRINT_GUARD: fingerprint_guard,
        MicroCareer.RETRIEVER: retriever,
        MicroCareer.SALIENCE_ROUTER: salience_router,
        MicroCareer.RELEASE_SENTINEL: release_sentinel,
        MicroCareer.VERSION_AUDITOR: version_auditor,
        MicroCareer.MANIFEST_WRITER: manifest_writer,
        MicroCareer.SCHEMA_VALIDATOR: schema_validator,
        MicroCareer.READINESS_GATE: readiness_gate,
        MicroCareer.DETERMINISM_CHECKER: determinism_checker,
        MicroCareer.SATELLITE_WATCH: satellite_watch,
        MicroCareer.HEALTH_MONITOR: health_monitor,
        MicroCareer.PORT_WATCH: port_watch,
        MicroCareer.LOG_TRIAGE: log_triage,
        MicroCareer.BENCHMARK_RUNNER: benchmark_runner,
        MicroCareer.SLA_WATCHER: sla_watcher,
        MicroCareer.ROBOTICS_SATELLITE: robotics_satellite,
        MicroCareer.SCHEMA_DESIGNER: schema_designer,
        MicroCareer.API_CONTRACT_AUDITOR: api_contract_auditor,
        MicroCareer.SURFACE_MAPPER: surface_mapper,
        MicroCareer.DOC_SYNTHESIZER: doc_synthesizer,
        MicroCareer.ARCHITECTURE_REVIEWER: architecture_reviewer,
        MicroCareer.DOCTRINE_CURATOR: doctrine_curator,
        MicroCareer.SURFACE_BRIDGE: surface_bridge,
        MicroCareer.MCP_WIRING: mcp_wiring,
        MicroCareer.REPO_SCANNER: repo_scanner,
        MicroCareer.BUS_ROUTER: bus_router,
        MicroCareer.LOOM_BRIDGE: loom_bridge,
        MicroCareer.CODING_LAB_BRIDGE: coding_lab_bridge,
        MicroCareer.MEMORY_DESK_BRIDGE: memory_desk_bridge,
        MicroCareer.PROCESSOR_BRIDGE: processor_bridge,
        MicroCareer.PYTHON_ARM: _polyglot_arm("python"),
        MicroCareer.RUST_ARM: _polyglot_arm("rust"),
        MicroCareer.JULIA_ARM: _polyglot_arm("julia"),
        MicroCareer.TYPESCRIPT_ARM: _polyglot_arm("typescript"),
        MicroCareer.MOTOKO_ARM: _polyglot_arm("motoko"),
        MicroCareer.ORBITAL_ANALYST: orbital_analyst,
        MicroCareer.SEISMIC_WATCH: seismic_watch,
        MicroCareer.ROBOTICS_COORD: robotics_coord,
        MicroCareer.POWER_GRID: power_grid,
        MicroCareer.TERRAIN_MAPPER: terrain_mapper,
        MicroCareer.ENTERPRISE_MONTE: enterprise_monte,
        MicroCareer.LOGIC_PROVER_CARETAKER: logic_prover_caretaker,
        MicroCareer.PATTERN_FORGE_CARETAKER: pattern_forge_caretaker,
        MicroCareer.EMERGENCE_WATCHER: emergence_watcher,
        MicroCareer.ADAPTATION_TUNER: adaptation_tuner,
        MicroCareer.VAULT_CURATOR: vault_curator,
        MicroCareer.RECEIPT_CHAIN: receipt_chain,
        MicroCareer.KNOWLEDGE_INDEXER: knowledge_indexer,
        MicroCareer.SOVEREIGN_GATE: sovereign_gate,
        MicroCareer.INTERIOR_DATACENTER: interior_datacenter,
        MicroCareer.ENGINE_REGISTRY_KEEPER: engine_registry_keeper,
        MicroCareer.PROTOCOL_EXECUTOR: protocol_executor,
        MicroCareer.LAW_COMPILER: law_compiler,
        MicroCareer.CHARTER_KEEPER: charter_keeper,
        MicroCareer.LIBRARY_FEEDER: library_feeder,
        MicroCareer.SIGNAL_ROUTER: signal_router,
        MicroCareer.PHYSICS_FOUNDATION: physics_foundation,
        MicroCareer.EDGE_PROTOCOL_OPS: edge_protocol_ops,
        MicroCareer.OCTOPUS_CONTROLLER: octopus_controller,
        MicroCareer.WORKFLOW_ORCHESTRATOR: workflow_orchestrator,
        MicroCareer.DOMAIN_SIGNAL_HUB: domain_signal_hub,
        MicroCareer.TRAINING_CORPUS_CURATOR: training_corpus_curator,
        MicroCareer.SHOWCASE_BROADCASTER: showcase_broadcaster,
        MicroCareer.DEVKIT_PACKAGER: devkit_packager,
        MicroCareer.PROCESSOR_RELEASE_GATE: processor_release_gate,
    }


def register_production_tasks(
    micro: MicroOrchestrator,
    *,
    mesie_root: Optional[Path] = None,
) -> None:
    root = mesie_root or ROOT
    for career, fn in build_task_registry(micro, root).items():
        micro.register_task(career, fn)