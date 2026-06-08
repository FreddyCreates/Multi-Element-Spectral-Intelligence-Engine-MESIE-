"""Stream + generate native local AI deliverables inside MAESI SDK."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data import list_references, load_reference_record
from mesie.sdk import FORMAL_COMPOSITION, MAESIClient, SOLUS_BRAND
from mesie.sdk.native_ai.stream import StreamPhase


def main() -> None:
    print(f"=== {SOLUS_BRAND} Native Local AI — stream + deliverables ===\n")
    print(f"Formula: {FORMAL_COMPOSITION}\n")

    refs = [load_reference_record(n) for n in list_references()[:8]]
    client = MAESIClient(fast=True, use_fingerprint=True, use_solus_caretakers=True)
    engine = client.native_ai

    print("Streaming phases:\n")
    report = None
    gen = engine.stream_generate(refs, run_id="sdk_deliverable_demo")
    try:
        while True:
            ev = next(gen)
            bar = "█" * int(ev.progress * 20)
            print(f"  [{bar:<20}] {ev.phase.value:12} {ev.message}")
    except StopIteration as stop:
        report = stop.value

    if report is None:
        print("Generation failed.")
        sys.exit(1)

    print(f"\n{report.plain_summary}")
    print(f"\nDeliverables:")
    print(f"  JSON:     {report.bundle.json_path}")
    print(f"  Markdown: {report.bundle.markdown_path}")
    if report.bundle.stream_log_path:
        print(f"  Stream:   {report.bundle.stream_log_path}")
    if report.bundle.vault_snapshot_path:
        print(f"  Vault:    {report.bundle.vault_snapshot_path}")
    if report.bundle.token_bundle_path:
        print(f"  Tokens:   {report.bundle.token_bundle_path}")

    manifest = ROOT / "deliverables" / "native_ai" / "NativeAI_Manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps(
            {
                "brand": SOLUS_BRAND,
                "formula": FORMAL_COMPOSITION,
                "sovereign": True,
                "third_party": False,
                "latest_run": report.run_id,
                "vault_size": report.vault.get("vault_size"),
                "compound_work_units": report.vault.get("compound_work_units"),
                "files": {
                    "json": str(report.bundle.json_path),
                    "markdown": str(report.bundle.markdown_path),
                    "stream": str(report.bundle.stream_log_path) if report.bundle.stream_log_path else None,
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"  Manifest: {manifest}")


if __name__ == "__main__":
    main()