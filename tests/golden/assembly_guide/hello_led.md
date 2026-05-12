# Build Guide: HelloLED

A single LED with a current-limit resistor across the supply rails.

## Ingredients

| Refdes | Part | Value / Spec | Quantity | Notes |
|--------|------|--------------|----------|-------|
| D1 | LED | red, 5 mm | 1 | Longer lead is the anode (+) |
| R1 | Resistor | 330 Ω | 1 | ¼ W carbon film is fine |

Also: a standard 830-pin solderless breadboard, an assortment of jumper wires (red for the positive rail, black for ground rail, any colour for signals), and a 5 V supply.

## Method

1. Orient the breadboard with its long axis horizontal and the trough running
   left-to-right through the middle. Connect your 5 V supply: the positive
   lead to the top `+` rail (positive rail), the negative lead to the top `-`
   rail (ground rail).
2. Plug R1 (Resistor): one lead at position 12 (any of 12A–12E), the other at
   position 15 (any of 15A–15E).
3. Plug D1 (LED): one lead at position 17 (any of 17A–17E), the other at
   position 18 (any of 18A–18E).
4. Run a jumper from position 15 (any of 15A–15E) to position 17 (any of
   17A–17E).
5. Run a jumper from position 18 (any of 18A–18E) to the top `-` rail.
6. Run a jumper from position 12 (any of 12A–12E) to the top `+` rail.
7. Verify nothing is shorted by inspecting the rails with a multimeter
   (continuity beep between `+` and `-` means trouble). Then connect the
   supply and observe.

## Notes & Gotchas

### General

- **Double-check the supply voltage before powering up.** Most TTL / CMOS logic survives 3.3 V – 5.5 V; an accidental 12 V from a bench supply destroys every chip on the board in microseconds. Set the supply, measure it with a multimeter, and only then connect.
- **Resistor wattage matters.** Standard ¼-W carbon-film resistors are fine below ~60 V across the part. Power resistors (½ W, 1 W) are needed for current-sense or load-dump positions; the BOM lists value only, not wattage — confirm against the schematic's expected current.
- **Tie unused CMOS inputs.** Any input pin not driven by the circuit must be wired to VCC or GND. Floating CMOS inputs drift unpredictably and can cause oscillation, excess supply current, or random behaviour. If your design has unused gates on a multi-gate chip, ground their inputs explicitly with a jumper.
- **Power-rail continuity.** Some 830-pin breadboards split each power rail into two segments at the middle of the board, with a visible break in the colored stripe. If your circuit uses the full rail length, bridge the gap with a jumper before powering on.

### Per-component

- **LED polarity matters.** The longer lead of a fresh LED is the anode (+); the shorter lead is the cathode (−). If the leads have been trimmed, look for the flat side of the body — that's the cathode side. Reversing the LED is silent: nothing lights up and the framework's topology check can't catch it.
- **Always use a current-limit resistor** in series with an LED. Without it, the LED draws too much current at any sensible supply voltage and dies in a flash. R = (V_supply − V_F) / I_target; 330 Ω at 5 V drives ~10 mA through a 2 V red LED.
