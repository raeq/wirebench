# Build Guide: WaterAlarm

Water level alarm.

## Ingredients

| Refdes | Part | Value / Spec | Quantity | Notes |
|--------|------|--------------|----------|-------|
| D1 | LED | red, 5 mm | 1 | Longer lead is the anode (+) |
| D2 | LED | green, 5 mm | 1 | Longer lead is the anode (+) |
| U1 | ULN2003A | ULN2003A | 1 |  |
| U2 | SN74HC04 | SN74HC04 | 1 |  |
| U3 | CD4069 | CD4069 | 1 |  |
| U4 | CD4043 | CD4043 | 1 |  |

Also: a standard 830-pin solderless breadboard, an assortment of jumper wires (red for the positive rail, black for ground rail, any colour for signals), and a 5 V supply.

## Method

1. Orient the breadboard with its long axis horizontal and the trough running
   left-to-right through the middle. Connect your 5 V supply: the positive
   lead to the top `+` rail (positive rail), the negative lead to the top `-`
   rail (ground rail).
2. Plug U1 (ULN2003A, DIP-16) straddling the trough: pin 1 at 10E, pin 16 at
   10F. The chip's notch / dot marks pin 1 — make sure it lines up.
3. Plug U4 (CD4043, DIP-16) straddling the trough: pin 1 at 20E, pin 14 at
   22F. The chip's notch / dot marks pin 1 — make sure it lines up.
4. Plug U2 (SN74HC04, DIP-14) straddling the trough: pin 1 at 30E, pin 13 at
   31F. The chip's notch / dot marks pin 1 — make sure it lines up.
5. Plug U3 (CD4069, DIP-14) straddling the trough: pin 1 at 39E, pin 13 at
   40F. The chip's notch / dot marks pin 1 — make sure it lines up.
6. Plug D1 (LED): one lead at position 50 (any of 50A–50E), the other at
   position 51 (any of 51A–51E).
7. Plug D2 (LED): one lead at position 53 (any of 53A–53E), the other at
   position 54 (any of 54A–54E).
8. Run a jumper from position 20 (any of 20A–20E) to position 39 (any of
   39A–39E).
9. Run a jumper from position 39 (any of 39A–39E) to position 50 (any of
   50A–50E).
10. Run a jumper from position 40 (any of 40A–40E) to position 53 (any of
   53A–53E).
11. Run a jumper from position 23 (any of 23F–23J) to the top `-` rail.
12. Run a jumper from position 24 (any of 24A–24E) to the top `-` rail.
13. Run a jumper from position 24 (any of 24F–24J) to the top `-` rail.
14. Run a jumper from position 25 (any of 25A–25E) to the top `-` rail.
15. Run a jumper from position 26 (any of 26F–26J) to the top `-` rail.
16. Run a jumper from position 27 (any of 27F–27J) to the top `-` rail.
17. Run a jumper from position 31 (any of 31F–31J) to the top `-` rail.
18. Run a jumper from position 32 (any of 32A–32E) to the top `-` rail.
19. Run a jumper from position 33 (any of 33F–33J) to the top `-` rail.
20. Run a jumper from position 34 (any of 34A–34E) to the top `-` rail.
21. Run a jumper from position 35 (any of 35F–35J) to the top `-` rail.
22. Run a jumper from position 40 (any of 40F–40J) to the top `-` rail.
23. Run a jumper from position 41 (any of 41A–41E) to the top `-` rail.
24. Run a jumper from position 42 (any of 42F–42J) to the top `-` rail.
25. Run a jumper from position 43 (any of 43A–43E) to the top `-` rail.
26. Run a jumper from position 44 (any of 44F–44J) to the top `-` rail.
27. Run a jumper from position 26 (any of 26A–26E) to the top `+` rail.
28. Run a jumper from position 10 (any of 10F–10J) to position 22 (any of
   22A–22E).
29. Run a jumper from position 11 (any of 11F–11J) to position 30 (any of
   30A–30E).
30. Run a jumper from position 21 (any of 21A–21E) to position 31 (any of
   31A–31E).
31. Verify nothing is shorted by inspecting the rails with a multimeter
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
