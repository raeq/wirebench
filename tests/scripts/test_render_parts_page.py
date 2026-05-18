"""Tests for `scripts/render_parts_page.py`.

The script walks the registry and writes a Markdown table to
`docs/parts.md`.  These tests verify the table contains every
registered part and that the output is deterministic across runs.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / 'scripts' / 'render_parts_page.py'


def _run(output_path: Path) -> int:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), '--output', str(output_path)],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        f"render_parts_page.py exited {result.returncode}: "
        f"{result.stderr or result.stdout}"
    )
    return result.returncode


def test_output_contains_every_registered_part(tmp_path: Path) -> None:
    """Importing the same registry and walking it should produce a
    Markdown body that mentions every registered class name.

    Both the registry walk and the page render run in subprocesses to
    avoid contamination from demo-local Board classes that earlier
    tests in this session may have registered.  The script and this
    test see the same fresh registry state."""
    out = tmp_path / 'parts.md'
    _run(out)
    body = out.read_text()

    listing = subprocess.run(
        [sys.executable, '-c',
         'import json, sys; sys.path.insert(0, "src"); '
         'from cli.parts_data import all_parts; '
         'json.dump([p["class_name"] for p in all_parts()], sys.stdout)'],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    )
    import json as _json
    for name in _json.loads(listing.stdout):
        assert name in body, f"{name} missing from rendered page"


def test_output_is_deterministic(tmp_path: Path) -> None:
    """Re-running the generator twice produces byte-identical output."""
    a = tmp_path / 'a.md'
    b = tmp_path / 'b.md'
    _run(a)
    _run(b)
    assert a.read_text() == b.read_text()


def test_output_has_expected_section_headers(tmp_path: Path) -> None:
    out = tmp_path / 'parts.md'
    _run(out)
    text = out.read_text()
    assert "# Components" in text
    assert "| Refdes | Class | Kind | Description |" in text
    assert "## Filtering at the command line" in text


def test_committed_docs_parts_md_is_up_to_date(tmp_path: Path) -> None:
    """The committed `docs/parts.md` matches what the generator
    produces now — catches forgotten regenerations after registry
    changes."""
    fresh = tmp_path / 'parts.md'
    _run(fresh)
    committed = (REPO_ROOT / 'docs' / 'parts.md').read_text()
    assert fresh.read_text() == committed, (
        "docs/parts.md is stale — re-run "
        "`uv run python scripts/render_parts_page.py`"
    )
