"""Generate the per-demo `docs/` artefacts.

Auto-discovers every demo by walking `demos/<subdir>/*.py`, importing
each module, and finding every `Circuit` subclass *defined in* that
module.  For each such class, exports all ten formats (bom, dot,
kicad, mermaid, spice, yosys, assembly_guide, net_report,
domain_report, interface_report) into `demos/<subdir>/docs/<Class>.<ext>`,
and additionally renders the Graphviz output as a top-to-bottom SVG
using the real `dot` binary.

The `assembly_guide` format refuses SMD and multi-board designs by
raising `BreadboardIncompatibleError`; for those, the script writes a
short stub Markdown that explains the refusal and points at the other
exports.

Run from the repo root:

    uv run python scripts/render_demo_docs.py

Re-run any time a demo's structure changes — the script overwrites
existing artefacts in place so the docs/ directory always matches
the current source.

Adding a new demo: drop a folder under `demos/` containing a
top-level Python file with one or more `Circuit` subclasses; the
script will pick them up next run without any registration here.
"""
from __future__ import annotations

import importlib
import subprocess
import sys
import warnings
from pathlib import Path
from typing import Iterator

_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO / 'src'))
for _d in sorted((_REPO / 'demos').iterdir()):
    if _d.is_dir():
        sys.path.insert(0, str(_d))

# Trigger every component registration.
import components.chips           # noqa: F401, E402
import components.passives        # noqa: F401, E402
import components.connectors      # noqa: F401, E402
import components.diodes          # noqa: F401, E402
import components.transistors     # noqa: F401, E402
import framework.board                  # noqa: F401, E402
import framework.export.bom              # noqa: F401, E402
import framework.export.dot              # noqa: F401, E402
import framework.export.kicad            # noqa: F401, E402
import framework.export.mermaid          # noqa: F401, E402
import framework.export.spice            # noqa: F401, E402
import framework.export.yosys            # noqa: F401, E402
import framework.export.assembly_guide   # noqa: F401, E402
import framework.export.net_report       # noqa: F401, E402
import framework.export.domain_report    # noqa: F401, E402
import framework.export.interface_report # noqa: F401, E402

from framework.circuit import Circuit                # noqa: E402
from framework.errors import BreadboardIncompatibleError  # noqa: E402
from framework.export import export_to_string         # noqa: E402


# Per-format file extension.  Conventions match each format's
# real-world tools: KiCad eats `.net`, Mermaid CLI eats `.mmd`,
# Yosys eats JSON, SPICE decks are `.cir`.
EXTENSIONS = {
    'bom':              'bom.csv',
    'dot':              'dot',
    'kicad':            'net',
    'mermaid':          'mmd',
    'spice':            'cir',
    'yosys':            'yosys.json',
    'assembly_guide':   'md',
    'net_report':       'net-report.md',
    'domain_report':    'domain-report.md',
    'interface_report': 'interface-report.md',
}


def _discover() -> Iterator[tuple[str, str, type]]:
    """Walk every `demos/<subdir>/*.py` and yield each `Circuit`
    subclass *defined in* the imported module.

    The `obj.__module__ == mod_name` guard prevents yielding classes
    that were imported into the module from elsewhere (so e.g.
    `from wirebench import Circuit` doesn't inject Circuit itself
    into the rendering list).  Files whose name starts with `_` are
    skipped — that's the convention for private modules; same for
    subdirectories beginning with `_`."""
    demos_root = _REPO / 'demos'
    for demo_dir in sorted(demos_root.iterdir()):
        if not demo_dir.is_dir() or demo_dir.name.startswith('_'):
            continue
        for py_file in sorted(demo_dir.glob('*.py')):
            if py_file.name.startswith('_'):
                continue
            mod_name = py_file.stem
            try:
                mod = importlib.import_module(mod_name)
            except Exception as exc:
                print(f"  ! skipping {demo_dir.name}/{py_file.name}: "
                      f"import failed ({exc!r})")
                continue
            for name in sorted(dir(mod)):
                obj = getattr(mod, name)
                if (isinstance(obj, type)
                        and issubclass(obj, Circuit)
                        and obj.__module__ == mod_name):
                    yield demo_dir.name, name, obj


