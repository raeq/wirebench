# Golden BOM CSV files

Reference output for the BOM CSV exporter, one file per application.
The golden test asserts byte-equality so any change in the BOM output
surfaces as a deliberate diff in the PR that introduced it.

Refresh:

    UPDATE_GOLDEN=1 python -m pytest tests/framework/export/bom/test_bom_golden.py

Review the resulting diff in the PR.
