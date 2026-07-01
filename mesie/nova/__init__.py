"""NOVA — adaptive cognitive linguistic translator sphere around MESIE."""

from mesie.nova.sphere import NovaSphere, NovaResponse

try:
    from mesie.version_info import NOVA_VERSION
except ImportError:
    NOVA_VERSION = "1.0.0"

__all__ = ["NovaSphere", "NovaResponse", "NOVA_VERSION"]