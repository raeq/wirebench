# `backup_power` demo audit

## Question

Per `docs/behavioural-cell-audit-spec.md` §8, the user asked: why doesn't
`demos/backup_power/` raise `FloatingNetError` at construction, given that
its three top-level chips — TPS2660 (eFuse), LM5002 (boost controller),
LM5160 (buck converter) — all ship with `cells=[]` and declare OUT pins?
By §3 of the spec, any design that *places one of these chips in the
middle of a drive path* should raise `FloatingNetError`.

## Finding: possibility (2) — confirmed, with a twist

Of the three possibilities the spec enumerated, the answer is (2): the
demo's topology happens to keep the ERC walker away from the suspect
chips. The twist is that it doesn't do this via "Rails at every
intermediate net" but via something stronger:

**The three suspect chips are never wired to anything.**

`demos/backup_power/backup_power.py` instantiates `TPS2660`, `LM5002`,
and `LM5160` (and the supporting passives — `L1`, `D1`, `C10`, etc.) so
they appear on the BOM, the netlist, and the assembly guide via the
framework's auto-collect machinery. But the demo body contains **zero
`wire()` calls** that touch any of those chips' ports. Confirmed
by inspection:

```text
tps2660: 0 pins on a node, 10 floating
lm5002:  0 pins on a node,  8 floating
lm5160:  0 pins on a node, 16 floating
```

The framework's logical-net walker (`compute_logical_nets`) starts from
ports that are on a `Node` and walks the graph. Ports that aren't on any
node are simply absent from the walk — they can't be "floating" because
they're not even on a net. The ERC check for `FloatingNetError` finds
nothing to complain about.

## Why the demo does this deliberately

A comment at `demos/backup_power/backup_power.py:155-162` documents the
choice:

> No top-level signal wires. The three TI ICs are opaque in the
> voltage-only graph, the L-C boost network is opaque too (Capacitor /
> Inductor `.evaluate()` are no-ops), and any wire between them and the
> supervisor's rails would either short the rail or be flagged as a
> floating multi-BIDIR net. The supervisor's outputs drive the
> composite's external ports directly; the chips and passives ride on
> the BOM via auto-collect for documentation and downstream export.

In other words, the demo author knew the chips were unmodelled, knew
wiring them up would either short or float, and chose to leave them
unwired. The actual *behaviour* of the design — `vout_v`, `bulk_v`,
`flt_b`, `backup_active` — is computed by the `BackupSupervisor`
concept cell whose ports become the composite's external surface. The
chips are decorative parts on the BOM; the supervisor is the model.

## Verdict

**Not a defect.** The demo constructs cleanly because the framework's
ERC correctly *cannot find anything wrong* with chips that aren't
wired up. Auto-collect captures the chips for procurement purposes;
the `BackupSupervisor` cell carries the design's actual electrical
behaviour at a level the framework can validate.

The audit's standard for "this demo is correct" is satisfied — the
demo is *correct by design*, not *passing by accident*. The author
made a deliberate choice to model the design at the level of the
supervisor cell rather than at the chip-pin wiring level. The
framework's tools confirm the choice's consequences:

- ERC accepts the supervisor's port surface (it has a real driver and
  consistent directions);
- the BOM lists every chip and passive for procurement;
- the SPICE / KiCad / DOT / Mermaid / Yosys / assembly-guide exports
  all emit something sensible (chips appear as nodes with no edges,
  capacitors and inductors as 2-terminal parts on the BOM);
- the simulation traces the supervisor's output across the scenario
  sweep without referencing the chips at all.

## What would change this verdict?

If the demo were rewritten to wire TPS2660 / LM5002 / LM5160 to the
rails and to the passive network around them, the framework's ERC
would immediately raise `FloatingNetError` (or `ShortCircuitError`,
depending on which net the writer reached first). That outcome would
mean either:

- the chips would need behavioural cells (per the same pattern as
  `LinearRegulator` for the linear-regulator parts the audit spec
  covers — this would be phase 7 of the implementation, "specialty
  ICs as placeholder cells"); or
- the demo's high-level architecture would have to change.

Neither is on the work-package's critical path for phase 1. The
chips remain `cells=[]` until the audit reaches phase 7; the demo
remains correct in its current shape.

## Cross-reference

- `docs/behavioural-cell-audit-spec.md` §8 (audit prompt)
- `docs/behavioural-cell-audit-spec.md` §7.2.8 (specialty IC plan)
- `demos/backup_power/backup_power.py:104-153` (demo construction)
- `src/components/chips/concepts/backup_supervisor.py` (the cell that
  carries the demo's behaviour)
