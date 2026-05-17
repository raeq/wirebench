"""Tests for `framework.pin_function.infer_pin_function` — the name-
based classifier used by Pin construction-time invariants and by ERC
walkers."""
import pytest

from framework.pin_function import PinFunction, infer_pin_function


# Each row: (pin name → expected PinFunction).  None means "this name
# should NOT match any function" (i.e. a signal pin).
_INFERENCE_TABLE: list[tuple[str, PinFunction | None]] = [
    # POWER: canonical supply names.
    ('VCC',         PinFunction.POWER),
    ('VDD',         PinFunction.POWER),
    ('AVCC',        PinFunction.POWER),
    ('VBUS',        PinFunction.POWER),
    # GROUND: canonical return names.
    ('GND',         PinFunction.GROUND),
    ('VSS',         PinFunction.GROUND),
    ('AGND',        PinFunction.GROUND),
    ('DGND',        PinFunction.GROUND),
    # REFERENCE: ADC / comparator reference inputs.
    ('AREF',        PinFunction.REFERENCE),
    ('VREF',        PinFunction.REFERENCE),
    ('VBG',         PinFunction.REFERENCE),
    ('BG_REF',      PinFunction.REFERENCE),
    # RESET: every common spelling.
    ('RESET',       PinFunction.RESET),
    ('RST',         PinFunction.RESET),
    ('NRST',        PinFunction.RESET),
    ('NRESET',      PinFunction.RESET),
    ('RST_N',       PinFunction.RESET),
    ('RESET_B',     PinFunction.RESET),
    # CLOCK_IN: external clock entry points.
    ('CLKIN',       PinFunction.CLOCK_IN),
    ('EXTCLK',      PinFunction.CLOCK_IN),
    ('OSCIN',       PinFunction.CLOCK_IN),
    ('CLK_IN',      PinFunction.CLOCK_IN),
    # NC: explicit no-connect.
    ('NC',          PinFunction.NC),
    ('N.C.',        PinFunction.NC),
    ('DNC',         PinFunction.NC),
    # Signal pins (no function inference).  Anchoring the regex
    # protects against false positives: VDD_SENSE is a sense input,
    # not a supply; RESET_PULSE is a signal output, not a reset
    # input; CLK is a generic clock signal, not necessarily a
    # CLOCK_IN; XTAL pins are crystal-pair endpoints, not single-
    # pin functions; OE is an output enable; SDA/SCL are I²C lines.
    ('VDD_SENSE',   None),
    ('VCC_NEG',     None),
    ('RESET_PULSE', None),
    ('CLK',         None),
    ('SCLK',        None),
    ('XTAL1',       None),
    ('XTAL2',       None),
    ('OE',          None),
    ('SDA',         None),
    ('SCL',         None),
    ('IN',          None),
    ('OUT',         None),
    ('D0',          None),
    ('PB5',         None),
    ('a_1',         None),
]


@pytest.mark.parametrize('name,expected', _INFERENCE_TABLE)
def test_inference_table(name, expected):
    assert infer_pin_function(name) is expected


@pytest.mark.parametrize('lower,upper', [
    ('vcc',  'VCC'),
    ('Vdd',  'VDD'),
    ('gnd',  'GND'),
    ('vSs',  'VSS'),
    ('aref', 'AREF'),
    ('rst',  'RST'),
    ('Nrst', 'NRST'),
    ('clkin','CLKIN'),
    ('nc',   'NC'),
    ('dnc',  'DNC'),
])
def test_inference_is_case_insensitive(lower, upper):
    assert infer_pin_function(lower) is infer_pin_function(upper)


def test_unknown_names_are_signal_pins():
    # A pin name the framework has no opinion on should classify as
    # `None` — the caller (ERC, assembly guide) treats it as a regular
    # signal pin with no special wiring requirements.
    assert infer_pin_function('FOOBAR') is None
    assert infer_pin_function('')      is None
    assert infer_pin_function('_')     is None


def test_anchoring_rejects_prefixed_or_suffixed_matches():
    # Anchored regex discipline — a near-miss must NOT match.
    # If anchoring breaks, a signal pin named XVCC would silently get
    # POWER treatment and a downstream ERC would refuse to wire it,
    # so this is load-bearing.
    assert infer_pin_function('XVCC')       is None
    assert infer_pin_function('VCCX')       is None
    assert infer_pin_function('MY_RESET')   is None
    assert infer_pin_function('RESET_DONE') is None
    assert infer_pin_function('NCB')        is None
    assert infer_pin_function('NC_OUT')     is None


def test_pin_function_values_are_lowercase_role_names():
    # Stable string values matter for ERC error messages, golden
    # tests, and any future serialization.  Lock them in.
    assert PinFunction.POWER.value     == 'power'
    assert PinFunction.GROUND.value    == 'ground'
    assert PinFunction.REFERENCE.value == 'reference'
    assert PinFunction.RESET.value     == 'reset'
    assert PinFunction.CLOCK_IN.value  == 'clock_in'
    assert PinFunction.NC.value        == 'nc'


# --- Chip-level PIN_FUNCTIONS override interaction ---

def test_chip_pin_functions_override_takes_precedence_over_inference():
    # The Chip.pin_function classmethod is where overrides are
    # consulted.  An override mapping a non-canonical name to a
    # function (e.g. 'PWR' → POWER) makes the chip-level lookup return
    # POWER even though the bare regex would say None.
    from framework.chip import Chip

    class _FakeChip(Chip):
        PIN_FUNCTIONS = {'PWR': PinFunction.POWER, 'RTN': PinFunction.GROUND}
        __slots__ = ()
        BARE_FIRMWARE_DRIVEN = True   # skip the OUT-driver check; this is a stub
        def __call__(self, *a, **kw): ...

    assert _FakeChip.pin_function('PWR') is PinFunction.POWER
    assert _FakeChip.pin_function('RTN') is PinFunction.GROUND
    # Inference still applies for names not in the override map.
    assert _FakeChip.pin_function('VCC') is PinFunction.POWER
    assert _FakeChip.pin_function('FOO') is None


def test_chip_pin_functions_override_can_demote_a_canonical_name_to_signal():
    # Mapping a canonical name to None opts out of inference — useful
    # if a chip has a pin literally named 'VCC' that is, for that
    # specific part, not actually a supply (rare but possible on
    # multi-channel parts where 'VCC' is the channel number, etc.).
    from framework.chip import Chip

    class _FakeChip(Chip):
        PIN_FUNCTIONS = {'VCC': None}
        __slots__ = ()
        BARE_FIRMWARE_DRIVEN = True
        def __call__(self, *a, **kw): ...

    assert _FakeChip.pin_function('VCC') is None
