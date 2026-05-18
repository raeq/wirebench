"""Per-error-class regex extractors for `wirebench validate`.

Each extractor takes the raw `str(e)` of a framework exception and
returns a `Details` dict populated with whatever structured fields the
message exposes.  Unmatched fields stay at their default (`None` or
empty list) so the consumer always sees the same schema shape.

The framework's exception classes carry their structured payload only
in the message string today.  When a future refactor lifts those into
exception attributes (e.g. `e.refdes`, `e.pins`), the extractors here
collapse into trivial attribute reads.  Until then, regex is the
substrate.
"""
from __future__ import annotations

import re
from typing import Callable, TypedDict


class Details(TypedDict):
    refdes:     str | None
    pin:        str | None
    pins:       list[str]
    parts:      list[str]
    nets:       list[str]
    domain:     str | None
    pin_number: int | None


def empty_details() -> Details:
    return {
        'refdes':     None,
        'pin':        None,
        'pins':       [],
        'parts':      [],
        'nets':       [],
        'domain':     None,
        'pin_number': None,
    }


_Extractor = Callable[[str], Details]


def _strip_quotes(token: str) -> str:
    token = token.strip()
    if len(token) >= 2 and token[0] == token[-1] and token[0] in ("'", '"'):
        return token[1:-1]
    return token


def _split_quoted_list(payload: str) -> list[str]:
    """Split a 'a', 'b', 'c' payload into ['a', 'b', 'c']."""
    return [_strip_quotes(token) for token in payload.split(',')]


def _split_part_pin_list(payload: str) -> tuple[list[str], list[str]]:
    """Split a "'Part.pin', 'Part.pin'" payload into matching lists."""
    parts: list[str] = []
    pins:  list[str] = []
    for token in _split_quoted_list(payload):
        if '.' in token:
            part, pin = token.split('.', 1)
            parts.append(part)
            pins.append(pin)
        else:
            pins.append(token)
    return parts, pins


# --------------------------------------------------------------- patterns


_SHORT_WIRE = re.compile(
    r"^wire\(\) has multiple drivers \(([^)]+)\) — short circuit$"
)
_SHORT_NET = re.compile(
    r"^Short circuit on logical net — multiple drivers: (.+)$"
)
_FLOATING_NET = re.compile(
    r"^Floating logical net — multiple passive BIDIRs with no driver: (.+)$"
)
_INCOMPATIBLE_MATE = re.compile(
    r"^(\w+) mates with (\w+), not (\w+)$"
)
_PARTCONFIG_OUT_NO_CELL = re.compile(
    r"^(\w+) declares pin '(\w+)' \(pin (\d+)\) as Direction\.OUT"
)
_PARTCONFIG_DRIVE_WRONG_DIR = re.compile(
    r"^(\w+) declares pin '(\w+)' as '(\w+)' but its direction is"
)
_PARTCONFIG_TYPO_ENTRY = re.compile(
    r"^(\w+) declares PIN_DRIVE_TYPES entry '(\w+)'"
)
_PARTPARAM_PIN_FUNCTION = re.compile(
    r"^pin (\d+) \((\w+)\) has pin function"
)
_DOMAIN_CROSSING = re.compile(
    r"^Cannot wire ports across ground domains: (.+)$"
)
_DOMAIN_TOKEN = re.compile(r"^'([^']*)'\s*\(([^)]+)\)$")
_BREADBOARD_BULLET = re.compile(
    r"^\s*-\s+(\w+)\s+pin\s+(\d+)\s+\(([^)]+)\)"
)


# --------------------------------------------------------------- extractors


def extract_short_circuit(message: str) -> Details:
    out = empty_details()
    m = _SHORT_WIRE.match(message)
    if m:
        out['pins'] = _split_quoted_list(m.group(1))
        return out
    m = _SHORT_NET.match(message)
    if m:
        parts, pins = _split_part_pin_list(m.group(1))
        out['parts'] = parts
        out['pins'] = pins
    return out


def extract_floating_net(message: str) -> Details:
    out = empty_details()
    m = _FLOATING_NET.match(message)
    if m:
        parts, pins = _split_part_pin_list(m.group(1))
        out['parts'] = parts
        out['pins'] = pins
    return out


def extract_incompatible_mate(message: str) -> Details:
    out = empty_details()
    m = _INCOMPATIBLE_MATE.match(message)
    if m:
        out['parts'] = [m.group(1), m.group(3)]
    return out


def extract_part_configuration(message: str) -> Details:
    out = empty_details()
    m = _PARTCONFIG_OUT_NO_CELL.match(message)
    if m:
        out['parts'] = [m.group(1)]
        out['pin'] = m.group(2)
        out['pin_number'] = int(m.group(3))
        return out
    m = _PARTCONFIG_DRIVE_WRONG_DIR.match(message)
    if m:
        out['parts'] = [m.group(1)]
        out['pin'] = m.group(2)
        return out
    m = _PARTCONFIG_TYPO_ENTRY.match(message)
    if m:
        out['parts'] = [m.group(1)]
        out['pin'] = m.group(2)
    return out


def extract_part_parameter(message: str) -> Details:
    out = empty_details()
    m = _PARTPARAM_PIN_FUNCTION.match(message)
    if m:
        out['pin_number'] = int(m.group(1))
        out['pin'] = m.group(2)
    return out


def extract_domain_crossing(message: str) -> Details:
    out = empty_details()
    m = _DOMAIN_CROSSING.match(message)
    if not m:
        return out
    pins:    list[str] = []
    domains: list[str] = []
    for token in m.group(1).split('),'):
        token = token.strip()
        if not token.endswith(')'):
            token = token + ')'
        tm = _DOMAIN_TOKEN.match(token)
        if tm:
            pins.append(tm.group(1))
            domains.append(tm.group(2))
    out['pins'] = pins
    out['domain'] = next(
        (d for d in domains if d.upper() != 'ELECTRICAL'),
        domains[0] if domains else None,
    )
    return out


def extract_breadboard_incompatible(message: str) -> Details:
    out = empty_details()
    parts: list[str] = []
    pins:  list[str] = []
    for line in message.splitlines()[1:]:
        m = _BREADBOARD_BULLET.match(line)
        if m:
            parts.append(m.group(1))
            pins.append(m.group(3))
    out['parts'] = parts
    out['pins'] = pins
    return out


# Lookup by exception class name. Listed alongside their target classes
# so adding a new extractor is one-line: write the function, add the
# row.
EXTRACTORS: dict[str, _Extractor] = {
    'ShortCircuitError':          extract_short_circuit,
    'FloatingNetError':           extract_floating_net,
    'IncompatibleMateError':      extract_incompatible_mate,
    'PartConfigurationError':     extract_part_configuration,
    'PartParameterError':         extract_part_parameter,
    'DomainCrossingError':        extract_domain_crossing,
    'BreadboardIncompatibleError': extract_breadboard_incompatible,
}


def extract(error_class: str, message: str) -> Details:
    """Dispatch to the per-class extractor, or return defaults."""
    fn = EXTRACTORS.get(error_class)
    if fn is None:
        return empty_details()
    return fn(message)
