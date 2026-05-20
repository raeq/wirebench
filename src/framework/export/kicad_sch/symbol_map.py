"""Mapping from wirebench component classes to KiCad library symbols.

`lookup(part)` returns a `SymbolEntry` describing which vendored library
symbol to use, plus metadata for the schematic instance (value, refdes
prefix).  Unknown parts get `None`; callers may fall back to
`FALLBACK_CHIP` or `FALLBACK_CONNECTOR` as appropriate.
"""
from __future__ import annotations

from dataclasses import dataclass

from framework.part import Part


@dataclass(frozen=True, slots=True)
class SymbolEntry:
    lib: str
    name: str
    value_template: str  # empty → use the part's class name or value attr
    refdes_prefix: str


# ---------------------------------------------------------------------------
# Static mapping: wirebench class name → KiCad symbol
# ---------------------------------------------------------------------------

_BY_CLASS: dict[str, SymbolEntry] = {
    # ---- passives ----
    'Resistor':     SymbolEntry('Device', 'R',            '',     'R'),
    'Capacitor':    SymbolEntry('Device', 'C',            '',     'C'),
    'Inductor':     SymbolEntry('Device', 'L',            '',     'L'),
    'LED':          SymbolEntry('Device', 'LED',          '',     'D'),
    'Cell':         SymbolEntry('Device', 'Battery_Cell', '',     'B'),
    'Photoresistor':    SymbolEntry('Device', 'R_Photo',         'LDR',     'R'),
    'Speaker':          SymbolEntry('Device', 'Speaker',         'Speaker', 'LS'),
    'CrystalEarpiece':  SymbolEntry('Device', 'Speaker_Crystal', 'Earpiece','BZ'),
    'VariableCapacitor':SymbolEntry('Device', 'C_Variable',      'VC',      'C'),
    'FerriteAerial':    SymbolEntry('Device', 'L_Ferrite',       'Aerial',  'L'),
    'Antenna':          SymbolEntry('Device', 'Antenna',         'Antenna', 'A'),
    'Earth':            SymbolEntry('power',  'Earth',           'Earth',   'E'),

    # ---- discrete diodes ----
    'D1N4001':  SymbolEntry('Diode', '1N4001', '1N4001', 'D'),
    'D1N4007':  SymbolEntry('Diode', '1N4007', '1N4007', 'D'),
    'D1N4148':  SymbolEntry('Diode', '1N4148', '1N4148', 'D'),
    'D1N5817':  SymbolEntry('Diode', '1N5817', '1N5817', 'D'),
    # No vendored germanium symbol — use the generic Diode glyph.
    'D_OA90':   SymbolEntry('Device', 'D', 'OA90', 'D'),
    'D1N4728A': SymbolEntry('Device', 'D_Zener', '1N4728A', 'D'),
    'D1N4742A': SymbolEntry('Device', 'D_Zener', '1N4742A', 'D'),

    # ---- linear regulators ----
    'LM7805':   SymbolEntry('Regulator_Linear', 'L7805',   'L7805',    'U'),
    'LM7812':   SymbolEntry('Regulator_Linear', 'L7812',   'L7812',    'U'),
    'LM7905':   SymbolEntry('Regulator_Linear', 'L7905',   'L7905',    'U'),
    'LM317':    SymbolEntry('Regulator_Linear', 'LM317',   'LM317',    'U'),
    'LM337':    SymbolEntry('Regulator_Linear', 'LM337',   'LM337',    'U'),
    'LM5002':   SymbolEntry('Regulator_Linear', 'LM5002',  'LM5002',   'U'),
    'AMS1117_33': SymbolEntry('Regulator_Linear', 'AMS1117-3.3', 'AMS1117-3.3', 'U'),
    'AMS1117_50': SymbolEntry('Regulator_Linear', 'AMS1117-5.0', 'AMS1117-5.0', 'U'),
    'LP2950':   SymbolEntry('Regulator_Linear', 'LP2950',  'LP2950',   'U'),

    # ---- 74HC series (Texas Instruments) ----
    'SN74HC00':  SymbolEntry('74xx', '74HC00',   'SN74HC00',  'U'),
    'SN74HC02':  SymbolEntry('74xx', '74HC02',   'SN74HC02',  'U'),
    'SN74HC04':  SymbolEntry('74xx', '74HC04',   'SN74HC04',  'U'),
    'SN74HC08':  SymbolEntry('74xx', '74HC08',   'SN74HC08',  'U'),
    'SN74HC32':  SymbolEntry('74xx', '74HC32',   'SN74HC32',  'U'),
    'SN74HC74':  SymbolEntry('74xx', '74HC74',   'SN74HC74',  'U'),
    'SN74HC86':  SymbolEntry('74xx', '74HC86',   'SN74HC86',  'U'),
    'SN74HC138': SymbolEntry('74xx', '74HC138',  'SN74HC138', 'U'),
    'SN74HC139': SymbolEntry('74xx', '74HC139',  'SN74HC139', 'U'),
    'SN74HC165': SymbolEntry('74xx', '74HC165',  'SN74HC165', 'U'),
    'SN74HC174': SymbolEntry('74xx', '74HC174',  'SN74HC174', 'U'),
    'SN74HC273': SymbolEntry('74xx', '74HC273',  'SN74HC273', 'U'),
    'SN74HC541': SymbolEntry('74xx', '74HC541',  'SN74HC541', 'U'),
    'SN74HC595': SymbolEntry('74xx', '74HC595',  'SN74HC595', 'U'),
    'SN74AHC1G14': SymbolEntry('74xx', '74AHC1G14', 'SN74AHC1G14', 'U'),

    # ---- 4000 CMOS series ----
    'CD4069':   SymbolEntry('4xxx', '4069', 'CD4069', 'U'),
    'CD4017':   SymbolEntry('4xxx', 'CD4017B', 'CD4017', 'U'),
}

# Fallbacks used by the renderer when no entry is found.
FALLBACK_CHIP = SymbolEntry('Device', 'R', '', 'U')  # placeholder — renderer skips unknown chips
FALLBACK_CONNECTOR = SymbolEntry('Connector_Generic', 'Conn_01x01', '', 'J')


def lookup(part: Part) -> SymbolEntry | None:
    """Return the symbol entry for `part`, walking the MRO.

    Returns None if no entry exists for this class or any of its bases.
    """
    for cls in type(part).__mro__:
        entry = _BY_CLASS.get(cls.__name__)
        if entry is not None:
            return entry
    return None


def lookup_by_name(class_name: str) -> SymbolEntry | None:
    return _BY_CLASS.get(class_name)


def connector_entry(pin_count: int) -> SymbolEntry:
    """Generic connector symbol for `pin_count` pins."""
    sym = f'Conn_01x{pin_count:02d}'
    return SymbolEntry('Connector_Generic', sym, '', 'J')
