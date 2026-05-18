"""End-to-end tests for the `wirebench import-kicad` CLI."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _invoke(*args: str) -> tuple[int, str, str]:
    cmd = [sys.executable, '-m', 'cli.main', 'import-kicad', *args]
    result = subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, text=True,
    )
    return result.returncode, result.stdout, result.stderr


def test_emit_python_writes_runnable_source(tmp_path):
    netlist = REPO_ROOT / 'demos' / 'hello_led' / 'docs' / 'HelloLED.net'
    output = tmp_path / 'imported.py'
    code, out, _ = _invoke(str(netlist), '--output', str(output))
    assert code == 0
    assert 'parts' in out
    assert output.exists()
    # Execute the generated source via a subprocess so registry
    # side-effects don't leak into the test session.
    result = subprocess.run(
        [sys.executable, str(output)],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert 'Constructed' in result.stdout


def test_emit_circuit_produces_json(tmp_path):
    netlist = REPO_ROOT / 'demos' / 'water_alarm' / 'docs' / 'WaterAlarm.net'
    code, out, _ = _invoke(str(netlist), '--emit', 'circuit')
    assert code == 0
    payload = json.loads(out)
    assert payload['status'] == 'constructed'
    assert payload['parts'] > 0
    assert payload['nets'] > 0


def test_strict_mode_fails_on_unmapped_value(tmp_path):
    netlist = tmp_path / 'unknown.net'
    netlist.write_text("""
        (export (version "E")
          (components
            (comp (ref "U1") (value "FrobnicatorX9000")
              (libsource (lib "X") (part "FrobnicatorX9000"))))
          (nets))
    """)
    code, _, err = _invoke(str(netlist), '--strict')
    assert code == 1
    assert 'FrobnicatorX9000' in err


def test_nonexistent_input_returns_error(tmp_path):
    code, _, err = _invoke(str(tmp_path / 'does-not-exist.net'))
    assert code == 2
    assert 'not found' in err


def test_missing_subcommand_arg_returns_usage_error():
    code, _, _ = _invoke()
    assert code == 2
