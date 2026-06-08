"""Octopus MEMORY arm — SOLUS reasons every spectral cycle + mints receipt tokens."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Optional

from mesie.enterprise.receipt_chain import ComputationalReceiptChain
from mesie.io.loaders import RecordInput, load_record
from mesie.sdk.solus.math_layer import SolusMathLayer


class SolusMemoryArm:
    """MEMORY arm handler: local SOLUS math on every cycle, sealed receipt chain."""

    def __init__(
        self,
        math_layer: Optional[SolusMathLayer] = None,
        receipt_chain: Optional[ComputationalReceiptChain] = None,
    ) -> None:
        self.math = math_layer or SolusMathLayer()
        self.chain = receipt_chain or ComputationalReceiptChain()

    def run_cycle(
        self,
        record: RecordInput,
        *,
        cycle_context: Dict[str, Any],
        intelligence_memory: Optional[Dict[str, Any]] = None,
        intelligence_reason: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Full MEMORY arm: intelligence objects + SOLUS cycle reasoning + minted token."""
        rec = load_record(record)
        comp = rec.components[0]
        ctx = {
            **cycle_context,
            "record_id": rec.record_id,
            "cycle_id": cycle_context.get("cycle_id", rec.record_id),
        }

        solus = self.math.reason_spectral_cycle(
            comp.frequency.tolist(),
            comp.amplitude.tolist(),
            cycle_context=ctx,
        )

        receipt, token = self.chain.append_spectral_cycle(
            cycle_id=str(ctx["cycle_id"]),
            record_id=rec.record_id,
            work={
                "match_score": ctx.get("match_score", 0),
                "similarity": ctx.get("similarity", 0),
                "anomaly": ctx.get("anomaly", 0),
                "neighbors": ctx.get("neighbors", 0),
                "valid": ctx.get("valid", True),
                "arms": ctx.get("arms", []),
            },
            solus_proof={
                "conclusion": solus.get("conclusion", ""),
                "logic_confidence": solus.get("logic_confidence", 0),
                "signal_ratio": solus.get("signal_ratio", 0),
                "proof_steps": solus.get("proof_steps", 1),
                "caretakers": solus.get("caretakers", []),
                "formula": solus.get("formula"),
                "composition_hash": solus.get("composition_hash"),
                "formal_models": list((solus.get("formal_models") or {}).keys()),
                "third_party": False,
            },
        )

        chain_state = self.chain.verify_chain()
        return {
            "sovereign": True,
            "memory_arm": "solus",
            "solus_cycle": solus,
            "intelligence_memory": intelligence_memory or {},
            "intelligence_reason": intelligence_reason or {},
            "receipt": asdict(receipt),
            "minted_token": asdict(token),
            "receipt_chain": {
                "verified": chain_state.verified,
                "chain_length": chain_state.chain_length,
                "head_hash": chain_state.head_hash,
                "tokens_minted": chain_state.tokens_minted,
            },
        }