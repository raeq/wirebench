"""Round-trip tests for `.wirebench` — per spec §12 (#15-18)."""
import json
import warnings
from pathlib import Path

import pytest

# Trigger registration.
import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.board      # noqa: F401

from framework.board import Board
from framework.circuit import Circuit
from framework.format import load_wirebench, save_wirebench
from framework.refdes import RefdesBearing

from water_alarm import WaterAlarm
from water_alarm_split import (
    ControllerBoard, SensorBoard, WaterAlarmAssembly,
)


def _load_silently(*args, **kwargs):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return load_wirebench(*args, **kwargs)


def _save_silently(*args, **kwargs):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return save_wirebench(*args, **kwargs)


def _refdes_set(circuit: Circuit) -> set[str]:
    return {fn.refdes for fn in circuit.parts if isinstance(fn, RefdesBearing)}


def _component_count(circuit: Circuit) -> int:
    return len(circuit.parts)


@pytest.mark.parametrize("factory", [
    lambda: WaterAlarm(),
    lambda: SensorBoard(refdes_number=1),
    lambda: ControllerBoard(refdes_number=2),
    lambda: WaterAlarmAssembly(),
], ids=["WaterAlarm", "SensorBoard", "ControllerBoard", "WaterAlarmAssembly"])
def test_roundtrip_preserves_structure(factory, tmp_path):
    original = factory()
    p1 = tmp_path / "a.wirebench"
    _save_silently(original, p1)
    loaded = _load_silently(p1)

    # Same component count and refdes set.
    assert _component_count(loaded) == _component_count(original)
    assert _refdes_set(loaded) == _refdes_set(original)

    # Save again and assert byte-identical (determinism).
    p2 = tmp_path / "b.wirebench"
    _save_silently(loaded, p2)
    assert p1.read_text() == p2.read_text()


def test_roundtrip_water_alarm_behaves_identically(tmp_path):
    original = WaterAlarm()
    p = tmp_path / "w.wirebench"
    _save_silently(original, p)
    loaded = _load_silently(p)

    VCC, GND = 5.0, 0.0
    inputs = [(GND, GND), (VCC, GND), (VCC, VCC), (VCC, GND), (GND, GND)]
    for low, high in inputs:
        s = original(low, high)
        # Loaded model: drive via surface ports and evaluate.
        loaded._ports['low_probe'].drive(low)
        loaded._ports['high_probe'].drive(high)
        loaded.evaluate()
        a = loaded._ports['state'].value
        assert s == a, f"({low}, {high}): original={s} loaded={a}"


def _drive_and_snapshot(circuit, drives: dict) -> dict:
    """Drive a set of surface ports and return a snapshot of all
    surface-port values after evaluation. Used to compare original vs.
    loaded models without needing subclass-specific accessors."""
    for name, value in drives.items():
        circuit._ports[name].drive(value)
    circuit.evaluate()
    return {name: port.value for name, port in circuit._ports.items()}


def test_roundtrip_water_alarm_assembly_behaves_identically(tmp_path):
    original = WaterAlarmAssembly()
    p = tmp_path / "asm.wirebench"
    _save_silently(original, p)
    loaded = _load_silently(p)

    VCC, GND = 5.0, 0.0
    for low, high in [(GND, GND), (VCC, GND), (VCC, VCC), (VCC, GND), (GND, GND)]:
        drives = {'low_probe': low, 'high_probe': high}
        a = _drive_and_snapshot(original, drives)
        b = _drive_and_snapshot(loaded,   drives)
        assert a == b, f"({low}, {high}): original={a} loaded={b}"


def test_roundtrip_sensor_board_behaves_identically(tmp_path):
    # Standalone boards have BIDIR connector pins whose effective
    # direction is set by toposort only when the connector is mated.
    # Unmated, a second external drive vs. a stale internal value
    # raises a contention error on the second cycle. Limit the test to
    # a single drive cycle — enough to demonstrate that the loaded
    # board behaves identically to the original under the same input.
    original = SensorBoard(refdes_number=1)
    p = tmp_path / "sensor.wirebench"
    _save_silently(original, p)
    loaded = _load_silently(p)

    drives = {'J1.p3': 5.0, 'J1.p4': 0.0}
    a = _drive_and_snapshot(original, drives)
    b = _drive_and_snapshot(loaded,   drives)
    assert a == b, f"original={a} loaded={b}"


def test_roundtrip_controller_board_behaves_identically(tmp_path):
    original = ControllerBoard(refdes_number=2)
    p = tmp_path / "controller.wirebench"
    _save_silently(original, p)
    loaded = _load_silently(p)

    # Single drive cycle (see SensorBoard note above for the reason).
    # Use inputs that avoid latch S=R=1: p5=False, p6=False gives
    # s_1=False, r_1=True (via the inverter) which is a clean reset.
    drives = {'P1.p5': False, 'P1.p6': False}
    a = _drive_and_snapshot(original, drives)
    b = _drive_and_snapshot(loaded,   drives)
    assert a == b, f"original={a} loaded={b}"


def test_determinism_two_saves_byte_identical(tmp_path):
    asm = WaterAlarmAssembly()
    p1 = tmp_path / "1.wirebench"
    p2 = tmp_path / "2.wirebench"
    _save_silently(asm, p1)
    _save_silently(asm, p2)
    assert p1.read_text() == p2.read_text()


def test_hand_edited_file_loads(tmp_path):
    # Minimal sanity-check design: two resistors, no wires.  Resistor
    # terminals are mandatory=False so an unconnected design loads.
    content = {
        "format_version": "1.0.0",
        "root": {
            "type": "Circuit",
            "components": [
                {"type": "Resistor", "refdes": "R1", "ohms": 330},
                {"type": "Resistor", "refdes": "R2", "ohms": 1000},
            ],
            "wires": [],
        },
    }
    p = tmp_path / "hand.wirebench"
    p.write_text(json.dumps(content))
    loaded = _load_silently(p)
    assert len(loaded.parts) == 2
    assert _refdes_set(loaded) == {"R1", "R2"}


def test_mated_assembly_loader_terminates(tmp_path):
    # The mated assembly's logical-net walker traverses Pin conductors;
    # this test verifies the loader can rebuild it without infinite
    # recursion.  (Regression check.)
    asm = WaterAlarmAssembly()
    p = tmp_path / "asm.wirebench"
    _save_silently(asm, p)
    loaded = _load_silently(p)
    assert isinstance(loaded, Circuit)
    assert len(loaded.parts) == 2  # two boards
    for b in loaded.parts:
        assert isinstance(b, Board)
