"""End-to-end SPICE export of the WaterAlarm applications."""
import re
import shutil
import subprocess
import warnings

import pytest

# Trigger registrations.
import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.export.spice  # noqa: F401

from framework.export import export

from water_alarm import WaterAlarm
from water_alarm_split import WaterAlarmAssembly


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


def test_water_alarm_exports_to_valid_deck(tmp_path):
    design = _silently(WaterAlarm)
    out = tmp_path / 'wa.cir'
    export(design, 'spice', out)
    text = out.read_text()

    assert out.exists()
    assert '.TITLE' in text
    assert '.END' in text.splitlines()[-3:][-1] or text.rstrip().endswith('.END')
    # Every refdes-bearing component appears.
    assert re.search(r'^U1\b', text, flags=re.M)         # ULN2003A
    assert re.search(r'^D1\b', text, flags=re.M)         # red LED
    assert re.search(r'^D2\b', text, flags=re.M)         # green LED
    # Models reference the library by default.
    assert '.LIB' in text


def test_water_alarm_assembly_exports_with_hierarchy(tmp_path):
    asm = _silently(WaterAlarmAssembly)
    out = tmp_path / 'asm.cir'
    export(asm, 'spice', out)
    text = out.read_text()

    # Two .SUBCKT blocks (one per Board) with matching .ENDS.
    subckts = re.findall(r'^\.SUBCKT\s+(\S+)', text, flags=re.M)
    ends    = re.findall(r'^\.ENDS\s+(\S+)',   text, flags=re.M)
    assert len(subckts) == 2, f"Expected 2 .SUBCKT blocks, got {subckts}"
    assert subckts == ends, f"SUBCKT/ENDS mismatch: {subckts} vs {ends}"
    # X-instances at top level invoking each board subckt.
    for name in subckts:
        assert re.search(rf'^X\S+\s+.+\s+{re.escape(name)}$', text, flags=re.M)


@pytest.mark.skipif(
    not shutil.which('ngspice'),
    reason='ngspice not installed',
)
def test_water_alarm_deck_parses_under_ngspice(tmp_path):
    """Optional: pipe the deck through ngspice -b to verify it parses.

    Skips cleanly when ngspice isn't on PATH so CI works without it.
    """
    design = _silently(WaterAlarm)
    out = tmp_path / 'wa.cir'
    export(design, 'spice', out)

    # Copy the model library next to the deck so the .LIB directive
    # resolves regardless of cwd.
    import framework.export.spice as spice_pkg
    from pathlib import Path
    lib_src = Path(spice_pkg.__path__[0]) / 'spice-models.lib'
    (tmp_path / 'spice-models.lib').write_text(lib_src.read_text())

    result = subprocess.run(
        ['ngspice', '-b', str(out)],
        capture_output=True, text=True, cwd=tmp_path, timeout=30,
    )
    # ngspice exits 0 on a parse-clean deck even without a directive.
    # Some builds exit non-zero if no analysis is requested; treat
    # parse errors as failure but ignore "no analysis" exits.
    if result.returncode != 0:
        # Tolerate "no analysis specified" style warnings; fail on
        # parse / syntax errors.
        if 'Error' in result.stderr or 'syntax' in result.stderr.lower():
            pytest.fail(f"ngspice rejected deck:\n{result.stderr}")
