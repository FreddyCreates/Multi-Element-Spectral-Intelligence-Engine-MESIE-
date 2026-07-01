# Production Readiness Runbook

Quick commands for the `trust/production_readiness` bundle on branch `trust/production-readiness`.

## Health check

```bash
python scripts/run_trust_bundle_check.py
```

Validates `MANIFEST.json` paths and runs core pytest gate.

## Deliverable safety

```bash
python scripts/synthesize_deliverable_runs.py
```

Preserves partial vs full run snapshots under `*/runs/`; writes synthesis to `trust/production_readiness/synthesis/`.

## Processor platform

```bash
.\Start-VirtualProcessor.ps1
# or
python -m mesie.processor --serve
```

| Endpoint | Purpose |
|----------|---------|
| `GET /processor/chips` | Virtual chip SKU catalog |
| `POST /processor/virtual-chip` | Certify chip by `chip_id` |
| `POST /processor/read-signal` | Universal signal ingest |
| `POST /processor/mesh/pulse` | VP mesh gossip round |

MCP shim (`mesie-processor`): `processor_list_chips`, `processor_virtual_chip`, `processor_read_signal`, `processor_mesh_pulse`.

## NOVA runtime

```powershell
.\Start-NovaRuntime.ps1
```

## Compute fabric (separate deliverable tree)

```bash
python scripts/run_compute_fabric_suite.py
```

Artifacts: `deliverables/virtual_silicon/` (not under this trust folder).

## Git hygiene

Never commit: `.processor_vault/`, `.novamini_vault/`, `library/mesh_peers/vp_nodes/`, runtime `*.jsonl` feeds, deploy logs.