def _construct(cls: type) -> Circuit | None:
    """Best-effort instantiation.

    Demo top-level classes typically construct one of two ways:
    `cls()` for free-standing Circuits, or `cls(refdes_number=1)` for
    Board subclasses.  Try both unconditionally — the first call may
    fail with `TypeError`, `pydantic.ValidationError`, or any other
    'missing required arg' shape; we don't try to distinguish.  If
    both fail, the class needs per-class glue and is skipped."""
    from typing import Any, cast
    factory = cast(Any, cls)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        try:
            inst: Circuit = factory()
            return inst
        except Exception:
            pass
        try:
            return cast(Circuit, factory(refdes_number=1))
        except Exception:
            return None


def _refusal_stub(class_name: str, error: BreadboardIncompatibleError) -> str:
    """Brief Markdown stub for designs the assembly-guide exporter
    refuses.  Names the design, surfaces the refusal reason, and
    points at the other export formats."""
    return (
        f"# {class_name}\n"
        f"\n"
        f"This design cannot be assembled on a standard 830-pin solderless "
        f"breadboard.  The assembly-guide exporter refused with:\n"
        f"\n"
        f"```\n"
        f"{error}\n"
        f"```\n"
        f"\n"
        f"## Use a different export\n"
        f"\n"
        f"- **PCB layout** — `{class_name}.net` is a KiCad netlist; "
        f"import into Pcbnew to lay out a board.\n"
        f"- **Simulation** — `{class_name}.cir` is a SPICE deck; run it "
        f"in ngspice or LTspice before committing to silicon.\n"
        f"- **Documentation** — `{class_name}.svg` (rendered from "
        f"`{class_name}.dot`) and `{class_name}.mmd` give the schematic "
        f"as a graph diagram.\n"
        f"- **Procurement** — `{class_name}.bom.csv` is the parts list "
        f"for the PCB build.\n"
    )


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
    total_files = 0
    rendered = 0
    skipped = 0
    seen_demos: set[str] = set()
    for demo, class_name, cls in _discover():
        seen_demos.add(demo)
        circuit = _construct(cls)
        if circuit is None:
            print(f"  - {demo}/{class_name}: skipped (cannot construct)")
            skipped += 1
            continue
        docs = _REPO / 'demos' / demo / 'docs'
        docs.mkdir(parents=True, exist_ok=True)
        for fmt, ext in EXTENSIONS.items():
            path = docs / f"{class_name}.{ext}"
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    out = export_to_string(circuit, fmt)
            except BreadboardIncompatibleError as e:
                # Only the assembly_guide refuses on substrate grounds —
                # preserve the refusal as a stub doc.
                out = _refusal_stub(class_name, e)
            path.write_text(out)
            total_files += 1
        # Rewrite the saved .dot and .mmd to top-to-bottom layout —
        # the library currently emits left-to-right by default, but
        # the docs/ artefacts are saved as TB / TD so the eyes that
        # read them get vertical signal flow.
        dot_path = docs / f"{class_name}.dot"
        mmd_path = docs / f"{class_name}.mmd"
        _retarget_dot_to_tb(dot_path)
        _retarget_mermaid_to_td(mmd_path)
        svg_path = docs / f"{class_name}.svg"
        _render_svg(dot_path, svg_path)
        total_files += 1
        rendered += 1
        print(f"  + {demo}/{class_name}: {len(EXTENSIONS) + 1} artefacts")

    print(f"\nWrote {total_files} files for {rendered} classes "
          f"across {len(seen_demos)} demos "
          f"({skipped} classes skipped).")


if __name__ == '__main__':
    main()
