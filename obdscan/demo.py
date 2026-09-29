from __future__ import annotations

import math
import time
from types import SimpleNamespace

from obd import Unit

from .ui import console

# name: (base value, swing, period in seconds, unit)
LIVE = {
    "RPM": (2200, 900, 20, "rpm"),
    "SPEED": (60, 40, 30, "kilometer/hour"),
    "COOLANT_TEMP": (90, 3, 60, "degC"),
    "ENGINE_LOAD": (35, 20, 15, "percent"),
    "THROTTLE_POS": (20, 15, 12, "percent"),
    "INTAKE_TEMP": (32, 2, 90, "degC"),
    "INTAKE_PRESSURE": (45, 15, 14, "kilopascal"),
    "MAF": (12, 8, 13, "gram/second"),
    "TIMING_ADVANCE": (15, 8, 17, "degree"),
    "FUEL_LEVEL": (62, 0.5, 120, "percent"),
}


class _Response:
    def __init__(self, value):
        self.value = value

    def is_null(self) -> bool:
        return self.value is None


class FakeOBD:
    """Stands in for obd.OBD. Answers only a subset of commands, like a real car."""

    def __init__(self) -> None:
        self.start = time.perf_counter()
        self.codes = [("P0301", "Cylinder 1 Misfire Detected")]

    def _live(self, name: str) -> _Response:
        base, swing, period, unit = LIVE[name]
        t = time.perf_counter() - self.start
        value = base + swing * math.sin(2 * math.pi * t / period)
        return _Response(Unit.Quantity(value, unit))

    def _monitor(self, name: str) -> _Response:
        tests = {
            i: SimpleNamespace(desc=f"{name} test {i}", value=10 * i + 3,
                                min=0, max=50, passed=(i != 3))
            for i in range(1, 4)
        }
        return _Response(SimpleNamespace(tests=tests))

    def query(self, command, force: bool = False) -> _Response:
        time.sleep(0.03)  # imitate cable latency
        name = command.name
        mode = command.command[:2]

        if name == "GET_DTC":
            return _Response(list(self.codes))
        if name == "GET_CURRENT_DTC":
            return _Response([])
        if name == "CLEAR_DTC":
            self.codes = []
            return _Response("cleared")
        if mode == b"01" and name in LIVE:
            return self._live(name)
        if mode == b"02" and name.startswith("DTC_") and name[4:] in LIVE:
            if not self.codes:  # clearing codes erases the freeze frame
                return _Response(None)
            base, _, _, unit = LIVE[name[4:]]
            return _Response(Unit.Quantity(base, unit))
        if mode == b"06" and sum(name.encode()) % 3 == 0:
            return self._monitor(name)
        return _Response(None)

    def close(self) -> None:
        pass


def connect() -> FakeOBD:
    console.print("[yellow]DEMO MODE: simulated car, no cable used.[/]")
    return FakeOBD()