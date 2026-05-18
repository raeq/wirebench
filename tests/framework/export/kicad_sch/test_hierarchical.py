"""Tests for hierarchical kicad_sch emission (Phase 2.5c)."""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / 'src'))
for _d in sorted((_REPO / 'demos').iterdir()):
    if _d.is_dir():
        sys.path.insert(0, str(_d))

import components.chips        # noqa: F401, E402
import components.passives     # noqa: F401, E402
import components.connectors   # noqa: F401, E402
import components.diodes       # noqa: F401, E402
import framework.export.kicad_sch  # noqa: F401, E402

from framework.export import export_to_string
from framework.export.kicad_sch.hierarchical import (
    collect_boards, is_multi_board, sub_sheet_filename, emit_top_level,
)
from framework.export.kicad_sch.renderer import render_all
from framework.export.base import ExporterContext


def _silently(fn, *a, **k):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return fn(*a, **k)


def _tokenise(text: str):
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c in ' \t\n\r':
            i += 1; continue
        if c in '()':
            yield c; i += 1; continue
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == '\\' else 1
            yield text[i:j + 1]
            i = j + 1; continue
        j = i
        while j < n and text[j] not in ' \t\n\r()':
            j += 1
        yield text[i:j]; i = j


def _parse(text: str):
    tokens = list(_tokenise(text))
    pos = [0]

    def parse_one():
        if pos[0] >= len(tokens):
            raise ValueError("unexpected EOF")
        tok = tokens[pos[0]]
        pos[0] += 1
        if tok == '(':
            out = []
            while pos[0] < len(tokens) and tokens[pos[0]] != ')':
                out.append(parse_one())
            if pos[0] >= len(tokens):
                raise ValueError("missing closing paren")
            pos[0] += 1
            return out
        if tok == ')':
            raise ValueError("unexpected ')'")
        return tok

    result = parse_one()
    if pos[0] != len(tokens):
        raise ValueError(f"trailing tokens: {tokens[pos[0]:]}")
    return result


def test_collect_boards_flat():
    from hello_led import HelloLED
    design = _silently(HelloLED)
    assert collect_boards(design) == []


def test_collect_boards_multi():
    from water_alarm_split import WaterAlarmAssembly
    asm = _silently(WaterAlarmAssembly)
    boards = collect_boards(asm)
    assert len(boards) == 2


def test_is_multi_board_false():
    from hello_led import HelloLED
    assert not is_multi_board(_silently(HelloLED))


def test_is_multi_board_true():
    from water_alarm_split import WaterAlarmAssembly
    assert is_multi_board(_silently(WaterAlarmAssembly))


def test_sub_sheet_filename():
    assert sub_sheet_filename('WaterAlarmAssembly', 'SensorBoard') == \
        'WaterAlarmAssembly__SensorBoard.kicad_sch'


def test_emit_top_level_parses():
    from water_alarm_split import WaterAlarmAssembly
    asm = _silently(WaterAlarmAssembly)
    boards = collect_boards(asm)
    text = emit_top_level(boards, 'WaterAlarmAssembly')
    tree = _parse(text)
    assert isinstance(tree, list)
    assert tree[0] == 'kicad_sch'


def test_emit_top_level_has_sheet_blocks():
    from water_alarm_split import WaterAlarmAssembly
    asm = _silently(WaterAlarmAssembly)
    boards = collect_boards(asm)
    text = emit_top_level(boards, 'WaterAlarmAssembly')
    tree = _parse(text)
    sheet_blocks = [b for b in tree if isinstance(b, list) and b and b[0] == 'sheet']
    assert len(sheet_blocks) == len(boards)


def test_emit_top_level_sheetnames():
    from water_alarm_split import WaterAlarmAssembly
    asm = _silently(WaterAlarmAssembly)
    boards = collect_boards(asm)
    text = emit_top_level(boards, 'WaterAlarmAssembly')
    assert 'SensorBoard' in text
    assert 'ControllerBoard' in text


