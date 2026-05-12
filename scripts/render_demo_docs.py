"""Generate the per-demo `docs/` artefacts.

For every top-level construct in `demos/<name>/<name>.py`, exports
all six formats (bom, dot, kicad, mermaid, spice, yosys) into
`demos/<name>/docs/<Class>.<ext>`, and additionally renders the
Graphviz output as a top-to-bottom SVG using the real `dot` binary.

Run from the repo root:

    uv run python scripts/render_demo_docs.py

Re-run any time a demo's structure changes — the script overwrites
existing artefacts in place so the docs/ directory always matches
the current source.
"""
from __future__ import annotations

import subprocess
import sys
import warnings
from pathlib import Path
from typing import Callable

_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO / 'src'))
for _d in sorted((_REPO / 'demos').iterdir()):
    if _d.is_dir():
        sys.path.insert(0, str(_d))

# Trigger every component / demo registration.
import components.chips           # noqa: F401, E402
import components.passives        # noqa: F401, E402
import components.connectors      # noqa: F401, E402
import components.diodes          # noqa: F401, E402
import components.transistors     # noqa: F401, E402
import framework.board            # noqa: F401, E402
import framework.export.bom       # noqa: F401, E402
import framework.export.dot       # noqa: F401, E402
import framework.export.kicad     # noqa: F401, E402
import framework.export.mermaid   # noqa: F401, E402
import framework.export.spice     # noqa: F401, E402
import framework.export.yosys     # noqa: F401, E402

from framework.export import export_to_string


# Per-format file extension.  Conventions match each format's
# real-world tools: KiCad eats `.net`, Mermaid CLI eats `.mmd`,
# Yosys eats JSON, SPICE decks are `.cir`.
EXTENSIONS = {
    'bom':     'bom.csv',
    'dot':     'dot',
    'kicad':   'net',
    'mermaid': 'mmd',
    'spice':   'cir',
    'yosys':   'yosys.json',
}


def _constructs() -> dict[str, list[tuple[str, Callable]]]:
    """Map demo-directory name → list of (class_name, factory)."""
    from water_alarm import WaterAlarm
    from water_alarm_split import (
        SensorBoard, ControllerBoard, WaterAlarmAssembly,
    )
    from dice import Dice
    from digital_thermometer import DigitalThermometer
    from doorbell_protector import DoorbellProtector
    from backup_power import BackupPower
    from fan_cooling import FanCoolingBoard, CooledSystem
    from bldc_motor import BLDCControllerBoard, BLDCSystem
    from isolated_rs232 import IsolatedRS232Board, IsolatedRS232Link
    from li_ion_fuel_gauge import BatteryPackBoard

    return {
        'water_alarm': [
            ('WaterAlarm', lambda: WaterAlarm()),
        ],
        'water_alarm_split': [
            ('SensorBoard',          lambda: SensorBoard(refdes_number=1)),
            ('ControllerBoard',      lambda: ControllerBoard(refdes_number=2)),
            ('WaterAlarmAssembly',   lambda: WaterAlarmAssembly()),
        ],
        'dice': [
            ('Dice', lambda: Dice()),
        ],
        'digital_thermometer': [
            ('DigitalThermometer', lambda: DigitalThermometer()),
        ],
        'doorbell_protector': [
            ('DoorbellProtector', lambda: DoorbellProtector()),
        ],
        'backup_power': [
            ('BackupPower', lambda: BackupPower()),
        ],
        'fan_cooling': [
            ('FanCoolingBoard', lambda: FanCoolingBoard(refdes_number=1)),
            ('CooledSystem',    lambda: CooledSystem()),
        ],
        'bldc_motor': [
            ('BLDCControllerBoard', lambda: BLDCControllerBoard(refdes_number=1)),
            ('BLDCSystem',          lambda: BLDCSystem()),
        ],
        'isolated_rs232': [
            ('IsolatedRS232Board', lambda: IsolatedRS232Board(refdes_number=1)),
            ('IsolatedRS232Link',  lambda: IsolatedRS232Link()),
        ],
        'li_ion_fuel_gauge': [
            ('BatteryPackBoard', lambda: BatteryPackBoard(refdes_number=1)),
        ],
    }


def _retarget_dot_to_tb(dot_path: Path) -> None:
    """Rewrite a `.dot` file in place so its `rankdir` is `TB` instead
    of `LR`.  The library currently emits LR, but the docs/ artefacts
    are saved as top-to-bottom diagrams (matches the matching `.mmd`
    convention)."""
    text = dot_path.read_text()
    if 'rankdir=LR' in text:
        dot_path.write_text(text.replace('rankdir=LR', 'rankdir=TB'))


def _retarget_mermaid_to_td(mmd_path: Path) -> None:
    """Rewrite a `.mmd` file in place so its `flowchart` direction is
    `TD` (top-down) instead of `LR`.  Mermaid uses `TD` as the canonical
    spelling for the same direction Graphviz calls `TB`."""
    text = mmd_path.read_text()
    if 'flowchart LR' in text:
        mmd_path.write_text(text.replace('flowchart LR', 'flowchart TD'))


def _render_svg(dot_path: Path, svg_path: Path) -> None:
    """Render a `.dot` source to an SVG.  The source has already been
    rewritten to `rankdir=TB` by `_retarget_dot_to_tb`, so we just
    point `dot` at the file on disk."""
    result = subprocess.run(
        ['dot', '-Tsvg', '-o', str(svg_path), str(dot_path)],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"dot rejected {dot_path}: {result.stderr.strip()}"
        )


def main() -> None:
    constructs = _constructs()
    total = 0
    for demo, cells in constructs.items():
        docs = _REPO / 'demos' / demo / 'docs'
        docs.mkdir(parents=True, exist_ok=True)
        for class_name, factory in cells:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                circuit = factory()
            for fmt, ext in EXTENSIONS.items():
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    out = export_to_string(circuit, fmt)
                path = docs / f"{class_name}.{ext}"
                path.write_text(out)
                total += 1
            # Rewrite the saved .dot and .mmd to top-to-bottom layout
            # — the library currently emits left-to-right by default,
            # but the docs/ artefacts are saved as TB / TD so the
            # eyes that read them get vertical signal flow.
            dot_path = docs / f"{class_name}.dot"
            mmd_path = docs / f"{class_name}.mmd"
            _retarget_dot_to_tb(dot_path)
            _retarget_mermaid_to_td(mmd_path)
            # Render the (now TB) DOT to an SVG using the real
            # graphviz binary.
            svg_path = docs / f"{class_name}.svg"
            _render_svg(dot_path, svg_path)
            total += 1
            print(f"  {demo}/{class_name}: 7 artefacts")
    print(f"\nWrote {total} files across {len(constructs)} demos.")


if __name__ == '__main__':
    main()
