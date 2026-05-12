"""Generate docs/substrate-compatibility-audit.md.

Walks the component registry, constructs every class via the same
best-effort instantiation used elsewhere in the framework, reads the
six substrate-compatibility properties, and emits a Markdown table.

Run from the repo root:

    uv run python scripts/generate_substrate_audit.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_SRC = _REPO / 'src'
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import components.chips     # noqa: F401, E402
import components.diodes    # noqa: F401, E402
import components.passives  # noqa: F401, E402
import components.transistors  # noqa: F401, E402
import components.connectors  # noqa: F401, E402

from framework.factor import FactorNode  # noqa: E402
from framework.registry import _REGISTRY  # noqa: E402


def _construct(cls: type) -> FactorNode | None:
    """Same registry-sweep helper used by the audit test."""
    try:
        if hasattr(cls, 'REFDES_PREFIX'):
            kwargs: dict[str, object] = {'refdes_number': 1}
            name = cls.__name__
            if name == 'Resistor':       kwargs['ohms']    = 330
            elif name == 'Capacitor':    kwargs['farads']  = 100e-9
            elif name == 'Inductor':     kwargs['henries'] = 100e-6
            elif name == 'LED':          kwargs['color']   = 'red'
            elif name == 'Cell':         kwargs['initial_state_of_charge'] = 1.0
            elif name == 'NE555_Monostable': kwargs['duration_ms'] = 1.0
            elif 'Header' in name and ('Female' in name or 'Male' in name):
                kwargs.update({'pin_count': 4, 'pitch_mm': 2.54})
            elif name in ('IDC2xNMale', 'IDC2xNSocket'):
                kwargs.update({'pin_count': 10, 'pitch_mm': 2.54})
            elif name == 'ScrewTerminalBlock':
                kwargs.update({'pin_count': 4, 'pitch_mm': 5.08})
            elif name.startswith('JST'):
                kwargs['pin_count'] = 4
            elif name == 'ISOW7841':
                from framework.ground import GroundDomain
                kwargs['iso_domain'] = GroundDomain('iso_audit')
            return cls(**kwargs)  # type: ignore[call-arg]
        if cls.__name__ == 'Rail':
            return cls(level=True)  # type: ignore[call-arg]
        if cls.__name__ == 'DiodeOR':
            return cls(input_names=('a',))  # type: ignore[call-arg]
        if cls.__name__ == 'Monostable':
            return cls(duration_ms=1.0)  # type: ignore[call-arg]
        return cls()  # type: ignore[call-arg]
    except Exception:
        return None


def _flag(b: bool) -> str:
    return 'Y' if b else 'N'


def main() -> None:
    lines = [
        "# Substrate-Compatibility Audit",
        "",
        "Generated from the live `is_*` properties on every registered "
        "component.  Re-generate with `uv run python scripts/generate_substrate_audit.py`.",
        "",
        "Columns:",
        "",
        "- **TH**: `is_through_hole` — leads pass through breadboard / perfboard holes",
        "- **SMD**: `is_smd` — surface-mount pad geometry",
        "- **BB**: `is_breadboard_compatible` — fits a standard 830-pin solderless breadboard",
        "- **PB**: `is_perfboard_compatible` — fits standard 0.1\" perfboard",
        "- **PCB**: `is_pcb_compatible` — placeable on a custom PCB (THT or SMD)",
        "- **DB**: `is_dead_bug_compatible` — wired point-to-point in dead-bug fashion",
        "",
        "| Class | TH | SMD | BB | PB | PCB | DB | Footprint |",
        "|-------|----|-----|----|----|-----|----|-----------|",
    ]

    rows: list[tuple[str, str]] = []
    for name in sorted(_REGISTRY):
        cls = _REGISTRY[name]
        inst = _construct(cls)
        if inst is None:
            rows.append((name, f"| {name} | ?  | ?  | ?  | ?  | ?  | ?  | (could not instantiate) |"))
            continue
        fp = inst.FOOTPRINT or '—'
        row = (
            f"| {name} | {_flag(inst.is_through_hole)} "
            f"| {_flag(inst.is_smd)} "
            f"| {_flag(inst.is_breadboard_compatible)} "
            f"| {_flag(inst.is_perfboard_compatible)} "
            f"| {_flag(inst.is_pcb_compatible)} "
            f"| {_flag(inst.is_dead_bug_compatible)} "
            f"| `{fp}` |"
        )
        rows.append((name, row))

    for _, line in rows:
        lines.append(line)

    out_path = _REPO / 'docs' / 'substrate-compatibility-audit.md'
    out_path.write_text('\n'.join(lines) + '\n')
    print(f"Wrote {out_path} ({len(rows)} components).")


if __name__ == '__main__':
    main()
