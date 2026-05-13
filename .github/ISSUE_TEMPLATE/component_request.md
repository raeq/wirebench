---
name: Component request
about: Request a new chip, connector, or passive part class
title: 'Add: <PART_NUMBER>'
labels: component
---

## Part number

Manufacturer + part number (e.g. Texas Instruments `LM7805`,
NXP `BC547`, JST `XH-2.54-4P-male`).

## Datasheet

Link to the canonical datasheet PDF.

## Pin table

```
Pin | Name    | Direction | Notes
----|---------|-----------|------
1   | VIN     | IN        |
2   | GND     | BIDIR     |
3   | VOUT    | OUT       |
```

## What designs would use it

Name a design or two that would use this part. If it's already in
the demos folder, link the demo file. If not, sketch the application
(e.g. "5V regulator for ATmega328P + sensors").

## Behavioural requirements

Does the part need a behavioural cell (e.g. a comparator with
threshold logic, a regulator with current-limit), or is it a passive
that the framework can model directly? See
`.plans/behavioural-cell-audit-spec.md` for the cell pattern.
