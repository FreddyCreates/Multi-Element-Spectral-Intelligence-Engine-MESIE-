"""Manipulator hands — MOVE/CONTROL arms to gripper + fleet command envelopes."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from mesie.octopus.arms import ArmId


@dataclass
class HandCommand:
    """Spectral manipulator command — software hands for robotics fleet."""

    action: str  # reach | grip | release | rotate | pulse
    dof: int = 6
    grip_strength: float = 0.85
    spectral_target: Dict[str, Any] = field(default_factory=dict)
    arm_id: str = "move"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HandExecutionReport:
    ok: bool
    command: HandCommand
    arm_responses: Dict[str, Any]
    fusion_dims: int
    threat_p50_ms: Optional[float]
    manipulator_envelope: Dict[str, Any]
    latency_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "command": self.command.to_dict(),
            "arm_responses": self.arm_responses,
            "fusion_dims": self.fusion_dims,
            "threat_p50_ms": self.threat_p50_ms,
            "manipulator_envelope": self.manipulator_envelope,
            "latency_ms": self.latency_ms,
        }


class ManipulatorHands:
    """Arms + hands — octopus MOVE/CONTROL + robotics pulse for fleet dispatch."""

    def __init__(self, *, octopus_controller: Any = None) -> None:
        self._octopus = octopus_controller

    def _controller(self):
        if self._octopus is None:
            from mesie.octopus.controller import OctopusController

            self._octopus = OctopusController()
        return self._octopus

    def execute(self, cmd: HandCommand) -> HandExecutionReport:
        t0 = time.perf_counter()
        ctrl = self._controller()
        arms = ctrl._arms
        arm_responses: Dict[str, Any] = {}

        move_arm = arms.get(ArmId.MOVE)
        control_arm = arms.get(ArmId.CONTROL)
        if move_arm:
            rep = move_arm.reach(
                action="advance" if cmd.action == "reach" else cmd.action,
                payload={"steps": cmd.dof, "delta": 0.1, **cmd.spectral_target},
            )
            arm_responses["move"] = rep.to_dict()
        if control_arm and cmd.action in ("grip", "release", "rotate"):
            rep = control_arm.reach(action=cmd.action, payload={"grip_strength": cmd.grip_strength})
            arm_responses["control"] = rep.to_dict()

        fusion_dims = 0
        threat_p50: Optional[float] = None
        try:
            from mesie.processor.virtual_processor import VirtualProcessor

            pulse = VirtualProcessor().robotics_pulse()
            out = pulse.output if hasattr(pulse, "output") else pulse
            if isinstance(out, dict):
                fusion_dims = int(out.get("fusion_dims", 0))
                threat_p50 = out.get("threat_p50_ms")
        except Exception:
            pass

        envelope = {
            "protocol": "MESIE-MANIPULATOR-HANDS/1.0",
            "action": cmd.action,
            "dof": cmd.dof,
            "grip_strength": cmd.grip_strength,
            "spectral_target": cmd.spectral_target,
            "fleet_route": "robotics_satellite",
            "ts": time.time(),
        }
        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        return HandExecutionReport(
            ok=bool(arm_responses),
            command=cmd,
            arm_responses=arm_responses,
            fusion_dims=fusion_dims,
            threat_p50_ms=threat_p50,
            manipulator_envelope=envelope,
            latency_ms=elapsed,
        )
