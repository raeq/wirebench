# Golden SPICE decks

Reference output for the SPICE exporter, one file per application.
The golden test asserts byte-equality against these files so any
change in the exporter's output surfaces as a deliberate diff in the
PR that introduced it.

When a change is legitimately expected to alter the SPICE output
(new chip pin, renamed net, reformatted line), refresh the goldens:

    UPDATE_GOLDEN=1 python -m pytest tests/framework/export/test_spice_golden.py

Review the resulting diff in the PR — that diff *is* the record of
what changed in the exporter's behaviour.
