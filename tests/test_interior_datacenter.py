"""Interior DC, cluster edge, deployment doctrine."""

from __future__ import annotations

from mesie.production.cluster_edge import ClusterEdgeFabric
from mesie.production.deployment_doctrine import DeploymentClass, build_deployment_doctrine
from mesie.production.interior_datacenter import InteriorDataCenter


def test_interior_dc_catalog():
    dc = InteriorDataCenter()
    report = dc.catalog()
    assert report.sovereign
    assert not report.third_party_cloud
    assert report.total_shards >= 10
    assert report.knowledge["technical_concepts"] >= 10


def test_deployment_doctrine_third_way():
    doc = build_deployment_doctrine()
    assert doc.primary_deployment == DeploymentClass.EDGE_CONTESTED.value
    assert "cloud" in doc.not_a_deploy_target[0].lower()
    assert any(p.profile_id == "gsa_drone_contractor" for p in doc.operator_profiles)
    assert "LLC" in doc.evidence_language["say_instead_of_independent_lab"]


def test_cluster_edge_fabric():
    rep = ClusterEdgeFabric(n_nodes=4, n_agents=200).run()
    assert not rep.cloud_required
    assert rep.interior_dc_shards >= 10
    assert rep.deployment_class == DeploymentClass.CLUSTER_EDGE.value