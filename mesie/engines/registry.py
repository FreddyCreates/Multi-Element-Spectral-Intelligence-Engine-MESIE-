"""Default engine registry for internal API."""

from __future__ import annotations

from mesie.engines.base import EngineRegistry
from mesie.engines.control_engine import ControlEngine
from mesie.engines.embedding_engine import EmbeddingEngine
from mesie.engines.generation_engine import GenerationEngine
from mesie.engines.intelligence_engine import IntelligenceEngine
from mesie.engines.logic_engine import LogicEngine
from mesie.engines.matching_engine import MatchingEngine
from mesie.engines.movement_engine import MovementEngine
from mesie.engines.validation_engine import ValidationEngine
from mesie.engines.workflow_engine import WorkflowEngine
from mesie.internal_api.bus import InternalBus


def build_default_registry(bus: InternalBus | None = None) -> EngineRegistry:
    """Register all built-in engines; attach workflow engine to bus."""
    registry = EngineRegistry()
    bus = bus or InternalBus()

    engines = [
        EmbeddingEngine(),
        MatchingEngine(),
        GenerationEngine(),
        ValidationEngine(),
        IntelligenceEngine(),
        ControlEngine(),
        MovementEngine(),
        LogicEngine(),
    ]
    workflow = WorkflowEngine(bus=bus)
    engines.append(workflow)

    for eng in engines:
        registry.register(eng)
        bus.register_engine(eng.name, eng.handle)

    return registry