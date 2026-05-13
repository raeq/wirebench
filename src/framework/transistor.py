from __future__ import annotations

from typing import ClassVar

from framework.part import Part


class Transistor(Part):
    """Three-terminal active device — BJT or MOSFET.

    A black-box marker class: subclasses declare their terminal ports
    (collector/base/emitter for BJTs, drain/gate/source for MOSFETs) and
    set the class-level markers below.  No behavioural model — `evaluate`
    is a no-op and `__call__` is a no-op stub.  SPICE / analog tools see
    a `.MODEL` reference by the class name; for accurate device
    behaviour, substitute a vendor model in `spice-models.lib`.

    `_SPICE_PREFIX` distinguishes the SPICE element letter ('Q' for
    bipolar, 'M' for MOSFET).  `_SPICE_PIN_ORDER` lists the port names
    in the order SPICE expects them in the element line: ('c','b','e')
    for BJTs, ('d','g','s') for MOSFETs.
    """

    __slots__ = ()

    REFDES_PREFIX: ClassVar[str] = 'Q'
    _SPICE_PREFIX: ClassVar[str] = 'Q'
    _SPICE_PIN_ORDER: ClassVar[tuple[str, ...]] = ()


class BJT(Transistor):
    """Bipolar junction transistor — emits as `Q<n> <C> <B> <E> <model>`
    in SPICE.  Subclasses provide the C/B/E ports and PIN_NUMBERS."""

    __slots__ = ()

    _SPICE_PREFIX: ClassVar[str] = 'Q'
    _SPICE_PIN_ORDER: ClassVar[tuple[str, ...]] = ('c', 'b', 'e')


class MOSFET(Transistor):
    """Field-effect transistor (enhancement-mode) — emits as
    `M<n> <D> <G> <S> <model>` in SPICE.  Subclasses provide the D/G/S
    ports and PIN_NUMBERS."""

    __slots__ = ()

    _SPICE_PREFIX: ClassVar[str] = 'M'
    _SPICE_PIN_ORDER: ClassVar[tuple[str, ...]] = ('d', 'g', 's')
