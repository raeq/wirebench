"""Reusable scenario-runner for demo `_main()` functions.

A demo typically prints a bill of materials, then walks the user
through a sequence of stimulus → response steps.  The mechanics —
calling the circuit, collecting per-row values, and aligning the
results into a fixed-width table — are the same every time.  Move
that work here so a demo's `_main()` reads like a data file.

Example:

    from circuitry import run_scenarios

    run_scenarios(
        WaterAlarm(),
        scenarios=[
            ("tank empty",      (GND, GND)),
            ("low probe wet",   (VCC, GND)),
            ("high probe wet",  (VCC, VCC)),
        ],
        columns=[
            ("low",   lambda c, a, k: f"{a[0]:.1f}"),
            ("high",  lambda c, a, k: f"{a[1]:.1f}"),
            ("state", lambda c, a, k: c.state),
        ],
    )
"""
from __future__ import annotations

from typing import Any, Callable, Iterable, Mapping, Sequence, cast

from framework.circuit import Circuit
from framework.refdes import RefdesBearing


# A scenario is either (label, args) or (label, args, kwargs).
Scenario = tuple[Any, ...]   # too noisy to spell as a TypeAlias for both shapes

# A column gets the live circuit and the args / kwargs the scenario
# was invoked with, and returns whatever should appear in that cell.
ColumnFn = Callable[[Circuit, tuple[Any, ...], Mapping[str, Any]], Any]
Column = tuple[str, ColumnFn]


def _default_value_annotators() -> dict[str, Callable[[Any], str]]:
    """Per-class value suffix in the BOM listing.  Resistor and
    Capacitor render their values; LED renders its colour."""
    return {
        'Resistor':  lambda r: f"  ({float(r.ohms):g} Ω)",
        'Capacitor': lambda c: f"  ({float(c.farads):g} F)",
        'LED':       lambda d: f"  ({d.color})",
    }


def print_bom(
    circuit: Circuit,
    *,
    value_annotators: Mapping[str, Callable[[Any], str]] | None = None,
) -> None:
    """Print the refdes-bearing parts of `circuit` as a BOM.

    Walks `circuit._factor_nodes`, picks out the parts with refdes,
    and emits one line per part: ``  R1    Resistor  (220 Ω)``.
    Use `value_annotators` to override or extend the default
    per-class value suffix (Resistor → ohms, Capacitor → farads,
    LED → color).
    """
    annotators = _default_value_annotators()
    if value_annotators:
        annotators.update(value_annotators)
    print("Bill of materials:")
    for fn in circuit._factor_nodes:
        if not isinstance(fn, RefdesBearing):
            continue
        cls = type(fn).__name__
        extra = annotators.get(cls, lambda _: '')(fn)
        print(f"  {fn.refdes:5s} {cls}{extra}")


def run_scenarios(
    circuit: Circuit,
    *,
    scenarios: Iterable[Scenario],
    columns: Sequence[Column],
    bom: bool = True,
    label_header: str = 'event',
) -> None:
    """Run a list of scenarios and print results as an aligned table.

    Each scenario is either ``(label, args)`` or
    ``(label, args, kwargs)``.  After invoking ``circuit(*args, **kwargs)``
    each column's getter is called with ``(circuit, args, kwargs)``;
    the returned value is stringified and placed in that column.

    Column widths are computed from the longest value (or the header
    width, whichever is greater) so the resulting table aligns.
    """
    if bom:
        print_bom(circuit)
        print()

    headers = [label_header] + [h for h, _ in columns]
    rows: list[list[str]] = []
    for entry in scenarios:
        label = entry[0]
        args: tuple[Any, ...] = entry[1] if len(entry) > 1 else ()
        kwargs: Mapping[str, Any] = entry[2] if len(entry) > 2 else {}
        # Circuit subclasses define __call__ with their own signature
        # (the abstract base declares it abstract).  mypy can't see
        # through the dynamic call, so we cast to Any for the dispatch.
        cast(Any, circuit)(*args, **kwargs)
        row = [label] + [str(getter(circuit, args, kwargs)) for _, getter in columns]
        rows.append(row)

    widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows))
        for i in range(len(headers))
    ]
    sep = ' | '
    header_line = sep.join(h.ljust(w) for h, w in zip(headers, widths))
    print(header_line)
    print('-' * len(header_line))
    for row in rows:
        print(sep.join(v.ljust(w) for v, w in zip(row, widths)))
