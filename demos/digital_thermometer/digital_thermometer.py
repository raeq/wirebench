"""Digital thermometer — composite-circuit demo.

Faithful recreation of the Arduino project at
https://projecthub.arduino.cc/theoasve/from-sensor-to-screen-build-a-digital-thermometer-in-minutes-2f9736
— an integer-Celsius thermometer reading a DHT11 sensor and showing the
value on a 4-digit common-anode 7-segment display.

Bill of materials (matches the source project verbatim):
    U1  Uno_ThermometerSketch   ATmega328P running the digital-thermometer firmware
    U2  DHT11                   single-bus humidity/temperature sensor
    U3  Display5641AS           common-anode quad-digit 7-segment display
    R1  Resistor                220 Ω current limiter on the digit-1 common

Run directly to see a per-phase, per-temperature trace of which digit
glyph is multiplexed onto the display:

    python demos/digital_thermometer.py

Firmware modelling note
-----------------------
The behaviour of an Arduino sketch (reading DHT11 frames, multiplexing
the display) cannot be faithfully simulated by a steady-state voltage
graph — both the DHT11 single-bus protocol and the digit scan are
bit-banged over time.  We respect the chip surface (ATmega328P pins are
identical to the real silicon's) and model the firmware as an internal
`_ThermometerSketch` cell that drives the relevant pin inner faces from
within the chip — exactly the position firmware occupies on real
hardware.  The temperature reading is set as Python-level state on the
sketch cell (an explicit escape hatch; the DHT11 wire still exists in
the BOM but its 40-bit frames are not decoded).
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make `src/` importable when this file is run as a script.
_SRC = Path(__file__).resolve().parent.parent.parent / 'src'
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from pydantic import validate_call

from wirebench import (
    Chip, Circuit, Part,
    Direction, Port, Pin, PinId,
    GroundDomain, ELECTRICAL,
    RefdesNumber, validate_refdes,
    Analog, Digital, wire,
    ATmega328P, DHT11_Module, Display5641AS, Resistor, Rail,
    run_scenarios,
)
from framework.registry import register


# Segments lit for each character the firmware can display.  Common-
# anode polarity is applied at drive time: a segment listed here is
# driven LOW (cathode sinks current); the rest are driven HIGH (off).
_CHAR_SEGMENTS: dict[str, frozenset[str]] = {
    '0': frozenset({'a', 'b', 'c', 'd', 'e', 'f'}),
    '1': frozenset({'b', 'c'}),
    '2': frozenset({'a', 'b', 'd', 'e', 'g'}),
    '3': frozenset({'a', 'b', 'c', 'd', 'g'}),
    '4': frozenset({'b', 'c', 'f', 'g'}),
    '5': frozenset({'a', 'c', 'd', 'f', 'g'}),
    '6': frozenset({'a', 'c', 'd', 'e', 'f', 'g'}),
    '7': frozenset({'a', 'b', 'c'}),
    '8': frozenset({'a', 'b', 'c', 'd', 'e', 'f', 'g'}),
    '9': frozenset({'a', 'b', 'c', 'd', 'f', 'g'}),
    'C': frozenset({'a', 'd', 'e', 'f'}),
    '-': frozenset({'g'}),
    ' ': frozenset(),
}

_SEGMENT_NAMES = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'dp')


def _format_temperature(temp_c: float) -> tuple[str, str, str]:
    """Render temperature_c as three characters: tens, ones, 'C'.

    Out-of-range (< 0 or > 99) renders as '-', '-', 'C'.  The DHT11's
    nominal range is 0..50 °C, so 0..99 covers all realistic readings.
    """
    t = int(round(temp_c))
    if not 0 <= t <= 99:
        return ('-', '-', 'C')
    tens_char = ' ' if t < 10 else str(t // 10)
    ones_char = str(t % 10)
    return (tens_char, ones_char, 'C')


class _ThermometerSketch(Part):
    """Model of the Arduino sketch driving the multiplexed display.

    Not a placeable part: there is no soldering iron that installs
    firmware.  This cell exists to give the framework something whose
    `evaluate()` translates the temperature reading into pin drives,
    occupying the same logical position firmware does on real silicon.

    State (`_temperature_c`, `_phase`) is Python-level — the demo's
    `__call__` sets it before evaluation.  The 1-Wire frame decoding
    on DHT11.DATA is acknowledged as out of scope; the temperature
    value reaches this cell directly.
    """

    __slots__ = ('_ports', '_temperature_c', '_phase')

    DIGITS_DISPLAYED: int = 3   # only 3 of the display's 4 digits used

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL) -> None:
        out_names = (
            'dig_1', 'dig_2', 'dig_3',
            'seg_a', 'seg_b', 'seg_c', 'seg_d',
            'seg_e', 'seg_f', 'seg_g', 'seg_dp',
        )
        self._ports = {
            name: Port(name, Direction.OUT, domain,
                       mandatory=False, signal_type=Digital)
            for name in out_names
        }
        self._temperature_c: float = 0.0
        self._phase: int = 0

    @property
    def ports(self) -> dict[str, Port]:
        return self._ports

    @property
    def temperature_c(self) -> float:
        return self._temperature_c

    @property
    def phase(self) -> int:
        return self._phase

    def evaluate(self) -> None:
        chars = _format_temperature(self._temperature_c)
        p = self._phase % self.DIGITS_DISPLAYED
        char = chars[p]
        lit = _CHAR_SEGMENTS.get(char, frozenset({'g'}))   # unknown → '-'

        for i in range(1, self.DIGITS_DISPLAYED + 1):
            self._ports[f'dig_{i}'].drive(i == p + 1)

        # Common-anode: LOW = lit (cathode sinks), HIGH = off.
        for seg in _SEGMENT_NAMES:
            self._ports[f'seg_{seg}'].drive(seg not in lit)

    def __repr__(self) -> str:
        return (f"_ThermometerSketch(temp_c={self._temperature_c!r}, "
                f"phase={self._phase!r})")


@register('Uno_ThermometerSketch')
class Uno_ThermometerSketch(ATmega328P):
    """ATmega328P loaded with the digital-thermometer firmware.

    Same silicon, same 28-pin DIP surface as a bare ATmega328P — the
    only difference is that internal cells embody what the sketch does.
    Pin mapping (Arduino digital pin -> ATmega328P pin name):

        D3  -> PD3   digit 1 select  (through R1)
        D4  -> PD4   digit 2 select
        D5  -> PD5   digit 3 select
        D6  -> PD6   segment a
        D7  -> PD7   segment b
        D8  -> PB0   segment c
        D9  -> PB1   segment d
        D10 -> PB2   segment e
        D11 -> PB3   segment f
        D12 -> PB4   segment g
        D13 -> PB5   segment dp

    Pin PD2 (Arduino D2) is wired to DHT11.DATA at the composite level;
    its single-bus frames are not modelled.
    """

    __slots__ = ('_sketch',)

    _ARDUINO_PIN_TO_MCU_PIN: dict[str, str] = {
        # sketch port name -> ATmega328P pin name
        'dig_1':  'PD3',
        'dig_2':  'PD4',
        'dig_3':  'PD5',
        'seg_a':  'PD6',
        'seg_b':  'PD7',
        'seg_c':  'PB0',
        'seg_d':  'PB1',
        'seg_e':  'PB2',
        'seg_f':  'PB3',
        'seg_g':  'PB4',
        'seg_dp': 'PB5',
    }

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self, domain: GroundDomain = ELECTRICAL, *,
                 refdes_number: RefdesNumber) -> None:
        # Intentionally do NOT call super().__init__: ATmega328P
        # finalises Chip with cells=[], and we need to inject the
        # sketch.  Replicate ATmega328P's setup, then add cells.
        validate_refdes(self.REFDES_PREFIX, refdes_number)
        self._refdes_number = refdes_number
        self._sketch = _ThermometerSketch(domain)

        pins = [
            Pin(PinId(number, name), direction, domain,
                mandatory=False, signal_type=signal_type)
            for number, name, direction, signal_type in self._PIN_TABLE
        ]
        by_name = {p.id.name: p for p in pins}

        # Sketch outputs drive the relevant pin internal faces.  For each
        # such pin we fix the effective role to OUT: real silicon pins
        # are BIDIR, but in this firmware configuration the chip drives
        # them outward only — Pin.evaluate's BIDIR contention check
        # otherwise trips on repeated calls when the external face
        # retains the previous slot's value while the internal face
        # holds the new one.  This is what `_effective_role` exists to
        # express; the topological sort assigns it automatically only
        # for mated-connector cases (multiple BIDIRs on one net), so we
        # set it directly here for the firmware-driven case.
        for sketch_port, mcu_pin in self._ARDUINO_PIN_TO_MCU_PIN.items():
            pin = by_name[mcu_pin]
            # sketch_port is a dynamic name → use ports[...] indexing.
            wire(self._sketch.ports[sketch_port], pin.internal)
            pin._effective_role = Direction.OUT

        Chip.__init__(self, pins=pins, cells=[self._sketch])

    @property
    def sketch(self) -> _ThermometerSketch:
        """The firmware-model cell.  Composite circuits set its
        `_temperature_c` and `_phase` before evaluating."""
        return self._sketch

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(  # type: ignore[override]
        self, temperature_c: float, phase: int,
    ) -> None:
        """Standalone-test invocation: load firmware state and run the
        chip's internal evaluation.  Refuses if any pin is wired into a
        parent — the parent must drive sketch state directly via the
        `sketch` property and call its own `evaluate()`.

        Override widens ATmega328P.__call__(): this subclass embeds a
        sketch cell that needs temperature/phase inputs."""
        self._assert_no_inputs_wired()
        self._sketch._temperature_c = float(temperature_c)
        self._sketch._phase = int(phase)
        self.evaluate()
        return None

    def __repr__(self) -> str:
        return (f"Uno_ThermometerSketch(refdes={self.refdes!r}, "
                f"temp_c={self._sketch._temperature_c!r}, "
                f"phase={self._sketch._phase!r})")


class DigitalThermometer(Circuit):
    """Single-board digital thermometer.

    BOM:
        U1  Uno_ThermometerSketch   the Arduino with firmware loaded
        U2  DHT11                   sensor on D2
        U3  Display5641AS           4-digit common-anode display
        R1  Resistor (220 Ω)        current limiter on digit-1 common

    Wiring follows the project verbatim:
        D2  <-> DHT11.DATA          (single-bus; protocol unmodelled)
        D3  -> R1 -> Display.DIG_1  (R1 modelled as a 0-Ω pass-through
                                     so the simulator can propagate
                                     through it; its 220 Ω documents
                                     the real part's current-limiting
                                     role)
        D4  -> Display.DIG_2
        D5  -> Display.DIG_3
        D6..D13 -> Display.SEG_A..SEG_DP

    The 4th display digit (DIG_4) is tied to GND so digit 4 is always
    dark.  Power pins (VCC/AVCC/AREF/GND on the Arduino, VDD/GND on the
    DHT11) are documented as off-graph supply — the framework's Rail is
    Digital-typed and cannot drive Analog supply pins.

    Omits __slots__ so `Circuit.__init__` can auto-collect the parts
    from `self.__dict__`.
    """

    @validate_call(config={'arbitrary_types_allowed': True})
    def __init__(self) -> None:
        self.arduino = Uno_ThermometerSketch(refdes_number=1)
        self.dht11   = DHT11_Module(refdes_number=2)
        self.display = Display5641AS(refdes_number=3)
        self.r1      = Resistor(220, refdes_number=1)
        # Digital rail — used to tie the unused 4th-digit anode of the
        # display (a digital input) LOW.
        self.gnd     = Rail(False)
        # Analog rails — the DHT11 module declares its VCC / GND pins
        # as Analog (supply pins, not logic), so they need an
        # Analog-typed Rail for the simulator's port-compatibility
        # check.  Physically these are the same breadboard +/- rails;
        # the assembly-guide exporter recognises every Rail as a
        # logical rail regardless of signal type.
        self.vcc_a   = Rail(True,  signal_type=Analog)
        self.gnd_a   = Rail(False, signal_type=Analog)

        # DHT11 module: power and single-bus data.
        wire(self.dht11.DATA, self.arduino.PD2)
        wire(self.vcc_a.out,  self.dht11.VCC)
        wire(self.gnd_a.out,  self.dht11.GND)

        # Digit 1 common via the 220 Ω current limiter.  Both R1
        # terminals share the node with the source and sink — R1 is in
        # the BOM and on the wire-list but the simulator treats it as a
        # 0-Ω pass-through (a voltage-only solver can't propagate IxR).
        wire(self.arduino.PD3,
             self.r1.t1, self.r1.t2,
             self.display.DIG_1)

        # Remaining digit selects and all eight segment lines.
        wire(self.arduino.PD4, self.display.DIG_2)
        wire(self.arduino.PD5, self.display.DIG_3)
        wire(self.arduino.PD6, self.display.SEG_A)
        wire(self.arduino.PD7, self.display.SEG_B)
        wire(self.arduino.PB0, self.display.SEG_C)
        wire(self.arduino.PB1, self.display.SEG_D)
        wire(self.arduino.PB2, self.display.SEG_E)
        wire(self.arduino.PB3, self.display.SEG_F)
        wire(self.arduino.PB4, self.display.SEG_G)
        wire(self.arduino.PB5, self.display.SEG_DP)

        # The fourth display digit is unused — its anode is tied LOW so
        # the digit stays dark regardless of segment drive.
        wire(self.gnd.out, self.display.DIG_4)

        super().__init__(
            ports={
                # No port-level inputs: temperature is firmware-model state.
                # Expose the display's DIG_1 as a visible-state port for
                # debugging.
                'display_dig_1': self.display.DIG_1,
            },
        )

    @validate_call(config={'arbitrary_types_allowed': True})
    def __call__(self, temperature_c: float, phase: int) -> tuple[str, str, str, str]:
        """Run the circuit for one multiplexing slot.

        Sets the firmware-model state (temperature and current multiplex
        phase 0..2) directly on the sketch cell, then propagates signals
        through the whole circuit.  Returns the four-digit display
        snapshot — exactly one character is lit per call (or none, if
        the phase value selects no driven digit).
        """
        self.arduino.sketch._temperature_c = float(temperature_c)
        self.arduino.sketch._phase         = int(phase)
        self.evaluate()
        return self.display.glyphs

    def __repr__(self) -> str:
        return f"DigitalThermometer(glyphs={self.display.glyphs!r})"


def _main() -> None:
    """Walk through a multiplex cycle at several temperatures and print
    a per-pin / per-digit trace."""
    run_scenarios(
        DigitalThermometer(),
        scenarios=[
            (f"ambient = {t:>2.0f} °C, phase {p}", (t, p))
            for t in (5.0, 23.0, 40.0)
            for p in range(3)
        ],
        columns=[
            ("temp",   lambda c, a, k: f"{a[0]:>4.1f}"),
            ("phase",  lambda c, a, k: a[1]),
            ("glyphs", lambda c, a, k: ''.join(c.display.glyphs)),
        ],
    )


if __name__ == '__main__':
    _main()
