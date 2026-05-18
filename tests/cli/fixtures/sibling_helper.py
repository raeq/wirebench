"""Helper sibling module imported by sibling_import_design.py.

Exists to verify `wirebench validate` puts the design's directory on
sys.path so adjacent helper modules resolve the same way they would
when running the design directly."""


def helper_value() -> int:
    return 42
