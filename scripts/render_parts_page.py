"""Render `docs/parts.md` — the doc-site Components catalogue page.

Walks the framework's component registry, builds the same descriptor
dict the `wirebench parts` CLI uses, and emits a Markdown table — one
row per registered part.  Run from the docs workflow before
`mkdocs build` so the page is fresh on every deploy.

The page itself is committed to the repo so contributors browsing on
GitHub also see a populated catalogue; the workflow keeps it current.

Usage:

    uv run python scripts/render_parts_page.py [--output PATH]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO / 'src'))

from cli.parts_data import PartDescriptor, all_parts  # noqa: E402


def _format_module_cell(module: str, class_name: str) -> str:
    """`module.class_name` as a backticked import path.  No link to
    source — the source is one click from the GitHub repo URL in the
    site header, and adding inline anchors would couple the page to
    the on-disk file layout."""
    return f"`{module}.{class_name}`"


def _format_datasheet_cell(url: str | None) -> str:
    if not url:
        return "—"
    return f"[datasheet]({url})"


def _format_footprint_cell(footprint: str | None, kind: str) -> str:
    if footprint:
        return f"`{footprint}`"
    # Parameterised connectors compute footprint from instance state;
    # passives like Resistor have no fixed footprint.  Show 'various'
    # rather than an empty cell so the column reads as deliberate.
    if kind in ('connector', 'passive', 'diode', 'transistor', 'board'):
        return "various"
    return "—"


def _format_refdes_cell(prefix: str | None) -> str:
    if prefix:
        return f"`{prefix}`"
    return "—"


def _render(parts: list[PartDescriptor]) -> str:
    lines = [
        "# Components",
        "",
        "Every part wirebench models — every chip, connector, passive,",
        "diode, transistor, relay, and the `Board` base class.  Each row",
        "shows the refdes prefix the framework assigns when you place",
        "the part, the import path, the kind of component, and a",
        "one-line description from the class docstring.",
        "",
        f"**{len(parts)} parts** across "
        f"{len({p['kind'] for p in parts})} categories.",
        "",
        "| Refdes | Class | Kind | Description | Footprint | Datasheet |",
        "|--------|-------|------|-------------|-----------|-----------|",
    ]
    for p in parts:
        lines.append(
            f"| {_format_refdes_cell(p['refdes_prefix'])} "
            f"| {_format_module_cell(p['module'], p['class_name'])} "
            f"| {p['kind']} "
            f"| {p['description']} "
            f"| {_format_footprint_cell(p['footprint'], p['kind'])} "
            f"| {_format_datasheet_cell(p['datasheet'])} |"
        )
    lines.append("")
    lines.append(
        "## Filtering at the command line"
    )
    lines.append("")
    lines.append(
        "The same catalogue is available locally via the "
        "`wirebench parts` CLI:"
    )
    lines.append("")
    lines.append("```bash")
    lines.append("wirebench parts                    # every part, aligned text")
    lines.append("wirebench parts --kind chip        # only chips")
    lines.append("wirebench parts --prefix R         # only refdes-R parts (Resistor)")
    lines.append("wirebench parts --has-footprint    # only parts with a fixed footprint")
    lines.append("wirebench parts --pin-function POWER")
    lines.append("wirebench parts --json             # structured JSON for tooling")
    lines.append("```")
    lines.append("")
    lines.append(
        "Filters compose with AND — combine `--kind`, `--prefix`, "
        "`--has-cell`, `--has-footprint`, and `--pin-function` freely."
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description='Render the doc-site Components catalogue.',
    )
    parser.add_argument(
        '--output', default=str(_REPO / 'docs' / 'parts.md'),
        help='Output path (default: docs/parts.md in the repo).',
    )
    args = parser.parse_args(argv)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    text = _render(all_parts())
    output_path.write_text(text)
    print(f"  + {len(all_parts())} parts → {output_path}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
