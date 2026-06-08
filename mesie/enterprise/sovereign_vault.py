"""Sovereign Vault — every minted token embedded and kept with the AI for reuse.

Stores token composition, results, workflow, AI patterns locally. Zero third-party.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from mesie.enterprise.receipt_chain import ComputationalReceipt, MintedWorkToken
from mesie.sdk.solus.constants import FORMAL_COMPOSITION, LOCAL_ENGINE, PHI, SOLUS_BRAND

DEFAULT_VAULT_PATH = Path(__file__).resolve().parents[2] / "library" / "sovereign_vault.json"
EMBED_DIM = 32


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass
class VaultEntry:
    """One minted token and everything that happened with it — embedded for recall."""

    vault_id: str
    token_id: str
    receipt_id: str
    embedding: List[float]
    composition: Dict[str, Any]
    results: Dict[str, Any]
    workflow: Dict[str, Any]
    ai_patterns: Dict[str, Any]
    work_units: float
    chain_index: int
    record_id: str
    cycle_id: str
    timestamp_ms: float
    sovereign: bool = True
    third_party: bool = False
    brand: str = SOLUS_BRAND
    engine: str = LOCAL_ENGINE


@dataclass
class VaultCompoundState:
    """Accumulated work across all stored tokens."""

    total_tokens: int
    total_work_units: float
    verified_entries: int
    formula: str
    sovereign: bool


class VaultEmbedder:
    """Local embedder — packs token + composition + patterns into a sovereign vector."""

    def embed(
        self,
        *,
        token: MintedWorkToken,
        composition: Dict[str, Any],
        results: Dict[str, Any],
        workflow: Dict[str, Any],
        ai_patterns: Dict[str, Any],
    ) -> np.ndarray:
        comp_hash = str(composition.get("composition_hash", ""))
        digest = _sha256_text(comp_hash) if comp_hash else "0" * 64
        hash_feats = [int(digest[i : i + 2], 16) / 255.0 for i in range(0, 16, 2)]

        numeric = [
            float(token.work_units),
            float(results.get("match_score", 0)),
            float(results.get("similarity", 0)),
            float(results.get("anomaly", 0)),
            float(results.get("logic_confidence", 0)),
            float(results.get("signal_ratio", 0)),
            float(results.get("emergence_score", 0)),
            float(results.get("composite_score", 0)),
            float(len(workflow.get("steps", []))) / 10.0,
            float(len(ai_patterns.get("formal_models", []))) / 4.0,
            float(composition.get("adapted", 0) if isinstance(composition.get("adapted"), (int, float)) else 0),
            PHI / (PHI + 1),
        ]

        text_seed = json.dumps(
            {
                "conclusion": results.get("conclusion", ""),
                "formula": composition.get("formula", FORMAL_COMPOSITION),
                "workflow_id": workflow.get("workflow_id", ""),
            },
            sort_keys=True,
        )
        text_hash = _sha256_text(text_seed)
        text_feats = [int(text_hash[i : i + 2], 16) / 255.0 for i in range(0, 24, 2)]

        vec = np.array(hash_feats + numeric + text_feats, dtype=np.float64)[:EMBED_DIM]
        if vec.size < EMBED_DIM:
            vec = np.pad(vec, (0, EMBED_DIM - vec.size))
        norm = np.linalg.norm(vec)
        return vec / max(norm, 1e-12)


@dataclass
class SovereignVault:
    """On-prem vault: mint → embed → store → recall → compound."""

    max_entries: int = 4096
    persist_path: Optional[Path] = None
    auto_persist: bool = True
    _entries: List[VaultEntry] = field(default_factory=list)
    _matrix: Optional[np.ndarray] = field(default=None, init=False)
    _embedder: VaultEmbedder = field(default_factory=VaultEmbedder, init=False)

    def __post_init__(self) -> None:
        if self.persist_path is None:
            self.persist_path = DEFAULT_VAULT_PATH
        self._load_if_exists()

    def _rebuild_matrix(self) -> None:
        if not self._entries:
            self._matrix = None
            return
        self._matrix = np.stack([np.asarray(e.embedding, dtype=np.float64) for e in self._entries])

    def _load_if_exists(self) -> None:
        path = self.persist_path
        if path is None or not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for raw in data.get("entries", []):
                self._entries.append(VaultEntry(**raw))
            self._rebuild_matrix()
        except (json.JSONDecodeError, TypeError, KeyError):
            pass

    def persist(self) -> Path:
        path = self.persist_path or DEFAULT_VAULT_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "brand": SOLUS_BRAND,
            "sovereign": True,
            "third_party": False,
            "formula": FORMAL_COMPOSITION,
            "entries": [asdict(e) for e in self._entries],
            "compound": asdict(self.compound()),
            "saved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        return path

    def deposit(
        self,
        *,
        token: MintedWorkToken,
        receipt: ComputationalReceipt,
        composition: Dict[str, Any],
        results: Dict[str, Any],
        workflow: Optional[Dict[str, Any]] = None,
        ai_patterns: Optional[Dict[str, Any]] = None,
        record_id: str = "",
        cycle_id: str = "",
    ) -> VaultEntry:
        """Store a minted token with full embedded context."""
        wf = workflow or {}
        patterns = ai_patterns or {}
        embedding = self._embedder.embed(
            token=token,
            composition=composition,
            results=results,
            workflow=wf,
            ai_patterns=patterns,
        )
        vault_id = _sha256_text(f"{token.token_id}:{receipt.receipt_id}:{SOLUS_BRAND}")[:24]
        entry = VaultEntry(
            vault_id=vault_id,
            token_id=token.token_id,
            receipt_id=receipt.receipt_id,
            embedding=embedding.tolist(),
            composition={
                "formula": composition.get("formula", FORMAL_COMPOSITION),
                "composition_hash": composition.get("composition_hash"),
                "formal_models": composition.get("formal_models") or list(
                    (composition.get("formal_models_dict") or {}).keys()
                ),
                "proof_steps": composition.get("proof_steps", results.get("proof_steps")),
                "adapted": composition.get("adapted", results.get("adapted")),
                "sovereign": True,
                "third_party": False,
            },
            results={
                "conclusion": results.get("conclusion", ""),
                "match_score": results.get("match_score", receipt.work.get("match_score")),
                "similarity": results.get("similarity", receipt.work.get("similarity")),
                "anomaly": results.get("anomaly", receipt.work.get("anomaly")),
                "logic_confidence": results.get("logic_confidence", receipt.solus_proof.get("logic_confidence")),
                "signal_ratio": results.get("signal_ratio", receipt.solus_proof.get("signal_ratio")),
                "emergence_score": results.get("emergence_score"),
                "composite_score": results.get("composite_score"),
                "neighbors": results.get("neighbors", receipt.work.get("neighbors")),
                "receipt_hash": token.receipt_hash,
            },
            workflow={
                "workflow_id": wf.get("workflow_id", cycle_id),
                "steps": wf.get("steps", []),
                "completed": wf.get("completed"),
                "arms": wf.get("arms", receipt.work.get("arms", [])),
            },
            ai_patterns={
                "formal_models": patterns.get("formal_models")
                or receipt.solus_proof.get("formal_models", []),
                "caretakers": patterns.get("caretakers", receipt.solus_proof.get("caretakers", [])),
                "pattern_xray": patterns.get("pattern_xray"),
                "emerged": patterns.get("emerged", results.get("emerged")),
                "formula": FORMAL_COMPOSITION,
            },
            work_units=token.work_units,
            chain_index=token.chain_index,
            record_id=record_id or receipt.record_id,
            cycle_id=cycle_id or receipt.cycle_id,
            timestamp_ms=round(time.time() * 1000, 2),
        )
        self._entries.append(entry)
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries :]
        self._rebuild_matrix()
        if self.auto_persist:
            self.persist()
        return entry

    def recall(
        self,
        *,
        composition: Optional[Dict[str, Any]] = None,
        results: Optional[Dict[str, Any]] = None,
        workflow: Optional[Dict[str, Any]] = None,
        ai_patterns: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """Recall similar stored tokens — reuse prior work with the AI."""
        if not self._entries or self._matrix is None:
            return {"ok": True, "hits": [], "sovereign": True, "vault_size": 0}

        dummy_token = MintedWorkToken(
            token_id="query",
            receipt_id="query",
            receipt_hash="",
            work_units=1.0,
            chain_index=0,
            sovereign=True,
        )
        query = self._embedder.embed(
            token=dummy_token,
            composition=composition or {},
            results=results or {},
            workflow=workflow or {},
            ai_patterns=ai_patterns or {},
        )
        sims = self._matrix @ query
        idx = np.argsort(-sims)[:top_k]
        hits = []
        for i in idx:
            e = self._entries[int(i)]
            hits.append({
                "vault_id": e.vault_id,
                "token_id": e.token_id,
                "similarity": round(float(sims[int(i)]), 4),
                "work_units": e.work_units,
                "conclusion": e.results.get("conclusion", "")[:160],
                "composition_hash": e.composition.get("composition_hash"),
                "workflow_id": e.workflow.get("workflow_id"),
                "formal_models": e.ai_patterns.get("formal_models", []),
                "record_id": e.record_id,
                "cycle_id": e.cycle_id,
            })
        return {
            "ok": True,
            "hits": hits,
            "vault_size": len(self._entries),
            "sovereign": True,
            "third_party": False,
        }

    def get_token(self, token_id: str) -> Optional[VaultEntry]:
        for e in self._entries:
            if e.token_id == token_id:
                return e
        return None

    def compound(self) -> VaultCompoundState:
        units = sum(e.work_units for e in self._entries)
        return VaultCompoundState(
            total_tokens=len(self._entries),
            total_work_units=round(units, 4),
            verified_entries=len(self._entries),
            formula=FORMAL_COMPOSITION,
            sovereign=True,
        )

    @property
    def size(self) -> int:
        return len(self._entries)

    def to_dict(self) -> Dict[str, Any]:
        c = self.compound()
        return {
            "sovereign": True,
            "third_party": False,
            "brand": SOLUS_BRAND,
            "formula": FORMAL_COMPOSITION,
            "vault_size": c.total_tokens,
            "total_work_units": c.total_work_units,
            "persist_path": str(self.persist_path) if self.persist_path else None,
            "last_entry": asdict(self._entries[-1]) if self._entries else None,
        }