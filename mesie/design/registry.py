"""Design Reality Ecosystem — 10 cores × 20 paradigms = 200 intelligence agents."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.design.languages import CANONICAL_PROTOCOL_COUNT, extensions_for_core
from mesie.version_info import MESIE_VERSION

ROOT = Path(__file__).resolve().parents[2]
DESIGN_ROOT = ROOT / "mesie" / "design"
PROTOCOL = "MESIE-DESIGN-REALITY-ECOSYSTEM/1.0"

AGENT_ROLES = ("orchestrator", "worker", "helper", "executor")


@dataclass(frozen=True)
class DesignParadigm:
    paradigm_id: str
    name: str
    stack: str
    latin_agent: str
    role: str
    mesie_engine: str
    language: str = ""


@dataclass(frozen=True)
class DesignCore:
    core_id: str
    latin_name: str
    english_title: str
    reality_class: str
    paradigms: tuple[DesignParadigm, ...]
    protocols: tuple[str, ...]
    template_count: int
    library_path: str


def _p(pid: str, name: str, stack: str, latin: str, role: str, engine: str, language: str = "") -> DesignParadigm:
    return DesignParadigm(pid, name, stack, latin, role, engine, language or stack)


def _build_cores() -> List[DesignCore]:
    cores_spec = [
        (
            "core_spectralis",
            "Core Spectralis",
            "Web Foundation Intelligence",
            "web_reality",
            ("P16", "P05", "P20", "P25"),
            [
                ("html_semantic", "HTML5 Semantic", "html", "Agent Structura Semanticus", "orchestrator", "validation"),
                ("css_cascade", "CSS Cascade", "css", "Agent Stylus Harmonicus", "worker", "generation"),
                ("js_esnext", "JavaScript ESNext", "javascript", "Agent Scriptum Vivus", "executor", "polyglot"),
                ("ts_strict", "TypeScript Strict", "typescript", "Agent Typus Formalis", "helper", "logic"),
                ("react_concurrent", "React Concurrent", "react", "Agent Componentia Fluxus", "worker", "workflow"),
                ("vue_compose", "Vue Composition", "vue", "Agent Reactivus Componens", "worker", "workflow"),
                ("svelte_compile", "Svelte Compile", "svelte", "Agent Compiler Minimus", "helper", "generation"),
                ("astro_islands", "Astro Islands", "astro", "Agent Insula Statica", "helper", "polyglot"),
                ("web_components", "Web Components", "wc", "Agent Shadow Domus", "executor", "embedding"),
                ("pwa_shell", "PWA App Shell", "pwa", "Agent Shell Mobilicus", "orchestrator", "control"),
            ],
        ),
        (
            "core_geometrica",
            "Core Geometrica",
            "3D Spatial Reality Intelligence",
            "unreal_class_web",
            ("P21", "P22", "P23", "P24", "P41"),
            [
                ("threejs_webgl", "Three.js WebGL", "threejs", "Agent Geometria Triangula", "orchestrator", "movement"),
                ("babylon_pbr", "Babylon.js PBR", "babylon", "Agent Babylon Spectralis", "worker", "generation"),
                ("webgpu_compute", "WebGPU Compute", "webgpu", "Agent GPU Computantis", "executor", "intelligence"),
                ("gltf_pipeline", "glTF 2.0 Pipeline", "gltf", "Agent Formatus Interoperabilis", "helper", "validation"),
                ("shader_glsl", "GLSL Shaders", "glsl", "Agent Shader Harmonicus", "worker", "fingerprint"),
                ("instanced_mesh", "Instanced Mesh", "instancing", "Agent Multitudo Mesh", "helper", "matching"),
                ("scene_graph", "Scene Graph AGI", "scene_graph", "Agent Graphus Scaenae", "orchestrator", "workflow"),
                ("camera_orbit", "Orbital Camera", "camera", "Agent Camera Circumitus", "helper", "control"),
                ("physics_rapier", "Rapier Physics", "physics", "Agent Physica Collisio", "executor", "movement"),
                ("spectral_mesh", "Spectral Mesh φ", "spectral_mesh", "Agent Mesh Spectrorum", "orchestrator", "embedding"),
            ],
        ),
        (
            "core_materialis",
            "Core Materialis",
            "Design System & Token Intelligence",
            "material_reality",
            ("P25", "P05", "P18"),
            [
                ("design_tokens", "Design Tokens", "tokens", "Agent Token Phi", "orchestrator", "validation"),
                ("tailwind_utility", "Tailwind Utility", "tailwind", "Agent Classis Utilitas", "worker", "generation"),
                ("css_variables", "CSS Custom Properties", "css_vars", "Agent Variabilis Cascada", "helper", "embedding"),
                ("styled_components", "Styled Components", "styled", "Agent Stylus Inyectus", "worker", "polyglot"),
                ("emotion_css", "Emotion CSS-in-JS", "emotion", "Agent Emotio Stylus", "helper", "generation"),
                ("figma_tokens", "Figma Tokens", "figma", "Agent Figura Harmonica", "helper", "workflow"),
                ("dark_mode_phi", "Dark Mode φ", "dark", "Agent Noctis Phi", "executor", "control"),
                ("typography_scale", "Typography Scale", "type", "Agent Typographia Modulis", "worker", "intelligence"),
                ("icon_spectral", "Spectral Icon Set", "icons", "Agent Iconographia", "helper", "fingerprint"),
                ("mesie_css", "MESIE mesie.css", "mesie_css", "Agent Medina Stylus", "orchestrator", "validation"),
            ],
        ),
        (
            "core_kinetica",
            "Core Kinetica",
            "Motion & Temporal Intelligence",
            "kinetic_reality",
            ("P26", "P08"),
            [
                ("gsap_timeline", "GSAP Timeline", "gsap", "Agent Tempus Linealis", "orchestrator", "workflow"),
                ("framer_motion", "Framer Motion", "framer", "Agent Motus Fluidus", "worker", "movement"),
                ("lottie_vector", "Lottie Vector", "lottie", "Agent Animatio Vectoris", "helper", "generation"),
                ("css_spring", "CSS Spring Physics", "spring", "Agent Elasticus Phi", "helper", "control"),
                ("scroll_trigger", "ScrollTrigger", "scroll", "Agent Scroll Observator", "executor", "intelligence"),
                ("page_transition", "Page Transitions", "transition", "Agent Transitus Paginae", "worker", "workflow"),
                ("micro_interaction", "Micro-interactions", "micro", "Agent Parvus Motus", "helper", "matching"),
                ("phi_easing", "φ-Harmonic Easing", "easing", "Agent Easing Aureus", "orchestrator", "logic"),
                ("motion_reduce", "Reduced Motion A11y", "a11y_motion", "Agent Accessibilitas", "helper", "validation"),
                ("timeline_receipt", "Timeline Receipt Chain", "receipt", "Agent Chronologia Sigilli", "executor", "workflow"),
            ],
        ),
        (
            "core_spatialis",
            "Core Spatialis",
            "XR & Spatial UI Intelligence",
            "spatial_reality",
            ("P27", "P24"),
            [
                ("webxr_immersive", "WebXR Immersive", "webxr", "Agent Immersio Spatialis", "orchestrator", "control"),
                ("ar_overlay", "AR Overlay", "ar", "Agent Superpositio Realis", "worker", "intelligence"),
                ("vr_locomotion", "VR Locomotion", "vr", "Agent Locomotio Virtualis", "executor", "movement"),
                ("hand_tracking", "Hand Tracking UI", "hands", "Agent Manus Digitalis", "helper", "fingerprint"),
                ("spatial_audio", "Spatial Audio", "spatial_audio", "Agent Sonus Spatialis", "helper", "embedding"),
                ("depth_ui", "Depth-Layered UI", "depth_ui", "Agent Stratum Profundum", "worker", "workflow"),
                ("globe_spectral", "Spectral Globe", "globe", "Agent Globus Mundi", "orchestrator", "matching"),
                ("point_cloud", "Point Cloud Viz", "pointcloud", "Agent Nubes Punctorum", "executor", "embedding"),
                ("6dof_widget", "6DOF Widgets", "6dof", "Agent Sex Libertatis", "helper", "control"),
                ("mesh_anchor", "Mesh Anchor", "anchor", "Agent Ancora Retis", "helper", "movement"),
            ],
        ),
        (
            "core_datavis",
            "Core Datavis",
            "Dashboard & Spectral Chart Intelligence",
            "data_reality",
            ("P28", "P07", "P38"),
            [
                ("d3_spectral", "D3 Spectral", "d3", "Agent Data Vis Spectrorum", "orchestrator", "embedding"),
                ("canvas_chart", "Canvas Charts", "canvas", "Agent Chart Canvas", "worker", "generation"),
                ("webgl_heatmap", "WebGL Heatmap", "heatmap", "Agent Calor Cartographia", "executor", "fingerprint"),
                ("ops_dashboard", "4K Ops Dashboard", "dashboard", "Agent Tabula Imperii", "orchestrator", "control"),
                ("realtime_stream", "Realtime SSE Stream", "sse", "Agent Fluxus Temporis", "worker", "workflow"),
                ("ann_visual", "ANN Match Visual", "ann_vis", "Agent Vicinitas Visualis", "helper", "matching"),
                ("benchmark_panel", "Benchmark Panel", "bench", "Agent Metrum Competitio", "helper", "validation"),
                ("enterprise_kpi", "Enterprise KPI", "kpi", "Agent Indicium Mercatus", "worker", "intelligence"),
                ("mesh_topology", "Mesh Topology Map", "topology", "Agent Topologia Retis", "executor", "movement"),
                ("phi_gauge", "φ Gauge Widget", "gauge", "Agent Metrum Aureum", "helper", "logic"),
            ],
        ),
        (
            "core_sonora",
            "Core Sonora",
            "Audio-Visual Coupled Intelligence",
            "sonora_reality",
            ("P29", "P08"),
            [
                ("webaudio_synth", "WebAudio Synth", "webaudio", "Agent Sonus Syntheticus", "orchestrator", "generation"),
                ("spectrogram", "Spectrogram Live", "spectrogram", "Agent Spectrogramma", "worker", "fingerprint"),
                ("midi_spectral", "MIDI Spectral Map", "midi", "Agent Nota Frequens", "helper", "embedding"),
                ("waveform_phi", "φ Waveform", "waveform", "Agent Unda Harmonica", "worker", "matching"),
                ("acoustic_meta", "Acoustic Metamaterial UI", "acoustic", "Agent Metamateria Soni", "helper", "intelligence"),
                ("sonification", "Data Sonification", "sonify", "Agent Data Sonora", "executor", "generation"),
                ("binaural", "Binaural Spatial", "binaural", "Agent Binauralis", "helper", "control"),
                ("rhythm_pulse", "Rhythm Pulse NOVA", "rhythm", "Agent Pulsus Novae", "worker", "workflow"),
                ("eq_spectrum", "EQ Spectrum Match", "eq", "Agent Aequilibrium", "helper", "matching"),
                ("audio_envelope", "Audio Envelope Seal", "envelope", "Agent Envelopum Soni", "orchestrator", "validation"),
            ],
        ),
        (
            "core_architectura",
            "Core Architectura",
            "Enterprise Micro-Frontend Intelligence",
            "enterprise_reality",
            ("P30", "P06", "P11"),
            [
                ("micro_frontend", "Micro-Frontend Bus", "mfe", "Agent Frontis Modularis", "orchestrator", "workflow"),
                ("module_federation", "Module Federation", "federation", "Agent Foederatio Modulorum", "worker", "polyglot"),
                ("bff_graphql", "BFF GraphQL", "graphql", "Agent Schema Intermedius", "helper", "validation"),
                ("edge_ssr", "Edge SSR", "ssr", "Agent Server Marginalis", "executor", "control"),
                ("islands_arch", "Islands Architecture", "islands", "Agent Archipelagus UI", "helper", "generation"),
                ("design_system_pkg", "Design System Package", "ds_pkg", "Agent Systema Materialis", "worker", "embedding"),
                ("tenant_shell", "Multi-Tenant Shell", "tenant", "Agent Colonia Tenant", "orchestrator", "control"),
                ("receipt_ui", "Receipt Chain UI", "receipt_ui", "Agent Catena Probationis", "helper", "workflow"),
                ("biz_automation", "Auto-AI Business Ops", "auto_biz", "Agent Negotium Autonomum", "orchestrator", "intelligence"),
                ("icp_bridge_ui", "ICP Bridge Console", "icp_ui", "Agent Pontus Sovereign", "executor", "polyglot"),
            ],
        ),
        (
            "core_narrativa",
            "Core Narrativa",
            "Scholarly & Latin Content Intelligence",
            "narrative_reality",
            ("P31", "P12", "P35"),
            [
                ("latin_paper", "Latin Paper Viewer", "paper", "Agent Scriptum Latinum", "orchestrator", "logic"),
                ("md_scholar", "Scholarly Markdown", "md", "Agent Markdown Doctoralis", "worker", "generation"),
                ("story_scroll", "Story Scroll", "scroll_story", "Agent Narratio Scroll", "helper", "intelligence"),
                ("theorem_block", "Theorem Block", "theorem", "Agent Theorema Visibile", "helper", "logic"),
                ("citation_graph", "Citation Graph", "citation", "Agent Citatio Retis", "executor", "matching"),
                ("release_notes", "Release Notes AGI", "release", "Agent Notae Editionis", "worker", "workflow"),
                ("docs_portal", "Docs Portal", "docs", "Agent Portal Documentorum", "orchestrator", "validation"),
                ("research_pack", "Research Pack UI", "research", "Agent Fasciculus Research", "helper", "embedding"),
                ("phi_typography", "φ Scholar Typography", "phi_type", "Agent Typus Doctoralis", "helper", "generation"),
                ("abstract_gen", "Abstract Generator", "abstract", "Agent Abstractum Solus", "executor", "intelligence"),
            ],
        ),
        (
            "core_realitas",
            "Core Realitas",
            "Reality Engine — Unreal-Class Showcase Intelligence",
            "ultimate_reality",
            ("P41", "P21", "P24", "P36"),
            [
                ("reality_scene", "Reality Scene Composer", "scene", "Agent Scaena Realitatis", "orchestrator", "workflow"),
                ("pbr_spectral", "Spectral PBR Materials", "pbr", "Agent Materia Physica", "worker", "embedding"),
                ("light_probe", "Light Probe φ", "light", "Agent Lux Harmonica", "helper", "fingerprint"),
                ("post_fx", "Post-Processing FX", "postfx", "Agent Post Processus", "executor", "generation"),
                ("cinematic_cam", "Cinematic Camera", "cine", "Agent Camera Cinematica", "worker", "control"),
                ("product_showcase", "Product Showcase 3D", "showcase", "Agent Showcase Producti", "orchestrator", "intelligence"),
                ("virtual_booth", "Virtual Trade Booth", "booth", "Agent Booth Mercatus", "helper", "movement"),
                ("live_metrics_3d", "Live Metrics 3D", "metrics3d", "Agent Metrum Tridimensionale", "worker", "matching"),
                ("mesh_soak_vis", "Mesh Soak Visualizer", "soak", "Agent Visualisatio Retis", "executor", "movement"),
                ("unreal_class", "Unreal-Class Lane", "unreal_lane", "Agent Realitas Ultima", "orchestrator", "polyglot"),
            ],
        ),
    ]

    cores: List[DesignCore] = []
    for spec in cores_spec:
        cid, latin, english, rclass, protos, paradigms_raw = spec
        base_paradigms = [_p(*row) for row in paradigms_raw]
        ext_rows = extensions_for_core(cid)
        ext_paradigms = [_p(*row) for row in ext_rows]
        paradigms = tuple(base_paradigms + ext_paradigms)
        cores.append(
            DesignCore(
                core_id=cid,
                latin_name=latin,
                english_title=english,
                reality_class=rclass,
                paradigms=paradigms,
                protocols=protos,
                template_count=20,
                library_path=f"mesie/design/cores/{cid}",
            )
        )
    return cores


DESIGN_CORES: List[DesignCore] = _build_cores()


def paradigm_count() -> int:
    return sum(len(c.paradigms) for c in DESIGN_CORES)


def core_by_id(core_id: str) -> Optional[DesignCore]:
    for c in DESIGN_CORES:
        if c.core_id == core_id:
            return c
    return None


def design_ecosystem_manifest() -> Dict[str, Any]:
    from mesie.design.protocols import protocol_bus_manifest

    return {
        "protocol": PROTOCOL,
        "mesie_version": MESIE_VERSION,
        "core_count": len(DESIGN_CORES),
        "paradigm_count": paradigm_count(),
        "paradigms_per_core": 20,
        "target_paradigms": 200,
        "canonical_protocol_count": CANONICAL_PROTOCOL_COUNT,
        "reality_protocol": "MESIE-REALITY-ENGINE-CORES/1.0",
        "agent_roles": list(AGENT_ROLES),
        "intelligence": "SOLUS + MESIE native — all agents route to mesie engines (zero third-party inference)",
        "reality_vision": "Unreal-class web reality showcase — video-game roots, enterprise products",
        "protocol_bus": protocol_bus_manifest(),
        "cores": [
            {
                "core_id": c.core_id,
                "latin_name": c.latin_name,
                "english_title": c.english_title,
                "reality_class": c.reality_class,
                "paradigm_count": len(c.paradigms),
                "protocols": list(c.protocols),
                "library_path": c.library_path,
                "processor": f"GET /processor/design/cores/{c.core_id}",
                "paradigms": [
                    {
                        "paradigm_id": p.paradigm_id,
                        "name": p.name,
                        "stack": p.stack,
                        "latin_agent": p.latin_agent,
                        "role": p.role,
                        "mesie_engine": p.mesie_engine,
                        "language": p.language,
                    }
                    for p in c.paradigms
                ],
            }
            for c in DESIGN_CORES
        ],
        "surfaces": {
            "reality_engine": "websites/reality-engine/index.html",
            "computing_family": "websites/computing-family/index.html",
            "enterprise_4k": "websites/enterprise-4k/index.html",
        },
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }