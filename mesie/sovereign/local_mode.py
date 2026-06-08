"""Sovereign Local Mode — one switchboard for offline, own-models-only operation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from mesie.octopus.controller import OctopusConfig, OctopusController
from mesie.sdk import MAESIClient
from mesie.sdk.solus import (
    FORMAL_COMPOSITION,
    LOCAL_ENGINE,
    OWN_MODELS_ONLY,
    SDKSolusOrganism,
    SOLUS_BRAND,
    SolusFormalStack,
    composition_manifest,
)


@dataclass(frozen=True)
class SovereignLocalMode:
    """Central config: sovereign=True, third_party=False, SOLUS local engine only."""

    sovereign: bool = True
    third_party: bool = False
    engine: str = LOCAL_ENGINE
    brand: str = SOLUS_BRAND
    formula: str = FORMAL_COMPOSITION
    own_models_only: bool = OWN_MODELS_ONLY
    sla_latency_ms: float = 150.0
    session_id: str = "sovereign-local"
    deliverable_subdir: str = "sovereign_local"

    @classmethod
    def active(cls) -> SovereignLocalMode:
        return cls()

    def manifest(self) -> Dict[str, Any]:
        base = composition_manifest()
        return {
            **base,
            "mode": "sovereign-local",
            "own_models_only": self.own_models_only,
            "sla_latency_ms": self.sla_latency_ms,
        }

    @staticmethod
    def assert_payload(payload: Dict[str, Any]) -> None:
        if payload.get("sovereign") is False:
            raise AssertionError("expected sovereign=True")
        if payload.get("third_party") is True:
            raise AssertionError("expected third_party=False")

    def maesi_client(self) -> MAESIClient:
        return MAESIClient(
            fast=True,
            use_fingerprint=True,
            use_solus_caretakers=True,
            use_solus_math_layer=True,
        )

    def octopus_config(self) -> OctopusConfig:
        return OctopusConfig(use_solus_memory=True, use_polyglot_arms=True)

    def octopus(self) -> OctopusController:
        return OctopusController(config=self.octopus_config())

    def copilot(self, *, session_id: Optional[str] = None, sla_latency_ms: Optional[float] = None):
        from mesie.enterprise.copilot import EnterpriseAICopilot

        return EnterpriseAICopilot(
            session_id=session_id or self.session_id,
            sla_latency_ms=sla_latency_ms or self.sla_latency_ms,
            use_octopus=True,
        )

    def native_ai(self, root: Optional[Path] = None):
        from mesie.sdk.native_ai import NativeLocalAIEngine

        base = root or Path(__file__).resolve().parents[2]
        out = base / "deliverables" / "native_ai" / self.deliverable_subdir
        return NativeLocalAIEngine(session_id=self.session_id, deliverable_dir=str(out))

    def organism(self) -> SDKSolusOrganism:
        return SDKSolusOrganism()

    def formal_stack(self) -> SolusFormalStack:
        return SolusFormalStack()

    def field_access(self):
        """Airgapped field bridge — world computer via frequencies, not WiFi."""
        from mesie.sovereign.field_access import get_field_access_engine

        return get_field_access_engine()


def sovereign_active() -> SovereignLocalMode:
    """Return the active sovereign local mode singleton config."""
    return SovereignLocalMode.active()