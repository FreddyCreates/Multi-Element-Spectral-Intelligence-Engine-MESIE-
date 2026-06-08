"""SOLUS computational receipt chain — sealed math proofs minted as work tokens.

100% stdlib (hashlib + hmac). No third-party crypto or network dependencies.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from mesie.sdk.solus.constants import LOCAL_ENGINE, PHI, SOLUS_BRAND


def _canonical(payload: Dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _derive_chain_key(genesis: str, chain_len: int) -> bytes:
    seed = f"{SOLUS_BRAND}:{LOCAL_ENGINE}:{genesis}:{chain_len}:{PHI}".encode("utf-8")
    return hashlib.sha256(seed).digest()


@dataclass
class ComputationalReceipt:
    """One sealed proof-of-work receipt on the local chain."""

    receipt_id: str
    prev_hash: str
    cycle_id: str
    record_id: str
    work: Dict[str, Any]
    solus_proof: Dict[str, Any]
    sealed_digest: str
    timestamp_ms: float
    sovereign: bool = True
    engine: str = LOCAL_ENGINE


@dataclass
class MintedWorkToken:
    """Minted token proving a computational receipt was completed locally."""

    token_id: str
    receipt_id: str
    receipt_hash: str
    work_units: float
    chain_index: int
    sovereign: bool
    brand: str = SOLUS_BRAND
    engine: str = LOCAL_ENGINE


@dataclass
class ReceiptChainState:
    genesis_hash: str
    chain_length: int
    head_hash: str
    verified: bool
    tokens_minted: int


@dataclass
class ComputationalReceiptChain:
    """Append-only encrypted receipt chain — each link proves local SOLUS math work."""

    _genesis: str = field(default=f"{SOLUS_BRAND}-genesis-v1", init=False)
    _receipts: List[ComputationalReceipt] = field(default_factory=list)
    _tokens: List[MintedWorkToken] = field(default_factory=list)
    _head_hash: str = field(init=False, default="")

    def __post_init__(self) -> None:
        if not self._head_hash:
            self._head_hash = _sha256(self._genesis.encode("utf-8"))

    @property
    def genesis_hash(self) -> str:
        return _sha256(self._genesis.encode("utf-8"))

    @property
    def chain_length(self) -> int:
        return len(self._receipts)

    def _seal(self, prev_hash: str, body: Dict[str, Any], index: int) -> str:
        key = _derive_chain_key(self.genesis_hash, index)
        payload = prev_hash.encode("utf-8") + b"|" + _canonical(body)
        return hmac.new(key, payload, hashlib.sha256).hexdigest()

    def _work_units(self, work: Dict[str, Any], solus_proof: Dict[str, Any]) -> float:
        signal = float(work.get("match_score", 0) or work.get("similarity", 0))
        confidence = float(solus_proof.get("logic_confidence", 0.5))
        steps = float(solus_proof.get("proof_steps", 1))
        ratio = float(solus_proof.get("signal_ratio", 0.5))
        raw = signal * confidence * steps * (1.0 + ratio / PHI)
        return round(max(raw, 0.001), 6)

    def append_spectral_cycle(
        self,
        *,
        cycle_id: str,
        record_id: str,
        work: Dict[str, Any],
        solus_proof: Dict[str, Any],
    ) -> tuple[ComputationalReceipt, MintedWorkToken]:
        """Seal spectral-cycle work and mint a proof token."""
        index = self.chain_length
        body = {
            "cycle_id": cycle_id,
            "record_id": record_id,
            "work": work,
            "solus_proof": solus_proof,
            "timestamp_ms": round(time.time() * 1000, 2),
            "sovereign": True,
            "brand": SOLUS_BRAND,
        }
        sealed = self._seal(self._head_hash, body, index)
        receipt_id = _sha256((self._head_hash + sealed).encode("utf-8"))
        receipt = ComputationalReceipt(
            receipt_id=receipt_id,
            prev_hash=self._head_hash,
            cycle_id=cycle_id,
            record_id=record_id,
            work=work,
            solus_proof=solus_proof,
            sealed_digest=sealed,
            timestamp_ms=body["timestamp_ms"],
        )
        self._receipts.append(receipt)
        self._head_hash = _sha256(_canonical(asdict(receipt)))

        work_units = self._work_units(work, solus_proof)
        token_id = _sha256((receipt_id + ":MINT:" + SOLUS_BRAND).encode("utf-8"))[:32]
        token = MintedWorkToken(
            token_id=token_id,
            receipt_id=receipt_id,
            receipt_hash=self._head_hash,
            work_units=work_units,
            chain_index=index,
            sovereign=True,
        )
        self._tokens.append(token)
        return receipt, token

    def verify_chain(self) -> ReceiptChainState:
        """Verify every receipt seal and hash link."""
        prev = self.genesis_hash
        ok = True
        for i, receipt in enumerate(self._receipts):
            if receipt.prev_hash != prev:
                ok = False
                break
            body = {
                "cycle_id": receipt.cycle_id,
                "record_id": receipt.record_id,
                "work": receipt.work,
                "solus_proof": receipt.solus_proof,
                "timestamp_ms": receipt.timestamp_ms,
                "sovereign": receipt.sovereign,
                "brand": SOLUS_BRAND,
            }
            expected = self._seal(prev, body, i)
            if expected != receipt.sealed_digest:
                ok = False
                break
            prev = _sha256(_canonical(asdict(receipt)))
        if ok and self._receipts:
            ok = prev == self._head_hash
        return ReceiptChainState(
            genesis_hash=self.genesis_hash,
            chain_length=self.chain_length,
            head_hash=self._head_hash,
            verified=ok,
            tokens_minted=len(self._tokens),
        )

    def last_token(self) -> Optional[MintedWorkToken]:
        return self._tokens[-1] if self._tokens else None

    def to_dict(self) -> Dict[str, Any]:
        state = self.verify_chain()
        return {
            "genesis_hash": state.genesis_hash,
            "chain_length": state.chain_length,
            "head_hash": state.head_hash,
            "verified": state.verified,
            "tokens_minted": state.tokens_minted,
            "last_token": asdict(self._tokens[-1]) if self._tokens else None,
            "sovereign": True,
            "brand": SOLUS_BRAND,
        }