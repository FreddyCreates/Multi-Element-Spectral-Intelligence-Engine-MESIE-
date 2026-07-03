"""Canonical design languages — 20 runtimes per Reality Engine Core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

REALITY_PROTOCOL = "MESIE-REALITY-ENGINE-CORES/1.0"
CANONICAL_PROTOCOL_COUNT = 40


@dataclass(frozen=True)
class DesignLanguage:
    language_id: str
    display: str
    runtime: str  # maps to polyglot / native DSL / surface
    layer: str  # front | middle | back | bridge


# 20 canonical languages woven into every core (paradigm slots 11–20 use these bindings)
CANONICAL_LANGUAGES: Tuple[DesignLanguage, ...] = (
    DesignLanguage("python", "Python", "python", "back"),
    DesignLanguage("typescript", "TypeScript", "typescript", "front"),
    DesignLanguage("rust", "Rust", "rust", "back"),
    DesignLanguage("julia", "Julia", "julia", "middle"),
    DesignLanguage("haskell", "Haskell", "haskell", "middle"),
    DesignLanguage("motoko", "Motoko", "motoko", "back"),
    DesignLanguage("go", "Go", "go", "back"),
    DesignLanguage("kotlin", "Kotlin", "kotlin", "front"),
    DesignLanguage("swift", "Swift", "swift", "front"),
    DesignLanguage("wasm", "WebAssembly", "wasm", "bridge"),
    DesignLanguage("elixir", "Elixir", "elixir", "middle"),
    DesignLanguage("zig", "Zig", "zig", "back"),
    DesignLanguage("lua", "Lua", "lua", "middle"),
    DesignLanguage("solidity", "Solidity", "solidity", "back"),
    DesignLanguage("glsl", "GLSL", "glsl", "front"),
    DesignLanguage("graphql", "GraphQL", "graphql", "bridge"),
    DesignLanguage("sql", "SQL", "sql", "back"),
    DesignLanguage("markdown", "Markdown", "markdown", "front"),
    DesignLanguage("json_schema", "JSON Schema", "json_schema", "bridge"),
    DesignLanguage("mesie_dsl", "MESIE Native DSL", "mesie_dsl", "middle"),
)


def language_by_id(language_id: str) -> DesignLanguage | None:
    for lang in CANONICAL_LANGUAGES:
        if lang.language_id == language_id:
            return lang
    return None


def language_bindings_manifest() -> Dict[str, object]:
    return {
        "protocol": REALITY_PROTOCOL,
        "language_count": len(CANONICAL_LANGUAGES),
        "languages": [
            {
                "language_id": lang.language_id,
                "display": lang.display,
                "runtime": lang.runtime,
                "layer": lang.layer,
            }
            for lang in CANONICAL_LANGUAGES
        ],
    }


def extensions_for_core(core_id: str) -> List[Tuple[str, str, str, str, str, str, str]]:
    """Return 10 extension paradigm rows: (pid, name, stack, latin, role, engine, language)."""
    # Per-core extension stacks — language slot maps to CANONICAL_LANGUAGES[i]
    stacks_by_core: Dict[str, List[Tuple[str, str]]] = {
        "core_spectralis": [
            ("angular_signals", "Angular Signals", "angular"),
            ("next_app_router", "Next.js App Router", "next"),
            ("nuxt_hybrid", "Nuxt Hybrid", "nuxt"),
            ("remix_loader", "Remix Loaders", "remix"),
            ("qwik_resumable", "Qwik Resumable", "qwik"),
            ("lit_element", "Lit Web Components", "lit"),
            ("htmx_hypermedia", "HTMX Hypermedia", "htmx"),
            ("alpine_declarative", "Alpine Declarative", "alpine"),
            ("solidjs_fine", "Solid.js Fine-Grained", "solid"),
            ("ember_octane", "Ember Octane", "ember"),
        ],
        "core_geometrica": [
            ("playcanvas_engine", "PlayCanvas Engine", "playcanvas"),
            ("regl_pipeline", "regl Pipeline", "regl"),
            ("deckgl_layers", "deck.gl Layers", "deckgl"),
            ("cesium_globe", "Cesium Globe", "cesium"),
            ("potree_lidar", "Potree LiDAR", "potree"),
            ("vtkjs_volume", "VTK.js Volume", "vtk"),
            ("kepler_gl", "Kepler.gl", "kepler"),
            ("ogl_minimal", "OGL Minimal", "ogl"),
            ("model_viewer", "model-viewer", "model_viewer"),
            ("react_three_fiber", "React Three Fiber", "r3f"),
        ],
        "core_materialis": [
            ("sass_modules", "Sass Modules", "sass"),
            ("less_hierarchy", "Less Hierarchy", "less"),
            ("unocss_atomic", "UnoCSS Atomic", "unocss"),
            ("openprops", "Open Props", "openprops"),
            ("style_dictionary", "Style Dictionary", "style_dict"),
            ("chakra_system", "Chakra UI", "chakra"),
            ("mui_theme", "MUI Theme", "mui"),
            ("ant_design", "Ant Design", "antd"),
            ("theme_ui", "Theme UI", "theme_ui"),
            ("stitches_css", "Stitches CSS", "stitches"),
        ],
        "core_kinetica": [
            ("animejs_timeline", "anime.js", "anime"),
            ("motion_one", "Motion One", "motion_one"),
            ("theatrejs_studio", "Theatre.js", "theatre"),
            ("react_spring", "React Spring", "react_spring"),
            ("popmotion", "Popmotion", "popmotion"),
            ("waapi_native", "WAAPI Native", "waapi"),
            ("drei_helpers", "drei Helpers", "drei"),
            ("cinema4d_export", "C4D Export Lane", "c4d"),
            ("velocity_legacy", "Velocity.js", "velocity"),
            ("timeline_gsap_plugins", "GSAP Plugins", "gsap_plugins"),
        ],
        "core_spatialis": [
            ("aframe_scene", "A-Frame Scene", "aframe"),
            ("spark_ar_web", "Spark AR Web", "spark"),
            ("openxr_session", "OpenXR Session", "openxr"),
            ("8thwall_webar", "8th Wall WebAR", "8thwall"),
            ("hololens_web", "HoloLens Web", "hololens"),
            ("quest_browser", "Quest Browser", "quest"),
            ("niantic_lightship", "Lightship VPS", "lightship"),
            ("webvm_spatial", "WebVM Spatial", "webvm"),
            ("depth_mesh_anchor", "Depth Mesh Anchor", "depth_anchor"),
            ("hand_ui_gesture", "Hand UI Gesture", "gesture"),
        ],
        "core_datavis": [
            ("echarts_spectral", "ECharts Spectral", "echarts"),
            ("plotly_3d", "Plotly 3D", "plotly"),
            ("chartjs_canvas", "Chart.js", "chartjs"),
            ("vega_lite", "Vega-Lite", "vega"),
            ("observable_notebook", "Observable", "observable"),
            ("grafana_panel", "Grafana Panel", "grafana"),
            ("cytoscape_graph", "Cytoscape.js", "cytoscape"),
            ("sigmajs_network", "Sigma.js", "sigma"),
            ("superset_embed", "Superset Embed", "superset"),
            ("deck_stack", "deck.gl Stack", "deck_stack"),
        ],
        "core_sonora": [
            ("tonejs_synth", "Tone.js", "tone"),
            ("howler_spatial", "Howler.js", "howler"),
            ("p5_sound", "p5.sound", "p5_sound"),
            ("wavesurfer_ui", "WaveSurfer", "wavesurfer"),
            ("audioworklet_dsp", "AudioWorklet DSP", "worklet"),
            ("resonance_audio", "Resonance Audio", "resonance"),
            ("faust_web", "Faust Web", "faust"),
            ("csound_wasm", "Csound WASM", "csound"),
            ("supercollider_web", "SuperCollider Web", "scweb"),
            ("sonification_bus", "Sonification Bus", "sonify_bus"),
        ],
        "core_architectura": [
            ("single_spa", "single-spa", "single_spa"),
            ("qiankun_micro", "qiankun Micro", "qiankun"),
            ("nx_monorepo", "Nx Monorepo", "nx"),
            ("turborepo_cache", "Turborepo", "turbo"),
            ("storybook_isolate", "Storybook", "storybook"),
            ("chromatic_visual", "Chromatic", "chromatic"),
            ("cdk_stacks", "AWS CDK UI", "cdk"),
            ("k8s_dashboard", "K8s Dashboard", "k8s"),
            ("terraform_ui", "Terraform UI", "tf_ui"),
            ("lerna_publish", "Lerna Publish", "lerna"),
        ],
        "core_narrativa": [
            ("latex_pdf", "LaTeX PDF", "latex"),
            ("typst_compile", "Typst", "typst"),
            ("asciidoc_book", "AsciiDoc", "asciidoc"),
            ("docusaurus_site", "Docusaurus", "docusaurus"),
            ("vitepress_docs", "VitePress", "vitepress"),
            ("gitbook_portal", "GitBook", "gitbook"),
            ("notion_sync", "Notion Sync", "notion"),
            ("roam_graph", "Roam Graph", "roam"),
            ("muse_scholar", "Muse Scholar", "muse"),
            ("rst_sphinx", "Sphinx RST", "sphinx"),
        ],
        "core_realitas": [
            ("godot_web_export", "Godot Web Export", "godot"),
            ("unity_webgl", "Unity WebGL", "unity"),
            ("unreal_pixel_stream", "Unreal Pixel Streaming", "unreal"),
            ("blender_gltf", "Blender glTF", "blender"),
            ("nanite_proxy_web", "Nanite Proxy Web", "nanite"),
            ("lumen_gi_web", "Lumen GI Web", "lumen"),
            ("path_trace_wasm", "Path Trace WASM", "pathtrace"),
            ("gaussian_splat", "Gaussian Splat", "splat"),
            ("nerf_viewer", "NeRF Viewer", "nerf"),
            ("reality_composer_pro", "Reality Composer Pro", "rcp"),
        ],
    }
    stacks = stacks_by_core.get(core_id, [])
    roles = ("helper", "worker", "executor", "helper", "worker", "executor", "helper", "worker", "executor", "orchestrator")
    engines = ("polyglot", "generation", "workflow", "embedding", "matching", "control", "intelligence", "movement", "validation", "logic")
    rows: List[Tuple[str, str, str, str, str, str, str]] = []
    for i, (pid, name, stack) in enumerate(stacks):
        lang = CANONICAL_LANGUAGES[i % len(CANONICAL_LANGUAGES)]
        latin = f"Agent {name.split()[0]} Polyglotta"
        rows.append((pid, name, stack, latin, roles[i], engines[i], lang.language_id))
    return rows
