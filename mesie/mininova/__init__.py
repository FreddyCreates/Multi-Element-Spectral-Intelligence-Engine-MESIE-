"""MININOVA — lightweight adaptive sphere around NOVAMINI (MESIE-LM)."""

from mesie.mininova.sphere import MiniNovaResponse, MiniNovaSphere

try:
    from mesie.version_info import MININOVA_VERSION
except ImportError:
    MININOVA_VERSION = "1.0.0"

__all__ = ["MiniNovaSphere", "MiniNovaResponse", "MININOVA_VERSION"]