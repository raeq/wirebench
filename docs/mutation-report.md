# Mutation report

Tracking the mutation-testing follow-up for `src/framework/`.

## Status

**Infrastructure landed; full mutation pass pending.**

`mutmut` 3.5 is installed, configured, and wrappered via
`scripts/mutate.sh`.  The framework is scoped as the mutation target
(`paths_to_mutate = ["src/framework/"]`).  Components are excluded
on purpose — they're data-driven (pin tables, refdes prefixes,
footprints) where mutating a constant has low signal-to-noise.

The full mutation run was not landed in the same turn as the
infrastructure because mutmut 3.x's in-process `pytest.main()` stats
collector hits an exit-4 error that's resistant to `--override-ini`
and `-p no:cov` knobs.  Manual `pytest` invocations with identical
args inside the `mutants/` workspace pass cleanly, so it's a
plugin-state-reuse interaction between `pytest.main()` and
`pytest-cov` v7.

### Next steps to unblock the full run

Things that should be tried in the follow-up turn:

1. Run mutmut from a virtualenv that doesn't have `pytest-cov`
   installed (it's only needed for `scripts/cov.sh`, not for mutmut).
   Simplest path: `mutmut run` inside a separate venv built from
   `pip install -e .[dev] --no-deps` plus `pip install pytest mutmut`
   — explicitly skip pytest-cov.
2. Alternative: patch mutmut's `execute_pytest` to spawn pytest as a
   subprocess (current behaviour is in-process via `pytest.main()`).
3. Alternative: pin mutmut to an earlier version (2.x) where the
   stats collection used subprocess pytest.
4. Run the full mutation pass overnight or on a scheduled CI job
   (the project's `.github/workflows/test.yml` runs coverage; a
   second workflow `mutation.yml` triggered on `schedule:` would fit
   the "≤5% survival rate" target without blocking PRs).

## Target

≤5% mutant survival rate across `src/framework/`.  Industry
benchmark for a well-tested codebase is 5–10%; ≤5% is the project's
acceptance threshold.

## When the run completes

Append to this document:

- One section per `src/framework/` file with:
  - Total mutants generated
  - Killed / Survived / Timed-out / Suspicious counts
  - Survival rate
- For every surviving mutant that is **not** a documented equivalent
  mutation, the test file + test name that was added to kill it.
- "Equivalent mutations" subsection: list any mutants that are
  truly equivalent to the original (e.g., `x == x` → `x != x` where
  `x` is provably itself), with a one-line justification each.
- A top-5 list of "weak-spot clusters" — files / functions where
  many mutants survived, indicating a structural test gap.

## Equivalent mutations (running list)

None catalogued yet — the run hasn't completed.
