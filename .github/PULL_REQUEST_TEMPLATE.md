## What changed

One or two sentences. What problem this solves or what behaviour it
adds — not a re-statement of the diff.

## Test plan

- [ ] `uv run pytest` is green
- [ ] `uv run mypy src/ demos/` is clean
- [ ] Golden files regenerated (if a renderer or demo changed):
      `uv run python scripts/render_demo_docs.py` ran with reviewed diff
- [ ] New parts: pin-number test added in
      `tests/components/test_chip_pin_numbers.py`
- [ ] New chip subclasses: a behavioural cell drives every OUT pin, or
      `BARE_FIRMWARE_DRIVEN = True` is set with rationale

## Notes for reviewer

Anything non-obvious about the approach, or trade-offs you considered
and rejected.
