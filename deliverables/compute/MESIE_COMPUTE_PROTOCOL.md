# MESIE COMPUTE Protocol Stack

| Protocol | ID | Role |
|----------|-----|------|
| Spectral Transformer | `MESIE-ST-φ/1.0` | Native φ-harmonic encoder — rivals HF, no torch |
| φ-Kernel | `MESIE-φ-KERNEL/1.0` | Compression + slice index for transfer |
| Compute Hub | `MESIE-COMPUTE-HUB/1.0` | Orchestrates products, metrics, squads |
| Tri-Agent | `MESIE-TRI-AGENT/1.0` | 3×3 maintenance auto-agents |

## Endpoints (:8750)

```
GET  /processor/compute/status
GET  /processor/compute/products
GET  /processor/compute/metrics
GET  /processor/compute/transformers
POST /processor/compute/encode
POST /processor/compute/benchmark
POST /processor/compute/squads/run
```

## Live artifacts

- `deliverables/compute/MESIE_COMPUTE_LIVE_METRICS.json`
- `deliverables/compute/MESIE_COMPUTE_PRODUCTS.json`
- `deliverables/compute/MESIE_COMPUTE_HUB.json`
- `deliverables/compute/ST_PHI_REGISTRY.json`

## Start

```powershell
.\Start-MESIECompute.ps1
```