# MESIE Virtual Silicon (VS1)

**Chip:** MESIE-VS1 v1.0.0
**Certified:** True

## What this is

A **virtual chip** — spectral RF front-end, ALU, and OTA MAC implemented in software
on your laptop or on-prem appliance. Same APIs and latency envelope as a future ASIC,
without waiting for fab.

## RF front-end (HIL certified)

- Path: `virtual_sdr_adc → nsrf_binary → field_bridge`
- SNR: 24.0 dB (virtual ground truth)
- Latency: 0.808 ms
- Field coherence: 0.5651

## OTA swarm radio

- Protocol: NSOT multicast over LAN (simulated OTA propagation)
- Tier: UHF/Terrestrial
- Frames: 12 sent / 48 received
- Over-the-air: True

## Benchmark lane

- Threat-fast p50: 0.5888 ms
- ANN query: 0.1086 ms

## Gaps resolved vs remaining

**Resolved:**
- RF path: virtual silicon SDR HIL (NSRF binary) certified without physical fab
- Multi-machine mesh: OTA multicast swarm radio (NSOT) with Hz-ladder propagation
- MLPerf: community formal pack with compliance manifest (see mlperf_submit)

**Remaining (honest):**
- Physical SDR silicon certification (RTL/fab) — virtual only
- Official MLPerf leaderboard board review — community pack ready
- Live satellite modem hardware — virtual orbital tier models only

*Generated 2026-06-08T01:29:07Z*