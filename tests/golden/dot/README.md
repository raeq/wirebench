# Golden DOT files

Reference output for the Graphviz DOT exporter, one file per
application. The golden test asserts byte-equality.

Refresh:

    UPDATE_GOLDEN=1 python -m pytest tests/framework/export/dot/test_dot_golden.py
