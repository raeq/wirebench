from components.chips.rp2040 import RP2040
from framework.port import Direction


EXPECTED_PINS = (
    (  1, 'IOVDD_1',      Direction.IN),
    (  2, 'GP0',          Direction.BIDIR),
    (  3, 'GP1',          Direction.BIDIR),
    (  4, 'GP2',          Direction.BIDIR),
    (  5, 'GP3',          Direction.BIDIR),
    (  6, 'GP4',          Direction.BIDIR),
    (  7, 'GP5',          Direction.BIDIR),
    (  8, 'GP6',          Direction.BIDIR),
    (  9, 'GP7',          Direction.BIDIR),
    ( 10, 'IOVDD_2',      Direction.IN),
    ( 11, 'GP8',          Direction.BIDIR),
    ( 12, 'GP9',          Direction.BIDIR),
    ( 13, 'GP10',         Direction.BIDIR),
    ( 14, 'GP11',         Direction.BIDIR),
    ( 15, 'GP12',         Direction.BIDIR),
    ( 16, 'GP13',         Direction.BIDIR),
    ( 17, 'GP14',         Direction.BIDIR),
    ( 18, 'GP15',         Direction.BIDIR),
    ( 19, 'TESTEN',       Direction.IN),
    ( 20, 'XIN',          Direction.BIDIR),
    ( 21, 'XOUT',         Direction.BIDIR),
    ( 22, 'IOVDD_3',      Direction.IN),
    ( 23, 'DVDD_1',       Direction.IN),
    ( 24, 'SWCLK',        Direction.BIDIR),
    ( 25, 'SWDIO',        Direction.BIDIR),
    ( 26, 'RUN',          Direction.IN),
    ( 27, 'GP16',         Direction.BIDIR),
    ( 28, 'GP17',         Direction.BIDIR),
    ( 29, 'GP18',         Direction.BIDIR),
    ( 30, 'GP19',         Direction.BIDIR),
    ( 31, 'GP20',         Direction.BIDIR),
    ( 32, 'GP21',         Direction.BIDIR),
    ( 33, 'IOVDD_4',      Direction.IN),
    ( 34, 'GP22',         Direction.BIDIR),
    ( 35, 'GP23',         Direction.BIDIR),
    ( 36, 'GP24',         Direction.BIDIR),
    ( 37, 'GP25',         Direction.BIDIR),
    ( 38, 'GP26',         Direction.BIDIR),
    ( 39, 'GP27',         Direction.BIDIR),
    ( 40, 'GP28',         Direction.BIDIR),
    ( 41, 'GP29',         Direction.BIDIR),
    ( 42, 'IOVDD_5',      Direction.IN),
    ( 43, 'ADC_AVDD',     Direction.IN),
    ( 44, 'VREG_VIN',     Direction.IN),
    ( 45, 'VREG_VOUT',    Direction.OUT),
    ( 46, 'USB_DM',       Direction.BIDIR),
    ( 47, 'USB_DP',       Direction.BIDIR),
    ( 48, 'USB_VDD',      Direction.IN),
    ( 49, 'IOVDD_6',      Direction.IN),
    ( 50, 'DVDD_2',       Direction.IN),
    ( 51, 'QSPI_SD3',     Direction.BIDIR),
    ( 52, 'QSPI_SCLK',    Direction.BIDIR),
    ( 53, 'QSPI_SD0',     Direction.BIDIR),
    ( 54, 'QSPI_SD2',     Direction.BIDIR),
    ( 55, 'QSPI_SD1',     Direction.BIDIR),
    ( 56, 'QSPI_SS_N',    Direction.BIDIR),
)


def test_construction_with_refdes_1():
    ic = RP2040(refdes_number=1)
    assert ic.refdes == 'U1'


def test_refdes_prefix():
    assert RP2040.REFDES_PREFIX == 'U'


def test_footprint():
    assert RP2040.FOOTPRINT == 'Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm'


def test_pin_count():
    ic = RP2040(refdes_number=1)
    assert len(ic.pins) == 56


def test_pin_numbers_and_names_match_datasheet():
    ic = RP2040(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, name, _ in EXPECTED_PINS:
        assert by_number[number].id.name == name


def test_pin_directions_match_datasheet():
    ic = RP2040(refdes_number=1)
    by_number = {p.id.number: p for p in ic.pins}
    for number, _, direction in EXPECTED_PINS:
        assert by_number[number]._role is direction


def test_ports_keyed_by_pin_name():
    ic = RP2040(refdes_number=1)
    for _, name, _ in EXPECTED_PINS:
        assert name in ic.ports


def test_call_is_noop():
    ic = RP2040(refdes_number=1)
    assert ic() is None


def test_repr():
    assert repr(RP2040(refdes_number=1)) == "RP2040(refdes='U1')"
