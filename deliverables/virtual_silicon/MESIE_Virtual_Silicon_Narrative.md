# MESIE Virtual Silicon (MESIE-VS1)

**Chip:** MESIE-VS1 v1.2.0
**Certified:** True

## What this is

A **virtual chip** — spectral RF front-end, ALU, and OTA MAC implemented in software
on your laptop or on-prem appliance. Same APIs and latency envelope as a future ASIC,
without waiting for fab. **Not regular MCP** — invoke via Virtual Processor HTTP `:8750`.

## RF front-end (HIL certified)

- Path: `virtual_sdr_adc → nsrf_binary → field_bridge`
- Front-ends: 1
- SNR: 24.0 dB (virtual ground truth)
- Latency: 1.4077 ms
- Field coherence: 0.559

## OTA swarm radio

- Protocol: NSOT_multicast_v1
- Tier: UHF/Terrestrial
- Frames: 12 sent / 48 received

## Benchmark lane (statistical)

- Threat-fast p50: 1.1611 ms
- ANN p50 / p95: 0.3 / 0.6335 ms
- ANN backend: library_index:spectral_index.json

## Deploy

- `POST http://127.0.0.1:8750/processor/virtual-chip` body `{"chip_id": "MESIE-VS1"}`
- Manifest: `deliverables/virtual_silicon/MESIE_Chip_Deploy_Manifest.json`

*Generated 2026-06-26T09:04:50Z*