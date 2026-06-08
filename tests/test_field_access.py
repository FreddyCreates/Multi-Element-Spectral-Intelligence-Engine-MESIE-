"""Tests for airgapped field access — world computer via frequencies."""

from data import list_references, load_reference_record
from mesie.sovereign import FieldAccessEngine, SovereignLocalMode


def test_field_access_airgapped_connect():
    engine = FieldAccessEngine()
    conn = engine.connect()
    assert conn.connected
    assert conn.airgapped is True
    assert conn.internet_connected is False
    assert conn.sovereign is True
    assert conn.third_party is False
    assert conn.field_nodes >= 5
    assert conn.anchors >= 10


def test_bridge_spectrum_to_field():
    ref = load_reference_record(list_references()[0])
    engine = FieldAccessEngine()
    report = engine.bridge(ref)
    assert report.airgapped
    assert report.field_connected
    assert report.third_party is False
    assert report.best_anchor
    assert len(report.alignments) >= 1
    assert report.field_coherence >= 0


def test_schumann_alignment():
    engine = FieldAccessEngine()
    hits = engine.align(7.83, top_k=3)
    assert hits[0].anchor_id.startswith("schumann") or "schumann" in hits[0].anchor_name.lower()
    assert hits[0].alignment_score > 0.5


def test_field_mesh_route():
    engine = FieldAccessEngine()
    route = engine.route("ground", "ionosphere")
    assert route.ok
    assert route.airgapped
    assert route.sovereign
    assert len(route.hops) >= 2


def test_sovereign_local_mode_field_access():
    mode = SovereignLocalMode.active()
    fa = mode.field_access()
    status = fa.status()
    assert status["airgapped"]
    assert status["internet_connected"] is False
    assert status["access_mode"] == "frequency_field"