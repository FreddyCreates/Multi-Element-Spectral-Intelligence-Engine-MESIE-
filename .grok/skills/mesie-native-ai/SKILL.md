---
name: mesie-native-ai
description: >
  Fused SOLUS native AI: stream + generate JSON/MD deliverables inside SDK (vault + tokens). Triggers: deliverable, generate, local ai, native ai, solus sdk, stream. Use for /mesie-native-ai or MESIE/MAESI/NeuroAIX tasks.
---

# mesie-native-ai

Native MESIE / MAESI / NeuroAIX skill — **MAESI SDK & Knowledge**.

## When to use

- Fused SOLUS native AI: stream + generate JSON/MD deliverables inside SDK (vault + tokens).

## Tools in this skill

### `native-ai` — Native Local AI Deliverables
- Command: `python scripts/run_native_ai_deliverables.py`
- Deliverable: `deliverables/native_ai/NativeAI_Manifest.json`

## Agent workflow

1. `cd` to repo root: `Multi-Element-Spectral-Intelligence-Engine-MESIE-`
2. Run via unified CLI: `python -m mesie.tools.cli run <tool-id>`
3. Or run the command above directly.
4. Read deliverable path if present; summarize results for the user.
5. On failure: run `python -m mesie.tools.cli run test` to verify environment.

## Repo paths

- Tools registry: `mesie/tools/registry.py`
- CLI: `python -m mesie.tools.cli list`