"""Native Local AI Engine — fused SOLUS + MAESI + vault, streams and generates deliverables."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Sequence

from mesie.enterprise.receipt_chain import ComputationalReceiptChain
from mesie.enterprise.sovereign_vault import SovereignVault
from mesie.io.loaders import RecordInput, load_record
from mesie.sdk.native_ai.deliverables import DeliverableBundle, DeliverableWriter
from mesie.sdk.native_ai.stream import StreamEvent, StreamPhase
from mesie.sdk.solus import FORMAL_COMPOSITION, SDKSolusOrganism, SolusFormalStack, composition_manifest
from mesie.sdk.solus.constants import SOLUS_BRAND


@dataclass
class NativeAIDeliverableReport:
    run_id: str
    sovereign: bool
    brand: str
    formula: str
    conclusion: str
    plain_summary: str
    minted_token: Optional[Dict[str, Any]]
    vault: Dict[str, Any]
    formal_models: Dict[str, Any]
    neighbors: List[Dict[str, Any]]
    bundle: DeliverableBundle
    stream_events: int


@dataclass
class NativeLocalAIEngine:
    """Our own native local AI inside MAESI SDK — stream, generate, store, compound."""

    session_id: str = "native-ai"
    deliverable_dir: Optional[str] = None
    organism: SDKSolusOrganism = field(default_factory=SDKSolusOrganism)
    formal_stack: SolusFormalStack = field(default_factory=SolusFormalStack)
    vault: SovereignVault = field(default_factory=SovereignVault)
    receipts: ComputationalReceiptChain = field(default_factory=ComputationalReceiptChain)
    _maesi: Any = field(default=None, init=False)
    _indexed: bool = field(default=False, init=False)
    _stream_log: List[Dict[str, Any]] = field(default_factory=list, init=False)

    def _client(self):
        if self._maesi is None:
            from mesie.sdk.maesi_client import MAESIClient

            self._maesi = MAESIClient(
                fast=True,
                use_fingerprint=True,
                use_solus_caretakers=True,
                use_solus_math_layer=True,
            )
            if self._maesi.organism is None:
                self._maesi.organism = self.organism
            if self._maesi.math_layer is None:
                from mesie.sdk.solus.math_layer import SolusMathLayer

                self._maesi.math_layer = SolusMathLayer(organism=self.organism, formal_stack=self.formal_stack)
        return self._maesi

    def _emit(self, phase: StreamPhase, message: str, *, progress: float, data: Optional[Dict] = None, done: bool = False) -> StreamEvent:
        ev = StreamEvent(phase=phase, message=message, data=data or {}, progress=progress, done=done)
        self._stream_log.append(ev.to_dict())
        return ev

    def index_corpus(self, records: Sequence[RecordInput]) -> int:
        client = self._client()
        n = client.index_corpus(records)
        self._indexed = True
        return n

    def stream_generate(
        self,
        records: Sequence[RecordInput],
        *,
        run_id: Optional[str] = None,
        write_deliverable: bool = True,
    ) -> Generator[StreamEvent, None, NativeAIDeliverableReport]:
        """Stream native AI generation phase-by-phase; optionally write deliverables."""
        rid = run_id or f"run_{uuid.uuid4().hex[:12]}"
        self._stream_log = []
        t0 = time.perf_counter()

        yield self._emit(
            StreamPhase.BOOT,
            f"{SOLUS_BRAND} native local AI online — own models only",
            progress=0.02,
            data={"formula": FORMAL_COMPOSITION, "manifest": composition_manifest()},
        )

        if not records:
            yield self._emit(StreamPhase.COMPLETE, "no records", progress=1.0, done=True)
            raise ValueError("records required")

        n = self.index_corpus(records)
        yield self._emit(StreamPhase.INDEX, f"indexed {n} spectral records", progress=0.08, data={"corpus_size": n})

        rec = load_record(records[0])
        comp = rec.components[0]
        freqs = comp.frequency.tolist()
        amps = comp.amplitude.tolist()
        ctx = {"record_id": rec.record_id, "cycle_id": f"{self.session_id}_{rid}"}

        composed = self.formal_stack.compose_cycle(freqs, amps, cycle_context=ctx)
        models = composed.get("formal_models", {})

        for phase, key, msg in [
            (StreamPhase.LOGIC, "logic", "Logic model — formal proof substrate"),
            (StreamPhase.REASONING, "reasoning", "Reasoning model — inference chain"),
            (StreamPhase.EMERGENCE, "emergence", "Emergence model — pattern lift"),
            (StreamPhase.ADAPTATION, "adaptation", "Adaptation model — local recalibration"),
        ]:
            m = models.get(key, {})
            yield self._emit(
                phase,
                msg,
                progress={"logic": 0.2, "reasoning": 0.35, "emergence": 0.5, "adaptation": 0.65}[key],
                data={"model_id": m.get("model_id"), "conclusion": (m.get("brain") or {}).get("conclusion", "")[:120]},
            )

        client = self._client()
        q = client.query(records[0], top_k=5)
        yield self._emit(
            StreamPhase.QUERY,
            f"MAESI query — {len(q.neighbors)} neighbors",
            progress=0.72,
            data={"record_id": q.record_id, "neighbors": q.neighbors, "research": q.research_hits[:3]},
        )

        yield self._emit(
            StreamPhase.MEMORY,
            "spectral agent memory aligned",
            progress=0.78,
            data={"technical_hits": q.technical_hits[:3]},
        )

        receipt, token = self.receipts.append_spectral_cycle(
            cycle_id=ctx["cycle_id"],
            record_id=rec.record_id,
            work={
                "match_score": composed.get("composite_score", 0),
                "similarity": composed.get("composite_score", 0),
                "neighbors": len(q.neighbors),
                "session_id": self.session_id,
            },
            solus_proof={
                "conclusion": composed.get("conclusion", ""),
                "logic_confidence": composed.get("logic_confidence", 0),
                "signal_ratio": composed.get("signal_ratio", 0),
                "proof_steps": composed.get("proof_steps", 1),
                "formula": FORMAL_COMPOSITION,
                "composition_hash": composed.get("composition_hash"),
                "formal_models": list(models.keys()),
            },
        )
        yield self._emit(
            StreamPhase.MINT,
            f"minted work token {token.token_id[:16]}…",
            progress=0.85,
            data={"token_id": token.token_id, "work_units": token.work_units, "receipt_id": receipt.receipt_id},
        )

        vault_prior = self.vault.recall(results=composed, workflow={"workflow_id": self.session_id}, top_k=3)
        entry = self.vault.deposit(
            token=token,
            receipt=receipt,
            composition=composed,
            results={**composed, "neighbors": len(q.neighbors)},
            workflow={"workflow_id": self.session_id, "run_id": rid, "arms": ["native_ai", "stream"]},
            ai_patterns={
                "formal_models": list(models.keys()),
                "caretakers": composed.get("caretakers", []),
                "pattern_xray": composed.get("pattern_xray"),
            },
            record_id=rec.record_id,
            cycle_id=ctx["cycle_id"],
        )
        compound = self.vault.compound()
        yield self._emit(
            StreamPhase.VAULT,
            f"deposited to sovereign vault ({self.vault.size} tokens)",
            progress=0.92,
            data={
                "vault_id": entry.vault_id,
                "vault_size": self.vault.size,
                "compound_work_units": compound.total_work_units,
                "prior_hits": vault_prior.get("hits", []),
            },
        )

        elapsed_ms = (time.perf_counter() - t0) * 1000
        conclusion = str(composed.get("conclusion", ""))
        plain = (
            f"Native AI [{SOLUS_BRAND}]: {rid} — {FORMAL_COMPOSITION}. "
            f"Neighbors={len(q.neighbors)}, token={token.token_id[:12]}…, "
            f"vault={self.vault.size}, work={compound.total_work_units:.4f}, "
            f"{elapsed_ms:.1f}ms local."
        )

        bundle: DeliverableBundle = DeliverableBundle(
            run_id=rid,
            json_path=Path("pending"),
        )
        if write_deliverable:
            writer = DeliverableWriter()
            if self.deliverable_dir:
                writer.output_dir = Path(self.deliverable_dir)
            payload = {
                "plain_summary": plain,
                "conclusion": conclusion,
                "formal_models": models,
                "composition": {
                    "formula": FORMAL_COMPOSITION,
                    "composition_hash": composed.get("composition_hash"),
                    "formal_layers": composed.get("formal_layers"),
                },
                "query": {
                    "record_id": q.record_id,
                    "neighbors": q.neighbors,
                    "research_hits": q.research_hits,
                    "technical_hits": q.technical_hits,
                    "elapsed_ms": q.elapsed_ms,
                },
                "minted_token": {
                    "token_id": token.token_id,
                    "work_units": token.work_units,
                    "receipt_id": receipt.receipt_id,
                    "chain_index": token.chain_index,
                },
                "receipt_chain": self.receipts.to_dict(),
                "vault": {
                    "vault_id": entry.vault_id,
                    "vault_size": self.vault.size,
                    "compound_work_units": compound.total_work_units,
                },
                "vault_export": self.vault.to_dict(),
                "token_bundle": {
                    "latest": {
                        "token_id": token.token_id,
                        "composition_hash": composed.get("composition_hash"),
                        "conclusion": conclusion,
                    },
                    "compound_work_units": compound.total_work_units,
                },
                "elapsed_ms": round(elapsed_ms, 2),
            }
            bundle = writer.write_report(run_id=rid, payload=payload, stream_events=self._stream_log)
            yield self._emit(
                StreamPhase.DELIVERABLE,
                f"wrote {bundle.json_path.name}",
                progress=0.97,
                data={
                    "json": str(bundle.json_path),
                    "markdown": str(bundle.markdown_path) if bundle.markdown_path else None,
                    "stream_log": str(bundle.stream_log_path) if bundle.stream_log_path else None,
                },
            )

        yield self._emit(StreamPhase.COMPLETE, plain, progress=1.0, data={"run_id": rid}, done=True)

        return NativeAIDeliverableReport(
            run_id=rid,
            sovereign=True,
            brand=SOLUS_BRAND,
            formula=FORMAL_COMPOSITION,
            conclusion=conclusion,
            plain_summary=plain,
            minted_token={"token_id": token.token_id, "work_units": token.work_units},
            vault={"vault_size": self.vault.size, "compound_work_units": compound.total_work_units},
            formal_models=models,
            neighbors=q.neighbors,
            bundle=bundle,
            stream_events=len(self._stream_log),
        )

    def generate(self, records: Sequence[RecordInput], *, run_id: Optional[str] = None) -> NativeAIDeliverableReport:
        """Non-streaming: run full native AI cycle and return deliverable report."""
        gen = self.stream_generate(records, run_id=run_id, write_deliverable=True)
        try:
            while True:
                next(gen)
        except StopIteration as stop:
            if stop.value is None:
                raise RuntimeError("native AI generation failed") from stop
            return stop.value
        raise RuntimeError("native AI generation failed")