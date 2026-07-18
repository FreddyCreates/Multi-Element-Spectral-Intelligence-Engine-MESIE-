"""Evidence export in machine-readable JSON and human-readable Markdown."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_outputs(result: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "external_validation_results.json"
    md_path = output_dir / "external_validation_report.md"
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(result), encoding="utf-8")
    return json_path, md_path


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# MESIE External Dataset Validation Report",
        "",
        f"**Run ID:** `{result['run_id']}`",
        f"**Generated:** {result['generated_at']}",
        f"**Configuration SHA-256:** `{result['config_sha256']}`",
        "",
        "## Executive result",
        "",
        result["conclusion"],
        "",
        "## Benchmark results",
        "",
        "| Dataset | Domain | Feature set | Accuracy | Macro F1 | Feature ms/sample | Query ms/sample |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for dataset in result["datasets"]:
        for metric in dataset["results"]:
            lines.append(
                f"| {dataset['id']} | {dataset['domain']} | {metric['feature_set']} | "
                f"{metric['accuracy']:.4f} | {metric['macro_f1']:.4f} | "
                f"{metric['feature_ms_per_sample']:.6f} | {metric['query_ms_per_sample']:.6f} |"
            )

    lines.extend(["", "## Provenance", ""])
    for dataset in result["datasets"]:
        provenance = dataset["provenance"]
        lines.extend([
            f"### {dataset['id']}",
            "",
            f"- Source: {provenance['source_url']}",
            f"- Archive SHA-256: `{provenance['archive_sha256']}`",
            f"- Train/test samples: {provenance['train_samples']}/{provenance['test_samples']}",
            f"- Series length: {provenance['series_length']}",
            f"- Classes: {', '.join(provenance['classes'])}",
            "",
        ])

    lines.extend([
        "## Interpretation rules",
        "",
        "- Results are comparisons on official train/test splits; they are not claims of state-of-the-art performance.",
        "- `fft-32` is the frozen frequency-domain baseline.",
        "- `statistics` is a small non-spectral control baseline.",
        "- `mesie` uses z-normalized real-FFT amplitudes converted into MESIE records and embedded with the MESIE SDK.",
        "- `mesie-temporal-spectral-v2` preserves the MESIE embedding and adds frozen FFT, temporal-shape, and derivative-spectrum residual channels.",
        "- MESIE v2 is considered externally supported when it meets or exceeds the stronger baseline by the configured margin.",
        "- Dataset archives are identified by SHA-256 so later runs can detect source drift.",
        "",
        "## Reproduction",
        "",
        "```powershell",
        "mesie-validate-external run --config configs/public_ucr.json",
        "```",
        "",
    ])
    return "\n".join(lines)
