import pytest
from framework.chip import Chip
from framework.errors import WiredChipCallError
from framework.ground import ELECTRICAL
from framework.pin import Pin, PinId
from framework.port import Port, Direction
from framework.signals import Digital
from framework.wire import wire


# --- Abstract base ---

def test_chip_is_abstract_without_call():
    # Chip declares __call__ as @abstractmethod, so direct instantiation fails.
    with pytest.raises(TypeError):
        Chip(pins=[], cells=[])


# A minimal concrete subclass for the rest of the tests: one IN pin
# 'a' wired through to one OUT pin 'y' via no internal cell — just the
# pin-to-pin shorthand of testing Chip mechanics in isolation.
class _PassChip(Chip):
    __slots__ = ()

    def __init__(self) -> None:
        a = Pin(PinId(1, 'a'), Direction.IN,  ELECTRICAL, mandatory=False, signal_type=Digital)
        y = Pin(PinId(2, 'y'), Direction.OUT, ELECTRICAL, mandatory=False, signal_type=Digital)
        wire(a.internal, y.internal)   # IN pin's internal is OUT, OUT pin's internal is IN
        super().__init__(pins=[a, y], cells=[])

    def __call__(self, a: bool | None) -> bool | None:
        self._assert_no_inputs_wired()
        self._ports['a'].drive(a)
        self.evaluate()
        return self._ports['y'].value


# --- Encapsulation: ports are pin externals only ---

def test_chip_ports_are_pin_externals():
    chip = _PassChip()
    assert set(chip.ports.keys()) == {'a', 'y'}
    # The Port objects exposed are the externals — internals are private.
    assert chip.ports['a'].direction is Direction.IN
    assert chip.ports['y'].direction is Direction.OUT


def test_chip_pin_names_become_port_keys():
    chip = _PassChip()
    assert chip.ports['a'].name == 'a'
    assert chip.ports['y'].name == 'y'


# --- Pass-through behaviour via internal wiring ---

def test_chip_propagates_signal_through_internal_wire():
    chip = _PassChip()
    assert chip(True)  is True
    assert chip(False) is False
    assert chip(None)  is None


# --- Wired-input guard ---

def test_assert_no_inputs_wired_raises_when_input_is_connected():
    chip = _PassChip()
    driver = Port('drv', Direction.OUT, ELECTRICAL, signal_type=Digital)
    wire(driver, chip.ports['a'])
    with pytest.raises(WiredChipCallError, match="wired by an enclosing circuit"):
        chip(True)


def test_assert_no_inputs_wired_silent_when_inputs_unconnected():
    chip = _PassChip()
    # No external wiring — guard should be silent.
    assert chip(True) is True


def test_assert_no_inputs_wired_does_not_consider_outputs():
    chip = _PassChip()
    sink = Port('sink', Direction.IN, ELECTRICAL, signal_type=Digital)
    wire(chip.ports['y'], sink)   # OUT pin externally wired — should NOT trigger guard
    assert chip(True) is True


def test_assert_no_inputs_wired_catches_bidir():
    # BIDIR ports may be written from __call__, so they must trigger
    # the same silent-overwrite guard as IN ports.
    from framework.factor import FactorNode
    from framework.signals import Analog

    class _DummyBidir(FactorNode):
        __slots__ = ('_t',)

        def __init__(self):
            self._t = Port('t', Direction.BIDIR, ELECTRICAL, signal_type=Analog)

        @property
        def ports(self):
            return {'t': self._t}

        def evaluate(self):
            pass

        def __call__(self):
            self._assert_no_inputs_wired()

    dummy = _DummyBidir()
    other = Port('drv', Direction.OUT, ELECTRICAL, signal_type=Analog)
    wire(other, dummy.ports['t'])
    with pytest.raises(WiredChipCallError, match="wired by an enclosing circuit"):
        dummy()
