# Production Readiness Bundle

Wave-2 artifacts for `trust/production-readiness` — separate from the virtual silicon compute fabric (`deliverables/virtual_silicon/`).

## Contents

| Area | Location |
|------|----------|
| Deliverable run synthesis | `trust/production_readiness/synthesis/` |
| Versioning archives | `*/runs/` + `*/lineage/` under native AI and mission worlds |
| Virtual Processor platform | `mesie/processor/` extensions + `deliverables/processor/` |
| Universal signals | `mesie/signals/` |
| NOVA / MININOVA / NOVAMINI | `mesie/nova/`, `mesie/mininova/`, `mesie/novamini/` |
| Micro agentic runtime | `mesie/agentic/micro/` |

## Not in git

Runtime vaults (`.processor_vault/`, `.novamini_vault/`), deploy logs, and `*.wip` / `*.chipbase` scratch files are gitignored.

See `MANIFEST.json` and `RUNBOOK.md` for the full index and commands.

```bash
python scripts/run_trust_bundle_check.py
```
