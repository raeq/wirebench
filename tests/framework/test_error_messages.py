"""Every framework exception class carries a `PHYSICAL_JUSTIFICATION`
ClassVar — a one-or-two-sentence physical-world referent that explains
*why this rule exists*.  The justification renders as a `Why:` line in
the exception's `str(...)` output, turning the diagnostic from
*"tells you what's wrong"* into *"teaches you why the rule exists."*
"""
from __future__ import annotations

import inspect

import pytest

from framework import errors as E


def _every_framework_exception_class() -> list[type[E.WirebenchError]]:
    """Discover every WirebenchError subclass declared in framework.errors."""
    classes: list[type[E.WirebenchError]] = []
    for name, obj in vars(E).items():
        if not inspect.isclass(obj):
            continue
        if not issubclass(obj, E.WirebenchError):
            continue
        if obj.__module__ != E.__name__:
            continue
        classes.append(obj)
    return classes


EVERY_EXCEPTION = _every_framework_exception_class()


@pytest.mark.parametrize(
    'cls', EVERY_EXCEPTION, ids=lambda c: c.__name__,
)
def test_every_class_declares_physical_justification(
    cls: type[E.WirebenchError],
) -> None:
    """Each framework exception class carries a non-empty
    `PHYSICAL_JUSTIFICATION` string ending in a period."""
    justification = cls.PHYSICAL_JUSTIFICATION
    assert isinstance(justification, str), (
        f"{cls.__name__}.PHYSICAL_JUSTIFICATION must be a str; "
        f"got {type(justification).__name__}"
    )
    assert justification, (
        f"{cls.__name__}.PHYSICAL_JUSTIFICATION is empty — every class "
        f"must surface a physical justification."
    )
    assert justification.rstrip().endswith('.'), (
        f"{cls.__name__}.PHYSICAL_JUSTIFICATION must end with '.'; "
        f"got {justification!r}"
    )


@pytest.mark.parametrize(
    'cls', EVERY_EXCEPTION, ids=lambda c: c.__name__,
)
def test_justification_appears_in_str_output(
    cls: type[E.WirebenchError],
) -> None:
    """The class's `PHYSICAL_JUSTIFICATION` is included in `str(...)`."""
    instance = cls('test message')
    rendered = str(instance)
    assert 'Why: ' in rendered, (
        f"{cls.__name__}'s str(...) must include a 'Why:' line.  Got:\n"
        f"{rendered!r}"
    )
    assert cls.PHYSICAL_JUSTIFICATION in rendered, (
        f"{cls.__name__}'s str(...) must include the full "
        f"PHYSICAL_JUSTIFICATION text.  Got:\n{rendered!r}"
    )


def test_str_keeps_base_message_as_first_line() -> None:
    """The append-only design: the original message remains the head
    of the rendered output so existing `pytest.raises(..., match=...)`
    patterns continue to find it."""
    e = E.ShortCircuitError("multi-driver short")
    assert str(e).splitlines()[0] == "multi-driver short"


def test_source_locations_render_when_provided() -> None:
    """When the exception carries source locations, they render as a
    `Wired at:` line after the justification."""
    e = E.ShortCircuitError(
        "multi-driver short",
        source_locations=[('hello_led.py', 14), ('hello_led.py', 18)],
    )
    rendered = str(e)
    assert 'Wired at: ' in rendered
    assert 'hello_led.py:14' in rendered
    assert 'hello_led.py:18' in rendered


def test_source_locations_absent_when_not_provided() -> None:
    """No source-location line when the exception was raised without
    attribution — keeps the message tight for non-wiring defects."""
    e = E.RefdesError("bad refdes")
    assert 'Wired at:' not in str(e)


def test_source_locations_property_is_tuple() -> None:
    """`source_locations` exposes an immutable tuple regardless of how
    the constructor was called."""
    e = E.ShortCircuitError(
        "x", source_locations=[('a.py', 1), ('b.py', 2)],
    )
    assert e.source_locations == (('a.py', 1), ('b.py', 2))
    assert isinstance(e.source_locations, tuple)


def test_existing_match_patterns_still_hit() -> None:
    """Append-only design: regexes anchored on the base message still
    find their target after the new `Why:` / `Wired at:` lines."""
    import re
    e = E.ShortCircuitError(
        "Short circuit on logical net — multiple drivers: foo, bar",
        source_locations=[('x.py', 1)],
    )
    assert re.search(r'^Short circuit on logical net', str(e),
                     re.MULTILINE)
