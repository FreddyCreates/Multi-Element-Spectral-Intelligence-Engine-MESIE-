"""Validation engine — schema and quality checks."""

from __future__ import annotations

from typing import Optional

from mesie.engines.base import Engine
from mesie.internal_api.messages import EngineResponse, MessageEnvelope
from mesie.io.loaders import load_record
from mesie.validation.validators import validate_record


class ValidationEngine(Engine):
    name = "validation"
    capabilities = ["validate"]

    def handle(self, message: MessageEnvelope) -> Optional[EngineResponse]:
        if message.target not in (self.name, "*"):
            return None
        if message.action != "validate":
            return EngineResponse(False, self.name, message.action, error="Unknown action")

        try:
            rec = load_record(message.payload["record"])
            report = validate_record(rec)
            return EngineResponse(
                True,
                self.name,
                "validate",
                {
                    "is_valid": report.is_valid,
                    "level": report.level,
                    "errors": report.errors[:10],
                    "warnings": report.warnings[:10],
                },
            )
        except (KeyError, TypeError, ValueError) as exc:
            return EngineResponse(False, self.name, "validate", error=str(exc))