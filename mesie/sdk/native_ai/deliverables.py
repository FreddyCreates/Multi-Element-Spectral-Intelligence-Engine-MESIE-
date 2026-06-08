"""Native AI deliverable writers — JSON + Markdown inside the SDK."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.sdk.solus.constants import FORMAL_COMPOSITION, SOLUS_BRAND

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUT = ROOT / "deliverables" / "native_ai"


@dataclass
class DeliverableBundle:
    """Generated artifacts from one native AI run."""

    run_id: str
    json_path: Path
    markdown_path: Optional[Path] = None
    vault_snapshot_path: Optional[Path] = None
    token_bundle_path: Optional[Path] = None
    stream_log_path: Optional[Path] = None
    sovereign: bool = True
    third_party: bool = False
    brand: str = SOLUS_BRAND
    formula: str = FORMAL_COMPOSITION


@dataclass
class DeliverableWriter:
    """Write fused native AI outputs to deliverables/."""

    output_dir: Path = field(default_factory=lambda: DEFAULT_OUT)

    def write_report(
        self,
        *,
        run_id: str,
        payload: Dict[str, Any],
        stream_events: Optional[List[Dict[str, Any]]] = None,
    ) -> DeliverableBundle:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.output_dir / f"NativeAI_{run_id}.json"
        md_path = self.output_dir / f"NativeAI_{run_id}.md"
        stream_path = self.output_dir / f"NativeAI_{run_id}_stream.jsonl"

        doc = {
            "run_id": run_id,
            "brand": SOLUS_BRAND,
            "formula": FORMAL_COMPOSITION,
            "sovereign": True,
            "third_party": False,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            **payload,
        }
        json_path.write_text(json.dumps(doc, indent=2, default=str), encoding="utf-8")
        md_path.write_text(self._markdown(doc), encoding="utf-8")

        if stream_events:
            lines = [json.dumps(e, default=str) for e in stream_events]
            stream_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            stream_path = None

        vault_path = None
        token_path = None
        if payload.get("vault_export"):
            vault_path = self.output_dir / f"NativeAI_{run_id}_vault.json"
            vault_path.write_text(json.dumps(payload["vault_export"], indent=2, default=str), encoding="utf-8")
        if payload.get("token_bundle"):
            token_path = self.output_dir / f"NativeAI_{run_id}_tokens.json"
            token_path.write_text(json.dumps(payload["token_bundle"], indent=2, default=str), encoding="utf-8")

        return DeliverableBundle(
            run_id=run_id,
            json_path=json_path,
            markdown_path=md_path,
            vault_snapshot_path=vault_path,
            token_bundle_path=token_path,
            stream_log_path=stream_path,
        )

    @staticmethod
    def _markdown(doc: Dict[str, Any]) -> str:
        lines = [
            f"# Native Local AI Deliverable — {doc.get('run_id', 'run')}",
            "",
            f"*Generated {doc.get('generated_at', '')} — {SOLUS_BRAND} sovereign, zero third-party*",
            "",
            "## Composition",
            "",
            f"- **Formula:** `{doc.get('formula', FORMAL_COMPOSITION)}`",
            f"- **Sovereign:** {doc.get('sovereign', True)}",
            f"- **Third-party deps:** {doc.get('third_party', False)}",
            "",
        ]
        summary = doc.get("plain_summary") or doc.get("conclusion", "")
        if summary:
            lines.extend(["## Summary", "", str(summary), ""])

        formal = doc.get("formal_models") or doc.get("composition", {})
        if formal:
            lines.extend(["## Formal models", "", f"```json\n{json.dumps(formal, indent=2, default=str)}\n```", ""])

        vault = doc.get("vault", {})
        if vault:
            lines.extend([
                "## Sovereign vault",
                "",
                f"- Tokens stored: **{vault.get('vault_size', 0)}**",
                f"- Compound work units: **{vault.get('compound_work_units', 0)}**",
                "",
            ])

        minted = doc.get("minted_token")
        if minted:
            lines.extend([
                "## Minted token",
                "",
                f"- Token ID: `{minted.get('token_id', '')}`",
                f"- Work units: **{minted.get('work_units', 0)}**",
                "",
            ])

        if doc.get("neighbors"):
            lines.extend(["## Spectral neighbors", ""])
            for n in doc["neighbors"][:5]:
                lines.append(f"- `{n.get('record_id', n)}` sim={n.get('similarity', 'n/a')}")
            lines.append("")

        lines.extend([
            "## Files",
            "",
            f"- JSON: `deliverables/native_ai/NativeAI_{doc.get('run_id', 'run')}.json`",
            "",
        ])
        return "\n".join(lines)