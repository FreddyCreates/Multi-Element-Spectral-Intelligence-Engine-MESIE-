"""Production field router tests."""

from mesie.sovereign import RoutePolicy, get_field_access_engine


def test_alias_resolve():
    fa = get_field_access_engine(reset=True)
    assert fa.resolve("ground") == "ground-schumann"
    assert fa.resolve("world") == "world-computer-root"
    assert fa.resolve("leo0") == "orbital-leo-edge-000"


def test_route_ground_to_world():
    fa = get_field_access_engine(reset=True)
    r = fa.route("ground", "world")
    assert r.ok
    assert r.resolved_source == "ground-schumann"
    assert r.resolved_destination == "world-computer-root"
    assert len(r.hops) >= 2
    assert r.airgapped and r.sovereign and not r.third_party


def test_route_leo_to_geo():
    fa = get_field_access_engine(reset=True)
    r = fa.route("leo0", "geo", policy=RoutePolicy.ORBITAL_PREFERRED)
    assert r.ok
    assert "orbital" in r.resolved_source
    assert "geo" in r.resolved_destination


def test_presets_all_ok():
    fa = get_field_access_engine(reset=True)
    presets = fa.list_presets()
    assert len(presets) >= 8
    assert all(p["ok"] for p in presets)


def test_health_ready():
    fa = get_field_access_engine(reset=True)
    h = fa.health()
    assert h["ok"]
    assert h["graph_ready"]
    assert h["default_route_ok"]


def test_maesi_route_field():
    from mesie.sdk import MAESIClient

    client = MAESIClient()
    r = client.route_field("ground", "ionosphere")
    assert r.ok