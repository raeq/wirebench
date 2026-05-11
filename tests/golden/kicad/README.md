# Golden KiCad netlist files

Reference output for the KiCad netlist exporter. Byte-equality check.

Refresh:

    UPDATE_GOLDEN=1 python -m pytest tests/framework/export/kicad/test_kicad_golden.py
