# wirebench

> *Describe real electronic circuits in Python. The framework won't let
> a design that wouldn't physically work compile — so when your tests
> are green, the breadboard build matches.*

**KiCad's ERC catches defective wiring after you've drawn the schematic.
wirebench prevents you from constructing the wrong design in the first
place.** Install with `pip install wirebench`; the source is at
[github.com/raeq/wirebench](https://github.com/raeq/wirebench).

## Errors that teach, not just refuse

Every refusal includes four things: *what failed* (the existing
per-defect message), *why the rule exists* (one-line physical
justification), *where you wired the offence* (source-line traceback
to the `wire()` call), and — when one fix is overwhelmingly the right
answer — *what to try*. The rules stay strict; the experience of
meeting them is on your side.

```text
wire() has multiple drivers ('out', 'out') — short circuit
  Why: Two OUT-direction ports on one net fight each other on the
  copper — current sinks through the losing output stage until the
  FETs overheat; one driver per shared conductor.
  Wired at: hello_led.py:14
  Try: Remove one of the two wire() calls connecting out and out, OR
  insert a series element (resistor, diode) between them to break the
  direct conflict.
```

See [The rules](the-rules.md) for every rule and the demo where each
one is first caught.

## Where to go

- [Learning path](learning-path.md) — suggested order through every
  wirebench demo.
- [Prevention benchmark](prevention-benchmark.md) — what wirebench
  catches that KiCad ERC and SKiDL ERC don't, with reproducible test
  cases.
- [Design principles](design-principles.md) — why the framework is
  shaped the way it is.
- [The rules](the-rules.md) — every rule the framework enforces, with
  the physical justification and the demo where each one is first
  caught.
- [Components — auto index](parts.md) — auto-generated index of every
  modelled chip, connector, passive, and transducer.
- [Component notes — curated](component-library-data.md) — hand-curated
  narrative with datasheet links and per-part gotchas.

## See also

- [The `hello_led` README's *what this design is protected from*
  sidebar](https://github.com/raeq/wirebench/blob/main/demos/hello_led/README.md#what-this-design-is-protected-from)
  — a concrete example of how the framework refuses defective designs,
  with verbatim error-class output for two near-miss snippets.
- [All wirebench demos on
  GitHub](https://github.com/raeq/wirebench/tree/main/demos) —
  most carry the same *what this design is protected from* sidebar
  (a small number are source-only).
