"""Hand-curated mapping from KiCad netlist hints to wirebench class names.

The resolver applies four tiers (exact name → suffix-strip →
libsource map → value map → fallback to `UnknownPart`).  This module
provides the libsource and value tables; the suffix-strip list lives
here too, in `SUFFIX_STRIPS`.

Three lookup keys, checked in order by the resolver:

  1. `(libsource_lib, libsource_part)` — most specific.
  2. `value`                            — when the netlist's value
                                          already names the part.
  3. `value_with_suffix_stripped`       — driven by `SUFFIX_STRIPS`
                                          below; the resolver strips
                                          each suffix and retries the
                                          registry lookup.

The mapping is grown as imports surface unmatched parts.  The intent
is breadth over depth; perfect coverage is impossible without sharing
KiCad's entire library catalogue.
"""
from __future__ import annotations


# (libsource_lib, libsource_part) → wirebench class name
LIBSOURCE_MAP: dict[tuple[str, str], str] = {
    # Generic Device library equivalents.
    ('Device', 'R'):         'Resistor',
    ('Device', 'R_Small'):   'Resistor',
    ('Device', 'C'):         'Capacitor',
    ('Device', 'C_Small'):   'Capacitor',
    ('Device', 'CP'):        'Capacitor',   # polarised; same wirebench part for v1
    ('Device', 'L'):         'Inductor',
    ('Device', 'L_Small'):   'Inductor',
    ('Device', 'LED'):       'LED',
    ('Device', 'D'):         'D1N4148',     # generic diode → small-signal default
    ('Device', 'Battery_Cell'): 'Cell',

    # Regulators.
    ('Regulator_Linear', 'LM7805_TO220'):  'LM7805',
    ('Regulator_Linear', 'LM7805'):        'LM7805',
    ('Regulator_Linear', 'LM7812_TO220'):  'LM7812',
    ('Regulator_Linear', 'LM7812'):        'LM7812',
    ('Regulator_Linear', 'LM317_TO220'):   'LM317',
    ('Regulator_Linear', 'LM317'):         'LM317',
    ('Regulator_Linear', 'AMS1117-3.3'):   'AMS1117_33',
    ('Regulator_Linear', 'AMS1117-5.0'):   'AMS1117_50',

    # Logic.
    ('74xx', '74HC04'):    'SN74HC04',
    ('74xx', 'SN74HC04'):  'SN74HC04',
    ('4xxx', 'CD4069'):    'CD4069',
    ('4xxx', '4069'):      'CD4069',
    ('4xxx', 'CD4043'):    'CD4043',
    ('4xxx', 'CD4017'):    'CD4017',

    # Comparators / op-amps.
    ('Amplifier_Operational', 'LM393'):  'LM393',
    ('Amplifier_Operational', 'LM339'):  'LM339',
    ('Amplifier_Operational', 'LM311'):  'LM311',
    ('Amplifier_Operational', 'LM324'):  'LM324',
    ('Comparator', 'LM393'):              'LM393',
    ('Comparator', 'LM339'):              'LM339',

    # MCUs.
    ('MCU_Microchip_ATmega', 'ATmega328P'):      'ATmega328P',
    ('MCU_Microchip_ATmega', 'ATmega328P-PU'):   'ATmega328P',
    ('MCU_Microchip_ATmega', 'ATmega2560'):      'ATmega2560',
    ('MCU_Microchip_ATmega', 'ATmega32U4'):      'ATmega32U4',
    ('MCU_Microchip_ATtiny', 'ATtiny85'):        'ATtiny85',
    ('MCU_Microchip_ATtiny', 'ATtiny84'):        'ATtiny84',

    # Diodes.
    ('Diode', '1N4148'):  'D1N4148',
    ('Diode', '1N4001'):  'D1N4001',
    ('Diode', '1N4007'):  'D1N4007',
    ('Diode', '1N5817'):  'D1N5817',

    # The wirebench export emits a (lib "IC") (part "<ClassName>")
    # form; round-trip imports of our own output go through that.
    ('IC', 'ULN2003A'):  'ULN2003A',
    ('IC', 'SN74HC04'):  'SN74HC04',
    ('IC', 'CD4069'):    'CD4069',
    ('IC', 'CD4043'):    'CD4043',
}


# `value` → wirebench class name.  Last-ditch lookup when libsource
# doesn't match; covers schematics that only set `value` (KiCad's
# generic-symbol pattern) without a meaningful libsource.
VALUE_MAP: dict[str, str] = {
    'R':       'Resistor',
    'C':       'Capacitor',
    'L':       'Inductor',
    'LED':     'LED',
    'D':       'D1N4148',
}


# Suffixes the resolver strips before retrying registry lookup.
# Order matters — longer suffixes first so 'LM7805_TO220' strips to
# 'LM7805' rather than 'LM7805_TO' + '220'.
SUFFIX_STRIPS: tuple[str, ...] = (
    '_TO220', '_TO92', '_TO252', '_TO263', '_TO3',
    '_SOIC8', '_SOIC14', '_SOIC16', '_SOT223', '_SOT23',
    '_DIP8', '_DIP14', '_DIP16', '_DIP28', '_DIP40',
    '_TQFP44', '_TQFP100', '_QFN16', '_QFN20', '_QFN32', '_QFN48',
    '_SMD', '_THT', '_TH',
    '-PU', '-PB',  # ATmega328P-PU / -PB suffixes
)
