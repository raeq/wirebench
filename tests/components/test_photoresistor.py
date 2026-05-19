import pytest

from components.passives.photoresistor import Photoresistor
from framework.units import Ohms, Kilohms


def test_construction_with_refdes():
    p = Photoresistor(dark_ohms=Ohms(1_000_000), light_ohms=Ohms(500),
                      refdes_number=1)
    assert p.refdes == 'R1'
    assert p.refdes_number == 1


def test_refdes_prefix():
    assert Photoresistor.REFDES_PREFIX == 'R'


def test_dark_ohms_property_returns_unit_typed_value():
    p = Photoresistor(dark_ohms=1_000_000, light_ohms=500, refdes_number=1)
    assert isinstance(p.dark_ohms, Ohms)
    assert float(p.dark_ohms) == pytest.approx(1_000_000)


def test_light_ohms_property_returns_unit_typed_value():
    p = Photoresistor(dark_ohms=Ohms(1_000_000), light_ohms=Kilohms(0.5),
                      refdes_number=1)
    assert isinstance(p.light_ohms, Ohms)
    assert float(p.light_ohms) == pytest.approx(500)


def test_terminals_are_bidir_analog():
    """Same conductor-wildcard treatment as Resistor — both terminals
    are BIDIR Analog so the cell sits transparently in mixed Analog/
    Digital nets."""
    from framework.port import Direction
    from framework.signals import Analog
    p = Photoresistor(dark_ohms=Ohms(1_000_000), light_ohms=Ohms(500),
                      refdes_number=1)
    for name in ('t1', 't2'):
        port = p.ports[name]
        assert port.direction is Direction.BIDIR
        assert port.signal_type is Analog
        assert port.mandatory is True


def test_pin_numbers_match_resistor_convention():
    """t1 → 1, t2 → 2 — matches Resistor / Inductor / Capacitor so the
    breadboard renderer treats the part as a generic axial 2-lead."""
    assert Photoresistor.PIN_NUMBERS == {'t1': 1, 't2': 2}


def test_through_hole_substrate():
    """LDR is always THT — ORP12-class parts come in axial 5 mm
    packages.  SMD photoresistors are uncommon enough that defaulting
    to THT is the honest answer for the hobbyist audience."""
    p = Photoresistor(dark_ohms=Ohms(1_000_000), light_ohms=Ohms(500),
                      refdes_number=1)
    assert p.is_through_hole is True


def test_call_returns_dark_light_pair():
    """No signal interface; __call__ is a sizing calculator that
    returns the (dark, light) pair so the surrounding circuit can
    pick its divider partner."""
    p = Photoresistor(dark_ohms=1_000_000, light_ohms=500, refdes_number=1)
    dark, light = p()
    assert isinstance(dark, Ohms)
    assert isinstance(light, Ohms)
    assert float(dark) == pytest.approx(1_000_000)
    assert float(light) == pytest.approx(500)


def test_negative_values_rejected():
    with pytest.raises(Exception):
        Photoresistor(dark_ohms=-1, light_ohms=500, refdes_number=1)
    with pytest.raises(Exception):
        Photoresistor(dark_ohms=1000, light_ohms=-1, refdes_number=1)


def test_repr_round_trips():
    p = Photoresistor(dark_ohms=1_000_000, light_ohms=500, refdes_number=2)
    expected = "Photoresistor(dark_ohms=1000000.0, light_ohms=500.0, refdes='R2')"
    assert repr(p) == expected


def test_save_load_roundtrip(tmp_path):
    """Photoresistor round-trips via the generic ExtensionRecord
    fallback (SERIALIZE_KWARGS = ('dark_ohms', 'light_ohms', 'domain'))."""
    import warnings
    from framework.circuit import Circuit
    from framework.format import load_wirebench, save_wirebench
    from framework.wire import wire
    from components.passives.rail import Rail

    class TinyLDRDivider(Circuit):
        def __init__(self) -> None:
            self.vcc = Rail(True)
            self.gnd = Rail(False)
            self.ldr = Photoresistor(
                dark_ohms=Ohms(1_000_000), light_ohms=Ohms(500),
                refdes_number=1,
            )
            wire(self.vcc.out, self.ldr.t1)
            wire(self.gnd.out, self.ldr.t2)
            super().__init__()

        def __call__(self) -> None:
            pass

    from framework.registry import register
    if 'TinyLDRDivider' not in __import__('framework.registry').registry._REGISTRY:
        register('TinyLDRDivider')(TinyLDRDivider)
    original = TinyLDRDivider()
    p1 = tmp_path / "a.wirebench"
    p2 = tmp_path / "b.wirebench"
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        save_wirebench(original, p1)
        loaded = load_wirebench(p1)
        save_wirebench(loaded, p2)
    assert p1.read_text() == p2.read_text()
    # Roundtripped LDR preserves both value endpoints.
    loaded_ldr = next(
        fn for fn in loaded.parts if isinstance(fn, Photoresistor)
    )
    assert float(loaded_ldr.dark_ohms)  == pytest.approx(1_000_000)
    assert float(loaded_ldr.light_ohms) == pytest.approx(500)
