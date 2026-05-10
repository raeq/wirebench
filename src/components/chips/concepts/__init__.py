"""Cell-level building blocks of the chips in `components.chips`.

The contents — NORLatch, TriStateBuffer, Comparator — are silicon-level
abstractions used to *implement* specific chips. Nobody buys a "NOR
latch"; you buy a CD4043B that contains four of them.

Nothing is re-exported. Consumers must use the full module path
(`components.chips.concepts.nor_latch`, etc.) to import a concept.
The verbosity is the point: it advertises that you are reaching past
the pin-level API into a chip's silicon.
"""
