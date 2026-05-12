"""Schema-level tests for `.circuitry` files — per spec §12 (#9-14)."""
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

# Trigger component registration.
import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.board      # noqa: F401

from framework.errors import LoadError
from framework.format import load_circuitry


def _write(tmp_path: Path, content: dict) -> Path:
    p = tmp_path / "test.circuitry"
    p.write_text(json.dumps(content))
    return p


def test_unsupported_major_version_rejected(tmp_path: Path):
    p = _write(tmp_path, {
        "format_version": "2.0.0",
        "root": {"type": "Circuit", "components": [], "wires": []},
    })
    with pytest.raises(LoadError, match="Unsupported .circuitry format version"):
        load_circuitry(p)


def test_unknown_component_type_rejected(tmp_path: Path):
    p = _write(tmp_path, {
        "format_version": "1.0.0",
        "root": {
            "type": "Circuit",
            "components": [{"type": "FakeChip", "refdes": "U1"}],
            "wires": [],
        },
    })
    with pytest.raises(ValidationError):
        load_circuitry(p)


def test_bad_refdes_pattern_rejected(tmp_path: Path):
    # ResistorRecord requires refdes to match ^R\d+$; "U1" violates.
    p = _write(tmp_path, {
        "format_version": "1.0.0",
        "root": {
            "type": "Circuit",
            "components": [{"type": "Resistor", "refdes": "U1", "ohms": 100}],
            "wires": [],
        },
    })
    with pytest.raises(ValidationError):
        load_circuitry(p)


def test_missing_required_field_rejected(tmp_path: Path):
    # ResistorRecord requires `ohms`.
    p = _write(tmp_path, {
        "format_version": "1.0.0",
        "root": {
            "type": "Circuit",
            "components": [{"type": "Resistor", "refdes": "R1"}],
            "wires": [],
        },
    })
    with pytest.raises(ValidationError):
        load_circuitry(p)


def test_extra_top_level_keys_rejected(tmp_path: Path):
    p = _write(tmp_path, {
        "format_version": "1.0.0",
        "root": {"type": "Circuit", "components": [], "wires": []},
        "comment": "this should fail",
    })
    with pytest.raises(ValidationError):
        load_circuitry(p)


def test_empty_components_list_legal(tmp_path: Path):
    p = _write(tmp_path, {
        "format_version": "1.0.0",
        "root": {"type": "Circuit", "components": [], "wires": []},
    })
    circuit = load_circuitry(p)
    assert len(circuit._factor_nodes) == 0


def test_format_version_pattern_enforced(tmp_path: Path):
    p = _write(tmp_path, {
        "format_version": "not-a-version",
        "root": {"type": "Circuit", "components": [], "wires": []},
    })
    with pytest.raises(ValidationError):
        load_circuitry(p)
