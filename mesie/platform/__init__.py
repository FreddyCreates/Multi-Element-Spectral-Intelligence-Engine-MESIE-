"""MESIE Model Platforms — web surfaces, worker bridge, MVP ↔ protocol routing."""

from mesie.platform.model_catalog import build_unified_model_catalog
from mesie.platform.mvp_bridge import bridge_envelope, bridge_manifest
from mesie.platform.registry import PLATFORM_SERVICES, platform_manifest
from mesie.platform.worker_gateway import PlatformWorkerGateway

__all__ = [
    "PLATFORM_SERVICES",
    "PlatformWorkerGateway",
    "bridge_envelope",
    "bridge_manifest",
    "build_unified_model_catalog",
    "platform_manifest",
]