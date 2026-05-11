"""Round-trip tests for `.circuitry` — per spec §12 (#15-18)."""
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
from framework.format import load_circuitry, save_circuitry
from framework.refdes import RefdesBearing

from water_alarm import WaterAlarm
from water_alarm_split import (
    ControllerBoard, SensorBoard, WaterAlarmAssembly,
)


def _load_silently(*args, **kwargs):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return load_circuitry(*args, **kwargs)


def _save_silently(*args, **kwargs):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return save_circuitry(*args, **kwargs)


def _refdes_set(circuit: Circuit) -> set[str]:
    return {fn.refdes for fn in circuit._factor_nodes if isinstance(fn, RefdesBearing)}


def _component_count(circuit: Circuit) -> int:
    return len(circuit._factor_nodes)


@pytest.mark.parametrize("factory", [
    lambda: WaterAlarm(),
    lambda: SensorBoard(refdes_number=1),
    lambda: ControllerBoard(refdes_number=2),
    lambda: WaterAlarmAssembly(),
], ids=["WaterAlarm", "SensorBoard", "ControllerBoard", "WaterAlarmAssembly"])
def test_roundtrip_preserves_structure(factory, tmp_path):
    original = factory()
    p1 = tmp_path / "a.circuitry"
    _save_silently(original, p1)
    loaded = _load_silently(p1)

    # Same component count and refdes set.
    assert _component_count(loaded) == _component_count(original)
    assert _refdes_set(loaded) == _refdes_set(original)

    # Save again and assert byte-identical (determinism).
    p2 = tmp_path / "b.circuitry"
    _save_silently(loaded, p2)
    assert p1.read_text() == p2.read_text()


def test_roundtrip_water_alarm_behaves_identically(tmp_path):
    original = WaterAlarm()
    p = tmp_path / "w.circuitry"
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


def test_determinism_two_saves_byte_identical(tmp_path):
    asm = WaterAlarmAssembly()
    p1 = tmp_path / "1.circuitry"
    p2 = tmp_path / "2.circuitry"
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
    p = tmp_path / "hand.circuitry"
    p.write_text(json.dumps(content))
    loaded = _load_silently(p)
    assert len(loaded._factor_nodes) == 2
    assert _refdes_set(loaded) == {"R1", "R2"}


def test_mated_assembly_loader_terminates(tmp_path):
    # The mated assembly's logical-net walker traverses Pin conductors;
    # this test verifies the loader can rebuild it without infinite
    # recursion.  (Regression check.)
    asm = WaterAlarmAssembly()
    p = tmp_path / "asm.circuitry"
    _save_silently(asm, p)
    loaded = _load_silently(p)
    assert isinstance(loaded, Circuit)
    assert len(loaded._factor_nodes) == 2  # two boards
    for b in loaded._factor_nodes:
        assert isinstance(b, Board)
