# Build Guide: DoorbellProtector

Two-LM555 doorbell protector.

## Ingredients

| Refdes | Part | Value / Spec | Quantity | Notes |
|--------|------|--------------|----------|-------|
| C1 | Capacitor | 100 nF | 1 |  |
| C2 | Capacitor | 4.7 µF | 1 |  |
| C3 | Capacitor | 100 nF | 1 |  |
| C4 | Capacitor | 100 nF | 1 |  |
| C5 | Capacitor | 47 µF | 1 |  |
| D1 | D1N4007 | D1N4007 | 1 |  |
| D2 | LED | red, 5 mm | 1 | Longer lead is the anode (+) |
| K1 | Relay_SPDT | Relay_SPDT | 1 |  |
| Q1 | BC548 | BC548 | 1 |  |
| Q2 | Q2N3904 | Q2N3904 | 1 |  |
| R1 | Resistor | 1000 Ω | 1 | ¼ W carbon film is fine |
| R2 | Resistor | 1000000 Ω | 1 | ¼ W carbon film is fine |
| R3 | Resistor | 1000000 Ω | 1 | ¼ W carbon film is fine |
| R4 | Resistor | 1000 Ω | 1 | ¼ W carbon film is fine |
| R5 | Resistor | 10000 Ω | 1 | ¼ W carbon film is fine |
| R6 | Resistor | 1000000 Ω | 1 | ¼ W carbon film is fine |
| R7 | Resistor | 4700 Ω | 1 | ¼ W carbon film is fine |
| R8 | Resistor | 47000 Ω | 1 | ¼ W carbon film is fine |
| U1 | NE555_Monostable | NE555_Monostable | 1 |  |
| U2 | NE555_Monostable | NE555_Monostable | 1 |  |

Also: a standard 830-pin solderless breadboard, an assortment of jumper wires (red for the positive rail, black for ground rail, any colour for signals), and a 5 V supply.

## Method

1. Orient the breadboard with its long axis horizontal and the trough running
   left-to-right through the middle. Connect your 5 V supply: the positive
   lead to the top `+` rail (positive rail), the negative lead to the top `-`
   rail (ground rail).
2. Plug U1 (NE555_Monostable, DIP-8) straddling the trough: pin 1 at 10E, pin
   8 at 10F. The chip's notch / dot marks pin 1 — make sure it lines up.
3. Plug U2 (NE555_Monostable, DIP-8) straddling the trough: pin 1 at 16E, pin
   8 at 16F. The chip's notch / dot marks pin 1 — make sure it lines up.
4. Plug Q1 (BC548): one lead at position 24 (any of 24A–24E), the other at
   position 25 (any of 25A–25E).
5. Plug Q2 (Q2N3904): one lead at position 27 (any of 27A–27E), the other at
   position 28 (any of 28A–28E).
6. Plug D1 (D1N4007): one lead at position 30 (any of 30A–30E), the other at
   position 31 (any of 31A–31E).
7. Plug D2 (LED): one lead at position 33 (any of 33A–33E), the other at
   position 34 (any of 34A–34E).
8. Plug R1 (Resistor): one lead at position 36 (any of 36A–36E), the other at
   position 39 (any of 39A–39E).
9. Plug R2 (Resistor): one lead at position 41 (any of 41A–41E), the other at
   position 44 (any of 44A–44E).
10. Plug R3 (Resistor): one lead at position 46 (any of 46A–46E), the other at
   position 49 (any of 49A–49E).
11. Plug R4 (Resistor): one lead at position 51 (any of 51A–51E), the other at
   position 54 (any of 54A–54E).
12. Plug R5 (Resistor): one lead at position 56 (any of 56A–56E), the other at
   position 59 (any of 59A–59E).
13. Plug R6 (Resistor): one lead at position 61 (any of 61A–61E), the other at
   position 64 (any of 64A–64E).
14. Plug R7 (Resistor): one lead at position 66 (any of 66A–66E), the other at
   position 69 (any of 69A–69E).
15. Plug R8 (Resistor): one lead at position 71 (any of 71A–71E), the other at
   position 74 (any of 74A–74E).
16. Plug C1 (Capacitor): one lead at position 76 (any of 76A–76E), the other
   at position 77 (any of 77A–77E).
17. Plug C2 (Capacitor): one lead at position 79 (any of 79A–79E), the other
   at position 80 (any of 80A–80E).
18. Plug C3 (Capacitor): one lead at position 82 (any of 82A–82E), the other
   at position 83 (any of 83A–83E).
19. Plug C4 (Capacitor): one lead at position 85 (any of 85A–85E), the other
   at position 86 (any of 86A–86E).
20. Plug C5 (Capacitor): one lead at position 88 (any of 88A–88E), the other
   at position 89 (any of 89A–89E).
21. Plug K1 (Relay_SPDT): one lead at position 91 (any of 91A–91E), the other
   at position 92 (any of 92A–92E).
22. Run a jumper from position 12 (any of 12A–12E) to position 17 (any of
   17A–17E).
23. Run a jumper from position 17 (any of 17A–17E) to position 25 (any of
   25A–25E).
24. Run a jumper from position 25 (any of 25A–25E) to position 33 (any of
   33A–33E).
25. Run a jumper from position 33 (any of 33A–33E) to position 36 (any of
   36A–36E).
26. Run a jumper from position 36 (any of 36A–36E) to position 39 (any of
   39A–39E).
27. Run a jumper from position 39 (any of 39A–39E) to position 85 (any of
   85A–85E).
28. Run a jumper from position 85 (any of 85A–85E) to position 86 (any of
   86A–86E).
29. Run a jumper from position 86 (any of 86A–86E) to position 91 (any of
   91A–91E).
30. Run a jumper from position 19 (any of 19A–19E) to the top `+` rail.
31. Run a jumper from position 31 (any of 31A–31E) to the top `+` rail.
32. Run a jumper from position 34 (any of 34A–34E) to the top `-` rail.
33. Run a jumper from position 18 (any of 18A–18E) to position 28 (any of
   28A–28E).
34. Run a jumper from position 28 (any of 28A–28E) to position 51 (any of
   51A–51E).
35. Run a jumper from position 51 (any of 51A–51E) to position 54 (any of
   54A–54E).
36. Run a jumper from position 13 (any of 13A–13E) to position 27 (any of
   27A–27E).
37. Run a jumper from position 27 (any of 27A–27E) to position 56 (any of
   56A–56E).
38. Run a jumper from position 56 (any of 56A–56E) to position 59 (any of
   59A–59E).
39. Verify nothing is shorted by inspecting the rails with a multimeter
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
