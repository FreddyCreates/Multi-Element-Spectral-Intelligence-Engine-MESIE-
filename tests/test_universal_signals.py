"""Universal signal plane — read + generate."""

from __future__ import annotations

from mesie.signals import SignalTextEmitter, UniversalSignalReader


def test_read_text_signal():
    r = UniversalSignalReader().read("Everything is a signal", hint="text")
    assert r.modality.value == "text"
    assert r.fingerprint
    assert len(r.spectral_signature) > 0


def test_read_json_event():
    r = UniversalSignalReader().read({"event": "alert", "severity": 3})
    assert r.modality.value in ("json", "event", "state")
    assert r.fingerprint


def test_generate_analyst_brief():
    e = SignalTextEmitter().generate("orbital edge harmonic coupling", style="analyst_brief", max_chars=800)
    assert e.sovereign is True
    assert len(e.text) > 20
    assert e.signal_fingerprint