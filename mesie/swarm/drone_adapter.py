"""Drone platform adapter — PX4 / MAVSDK bridge interface."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from mesie.io.loaders import RecordInput


class DronePlatform(str, Enum):
    PX4 = "px4"
    MAVSDK = "mavsdk"
    GENERIC_UDP = "generic_udp"
    SIM = "sim"


@dataclass
class DroneCommand:
    command: str
    agent_id: str
    params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"command": self.command, "agent_id": self.agent_id, "params": self.params}


@dataclass
class AdapterStatus:
    platform: str
    connected: bool
    n_drones: int
    sim_mode: bool
    mavlink_port: int
    commands_queued: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "connected": self.connected,
            "n_drones": self.n_drones,
            "sim_mode": self.sim_mode,
            "mavlink_port": self.mavlink_port,
            "commands_queued": self.commands_queued,
        }


class DronePlatformAdapter:
    """Unified adapter — sim today, PX4/MAVSDK when hardware connected."""

    def __init__(
        self,
        platform: DronePlatform = DronePlatform.SIM,
        *,
        mavlink_port: int = 14540,
        n_drones: int = 1,
    ) -> None:
        self.platform = platform
        self.mavlink_port = mavlink_port
        self.n_drones = n_drones
        self._commands: List[DroneCommand] = []
        self._connected = platform == DronePlatform.SIM

    def connect(self) -> AdapterStatus:
        if self.platform == DronePlatform.MAVSDK:
            self._connected = self._probe_mavsdk()
        elif self.platform == DronePlatform.PX4:
            self._connected = self._probe_px4()
        else:
            self._connected = True
        return self.status()

    def _probe_mavsdk(self) -> bool:
        try:
            import mavsdk  # noqa: F401
            return False
        except ImportError:
            return False

    def _probe_px4(self) -> bool:
        return False

    def dispatch_spectral_threat(
        self,
        agent_id: str,
        *,
        threat: bool,
        route_id: str,
        score: float,
    ) -> DroneCommand:
        cmd = DroneCommand(
            command="engage" if threat else "hold",
            agent_id=agent_id,
            params={"route_id": route_id, "score": score, "platform": self.platform.value},
        )
        self._commands.append(cmd)
        return cmd

    def dispatch_formation(self, formation: str, agent_ids: List[str]) -> List[DroneCommand]:
        cmds = []
        for aid in agent_ids:
            c = DroneCommand("formation", aid, {"shape": formation})
            self._commands.append(c)
            cmds.append(c)
        return cmds

    def ingest_telemetry_spectrum(self, record: RecordInput) -> Dict[str, Any]:
        from mesie import validate_record
        from mesie.io.loaders import load_record

        rec = load_record(record)
        vr = validate_record(rec)
        return {
            "ok": vr.is_valid,
            "record_id": rec.record_id,
            "points": len(rec.components[0].frequency),
            "platform": self.platform.value,
        }

    def status(self) -> AdapterStatus:
        return AdapterStatus(
            platform=self.platform.value,
            connected=self._connected,
            n_drones=self.n_drones,
            sim_mode=self.platform == DronePlatform.SIM,
            mavlink_port=self.mavlink_port,
            commands_queued=len(self._commands),
        )

    def flush_commands(self) -> List[Dict[str, Any]]:
        out = [c.to_dict() for c in self._commands]
        self._commands.clear()
        return out