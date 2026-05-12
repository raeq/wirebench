# Build Guide: Dice

Push-button electronic dice on a single board.

## Ingredients

| Refdes | Part | Value / Spec | Quantity | Notes |
|--------|------|--------------|----------|-------|
| C1 | Capacitor | 10 nF | 1 |  |
| C2 | Capacitor | 100 nF | 1 |  |
| D1 | D1N4148 | D1N4148 | 1 |  |
| D2 | D1N4148 | D1N4148 | 1 |  |
| D3 | D1N4148 | D1N4148 | 1 |  |
| D4 | D1N4148 | D1N4148 | 1 |  |
| D5 | D1N4148 | D1N4148 | 1 |  |
| D6 | D1N4148 | D1N4148 | 1 |  |
| D7 | LED | red, 5 mm | 1 | Longer lead is the anode (+) |
| D8 | LED | red, 5 mm | 1 | Longer lead is the anode (+) |
| D9 | LED | red, 5 mm | 1 | Longer lead is the anode (+) |
| D10 | LED | red, 5 mm | 1 | Longer lead is the anode (+) |
| D11 | LED | red, 5 mm | 1 | Longer lead is the anode (+) |
| D12 | LED | red, 5 mm | 1 | Longer lead is the anode (+) |
| D13 | LED | red, 5 mm | 1 | Longer lead is the anode (+) |
| R1 | Resistor | 470 Ω | 1 | ¼ W carbon film is fine |
| R2 | Resistor | 330 Ω | 1 | ¼ W carbon film is fine |
| R3 | Resistor | 330 Ω | 1 | ¼ W carbon film is fine |
| R4 | Resistor | 330 Ω | 1 | ¼ W carbon film is fine |
| R5 | Resistor | 10000 Ω | 1 | ¼ W carbon film is fine |
| R6 | Resistor | 10000 Ω | 1 | ¼ W carbon film is fine |
| R7 | Resistor | 10000 Ω | 1 | ¼ W carbon film is fine |
| U1 | NE555 | NE555 | 1 |  |
| U2 | CD4017 | CD4017 | 1 |  |

Also: a standard 830-pin solderless breadboard, an assortment of jumper wires (red for the positive rail, black for ground rail, any colour for signals), and a 5 V supply.

## Method

1. Orient the breadboard with its long axis horizontal and the trough running
   left-to-right through the middle. Connect your 5 V supply: the positive
   lead to the top `+` rail (positive rail), the negative lead to the top `-`
   rail (ground rail).
2. Plug U2 (CD4017, DIP-16) straddling the trough: pin 1 at 10E, pin 16 at
   10F. The chip's notch / dot marks pin 1 — make sure it lines up.
3. Plug U1 (NE555, DIP-8) straddling the trough: pin 1 at 20E, pin 8 at 20F.
   The chip's notch / dot marks pin 1 — make sure it lines up.
4. Plug D1 (D1N4148): one lead at position 28 (any of 28A–28E), the other at
   position 29 (any of 29A–29E).
5. Plug D2 (D1N4148): one lead at position 31 (any of 31A–31E), the other at
   position 32 (any of 32A–32E).
6. Plug D3 (D1N4148): one lead at position 34 (any of 34A–34E), the other at
   position 35 (any of 35A–35E).
7. Plug D4 (D1N4148): one lead at position 37 (any of 37A–37E), the other at
   position 38 (any of 38A–38E).
8. Plug D5 (D1N4148): one lead at position 40 (any of 40A–40E), the other at
   position 41 (any of 41A–41E).
9. Plug D6 (D1N4148): one lead at position 43 (any of 43A–43E), the other at
   position 44 (any of 44A–44E).
10. Plug R1 (Resistor): one lead at position 46 (any of 46A–46E), the other at
   position 49 (any of 49A–49E).
11. Plug R2 (Resistor): one lead at position 51 (any of 51A–51E), the other at
   position 54 (any of 54A–54E).
12. Plug R3 (Resistor): one lead at position 56 (any of 56A–56E), the other at
   position 59 (any of 59A–59E).
13. Plug R4 (Resistor): one lead at position 61 (any of 61A–61E), the other at
   position 64 (any of 64A–64E).
14. Plug R5 (Resistor): one lead at position 66 (any of 66A–66E), the other at
   position 69 (any of 69A–69E).
15. Plug R6 (Resistor): one lead at position 71 (any of 71A–71E), the other at
   position 74 (any of 74A–74E).
16. Plug R7 (Resistor): one lead at position 76 (any of 76A–76E), the other at
   position 79 (any of 79A–79E).
