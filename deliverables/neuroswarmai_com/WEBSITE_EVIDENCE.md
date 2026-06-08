# NeuroSwarmAI.com — Evidence & Readiness

**Site:** https://neuroswarmai.com
**Readiness level:** L2_software_production
**Production ready (software):** True

## What we prove publicly

- Sub-ms threat-fast spectral decisions (measured locally, reproducible harness)
- Sovereign air-gapped software appliance architecture
- 12/12 military + 6/6 enterprise software scenarios on real reference data
- 56/56 theater week simulation ticks (Operation Spectral Shield)
- Virtual silicon RF HIL + OTA mesh (software-certified)

## What we do NOT claim

- Combat-certified or DoD-accredited (not claimed)
- 10K physical drones deployed (simulation + cluster math today)
- Live EW range or anechoic chamber validated (reference profiles only)
- Independent third-party audit completed (invited, not yet done)

## Close gaps — phased plan

| Phase | Task | Status |
|-------|------|--------|
| P0_now | Publish public evidence pack on neuroswarmai.com | ready |
| P0_now | Fix website wording: software validation not combat certified | ready |
| P0_now | One-command reproducibility for third parties | ready |
| P1_30d | Multi-host LAN/OTA soak (3+ machines) | planned |
| P1_30d | PX4 SITL hardware-in-loop gate | planned |
| P2_90d | SDR / RF anechoic or range partner test | planned |
| P2_90d | Third-party reproducibility audit | planned |
| P2_90d | Sovereign appliance penetration test | planned |

## Proof substrate

Sealed evidence graph with SHA256 artifact hashes and reproducible harness commands:

```bash
python scripts/run_proof_substrate.py
python scripts/run_proof_substrate.py --verify
```

- `deliverables/Proof_Substrate.json`
- `deliverables/neuroswarmai_com/proof_substrate.json`

## Reproduce on your machine

```bash
git clone <repo>
python scripts/run_neuroswarm_readiness.py
```

*Artifacts: 10+ files in evidence pack (incl. proof substrate)*