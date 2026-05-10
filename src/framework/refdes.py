"""IEEE 315 / ASME Y14.44 reference-designator support.

A reference designator ("refdes") names a specific *instance* of a part on
a board: `R1` is the first resistor, `D2` the second diode, `U3` the third
IC.  Refdes lets the model export to SPICE, KiCad, EDIF, etc., and lets
humans and downstream tools refer to specific parts unambiguously.

A refdes is `<class-prefix><integer>`.  The class prefix is a property of
the component type (declared as `REFDES_PREFIX` on the leaf class).  The
integer is supplied by the author at construction time.

Cells inside chips (NOR latches, comparators, etc.) do not carry a refdes
— they are private chip implementation, never individually visible on a
PCB.  The enclosing chip carries the refdes; exporters synthesise per-
channel references like `U3A` at export time from the chip's refdes plus
its channel index.
"""


# Full IEEE 315 prefix set the codebase will recognise. Authors choose
# from this list when adding new component classes.
IEEE_315_PREFIXES: frozenset[str] = frozenset({
    'A',   # assembly / sub-assembly
    'AT',  # attenuator
    'B',   # motor
    'BT',  # battery / cell
    'C',   # capacitor
    'CB',  # circuit breaker
    'D',   # diode (incl. LED, photodiode)
    'DS',  # display / indicator lamp
    'F',   # fuse
    'FL',  # filter
    'G',   # generator / power supply
    'H',   # hardware
    'HY',  # circulator
    'J',   # jack (chassis-side connector)
    'K',   # relay / contactor
    'L',   # inductor
    'LS',  # loudspeaker / buzzer
    'M',   # meter
    'MK',  # microphone
    'P',   # plug (cable-side connector)
    'Q',   # transistor (discrete)
    'R',   # resistor
    'RT',  # thermistor
    'RV',  # varistor
    'S',   # switch (general)
    'SW',  # switch (alternate)
    'T',   # transformer
    'TC',  # thermocouple
    'TP',  # test point
    'U',   # IC / inseparable assembly
    'V',   # vacuum tube / discharge device
    'VR',  # variable resistor / pot
    'W',   # cable / harness
    'X',   # socket
    'Y',   # crystal / oscillator
    'Z',   # zener (legacy)
})


def validate_refdes(prefix: str, number: int) -> None:
    """Validate a refdes prefix and number.

    Called by every refdes-bearing __init__ before any other side
    effects, so an invalid refdes fails loudly at the construction site.
    """
    if prefix not in IEEE_315_PREFIXES:
        raise ValueError(f"Unknown refdes prefix {prefix!r}; not in IEEE 315.")
    # bool is an int subclass — reject it explicitly (True is not a refdes 1).
    if isinstance(number, bool) or not isinstance(number, int) or number < 1:
        raise ValueError(f"refdes_number must be a positive int; got {number!r}.")