17. Plug C1 (Capacitor): one lead at position 81 (any of 81A–81E), the other
   at position 82 (any of 82A–82E).
18. Plug C2 (Capacitor): one lead at position 84 (any of 84A–84E), the other
   at position 85 (any of 85A–85E).
19. Plug D7 (LED): one lead at position 87 (any of 87A–87E), the other at
   position 88 (any of 88A–88E).
20. Plug D8 (LED): one lead at position 90 (any of 90A–90E), the other at
   position 91 (any of 91A–91E).
21. Plug D9 (LED): one lead at position 93 (any of 93A–93E), the other at
   position 94 (any of 94A–94E).
22. Plug D10 (LED): one lead at position 96 (any of 96A–96E), the other at
   position 97 (any of 97A–97E).
23. Plug D11 (LED): one lead at position 99 (any of 99A–99E), the other at
   position 100 (any of 100A–100E).
24. Plug D12 (LED): one lead at position 102 (any of 102A–102E), the other at
   position 103 (any of 103A–103E).
25. Plug D13 (LED): one lead at position 105 (any of 105A–105E), the other at
   position 106 (any of 106A–106E).
26. Run a jumper from position 11 (any of 11A–11E) to position 28 (any of
   28A–28E).
27. Run a jumper from position 29 (any of 29A–29E) to position 32 (any of
   32A–32E).
28. Run a jumper from position 32 (any of 32A–32E) to position 35 (any of
   35A–35E).
29. Run a jumper from position 35 (any of 35A–35E) to position 46 (any of
   46A–46E).
30. Run a jumper from position 46 (any of 46A–46E) to position 49 (any of
   49A–49E).
31. Run a jumper from position 49 (any of 49A–49E) to position 87 (any of
   87A–87E).
32. Run a jumper from position 38 (any of 38A–38E) to position 41 (any of
   41A–41E).
33. Run a jumper from position 41 (any of 41A–41E) to position 44 (any of
   44A–44E).
34. Run a jumper from position 44 (any of 44A–44E) to position 56 (any of
   56A–56E).
35. Run a jumper from position 56 (any of 56A–56E) to position 59 (any of
   59A–59E).
36. Run a jumper from position 59 (any of 59A–59E) to position 96 (any of
   96A–96E).
37. Run a jumper from position 96 (any of 96A–96E) to position 99 (any of
   99A–99E).
38. Run a jumper from position 100 (any of 100A–100E) to the top `-` rail.
39. Run a jumper from position 103 (any of 103A–103E) to the top `-` rail.
40. Run a jumper from position 106 (any of 106A–106E) to the top `-` rail.
41. Run a jumper from position 88 (any of 88A–88E) to the top `-` rail.
42. Run a jumper from position 91 (any of 91A–91E) to the top `-` rail.
43. Run a jumper from position 94 (any of 94A–94E) to the top `-` rail.
44. Run a jumper from position 97 (any of 97A–97E) to the top `-` rail.
45. Run a jumper from position 102 (any of 102A–102E) to position 105 (any of
   105A–105E).
46. Run a jumper from position 105 (any of 105A–105E) to position 16 (any of
   16F–16J).
47. Run a jumper from position 16 (any of 16F–16J) to position 43 (any of
   43A–43E).
48. Run a jumper from position 43 (any of 43A–43E) to position 61 (any of
   61A–61E).
49. Run a jumper from position 61 (any of 61A–61E) to position 64 (any of
   64A–64E).
50. Run a jumper from position 16 (any of 16A–16E) to position 31 (any of
   31A–31E).
51. Run a jumper from position 31 (any of 31A–31E) to position 40 (any of
   40A–40E).
52. Run a jumper from position 10 (any of 10A–10E) to position 34 (any of
   34A–34E).
53. Run a jumper from position 13 (any of 13A–13E) to position 37 (any of
   37A–37E).
54. Run a jumper from position 14 (any of 14F–14J) to position 51 (any of
   51A–51E).
55. Run a jumper from position 51 (any of 51A–51E) to position 54 (any of
   54A–54E).
56. Run a jumper from position 54 (any of 54A–54E) to position 90 (any of
   90A–90E).
57. Run a jumper from position 90 (any of 90A–90E) to position 93 (any of
   93A–93E).
58. Run a jumper from position 23 (any of 23A–23E) to the top `+` rail.
59. Run a jumper from position 11 (any of 11F–11J) to position 14 (any of
   14A–14E).
60. Verify nothing is shorted by inspecting the rails with a multimeter
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
