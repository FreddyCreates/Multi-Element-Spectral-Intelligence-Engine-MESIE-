"""Polyglot engine — exposes AISVectorPolyglot on the internal bus."""

from __future__ import annotations

from typing import Optional

from mesie.engines.base import Engine
from mesie.internal_api.messages import EngineResponse, MessageEnvelope
from mesie.io.loaders import load_record
from mesie.polyglot.contract import AISVectorMessage, PolyglotAction, RuntimeId
from mesie.polyglot.suite import AISVectorPolyglotSuite


class PolyglotEngine(Engine):
    name = "polyglot"
    capabilities = ["validate", "match", "embed", "rank", "vector_query", "parity", "health"]

    def __init__(self, suite: Optional[AISVectorPolyglotSuite] = None) -> None:
        self._suite = suite or AISVectorPolyglotSuite()

    @property
    def suite(self) -> AISVectorPolyglotSuite:
        return self._suite

    def handle(self, message: MessageEnvelope) -> Optional[EngineResponse]:
        if message.target not in (self.name, "*"):
            return None
        action = message.action
        if action not in self.capabilities:
            return EngineResponse(False, self.name, action, error=f"Unknown action: {action}")

        try:
            if action == "health":
                h = self._suite.health()
                return EngineResponse(True, self.name, action, {"name": h.name, "runtimes": h.runtimes})

            if action == "parity":
                a = load_record(message.payload["record_a"])
                b = load_record(message.payload["record_b"])
                return EngineResponse(True, self.name, action, self._suite.parity_matrix(a, b))

            if action == "vector_query":
                rec = load_record(message.payload["record"])
                top_k = int(message.payload.get("top_k", 5))
                q = self._suite.vector_query(rec, top_k=top_k)
                return EngineResponse(
                    True,
                    self.name,
                    action,
                    {
                        "record_id": q.record_id,
                        "neighbors": q.neighbors,
                        "fingerprint_hits": q.fingerprint_hits,
                        "technical_hits": q.technical_hits,
                        "elapsed_ms": q.elapsed_ms,
                    },
                )

            runtime = RuntimeId(message.payload.get("runtime", self._suite.routing.get(
                PolyglotAction(action), RuntimeId.PYTHON
            ).value))

            if action == "validate":
                resp = self._suite.validate(message.payload["record"], runtime)
            elif action == "match":
                resp = self._suite.match(
                    message.payload["record_a"],
                    message.payload["record_b"],
                    runtime,
                )
            elif action == "embed":
                resp = self._suite.embed(message.payload["record"], runtime)
            elif action == "rank":
                msg = AISVectorMessage(
                    action=PolyglotAction.RANK,
                    runtime=runtime,
                    record=message.payload.get("record"),
                    candidates=message.payload.get("candidates", []),
                    top_k=int(message.payload.get("top_k", 5)),
                )
                resp = self._suite.dispatch(msg)
            else:
                return EngineResponse(False, self.name, action, error="unhandled")

            return EngineResponse(resp.ok, self.name, action, resp.to_dict(), error=resp.error)
        except (KeyError, TypeError, ValueError) as exc:
            return EngineResponse(False, self.name, action, error=str(exc))