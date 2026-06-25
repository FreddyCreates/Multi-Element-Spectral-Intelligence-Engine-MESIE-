"""MESIE Virtual Processor — sovereign compute server for coding agents."""

from mesie.processor.accounting import LocalAccountingLedger, LRCReceipt
from mesie.processor.virtual_processor import VirtualProcessor, ProcessorResult

try:
    from mesie.version_info import MESIE_VERSION
except ImportError:
    MESIE_VERSION = "0.4.0"

PROCESSOR_VERSION = "1.0.0"

__all__ = [
    "VirtualProcessor",
    "ProcessorResult",
    "LocalAccountingLedger",
    "LRCReceipt",
    "PROCESSOR_VERSION",
    "MESIE_VERSION",
]