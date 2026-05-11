#!/usr/bin/env bash
# Run the test suite with coverage measurement.
#
# Usage:
#
#   scripts/cov.sh             # full suite + terminal + HTML + XML reports
#   scripts/cov.sh -k pattern  # pass extra pytest args through
#
# Coverage thresholds are enforced by `[tool.coverage.report] fail_under`
# in pyproject.toml; this script will exit non-zero if total coverage
# drops below 90%.  Per-tier targets (framework ≥95%, components ≥85%)
# are documented in docs/test-quality.md and checked there manually.
set -euo pipefail
cd "$(dirname "$0")/.."
exec python -m pytest \
    --cov=src \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    "$@"
