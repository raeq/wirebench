#!/usr/bin/env bash
# Mutation-test wrapper around mutmut.
#
# Configuration lives in `pyproject.toml [tool.mutmut]`:
#   - paths_to_mutate = "src/framework/"  (only the framework — components
#     are mostly data-driven and have low mutation-testing signal)
#   - runner = "python -m pytest -x --no-cov -q"
#
# Usage:
#
#   scripts/mutate.sh                       # full mutation pass over framework
#   scripts/mutate.sh src/framework/wire.py # one file
#   scripts/mutate.sh --resume              # continue an interrupted pass
#   scripts/mutate.sh --results             # show last run's results
#
# A full pass takes a long time (hours).  The cache at .mutmut-cache lets
# you resume mid-run; mutmut also re-uses cached results when the source
# hasn't changed.  Single-file runs are the practical iteration loop:
# kill survivors one file at a time.
set -euo pipefail

cd "$(dirname "$0")/.."

case "${1:-run}" in
  --resume)
    exec python -m mutmut run --resume
    ;;
  --results)
    exec python -m mutmut results
    ;;
  -h|--help)
    sed -n '2,20p' "$0"
    exit 0
    ;;
  src/*)
    exec python -m mutmut run --paths-to-mutate "$1"
    ;;
  run|"")
    exec python -m mutmut run
    ;;
  *)
    echo "Unknown argument: $1" >&2
    exec "$0" --help
    ;;
esac
