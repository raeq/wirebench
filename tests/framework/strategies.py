"""Reusable hypothesis strategies for property-based tests.

Each strategy produces *only valid* inputs — bounded ranges, no NaN,
no negative refdes numbers, no zero-ohm resistors.  Property tests
that consume these strategies should assert invariants that hold
across the entire valid input space.
"""
from __future__ import annotations

from string import ascii_uppercase, digits

from hypothesis import strategies as st

# Importing for registration so the strategies can construct live
# instances.  Components register themselves with the global registry
# at import time.
import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401

from components.chips.cd4043 import CD4043
from components.chips.cd4069 import CD4069
from components.chips.lm393 import LM393
from components.chips.sn74hc04 import SN74HC04
from components.chips.uln2003a import ULN2003A
from components.connectors.headers import (
    Header1xNFemale, Header1xNMale, Header2xNFemale, Header2xNMale,
)
from components.diodes import (
    D1N4001, D1N4007, D1N4148, D1N4733A, D1N4742A, D1N5817,
)
from components.passives.led import LED
from components.passives.rail import Rail
from components.passives.resistor import Resistor
from components.transistors import (
    BC547, BC557, BS170, IRFZ44N, IRLB8721, Q2N2222, Q2N3904,
    Q2N3906, Q2N7000, TIP120,
)


# ----- primitive value strategies ------------------------------------

def refdes_numbers():
    """Positive integers in the IEEE 315 refdes range (1..999)."""
    return st.integers(min_value=1, max_value=999)


def ohms():
    """Resistor values in a physically-plausible range, no NaN/Inf."""
    return st.floats(
        min_value=1.0, max_value=1e7,
        allow_nan=False, allow_infinity=False,
    )


def colors():
    """LED display colours that the project's LED implementation accepts."""
    return st.sampled_from(['red', 'green', 'blue', 'yellow', 'amber', 'white'])


def levels():
    """Boolean rail levels (True = supply, False = ground)."""
    return st.booleans()


def pin_counts_for_2xn():
    """Real-world 2xN header sizes — 4..40 in steps consistent with stock parts."""
    return st.sampled_from([4, 6, 8, 10, 14, 16, 20, 26, 30, 40])


def pitches_mm():
    """Standard header pitches in mm (2.54 / 1.27 / 2.0 / 2.5 / 1.0 / 1.25)."""
    return st.sampled_from([2.54, 1.27, 2.0, 2.5, 1.0, 1.25])


def random_pin_names():
    """Valid PinId.name strings: alphanumeric + underscore, start with a letter."""
    return st.text(
        alphabet=ascii_uppercase + digits + '_',
        min_size=1, max_size=12,
    ).filter(lambda s: s[0].isalpha())


# ----- component-instance strategies ---------------------------------

@st.composite
def resistors(draw):
    """Build a Resistor with randomised value and refdes."""
    return Resistor(ohms=draw(ohms()), refdes_number=draw(refdes_numbers()))


@st.composite
def leds(draw):
    """Build an LED with a randomised colour and refdes."""
    return LED(color=draw(colors()), refdes_number=draw(refdes_numbers()))


@st.composite
def rails(draw):
    """Build a Rail at a randomised level — no refdes (Rail has none)."""
    return Rail(level=draw(levels()))


@st.composite
def simple_chips(draw):
    """One of the 5 original chip classes with stable shape, built with a refdes."""
    cls = draw(st.sampled_from([SN74HC04, CD4069, LM393, CD4043, ULN2003A]))
    return cls(refdes_number=draw(refdes_numbers()))


@st.composite
def connectors(draw):
    """Pin-count-parameterised header connectors (1xN or 2xN, male or female)."""
    cls = draw(st.sampled_from([
        Header1xNMale, Header1xNFemale, Header2xNMale, Header2xNFemale,
    ]))
    return cls(
        refdes_number=draw(refdes_numbers()),
        pin_count=draw(pin_counts_for_2xn()),
        pitch_mm=draw(pitches_mm()),
    )


@st.composite
def bjt_transistors(draw):
    """A BJT discrete (NPN or PNP) built with a randomised refdes."""
    cls = draw(st.sampled_from([
        BC547, BC557, Q2N3904, Q2N3906, Q2N2222, TIP120,
    ]))
    return cls(refdes_number=draw(refdes_numbers()))


@st.composite
def mosfets(draw):
    """An N-MOSFET discrete built with a randomised refdes."""
    cls = draw(st.sampled_from([Q2N7000, BS170, IRLB8721, IRFZ44N]))
    return cls(refdes_number=draw(refdes_numbers()))


@st.composite
def diodes(draw):
    """A two-terminal diode (rectifier, Schottky, or Zener)."""
    cls = draw(st.sampled_from([
        D1N4148, D1N4001, D1N4007, D1N5817, D1N4733A, D1N4742A,
    ]))
    return cls(refdes_number=draw(refdes_numbers()))


# ----- pin-id sequence strategy (for PortMap tests) -------------------

@st.composite
def pin_id_sets(draw, min_pins=1, max_pins=20, duplicate_rate=0.3):
    """Sequence of (pin_number, canonical_name) pairs simulating a chip's
    pin table.  Pin numbers are unique and ascending; names may
    duplicate at the given rate (default 30%) so PortMap's
    disambiguation logic gets exercised."""
    size = draw(st.integers(min_value=min_pins, max_value=max_pins))
    # Generate a small pool of base names so duplicates appear naturally.
    pool_size = max(1, int(size * (1 - duplicate_rate)))
    name_pool = draw(st.lists(
        random_pin_names(),
        min_size=pool_size, max_size=pool_size, unique=True,
    ))
    pins: list[tuple[int, str]] = []
    for i in range(1, size + 1):
        # Pick a name from the pool; small pool + many pins → duplicates.
        idx = draw(st.integers(min_value=0, max_value=len(name_pool) - 1))
        pins.append((i, name_pool[idx]))
    return pins
