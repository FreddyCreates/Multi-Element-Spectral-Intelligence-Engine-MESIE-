# NeuroSwarmAI — Drone Swarm Intelligence (Built)

**Engine:** v2.0.0
**Result:** 16/16
**Runtime:** 13.72s

## What was built (not just read)

| Module | Capability |
|--------|------------|
| `mission_planner.py` | Full mission: spectral → route → PSO/MARL → formation → LAN → DTN → PX4 adapter |
| `lan_gossip.py` | Cross-machine UDP gossip + file-drop fallback |
| `task_allocation.py` | Particle swarm + lightweight MARL task assignment |
| `formation.py` | Boids separation, collision avoid, V-reform after attrition |
| `dtn_store.py` | Delay-tolerant store-forward for jammed links |
| `drone_adapter.py` | PX4/MAVSDK bridge (sim + hardware probe) |
| `swarm_mission_presets.json` | Strike / ISR / EW / Swarm Forge topologies |

## Mission presets executed

- **ew**: ok=True tasks=3 formation=v_shape 1074.3402ms
- **strike**: ok=True tasks=3 formation=v_shape 3358.7103ms
- **isr**: ok=True tasks=3 formation=v_shape 3766.6631ms
- **swarm_forge**: ok=True tasks=3 formation=v_shape 3889.2616ms

## Scale

- 100 agents: 0.049575 ms/agent, consensus=hold, jam_ok=True
- 1000 agents: 0.122948 ms/agent, consensus=hold, jam_ok=True
- 10000 agents: 0.111604 ms/agent, consensus=hold, jam_ok=True

## Routing nervous system

- [ok] ground-schumann→world-computer-root (frequency_field)
- [ok] ground→world (frequency_field)
- [ok] orbital-leo-edge-000→orbital-geo-backbone-000 (frequency_field)
- [ok] leo0→geo (frequency_field)
- [ok] schumann→root (frequency_field)
