"""Field Access suite — airgapped world-computer bridge via real frequencies."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data import list_references, load_reference_record
from mesie.sdk import MAESIClient
from mesie.sovereign import FieldAccessEngine, SovereignLocalMode


def main() -> None:
    print("=== Field Access — Airgapped World Computer ===\n")
    refs = [load_reference_record(n) for n in list_references()]
    t0 = time.perf_counter()
    results = []

    engine = FieldAccessEngine()
    conn = engine.connect()
    results.append(("connect", conn.connected and conn.airgapped and not conn.internet_connected))

    for i, ref in enumerate(refs, 1):
        br = engine.bridge(ref)
        ok = br.field_connected and br.sovereign and not br.third_party and br.best_anchor
        results.append((f"bridge_{ref.record_id}", ok))
        print(f"  [{'PASS' if ok else 'FAIL'}] bridge {ref.record_id} → {br.best_anchor} (coherence={br.field_coherence:.3f})")

    sch = engine.align(7.83, top_k=1)
    results.append(("schumann_align", sch[0].alignment_score > 0.5))

    route = engine.route("ground", "world")
    results.append(("route_ground_world", route.ok))

    orbital = engine.route("leo0", "geo", policy="orbital_preferred")
    results.append(("route_orbital", orbital.ok))

    presets = engine.list_presets()
    results.append(("presets_ok", all(p["ok"] for p in presets)))

    health = engine.health()
    results.append(("router_health", health.get("ok")))

    aliases = engine.route("schumann", "root")
    results.append(("alias_route", aliases.ok))

    mode = SovereignLocalMode.active()
    fa = mode.field_access()
    results.append(("sovereign_mode", fa.status()["airgapped"]))

    client = MAESIClient()
    cbr = client.bridge_to_field(refs[0])
    results.append(("maesi_bridge", cbr.sovereign and cbr.field_connected))

    nodes = engine.nodes()
    results.append(("node_mesh", len(nodes) >= 10))

    passed = sum(1 for _, ok in results if ok)
    elapsed = time.perf_counter() - t0
    payload = {
        "suite": "field_access",
        "access_mode": "frequency_field",
        "airgapped": True,
        "internet_connected": False,
        "third_party": False,
        "sovereign": True,
        "world_computer_id": conn.world_computer_id,
        "field_nodes": conn.field_nodes,
        "anchors": conn.anchors,
        "passed": passed,
        "total": len(results),
        "elapsed_s": round(elapsed, 2),
        "connection": {
            "plain_summary": conn.plain_summary,
            "orbital_nodes": conn.orbital_nodes,
            "ladder_tiers": conn.ladder_tiers,
        },
        "bridges": [
            {
                "record": ref.record_id,
                "best_anchor": engine.bridge(ref).best_anchor,
                "coherence": engine.bridge(ref).field_coherence,
            }
            for ref in refs
        ],
        "router": engine.route_table(),
        "health": health,
        "presets": presets,
        "tests": [{"name": n, "ok": ok} for n, ok in results],
    }

    out = ROOT / "deliverables" / "MESIE_Field_Access_Report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"\n{passed}/{len(results)} passed | airgapped field access | {elapsed:.1f}s")
    print(f"World computer: {conn.world_computer_id} | nodes={conn.field_nodes} | anchors={conn.anchors}")
    print(f"Report: {out}")
    print(f"\n{conn.plain_summary}")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()