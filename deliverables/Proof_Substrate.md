# MESIE Proof Substrate

**Verdict:** `partially_true_software_substrate` | **Seal:** `03760bc93bcac37e…`
**MESIE:** 0.3.3 | **MAESI SDK:** 1.4.0

Hash-linked evidence graph — claims bound to artifacts with reproducible harness commands.

## Tier summary

- **gap:** 2 claims
- **measured_local:** 3 claims
- **simulated_validated:** 3 claims

**Gaps open:** 2

## Claims → artifacts

### sub_ms_threat
- **Claim:** Sub-12ms threat-fast spectral decisions
- **Tier:** Measured on this machine (reproducible harness)
- **Measured:** p50 threat-fast ~0.85ms on Qualcomm ARM64 laptop harness
- **Limit:** Single-machine Python harness; not independent lab audit
- **Reproduce:** `python scripts/run_neuroswarm_audit.py --trials 1000`
  - `deliverables/NeuroSwarmAI_Audit_Evidence.json` → `89f2219ec79a…` (15182 B)
  - `deliverables/MAESI_SDK_Major_Benchmarks.json` → `87916835ab95…` (12463 B)

### swarm_10k
- **Claim:** 10K decentralized swarm coordination
- **Tier:** Software simulation validated (not physical HIL)
- **Measured:** ~0.05-0.11 ms/agent cluster-optimized in software sim
- **Limit:** In-process simulation; not 10K physical drones or multi-host mesh at scale
- **Reproduce:** `python scripts/run_drone_swarm_suite.py --agents 10000`
  - `deliverables/NeuroSwarmAI_Drone_Swarm_Report.json` → `c371091e234a…` (49891 B)
  - `deliverables/MESIE_Scenario_Simulation_Report.json` → `cbfc43e2d09a…` (27842 B)

### jam_failover
- **Claim:** Jamming failover to orbital routing
- **Tier:** Software simulation validated (not physical HIL)
- **Measured:** jam_ground=True scenarios pass orbital_preferred access modes
- **Limit:** Spectral jam profile reference; no RF anechoic or live EW range
- **Reproduce:** `python scripts/run_enterprise_drone_thesis.py`
  - `deliverables/MESIE_Enterprise_Drone_Defense_Offense_Thesis.json` → `951a13048693…` (4006 B)

### real_drone_hw
- **Claim:** Real drone hardware integration
- **Tier:** Known gap — not proven
- **Measured:** PX4/MAVSDK sim adapter dispatches commands; SIM platform only
- **Limit:** No published flight test video or cleared contractor validation
- **Reproduce:** `python scripts/run_drone_swarm_suite.py --agents 100`
  - `mesie/swarm/drone_adapter.py` → `c9702cd5261b…` (3825 B)

### sovereign_airgap
- **Claim:** Sovereign air-gapped on-prem appliance
- **Tier:** Measured on this machine (reproducible harness)
- **Measured:** field_access reports airgapped=true, third_party=false
- **Limit:** Self-reported engine status; not third-party penetration test
- **Reproduce:** `python scripts/run_production_tiers.py --tier both`
  - `deliverables/MESIE_Appliance_Manifest.json` → `0cc5f21e877b…` (1307 B)
  - `deliverables/MESIE_Production_Tiers_Report.json` → `22e455be2cb0…` (4018 B)

### mission_critical_100
- **Claim:** 100/100 mission-critical defense scenarios
- **Tier:** Software simulation validated (not physical HIL)
- **Measured:** 12 scenario sim + 7-day theater week ticks (software)
- **Limit:** Not DoD accreditation; scenario pass != combat validation
- **Reproduce:** `python scripts/run_scenario_simulation_suite.py && python scripts/run_mission_world_week.py --days 7`
  - `deliverables/MESIE_Scenario_Simulation_Report.json` → `cbfc43e2d09a…` (27842 B)
  - `deliverables/mission_worlds/theater_alpha_week_001_week_report.json` → `1eacd8aebb05…` (39260 B)

### external_corroboration
- **Claim:** Independent validation of NeuroSwarmAI.com deployment
- **Tier:** Known gap — not proven
- **Measured:** Public evidence pack publishable; independent audit not yet completed
- **Limit:** Self-published harness until third party reproduces and signs
- **Reproduce:** `python scripts/run_neuroswarm_readiness.py`
  - `deliverables/neuroswarmai_com/evidence_manifest.json` → `6695010d3e5d…` (4674 B)

### connectome_44_region
- **Claim:** 44-region connectome spectral intelligence
- **Tier:** Measured on this machine (reproducible harness)
- **Measured:** Connectome modules present; used in routing/cognitive paths
- **Limit:** Inspired architecture; not neuroscience certification
- **Reproduce:** `python examples/08_3d_connectome_brain.py`
  - `mesie/connectome/brain_regions.py` → `0b92d3da7147…` (16183 B)

## Verify seal

```bash
python scripts/run_proof_substrate.py --verify
```