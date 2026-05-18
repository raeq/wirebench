# wirebench

> *Describe real electronic circuits in Python. The framework won't let
> a design that wouldn't physically work compile — so when your tests
> are green, the breadboard build matches.*

**KiCad's ERC catches defective wiring after you've drawn the schematic.
wirebench prevents you from constructing the wrong design in the first
place.** Install with `pip install wirebench`; the source is at
[github.com/raeq/wirebench](https://github.com/raeq/wirebench).

## Where to go

- [Learning path](learning-path.md) — suggested order through the
  twelve demos.
- [Prevention benchmark](prevention-benchmark.md) — what wirebench
  catches that KiCad ERC and SKiDL ERC don't, with reproducible test
  cases.
- [Design principles](design-principles.md) — why the framework is
  shaped the way it is.
- [Component catalogue](component-library-data.md) — every modelled
  chip, connector, and passive, with datasheet links.

## See also

The demos at
[github.com/raeq/wirebench/tree/main/demos](https://github.com/raeq/wirebench/tree/main/demos)
each have their own `README.md` showing what defects the framework
would have refused in that design.
