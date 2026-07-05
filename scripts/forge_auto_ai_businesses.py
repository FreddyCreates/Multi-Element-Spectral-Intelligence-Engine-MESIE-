#!/usr/bin/env python3
"""Forge Alpha Harness library — manifests + per-business scaffold stubs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.harness.alpha_registry import harness_manifest  # noqa: E402
from mesie.harness.auto_business import AUTO_AI_BUSINESSES, auto_business_catalog  # noqa: E402
from mesie.harness.template_library import template_manifest  # noqa: E402

OUT = ROOT / "deliverables" / "harness"
TEMPLATES = ROOT / "templates" / "surfaces"
BUSINESS = ROOT / "templates" / "businesses"


def _write_surface_stubs() -> None:
    TEMPLATES.mkdir(parents=True, exist_ok=True)
    stubs = {
        "api_console.html": _stub("API Console", "Invoke :8750 processor ops"),
        "product_sku.html": _stub("Product SKU App", "Single virtual product surface"),
        "auto_business_ops.html": _stub("Auto-AI Business Ops", "You + native AI mission board"),
        "native_dsl_ide.html": _stub("Native DSL IDE", "Compile + run 8 sovereign languages"),
        "depth_explorer.html": _stub("Depth Explorer", "18 polyglot pillars"),
    }
    for name, html in stubs.items():
        path = TEMPLATES / name
        if not path.is_file():
            path.write_text(html, encoding="utf-8")


def _stub(title: str, subtitle: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{title} — MESIE Template</title>
  <link rel="stylesheet" href="../../websites/shared/mesie.css" />
</head>
<body>
  <div class="bg-grid"></div>
  <div style="padding:2rem;max-width:960px;margin:0 auto">
    <h1>{title}</h1>
    <p class="muted">{subtitle}</p>
    <p>Native intelligence on <code>:8750</code> — wire hooks from <code>TEMPLATE_LIBRARY.json</code></p>
    <a href="../../websites/computing-family/" class="btn btn-primary">Computing Family</a>
  </div>
</body>
</html>
"""


def _write_business_scaffolds() -> int:
    count = 0
    for b in AUTO_AI_BUSINESSES:
        base = BUSINESS / b.business_id
        base.mkdir(parents=True, exist_ok=True)
        spec = {
            "business_id": b.business_id,
            "title": b.title,
            "template_id": b.template_id,
            "harness_ids": list(b.harness_ids),
            "intelligence": b.intelligence,
            "operators": list(b.operators),
            "processor_ops": list(b.processor_ops),
            "github_repo": b.github_repo,
        }
        (base / "business.json").write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
        readme = f"""# {b.title}

Auto-AI business — native SOLUS/MESIE intelligence (no third-party inference).

- Template: `{b.template_id}`
- Harnesses: {", ".join(b.harness_ids)}
- Operators: {", ".join(b.operators)}

```powershell
python -m mesie.processor --serve
# open websites/computing-family/ or template surface
```
"""
        (base / "README.md").write_text(readme, encoding="utf-8")
        count += 1
    return count


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    _write_surface_stubs()
    n = _write_business_scaffolds()

    paths = {
        "ALPHA_HARNESS_MANIFEST.json": harness_manifest(),
        "TEMPLATE_LIBRARY.json": template_manifest(),
        "AUTO_AI_BUSINESS_CATALOG.json": auto_business_catalog(),
    }
    for name, payload in paths.items():
        p = OUT / name
        p.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"[forge] {p}")

    print(f"[forge] {n} business scaffolds in templates/businesses/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())