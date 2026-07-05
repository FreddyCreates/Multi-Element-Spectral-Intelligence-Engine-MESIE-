"""Alpha coding harnesses + template library for native-AI product surfaces."""

from mesie.harness.alpha_registry import ALPHA_HARNESSES, harness_manifest
from mesie.harness.template_library import TEMPLATE_LIBRARY, template_manifest
from mesie.harness.auto_business import AUTO_AI_BUSINESSES, auto_business_catalog

__all__ = [
    "ALPHA_HARNESSES",
    "harness_manifest",
    "TEMPLATE_LIBRARY",
    "template_manifest",
    "AUTO_AI_BUSINESSES",
    "auto_business_catalog",
]