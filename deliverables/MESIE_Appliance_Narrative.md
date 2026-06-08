# MESIE Sovereign Spectral Appliance — Tier 1

**Product:** MESIE Sovereign Spectral Appliance
**Company:** NeuroSwarmAI
**Appliance v1.1.0** | SDK 1.4.0 | MESIE 0.3.3

## Positioning

Shippable on-prem, air-gapped spectral intelligence unit for defense and enterprise edge.
Runs on **MESIE Virtual Silicon (VS1)** — a software virtual chip (RF front-end + spectral ALU + OTA MAC).
No cloud dependency. Threat decisions and enterprise agent steps run locally on sovereign hardware.

## Evidence (MAESI_SDK_Major_Benchmarks.json)

- Win rate: **100.0%** (14/14 benchmarks)
- Verdict: `strong_for_edge_spectral_swarms`
- Threat-fast p50: **0.8774 ms** (SLA ≤ 12.0 ms)
- Enterprise-fast p50: **1.2097 ms** (SLA ≤ 500.0 ms)
- Swarm 10K ms/agent: **0.090127**
- Source: `C:\Users\Medin\Multi-Element-Spectral-Intelligence-Engine-MESIE-\deliverables\MAESI_SDK_Major_Benchmarks.json`

## Headline wins

- **MQTT broker RTT** (messaging): 0.8774 ms vs 25.0 ms ref
- **gRPC unary RTT** (messaging): 0.8774 ms vs 15.0 ms ref
- **Redis vector search** (vector_db): 0.1529 ms vs 3.0 ms ref
- **ChromaDB query** (vector_db): 0.1529 ms vs 12.0 ms ref
- **Pinecone query** (vector_db): 0.1529 ms vs 45.0 ms ref
- **OpenAI GPT-4 tool call** (llm_agent): 1.2097 ms vs 1200.0 ms ref
- **Anthropic Claude tool call** (llm_agent): 1.2097 ms vs 900.0 ms ref
- **MLPerf edge ResNet50 int8** (ml_inference): 0.2824 ms vs 8.0 ms ref

## Deployment

- Mode: on_prem_airgapped
- Network: none_required
- Ingest: csv, udp, rf_sim, rf_udp, virtual_silicon_hil, ota_multicast
- Platform: Windows-10-10.0.26200-SP0

## Modules

- enterprise_copilot
- sovereign_vault
- field_access
- swarm_sdk
- virtual_silicon
- rf_adapter
- ota_mesh
- cluster_optimizer
- mlperf_pack

*Generated 2026-06-08T06:07:29Z*