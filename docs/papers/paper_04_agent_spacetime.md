# Paper 04: Embedding Autonomous Agents in Simulated Spacetime

**Authority state:** `INTERNAL_RESEARCH`  
**Claim boundary:** `repo_verified_architecture`  
**Series:** Spatium Computationis / Repo-Native NeuroAI Infrastructure  
**MESIE module:** `mesie/spacetime/`

## Abstract

This paper converts organism-agent and battleground material into a bounded architecture preprint. It studies embedding autonomous agents and operational zones inside a simulated spacetime so that routing, isolation, influence, communication, and quarantine can be represented spatially. Publication remains high-level unless Medina approves the release boundary. The architecture is a **design proposal and experimental framework**, not a verified production security system.

## Distinct thesis

Spatial embedding offers a design language for autonomous-agent coordination in which operational roles, trust boundaries, influence, and quarantine can be modeled as geometric regions and physical interaction rules.

## Contribution surface

- Three-tier signal classification: cooperative, hostile, shadow
- Agent placement as position-bearing entities in a simulated substrate
- Zone definitions as bounded geometric regions with semantic roles
- Influence and communication modeled through force analogies
- Architecture bridge from physical substrate to operational intelligence routing

## Repo implementation

| Component | Path |
|-----------|------|
| Signal tiers | `mesie/spacetime/signals.py` |
| Spatial agents | `mesie/spacetime/agents.py` |
| Zones + policy | `mesie/spacetime/zones.py` |
| Force analogies | `mesie/spacetime/forces.py` |
| Intelligence routing | `mesie/spacetime/routing.py` |
| Tick substrate | `mesie/spacetime/substrate.py` |
| Evaluation | `mesie/spacetime/eval.py` |
| Suite | `python scripts/run_spacetime_suite.py` |

## Bounded public claims

| Claim | Public wording |
|-------|----------------|
| Agents embed in tick-based 3D space | "Resident agents, threats, honeypots, and relays occupy a simulated operational substrate." |
| Tiered routing | "Cooperative, adversarial, and unknown inputs follow distinct route policies." |
| Influence analogy | "Attraction forces model authority/influence between agents — metaphorical, not empirical physics." |
| Production security | **Not claimed.** Repo contains experimental scaffolding only. |

## Run

```bash
python scripts/run_spacetime_suite.py
# or: python -m mesie.tools.cli run spacetime-suite
```

Deliverable: `deliverables/Paper04_Spacetime_Architecture_Report.json`

## IP / release gate

Before preprint release: agent registry diagram approval, pseudocode for tier classification, simulation traces, threat-model document, IP review of zone names and coordinates.