def test_emit_top_level_sheetfiles():
    from water_alarm_split import WaterAlarmAssembly
    asm = _silently(WaterAlarmAssembly)
    boards = collect_boards(asm)
    text = emit_top_level(boards, 'WaterAlarmAssembly')
    assert 'WaterAlarmAssembly__SensorBoard.kicad_sch' in text
    assert 'WaterAlarmAssembly__ControllerBoard.kicad_sch' in text


def test_emit_top_level_no_symbol_instances():
    from water_alarm_split import WaterAlarmAssembly
    asm = _silently(WaterAlarmAssembly)
    boards = collect_boards(asm)
    text = emit_top_level(boards, 'WaterAlarmAssembly')
    tree = _parse(text)
    top_symbols = [b for b in tree if isinstance(b, list) and b and b[0] == 'symbol']
    assert top_symbols == [], f"Top-level should have no symbol instances; got {top_symbols}"


def test_render_all_flat_returns_one_file():
    from hello_led import HelloLED
    design = _silently(HelloLED)
    ctx = ExporterContext(design, 'kicad_sch')
    files = render_all(design, ctx)
    assert list(files.keys()) == ['HelloLED.kicad_sch']


def test_render_all_multi_board_returns_three_files():
    from water_alarm_split import WaterAlarmAssembly
    asm = _silently(WaterAlarmAssembly)
    ctx = ExporterContext(asm, 'kicad_sch')
    files = render_all(asm, ctx)
    assert len(files) == 3
    assert 'WaterAlarmAssembly.kicad_sch' in files
    assert 'WaterAlarmAssembly__SensorBoard.kicad_sch' in files
    assert 'WaterAlarmAssembly__ControllerBoard.kicad_sch' in files


def test_render_all_sub_sheets_have_symbols():
    """Every sub-sheet must contain symbol instances.

    Uses CooledSystem (FanCoolingBoard + PowerSourceBoard) where both boards
    contain symbol-map-covered parts (Resistor, D1N4728A, SN74AHC1G14,
    Header connector).  WaterAlarmAssembly is not used here because
    ULN2003A has no vendored symbol yet.
    """
    from fan_cooling import CooledSystem
    asm = _silently(CooledSystem)
    ctx = ExporterContext(asm, 'kicad_sch')
    files = render_all(asm, ctx)
    sub_sheets = {n: c for n, c in files.items() if '__' in n}
    assert sub_sheets, "No sub-sheets found"
    for name, content in sub_sheets.items():
        tree = _parse(content)
        syms = [b for b in tree if isinstance(b, list) and b and b[0] == 'symbol']
        assert syms, f"Sub-sheet {name} has no symbol instances"


def test_render_all_top_level_is_not_giant():
    from water_alarm_split import WaterAlarmAssembly
    asm = _silently(WaterAlarmAssembly)
    ctx = ExporterContext(asm, 'kicad_sch')
    files = render_all(asm, ctx)
    top_text = files['WaterAlarmAssembly.kicad_sch']
    assert len(top_text.splitlines()) < 100


def test_export_to_string_multi_board_is_hierarchical():
    from water_alarm_split import WaterAlarmAssembly
    asm = _silently(WaterAlarmAssembly)
    text = export_to_string(asm, 'kicad_sch')
    tree = _parse(text)
    sheet_blocks = [b for b in tree if isinstance(b, list) and b and b[0] == 'sheet']
    assert len(sheet_blocks) >= 2, "Top-level should have sheet blocks for each Board"


def test_render_all_deterministic():
    from water_alarm_split import WaterAlarmAssembly
    asm = _silently(WaterAlarmAssembly)
    ctx1 = ExporterContext(asm, 'kicad_sch')
    ctx2 = ExporterContext(asm, 'kicad_sch')
    files1 = render_all(asm, ctx1)
    files2 = render_all(asm, ctx2)
    assert files1 == files2
