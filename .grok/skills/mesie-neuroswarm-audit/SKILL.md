---
name: mesie-neuroswarm-audit
description: >
  NeuroSwarmAI.com claims verifier — maps external audit critique to measured SDK evidence.
  Triggers: neuroswarm, audit evidence, claims verifier, 12ms latency, swarm benchmark.
  Use for /mesie-neuroswarm-audit or NeuroSwarmAI defense/edge claim validation.
---

# mesie-neuroswarm-audit

Evidence pack for **NeuroSwarmAI.com** — reproducible local harness addressing third-party audit critique.

## When to use

- Validate sub-ms spectral ops, 12ms threat-fast path, 10K swarm routing
- Document p50/p95/p99, noise/jamming degradation, sovereign air-gapped flags
- Produce customer/red-team runnable JSON + MD deliverables

## Tools in this skill

### `proof-substrate` — Proof Substrate
- Command: `python scripts/run_proof_substrate.py`
- Deliverable: `deliverables/Proof_Substrate.json`
- Verify seal: `python scripts/run_proof_substrate.py --verify`

### `neuroswarm-audit` — NeuroSwarm Audit Evidence
- Command: `python scripts/run_neuroswarm_audit.py --trials 1000`
- Deliverable: `deliverables/NeuroSwarmAI_Audit_Evidence.json`

## Agent workflow

1. `cd` to repo root: `Multi-Element-Spectral-Intelligence-Engine-MESIE-`
2. Run: `python -m mesie.tools.cli run neuroswarm-audit`
3. Read `deliverables/NeuroSwarmAI_Audit_Evidence.md` — critique → finding mapping
4. Cite measured p50/p99; note Threat-Fast vs Enterprise-Full SLA separation

## Repo paths

- Harness: `mesie/evaluation/neuroswarm_audit.py`
- Runner: `scripts/run_neuroswarm_audit.py`