#!/usr/bin/env python3
"""Enterprise federation suite — multi-user polyglot + arms/hands + manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.enterprise.federation import FederationOrchestrator
from mesie.enterprise.federation.protocol import EnterpriseFederationEnvelope


def main() -> int:
    orch = FederationOrchestrator()
    manifest = orch.export_manifest()

    env = EnterpriseFederationEnvelope(
        agent_id="suite-runner",
        tenant_id="default",
        org_id="mesie-enterprise",
        tool="polyglot.fingerprint",
        runtime="haskell",
        payload={"record": "earthquake_psd_reference"},
        delegation_chain=["cursor", "mesie-orchestrator"],
    )
    fp = orch.invoke(env)

    hands_env = EnterpriseFederationEnvelope(
        agent_id="suite-runner",
        tenant_id="default",
        tool="hands.pulse",
        hand_command={"action": "pulse", "dof": 6},
    )
    hands = orch.invoke(hands_env)

    report = {
        "ok": fp.get("ok") and hands.get("ok"),
        "manifest": manifest,
        "fingerprint_invoke": {"tool": fp.get("tool"), "latency_ms": fp.get("latency_ms")},
        "hands_invoke": {"tool": hands.get("tool"), "latency_ms": hands.get("latency_ms")},
        "registry": orch.registry.status(),
    }
    out = ROOT / "deliverables" / "enterprise" / "ENTERPRISE_FEDERATION_REPORT.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
