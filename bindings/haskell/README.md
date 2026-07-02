# MESIE Haskell Depth Bindings

Haskell depth implementations live under `mesie/depth/{pillar_id}/haskell/` — one cabal library per use-case pillar.

Forge or refresh all pillars:

```powershell
.\Start-DepthPillars.ps1 -Rebuild
```

Processor catalog: `GET http://127.0.0.1:8750/processor/depth`