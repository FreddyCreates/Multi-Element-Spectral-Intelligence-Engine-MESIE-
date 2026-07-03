# Reality Engine Cores — Architecture

## Vision

Ten **Reality Engine Cores** are modular enterprises. Each core hosts **20 design-language intelligence agents** (200 total), **templates**, **libraries**, and **protocol bindings**. Intelligence sits in the **middle**; **front** surfaces render products; **back** compute proves and receipts every cycle.

This layer competes conceptually with Unreal Engine pipelines — not as a game engine binary, but as a **web-native, sovereign, AGI-routed showcase fabric** tied to MESIE processor `:8750`.

## Stack

| Layer | Responsibility | Key modules |
|-------|----------------|-------------|
| **Front** | HTML/CSS/JS/3D/XR surfaces | `websites/reality-engine/`, paradigm templates |
| **Middle** | Brief encode, orchestration, envelopes | `mesie/design/orchestrator.py`, `reality_engine.py` |
| **Back** | Polyglot, processor, receipts | `mesie/processor/`, `mesie/polyglot/`, `mesie/enterprise/` |

## Cores (10)

See `mesie/design/registry.py` — `core_spectralis` through `core_realitas`.

Per-core folder (`mesie/design/cores/{core_id}/`):

```
libraries/     agent_{paradigm_id}.py  → run_agent()
templates/     {paradigm_id}.template.json
engines/       manifest.json
protocols/     CORE_ENVELOPE.json, LANGUAGE_BINDINGS.json
```

## Languages (20 per core)

Canonical bindings in `mesie/design/languages.py`:

Python, TypeScript, Rust, Julia, Haskell, Motoko, Go, Kotlin, Swift, WASM, Elixir, Zig, Lua, Solidity, GLSL, GraphQL, SQL, Markdown, JSON Schema, MESIE DSL.

Paradigms 1–10: stack specialists (Three.js, React, GSAP, …).  
Paradigms 11–20: polyglot language agents per core extension set.

## Protocols (40+)

`mesie/design/protocols.py` — bus `P01`–`P42`.  
Canonical count: **40** (`CANONICAL_PROTOCOL_COUNT`).  
Reality-specific: `P16`–`P24`, `P41` (ecosystem, Three.js, WebGL, PBR, scene graph, unreal-class).

## HTTP API

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/processor/design` | Full ecosystem catalog |
| GET | `/processor/design/cores/{id}` | Core snapshot |
| POST | `/processor/design/cores/{id}/orchestrate` | Brief → all agents |
| POST | `/processor/design/cores/{id}/invoke` | Single paradigm agent |
| GET | `/processor/reality/status` | Reality Engine status |
| POST | `/processor/reality/invoke` | Reality envelope invoke |

## Federation

`EnterpriseFederationEnvelope` with `tool: "reality.invoke"` or `design.*` routes through `FederationOrchestrator` → `RealityEngine`.

## Bootstrap

```bash
python scripts/forge_design_cores.py
python scripts/run_reality_engine_suite.py
```

## Showcase

Open `websites/reality-engine/index.html` with processor on `:8750`.
