"""Universal signal layer — everything is a signal, not only spectra."""

from mesie.signals.text_emitter import SignalTextEmitter, TextEmission
from mesie.signals.universal_reader import SignalModality, SignalReadResult, UniversalSignalReader

__all__ = [
    "SignalModality",
    "SignalReadResult",
    "UniversalSignalReader",
    "SignalTextEmitter",
    "TextEmission",
]