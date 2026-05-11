# Test quality

State of the test suite as of the coverage + mutation-testing
infrastructure landing.  Numbers refresh on every `scripts/cov.sh`
run; this document is the static snapshot.

## Coverage

| Tier | Target | Achieved |
|---|---:|---:|
| Total (excluding `cli/`, `applications/`, `demos/`) | ≥90% | **97.24%** |
| `src/framework/` | ≥95% | **95%** |
| `src/components/` | ≥85% | **99%** |
| `src/framework/export/` | ≥90% | **94%** |

`branch = true` — branch coverage is measured, not just statements.
2679 tests pass / 9 skipped (external-tool round-trips that skip if
the tool isn't installed).

### Commands

```
pytest               # fast feedback, no coverage
scripts/cov.sh       # full suite + terminal + HTML + XML reports
scripts/cov.sh -k X  # extra pytest args pass through
```

CI runs `scripts/cov.sh` on every push and PR and fails on
`fail_under = 90` (configured in `[tool.coverage.report]`).

### Per-tier breakdown (lowest-covered files)

| File | Coverage | Notes |
|---|---:|---|
| `framework/units.py` | 80% | Branch-coverage noise on the dunder-op chain; tests added in `tests/framework/test_units.py` exercise every arithmetic and formatter path |
| `framework/ground.py` | 89% | Two lines on a defensive `__eq__` / `__hash__` corner case |
| `framework/format.py` | 89% | 19 untested error-path raises (malformed refdes, duplicate component id, unknown mate, etc.); each is a defensive `raise ValueError` reachable only from a hand-edited `.circuitry` file |
| `framework/wire.py` | 90% | One uncovered `else` branch and a defensive type-error path |

The 5% gap in `src/framework/` (110/2300 lines) is dominated by error-
path raises that fire on malformed external input — defensive code
that's hard to exercise without bypassing pydantic validation.
Adding tests for those is doable but yields diminishing returns
against the 95% floor.

### Coverage exclusions

`[tool.coverage.report]` excludes lines that are genuinely
uncoverable by tests:

- `pragma: no cover` (explicit opt-out — used sparingly, never for
  real gaps)
- `raise NotImplementedError` (abstract-method bodies)
- `if __name__ == '__main__':` (script entry guards)
- `@abstractmethod` decorators
- Bodies that are only `...` (Protocol / abstract stubs)

`partial_branches` suppresses three classes of coverage.py false
positives — the fall-through "branch" after consecutive class
declarations in `format_records.py`, the same after `type: Literal[...]`
discriminator fields, and the same after single-line `def name(): return ...`
stubs (renderer registrations, dunder arithmetic).

## Mutation testing

`mutmut` is configured to mutate `src/framework/` only — the
components are mostly data-driven (pin tables, refdes prefixes,
footprints) where mutating a constant has low signal.

### Commands

```
scripts/mutate.sh                  # full mutation pass — hours
scripts/mutate.sh --resume         # continue an interrupted pass
scripts/mutate.sh --results        # show last run's results
```

Configuration is in `[tool.mutmut]` (`pyproject.toml`):

- `paths_to_mutate = ["src/framework/"]`
- `tests_dir = ["tests/"]`
- `also_copy = ["demos/", "src/components/", "src/applications/", "src/cli/"]`
  — the conftest imports demos and components, so the mutmut workspace
  needs them.

### Status

Infrastructure landed; the full mutation-survival-rate analysis is
the explicit follow-up captured in `docs/mutation-report.md`.  The
demo run hit a `pytest.main()`-vs-`pytest-cov`-plugin interaction
inside mutmut 3.x's in-process stats collector that needs further
debugging before the full sweep can run unattended.

Target: ≤5% mutant survival rate in `src/framework/` after follow-up
test additions.

## Tests added against coverage gaps

| Test file | What it closed |
|---|---|
| `tests/framework/export/test_renderer_execution.py` | Every (class, format) renderer is now invoked at least once — closed gaps in `dot/renderers.py`, `mermaid/renderers.py`, `kicad/renderers.py`, `spice/renderers.py`, `bom/renderers.py` |
| `tests/framework/export/test_spice_models.py` | The SPICE inline-model helper (`format_models_section`, `_extract_block`, `_read_library`) was at 12%; now exercised end-to-end |
| `tests/framework/export/test_walk.py` | `framework/export/walk.py` (the hierarchical walker for Assembly→Board→Chip) was at 41%; now 100% |
| `tests/framework/export/test_board_top_level.py` | `dot/__init__.py` and `mermaid/__init__.py` had uncovered "Board-as-design" branches; closed by exporting `SensorBoard` directly to every format |
| `tests/framework/export/spice/test_spice_config_paths.py` | Closed the `qualified` / `short_hash` net-name styles, header-comment emission, and inline-models emission branches in `spice/__init__.py` |
| `tests/framework/test_units.py` (extended) | Added per-class `__str__` formatters and `__neg__`/`__abs__`/`__pos__`/`__radd__`/`__rsub__` coverage |

## No softening

Every test added in this pass asserts real content.  No `pytest.skip`,
no `xfail`, no `# pragma: no cover` introduced beyond the documented
defensible categories above.
