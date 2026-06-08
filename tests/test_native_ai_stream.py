"""Native local AI — stream + generate deliverables inside SDK."""

import json
from pathlib import Path

from data import list_references, load_reference_record
from mesie.sdk import MAESIClient, FORMAL_COMPOSITION, SOLUS_BRAND
from mesie.sdk.native_ai import NativeLocalAIEngine, StreamPhase
from mesie.sdk.native_ai.deliverables import DeliverableWriter


def test_stream_phases(tmp_path):
    refs = [load_reference_record(n) for n in list_references()[:4]]
    engine = NativeLocalAIEngine(
        session_id="test-stream",
        deliverable_dir=str(tmp_path / "out"),
    )
    phases = []
    gen = engine.stream_generate(refs, run_id="stream_test", write_deliverable=True)
    try:
        while True:
            ev = next(gen)
            phases.append(ev.phase)
            assert ev.sovereign
            assert ev.third_party is False
    except StopIteration as stop:
        report = stop.value

    assert report is not None
    assert StreamPhase.BOOT in phases
    assert StreamPhase.LOGIC in phases
    assert StreamPhase.VAULT in phases
    assert StreamPhase.DELIVERABLE in phases
    assert StreamPhase.COMPLETE in phases
    assert report.bundle.json_path.exists()
    assert report.bundle.markdown_path.exists()


def test_generate_deliverable_content(tmp_path):
    refs = [load_reference_record(n) for n in list_references()[:3]]
    engine = NativeLocalAIEngine(deliverable_dir=str(tmp_path / "gen"))
    report = engine.generate(refs, run_id="content_test")
    data = json.loads(report.bundle.json_path.read_text(encoding="utf-8"))
    assert data["sovereign"] is True
    assert data["third_party"] is False
    assert data["formula"] == FORMAL_COMPOSITION
    assert data["minted_token"]["token_id"]
    assert data["vault"]["vault_size"] >= 1


def test_maesi_client_native_ai_stream(tmp_path):
    refs = [load_reference_record(n) for n in list_references()[:3]]
    client = MAESIClient()
    client.native_ai.deliverable_dir = str(tmp_path / "client")
    report = client.generate_native_deliverable(refs, run_id="client_test")
    assert report.brand == SOLUS_BRAND
    assert len(report.neighbors) >= 0
    assert report.stream_events >= 10


def test_deliverable_writer_markdown():
    writer = DeliverableWriter(output_dir=Path("."))
    md = writer._markdown({
        "run_id": "x",
        "formula": FORMAL_COMPOSITION,
        "plain_summary": "ok",
        "vault": {"vault_size": 2, "compound_work_units": 1.5},
    })
    assert "Native Local AI" in md
    assert FORMAL_COMPOSITION in md