"""Enterprise execution engine smoke tests."""

from __future__ import annotations

from pathlib import Path


def test_repo_unifier_thread():
    from mesie.enterprise.repo_unifier import build_thread_manifest, write_thread_manifest

    m = build_thread_manifest()
    assert m["product_count"] >= 14
    assert m["repos"][0]["id"] == "mesie-main"
    r = write_thread_manifest()
    assert Path(r["path"]).is_file()


def test_dag_list():
    from mesie.enterprise.execution_engine import EnterpriseExecutionEngine, _write_dag, DAG_PATH

    _write_dag()
    assert DAG_PATH.is_file()
    import json

    dag = json.loads(DAG_PATH.read_text(encoding="utf-8"))
    assert len(dag["nodes"]) == 13


def test_engine_partial_run():
    from mesie.enterprise.execution_engine import EnterpriseExecutionEngine

    eng = EnterpriseExecutionEngine(mission_id="test-partial")
    r = eng.run(
        stop_on_fail=False,
        skip=[
            "nova_snapshot",
            "compute_benchmark",
            "colony_bridge",
            "research_metamaterial",
            "sandbox_loop",
            "tri_agent_quality",
            "package_release",
        ],
    )
    assert r["nodes_run"] >= 5
    assert any(x.get("name") == "unify_repos" and x.get("ok") for x in r["results"])