"""Satellite micro agents — timer-driven background workers with careers."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from mesie.agentic.micro.brain import MiniBrain
from mesie.agentic.micro.career import MicroCareer


TaskFn = Callable[[MiniBrain], Dict[str, Any]]


@dataclass
class SatelliteAgent:
    """Micro agent that runs on an interval (satellite mode) or once."""

    brain: MiniBrain
    task_fn: TaskFn
    interval_s: float
    _timer: Optional[threading.Timer] = field(default=None, init=False, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    _satellite_active: bool = field(default=False, init=False, repr=False)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def run_once(self) -> Dict[str, Any]:
        with self._lock:
            try:
                result = self.task_fn(self.brain)
                pulse = self.brain.pulse(result)
                entry = {"pulse": pulse, "result": result, "ts": time.time()}
                self.history.append(entry)
                if len(self.history) > 64:
                    self.history = self.history[-64:]
                return entry
            except Exception as exc:
                err = {"ok": False, "error": str(exc)}
                self.brain.pulse(err)
                return {"pulse": self.brain.status(), "result": err, "ts": time.time()}

    def _tick(self) -> None:
        if not self.brain.alive:
            return
        self.run_once()
        self._schedule()

    def _schedule(self) -> None:
        if not self.brain.alive:
            return
        self._timer = threading.Timer(self.interval_s, self._tick)
        self._timer.daemon = True
        self._timer.start()

    def launch_satellite(self, *, immediate: bool = False) -> None:
        """Start recurring timer loop. immediate=True only for single-agent demos."""
        if self._satellite_active:
            return
        self._satellite_active = True
        if immediate:
            self.run_once()
        self._schedule()

    @property
    def satellite_active(self) -> bool:
        return self._satellite_active

    def stop(self) -> None:
        self.brain.retire()
        self._satellite_active = False
        if self._timer:
            self._timer.cancel()
            self._timer = None

    @property
    def status(self) -> Dict[str, Any]:
        return {
            **self.brain.status(),
            "interval_s": self.interval_s,
            "satellite_active": self.satellite_active,
            "history_len": len(self.history),
            "last": self.history[-1] if self.history else None,
        }