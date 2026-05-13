# Contributing to wirebench

wirebench is a Python framework that refuses to construct a circuit
whose wires wouldn't physically work. Contributions land best when
they preserve that property — the framework's value is the defects
it makes unconstructible, not the features it adds.

This document is the road map. Deeper material lives in
[`docs/`](docs/) (durable design reference, user-curated) and
[`.plans/`](.plans/) (Claude-generated implementation specs and
audits — local-only, gitignored).

## Design principles

Read [`docs/design-principles.md`](docs/design-principles.md) before
non-trivial changes. The short version:

- **Physical fidelity is primary.** Every class represents a physical
  thing. If you couldn't do it with a soldering iron, you can't do it
  in code.
- **Components are callable.** `__call__` is the sole signal
  interface; no setters, no mutator methods.
- **Invalid states raise.** Hardware has forbidden states (S=R=1,
  shoot-through, reversed-polarity electrolytics) — they raise leaves
  from `framework.errors`, never bare `ValueError` / `TypeError`.
- **`__slots__` everywhere.** Physical parts don't grow pins at
  runtime.

## The construction-time invariant model

A `Chip` subclass whose ports include an OUT pin must drive that
pin's internal face via a cell — or declare `BARE_FIRMWARE_DRIVEN =
True` (the opt-out for MCUs whose outputs are firmware-driven). The
`Chip.__init__` check enforces this at construction; a misconfigured
chip can't be instantiated.

When adding a new chip, the canonical pattern is in
[`src/components/chips/concepts/`](src/components/chips/concepts/):
the chip class composes one or more behavioural cells, wires its OUT
pins to cell outputs, and passes the cells in `parts=[...]`. See the
[behavioural-cell audit spec](.plans/behavioural-cell-audit-spec.md)
for the full pattern.

## Adding a new part

Take `LM7805` as the canonical example for a linear regulator:

1. Pick the right base class:
   - `Chip` for ICs (anything with internal logic + a pin table)
   - `Diode` / `Transistor` for those primitives
   - `Connector` for through-hole / SMD / cable connectors with a
     defined mate
   - Subclass directly from `Part` only for genuinely new categories
2. Declare the pin table as `PIN_NUMBERS = {'name': number, ...}` per
   the manufacturer's datasheet.
3. Set `REFDES_PREFIX` per IEEE 315 (`R`, `C`, `U`, `Q`, `D`, `J`,
   `K`, etc.).
4. Set `FOOTPRINT` to a KiCad footprint string (used by the KiCad
   exporter). Browse `Diode_THT:*`, `Package_TO_SOT_THT:*`, etc.
5. If the part has OUT pins: write a concept cell in
   `src/components/chips/concepts/`, instantiate it in the chip's
   `__init__`, wire it to the OUT pin's `.internal` face.
6. Add a pin-number test in
   `tests/components/test_chip_pin_numbers.py`.
7. Add a construction test in `tests/components/`.

The framework's auto-collect machinery picks up `self.<name>` part
attributes — so `self.cell = MyConceptCell(...)` is enough; no
explicit `parts=[...]` is needed for most subclasses.

## `.plans/` vs `docs/`

- `docs/` — durable, user-curated reference. Don't edit without an
  explicit ask. The user decides what's published there.
- `.plans/` — implementation specs, audits, status reports
  (Claude-authored working docs). Gitignored. Local-only.

If you're writing a plan, spec, audit, or report, it goes in
`.plans/`. If it's reference material a contributor would search for
months from now, it goes in `docs/`.

## Running tests

```bash
uv sync --extra dev
uv run pytest                        # full suite (3861 tests)
uv run pytest -k <pattern>           # subset
uv run mypy src/ demos/              # strict type-check
./scripts/cov.sh                     # full coverage report
```

The fast feedback loop is plain `uv run pytest`; coverage is opt-in
via the script because `pytest-cov` and `mutmut` don't co-exist (see
the comment block in `pyproject.toml`).

## Goldens

Several renderers (KiCad, yosys, SPICE, dot, mermaid, BOM) emit byte-
exact output that's compared against checked-in goldens under
`tests/golden/`. When a legitimate behaviour change shifts the
output, regenerate with `UPDATE_GOLDEN=1 uv run pytest <test_path>`
and review the diff — if it contains anything beyond the change you
intended, investigate before committing.

Per-demo doc exports under `demos/*/docs/` are similarly emitted by
`scripts/render_demo_docs.py`.

## Refdes prefixes

The framework enforces IEEE 315 reference-designator prefixes. The
canonical list lives in `src/framework/refdes.py`. A `RefdesError` at
construction usually means a `REFDES_PREFIX` on the class doesn't
match what the registry expects.

## Pre-existing errors

If `pytest`, `mypy`, or any other tooling reports an error — even one
you didn't author — fix it as part of the PR. The repo's standard is
that errors aren't negotiable; tolerating one quickly becomes
tolerating ten.

## Pull request flow

- Open a PR against `main`. The `tests` and `typecheck` workflows
  must pass before merge.
- The PR template is in `.github/PULL_REQUEST_TEMPLATE.md` — it's a
  short checklist; please fill it in.
- Squash on merge is fine; the commit message should describe the
  *why*, not just restate the diff.

## Releases

Tagged releases (`v0.X.Y` on `main`) trigger
`.github/workflows/release.yml`, which builds the wheel and sdist,
publishes to PyPI via a Trusted Publisher (OIDC; no stored API keys),
and creates a GitHub release with auto-generated notes. The workflow
refuses to publish unless the tag matches `pyproject.toml`'s
`version` field.
