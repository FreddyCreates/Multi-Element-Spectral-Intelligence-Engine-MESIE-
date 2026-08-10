# Agent Harnesses and Ship Set

This document defines the two shippable harnesses, the operator control plane, runtime support boundaries, and release outputs.

## Harnesses

### 1) Python Core Harness

- Entry: `mesie.harnesses.PythonCoreHarness`
- Scope: local/CI execution over the in-process MESIE core
- Wraps:
  - `GhostAgent` / `AgentSpawner` through `CoreEngine.spawn_ghost`
  - `WorkflowEngine` through `CoreEngine.dispatch("workflow", ...)`
- Provides:
  - profile-based runtime sizing (`local`, `dev`, `prod`)
  - deterministic `health_check()`
  - deterministic `startup_validation()`
  - structured run reports with failure category

### 2) Edge API Harness

- Entry: `mesie.harnesses.EdgeAPIHarness`
- Scope: remote execution surface on Worker endpoints
- Routes:
  - `GET /health`
  - `POST /v1/validate`
  - `POST /v1/match`
- Provides:
  - profile-based edge timeouts
  - minimal API key handling (`Authorization` and `X-MESIE-Key`)
  - deterministic startup checks on route set
  - structured run reports with failure category

## Operator Control Plane

Single CLI surface:

```bash
python3 -m mesie.cli harness --mode local|edge|hybrid --operation health|startup --profile local|dev|prod
```

Optional edge flags:

- `--edge-url` (default: `http://127.0.0.1:8787`)
- `--edge-api-key`

Outputs one JSON report for automation and release gates.

## Runtime and OS Support Matrix

| Runtime Surface | Linux | macOS | Windows x64 | Windows ARM64 |
|---|---|---|---|---|
| Python Core Harness (`mesie`) | ✅ Primary (CI) | ✅ Supported | ✅ Supported | ✅ Supported |
| Cloudflare Worker local dev (`wrangler dev`) | ✅ Supported | ✅ Supported | ✅ Supported | ❌ Unsupported (deploy-only) |
| Cloudflare Worker deploy runtime | ✅ Via Cloudflare | ✅ Via Cloudflare | ✅ Via Cloudflare | ✅ Via Cloudflare |
| MESIE Desktop packaging (`electron-builder`) | ✅ Target | ✅ Target | ✅ Target | ⚠️ Not an explicit local Worker dev target |

## Release Gates

1. Python harness:
   - run targeted agentic/workflow tests
   - run harness tests
2. Edge harness:
   - verify `/health`, `/v1/validate`, `/v1/match`
3. Desktop packaging smoke:
   - run `mesie-desktop` build targets per OS in release pipeline

## Release Outputs

- Python package artifacts (`python3 -m build`)
- Worker deploy configuration and workflow (`workers/mesie-api/`, `.github/workflows/deploy-mesie-api.yml`)
- Desktop installer outputs (`mesie-desktop` `dist/`)
- Ship-set manifest: `deliverables/mesie_harness_ship_set.json`

## Ship Set Tagging Guidance

Use a release tag that includes only harness shipping surfaces and their support matrix, for example:

- `ship/harnesses-v0.4.0`

Tag after Python, edge, and desktop release gates pass.
