---
name: mesie-drone-swarm
description: >
  Decentralized drone swarm coordination for NeuroSwarmAI — gossip consensus, field routing,
  jamming failover, 10K scale. Triggers: drone swarm, swarm coordination, chimeria, decentralized.
  Use for /mesie-drone-swarm or Chimeria Defense swarm doctrine validation.
---

# mesie-drone-swarm

NeuroSwarmAI / Chimeria Defense doctrine — no central commander, spectral backbone + field mesh.

## When to use

- Validate decentralized swarm at 100 / 1K / 10K agents
- Test jamming failover (ground jam → orbital_preferred)
- Test node attrition self-healing
- Validate routing nervous system (ground→world, leo→geo, aliases, presets)

## Tools

### `drone-swarm` — Drone Swarm Coordination Suite
- Command: `python scripts/run_drone_swarm_suite.py --agents 10000`
- Deliverable: `deliverables/NeuroSwarmAI_Drone_Swarm_Report.json`

## Copilot tools

- `mesie_drone_swarm_coordinate` — full decentralized coordination
- `mesie_swarm_routing_validate` — field router nervous-system checks

## Agent workflow

1. Run suite: `python -m mesie.tools.cli run drone-swarm`
2. Read doctrine mapping in deliverable MD
3. Cite ms/agent, e2e p50, jam failover for customer/red-team

## Repo paths

- Engine: `mesie/swarm/drone_coordination.py`
- Consensus: `mesie/swarm/consensus.py`
- Gossip: `mesie/swarm/mesh_gossip.py`