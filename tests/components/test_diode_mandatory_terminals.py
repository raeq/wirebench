"""Regression test for diode terminals being mandatory.

Every diode subclass declares `anode` and `cathode` ports. A real diode
with a floating terminal does nothing — leaving it unwired silently
violates the framework's physical-fidelity contract and produces
breadboard layouts where the diode sits with no jumpers attached.

Earlier these were `mandatory=False` to let demos declare BOM-only
parts (e.g. flyback diodes whose anode wasn't modelled in the
voltage-only graph); that pattern is exactly the bug this test exists
to catch.

Related: `tests/components/test_led.py` covers LED's anode/cathode and
`tests/components/test_resistor.py` covers Resistor's two terminals.
"""
from __future__ import annotations

import pytest

from components.diodes.d1n4001 import D1N4001
from components.diodes.d1n4007 import D1N4007
from components.diodes.d1n4148 import D1N4148
from components.diodes.d1n4728a import D1N4728A
from components.diodes.d1n4733a import D1N4733A
from components.diodes.d1n4742a import D1N4742A
from components.diodes.d1n5817 import D1N5817


_DIODE_CLASSES = [
    D1N4001, D1N4007, D1N4148,
    D1N4728A, D1N4733A, D1N4742A,
    D1N5817,
]


@pytest.mark.parametrize('cls', _DIODE_CLASSES, ids=[c.__name__ for c in _DIODE_CLASSES])
def test_diode_terminals_are_mandatory(cls):
    """Both anode and cathode must be `mandatory=True` on every diode
    subclass."""
    d = cls(refdes_number=1)
    assert d.ports['anode'].mandatory is True, (
        f"{cls.__name__}.anode must be mandatory — a real diode with "
        "a floating anode has no current path and does nothing."
    )
    assert d.ports['cathode'].mandatory is True, (
        f"{cls.__name__}.cathode must be mandatory — a real diode "
        "with a floating cathode has no current path and does nothing."
    )


@pytest.mark.parametrize('cls', _DIODE_CLASSES, ids=[c.__name__ for c in _DIODE_CLASSES])
def test_floating_diode_refused_at_circuit_construction(cls):
    """A Circuit that declares a diode but doesn't wire its terminals
    raises `UnconnectedPinError` at construction."""
    from framework.circuit import Circuit
    from framework.errors import UnconnectedPinError

    class _DanglingDiode(Circuit):
        def __init__(self) -> None:
            self.d = cls(refdes_number=1)
            super().__init__()

    with pytest.raises(UnconnectedPinError, match=cls.__name__):
        _DanglingDiode()
