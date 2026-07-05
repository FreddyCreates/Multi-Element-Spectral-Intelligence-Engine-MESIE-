"""NOVAMINI (MESIE-LM) — runtime, MAQUE, spectral memory."""

from __future__ import annotations

import json
from pathlib import Path

from mesie.novamini.maque import message, route, Vivi, FLOS
from mesie.novamini.runtime import NovaMiniRuntime, MODEL_ID
from mesie.novamini.spectral_memory import SpectralMemory, text_to_spectrum


def test_spectral_signature_stable():
    a = text_to_spectrum("hello novamini")
    b = text_to_spectrum("hello novamini")
    assert a.shape == b.shape
    assert float((a - b).max()) < 1e-9


def test_spectral_memory_recall(tmp_path: Path):
    mem = SpectralMemory(vault_dir=tmp_path / "vault")
    mem.store("What is NOVAMINI?", "NOVAMINI is the mini Nova runtime on MESIE-LM.")
    mem.store("weather today", "unrelated")
    hits = mem.recall("Tell me about NOVAMINI")
    assert hits
    assert "NOVAMINI" in hits[0]["spoken"] or "NOVAMINI" in hits[0]["user"]


def test_maque_message_shape():
    v = Vivi.spawn("NMIN")
    msg = message(sender="NMIN", receiver="LING", verb="query", via="NOVMINI", vivi=v, body={"text": "hi"})
    assert msg["maque"]["from"] == "NMIN"
    assert msg["maque"]["via"] == "NOVMINI"
    assert "NOVMINI" in FLOS


def test_novamini_chat_sovereign(tmp_path: Path):
    rt = NovaMiniRuntime(session_id="test-novamini", vault_root=tmp_path)
    resp = rt.chat("Who are you?")
    assert resp.sovereign is True
    assert resp.model_id == MODEL_ID
    assert resp.spoken
    assert resp.latency_ms >= 0
    assert "maque" in resp.to_dict()


def test_novamini_export_manifest(tmp_path: Path):
    rt = NovaMiniRuntime(session_id="export-test", vault_root=tmp_path)
    out = tmp_path / "manifest.json"
    rt.export_manifest(out)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["product"] == "NOVAMINI (MESIE-LM)"
    assert data["status"]["third_party_inference"] is False
    assert "sample" in data


# ── Artifact ingestion — "reason off whole artifacts," not just chat turns ──

def test_artifact_ingest_and_recall(tmp_path: Path):
    mem = SpectralMemory(vault_dir=tmp_path / "vault")
    text = (
        "RECITAL_PLUS_ONE requires every write to chain its prior_hash or be a "
        "genesis write. DUAL_READ enforces tier gating on every read."
    )
    result = mem.ingest_artifact("protocol-notes", text)
    assert result["ok"] is True
    assert result["chunks_indexed"] >= 1

    hits = mem.recall_artifacts("What does RECITAL_PLUS_ONE require?")
    assert hits
    assert any("prior_hash" in h["text"] for h in hits)
    assert mem.artifacts()[0]["name"] == "protocol-notes"


def test_artifact_ingest_empty_text_rejected(tmp_path: Path):
    mem = SpectralMemory(vault_dir=tmp_path / "vault")
    result = mem.ingest_artifact("empty", "   ")
    assert result["ok"] is False
    assert result["reason"] == "EMPTY_ARTIFACT"


def test_recall_all_separates_turns_and_artifacts(tmp_path: Path):
    mem = SpectralMemory(vault_dir=tmp_path / "vault")
    mem.store("What is NOVAMINI?", "NOVAMINI is the mini Nova runtime on MESIE-LM.")
    mem.ingest_artifact("notes", "RECITAL_PLUS_ONE chains every write to its prior_hash.")
    combined = mem.recall_all("RECITAL_PLUS_ONE prior_hash")
    assert "turns" in combined and "artifacts" in combined
    assert combined["artifacts"]


def test_artifact_persists_across_memory_instances(tmp_path: Path):
    vault = tmp_path / "vault"
    mem1 = SpectralMemory(vault_dir=vault)
    mem1.ingest_artifact("persisted-doc", "The phi heartbeat is 873 milliseconds.")
    mem2 = SpectralMemory(vault_dir=vault)
    assert len(mem2.artifacts()) == 1
    hits = mem2.recall_artifacts("phi heartbeat milliseconds")
    assert hits


def test_novamini_learn_ingests_real_file(tmp_path: Path):
    src = tmp_path / "doc.txt"
    src.write_text(
        "MEDINA-PROTOCOL/0.5 defines four vault tiers: PUBLIC, SHARED, PRIVATE, SOVEREIGN.",
        encoding="utf-8",
    )
    rt = NovaMiniRuntime(session_id="learn-test", vault_root=tmp_path / "vault")
    result = rt.learn(src)
    assert result["ok"] is True
    assert result["name"] == "doc.txt"
    assert rt.status()["memory"]["artifacts"] == 1


def test_novamini_learn_raw_text(tmp_path: Path):
    rt = NovaMiniRuntime(session_id="learn-text-test", vault_root=tmp_path / "vault")
    result = rt.learn("Arbitrary pasted knowledge about phi and the heartbeat.", name="pasted-note")
    assert result["ok"] is True
    assert result["name"] == "pasted-note"


def test_novamini_chat_grounds_response_in_learned_artifact(tmp_path: Path):
    rt = NovaMiniRuntime(session_id="grounded-chat-test", vault_root=tmp_path / "vault")
    rt.learn(
        "RECITAL_PLUS_ONE requires every write to chain its prior_hash or be a genesis write.",
        name="protocol-notes",
    )
    resp = rt.chat("What does RECITAL_PLUS_ONE require?")
    assert "prior_hash" in resp.spoken
    assert any(h["source"] == "artifact" for h in resp.memory_hits)