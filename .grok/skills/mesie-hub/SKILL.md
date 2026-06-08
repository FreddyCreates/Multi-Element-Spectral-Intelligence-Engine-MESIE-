---
name: mesie-hub
description: >
  Master hub for MESIE, MAESI, and NeuroAIX. Routes to all native skills and tools.
  Triggers: mesie, maesi, neuroaix, spectral engine, octopus, fingerprint, monte carlo.
  Use when user asks to run MESIE or needs the tool catalog.
---

# MESIE / MAESI / NeuroAIX Hub

**MESIE 0.3.3** | **MAESI SDK 1.4.0** — unified native suite: **52 tools**, **28 skills** (incl. hub).

```bash
python -m mesie.tools.cli list
python -m mesie.tools.cli run <tool-id>
```

## Skills map

| Skill | Tools |
|-------|-------|
| `/mesie-benchmark` | benchmark, major-benchmarks |
| `/mesie-data` | bundled-data, fix-data |
| `/mesie-deploy` | cloudflare, catalog |
| `/mesie-domains` | domains, scenario-sim |
| `/mesie-drone-swarm` | drone-swarm, mission-world-week |
| `/mesie-embed` | embed |
| `/mesie-embed-library` | embed-library, embed-mine |
| `/mesie-enterprise` | monte-carlo, multi-enterprise-20 |
| `/mesie-enterprise-ai` | enterprise-ai, pro-update, production-tiers, drone-thesis, trust-agents |
| `/mesie-fingerprint` | fingerprint |
| `/mesie-generate` | generate-psd, generate-fas, rotdnn |
| `/mesie-internal` | internal-bus, engines |
| `/mesie-knowledge` | knowledge |
| `/mesie-laptop` | laptop, virtual-silicon |
| `/mesie-logic-prover` | logic-prover |
| `/mesie-maesi` | maesi, fast-compute |
| `/mesie-match` | match, rank |
| `/mesie-native-ai` | native-ai |
| `/mesie-neuroaix` | neuroaix, cognitive |
| `/mesie-neuroswarm-audit` | neuroswarm-audit, is-this-true, proof-substrate, neuroswarm-readiness |
| `/mesie-octopus` | octopus |
| `/mesie-orbital` | orbital |
| `/mesie-pattern-forge` | pattern-forge |
| `/mesie-polyglot` | ais-polyglot |
| `/mesie-solus-organism` | solus-organism, sovereign-local-120, field-access, field-route, field-route-run |
| `/mesie-test` | test, sdk-drive |
| `/mesie-validate` | validate |

## Production stack (NeuroSwarmAI.com)

1. `/mesie-neuroswarm-readiness` — website evidence pack + gap closure plan
2. `/mesie-is-this-true` — honest external critique response
3. `/mesie-production-tiers` — Tier 1 appliance + Tier 2 cluster swarm
4. `/mesie-virtual-silicon` — VS1 RF HIL + OTA mesh certification
5. `/mesie-mission-world-week` — 7-day theater simulation
6. `/mesie-major-benchmarks` — third-party comparison harness

Regenerate skills: `python -m mesie.tools.cli skills`