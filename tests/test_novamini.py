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