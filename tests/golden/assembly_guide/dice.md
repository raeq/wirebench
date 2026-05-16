# Build Guide: Dice

Push-button electronic dice on a single board.

## Safety first

- **Put on safety glasses before powering anything up.** Electrolytic capacitors can vent boiling electrolyte if reverse-installed or over-volted; battery cells can flash violently on a short; small parts under tension (springs in switches, leads under a soldering iron) launch in unexpected directions. The glasses are cheap insurance against an afternoon you'd otherwise regret.
- **Discharge static before touching chips.** Touch a grounded metal surface (the bench frame, a radiator, the case of a mains-powered tool that's plugged in but switched off) before picking up MOSFETs or CMOS logic. A static spark you can't feel — under 100 V from walking across a carpet — punches through a gate oxide silently. The part still looks fine; it just doesn't work, and you spend two hours blaming your wiring. An ESD wrist strap clipped to a grounded surface is the permanent fix.
- **Wear insulating gloves when working above ~30 V or near mains.** Standard hobby breadboard work (3.3–24 V) doesn't need them; anything reaching into a wall-wart's primary side, a charged high-voltage capacitor, or a tube-amp B+ rail does. If the design includes a transformer, a switching supply's input stage, or a Cell pack above a few volts, treat it as hot until you've personally verified it's discharged.

## Parts

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

## Layout

Each part below is drawn the way it sits on the breadboard, with every pin labelled. Chips run left-to-right with the notch at the left; pin 1 is the top-left pin (closest to the notch). Sensors and modules are shown as a single horizontal row of pins. 2-lead passives are drawn axially with the value in line.

### C1 — Capacitor

```
t1 ─┤├─ t2   [10 nF]
```

### C2 — Capacitor

```
t1 ─┤├─ t2   [100 nF]
```

### D1 — D1N4148

```
anode ─▶├─ cathode   [D1N4148]
```

### D2 — D1N4148

```
anode ─▶├─ cathode   [D1N4148]
```

### D3 — D1N4148

```
anode ─▶├─ cathode   [D1N4148]
```

### D4 — D1N4148

```
anode ─▶├─ cathode   [D1N4148]
```

### D5 — D1N4148

```
anode ─▶├─ cathode   [D1N4148]
```

### D6 — D1N4148

```
anode ─▶├─ cathode   [D1N4148]
```

### D7 — LED

```
anode (+, long lead) ─▶├─ cathode (−, short lead)   [red, 5 mm]
```

### D8 — LED

```
anode (+, long lead) ─▶├─ cathode (−, short lead)   [red, 5 mm]
```

### D9 — LED

```
anode (+, long lead) ─▶├─ cathode (−, short lead)   [red, 5 mm]
```

### D10 — LED

```
anode (+, long lead) ─▶├─ cathode (−, short lead)   [red, 5 mm]
```

### D11 — LED

```
anode (+, long lead) ─▶├─ cathode (−, short lead)   [red, 5 mm]
```

### D12 — LED

```
anode (+, long lead) ─▶├─ cathode (−, short lead)   [red, 5 mm]
```

### D13 — LED

```
anode (+, long lead) ─▶├─ cathode (−, short lead)   [red, 5 mm]
```

### R1 — Resistor

```
t1 ─┤▮ 470 Ω ▮├─ t2
```

### R2 — Resistor

```
t1 ─┤▮ 330 Ω ▮├─ t2
```

### R3 — Resistor

```
t1 ─┤▮ 330 Ω ▮├─ t2
```

### R4 — Resistor

```
t1 ─┤▮ 330 Ω ▮├─ t2
```

### R5 — Resistor

```
t1 ─┤▮ 10000 Ω ▮├─ t2
```

### R6 — Resistor

```
t1 ─┤▮ 10000 Ω ▮├─ t2
```

### R7 — Resistor

```
t1 ─┤▮ 10000 Ω ▮├─ t2
```

### U1 — NE555

```
        1      2      3      4   
       GND   TRIG    OUT   RESET 
    ┌────────────────────────────┐
  U │           NE555            │
    └────────────────────────────┘
       VCC   DISCH  THRES  CONT  
        8      7      6      5   
```

### U2 — CD4017

```
       1    2    3    4    5    6    7    8  
      Q5   Q1   Q0   Q2   Q6   Q7   Q3   VSS 
    ┌────────────────────────────────────────┐
  U │                 CD4017                 │
    └────────────────────────────────────────┘
      VDD  RST  CLK  CE   CO   Q9   Q4   Q8  
      16   15   14   13   12   11   10    9  
```


## How to verify

Before you start wiring, take five minutes to confirm each part actually works. A multimeter on the diode-test and resistance settings catches most pre-install failures: dead LEDs, mis-bagged parts, transistors damaged in shipping, batteries below their safe-discharge limit. The checks below cover what you can verify with a basic multimeter; chips and complex modules generally need a working test rig instead, so they're not listed here.

- **For an electrolytic capacitor, use your multimeter's diode-test or continuity mode to confirm it charges.** Put the red probe on the + lead (longer / unmarked side) and the black on the − lead (the side with the stripe). A healthy cap shows a voltage that climbs over a second or two and then settles to OL — the meter is charging the cap through its internal current source. Reverse the leads briefly to discharge and repeat. A cap that immediately reads zero (continuous beep) is shorted; one that reads OL from the first touch is open or has lost its capacitance.
- **Confirm the printed value matches what the design calls for** — capacitor markings are easy to misread. Big electrolytics print the value directly (e.g. '100 µF 25 V'); smaller ceramics use a three-digit code where the first two digits are the value in pF and the third is the number of trailing zeros ('104' means 100,000 pF = 100 nF = 0.1 µF). A capacitance meter (built into many DMMs) confirms the value within ±10%.
- **Use the multimeter's diode-test mode on a silicon diode like the 1N4148.** Red probe on the anode (unmarked end), black probe on the cathode (banded end): the meter reads about 0.6 V — the diode's forward voltage drop. Swap the probes around and the meter reads OL: the diode blocks reverse current. Both directions showing 0.6 V means the diode is shorted; both showing OL means it's open. The body of the part should also have '1N4148' printed on it — a look-alike diode with the wrong markings is a mis-bag.
- **Set your multimeter to diode-test mode and probe the LED's leads.** Put the red probe on the long lead (anode +) and the black probe on the short lead (cathode −). A healthy LED lights up dimly — the meter is forcing a tiny current through it — and the reading shows the forward voltage (around 1.8 V for red, 2 V for yellow, 3.2 V for blue/white). Reverse the probes and the LED should stay dark with the meter reading OL. If both directions show OL the LED is open / dead; if both directions light the LED it has failed as a short. This also tells you which lead is the anode, useful if the leads were trimmed.
- **Measure the resistance with your multimeter before installing.** Set the meter to the Ω (ohms) range, probe one lead, then the other; the reading should match the value printed on the part (or decoded from its colour bands) to within a few percent. A reading of OL (open / infinity) means the resistor is broken inside; a value wildly different from what's marked usually means someone has swapped parts in the bin and you've grabbed the wrong one.


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
26. Run a jumper from D1 anode to U2 pin 2 — position 28 (any of 28A–28E) to
   position 11 (any of 11A–11E).
27. Run a jumper from D1 cathode to D2 cathode — position 29 (any of 29A–29E)
   to position 32 (any of 32A–32E).
28. Run a jumper from D2 cathode to D3 cathode — position 32 (any of 32A–32E)
   to position 35 (any of 35A–35E).
29. Run a jumper from D3 cathode to D7 anode — position 35 (any of 35A–35E) to
   position 87 (any of 87A–87E).
30. Run a jumper from D7 anode to R1 t1 — position 87 (any of 87A–87E) to
   position 46 (any of 46A–46E).
31. Run a jumper from R1 t1 to R1 t2 — position 46 (any of 46A–46E) to
   position 49 (any of 49A–49E).
32. Run a jumper from D10 anode to D11 anode — position 96 (any of 96A–96E) to
   position 99 (any of 99A–99E).
33. Run a jumper from D11 anode to D4 cathode — position 99 (any of 99A–99E)
   to position 38 (any of 38A–38E).
34. Run a jumper from D4 cathode to D5 cathode — position 38 (any of 38A–38E)
   to position 41 (any of 41A–41E).
35. Run a jumper from D5 cathode to D6 cathode — position 41 (any of 41A–41E)
   to position 44 (any of 44A–44E).
36. Run a jumper from D6 cathode to R3 t1 — position 44 (any of 44A–44E) to
   position 56 (any of 56A–56E).
37. Run a jumper from R3 t1 to R3 t2 — position 56 (any of 56A–56E) to
   position 59 (any of 59A–59E).
38. Run a jumper from D10 cathode at position 97 (any of 97A–97E) to the top
   `-` rail.
39. Run a jumper from D11 cathode at position 100 (any of 100A–100E) to the
   top `-` rail.
40. Run a jumper from D12 cathode at position 103 (any of 103A–103E) to the
   top `-` rail.
41. Run a jumper from D13 cathode at position 106 (any of 106A–106E) to the
   top `-` rail.
42. Run a jumper from D7 cathode at position 88 (any of 88A–88E) to the top
   `-` rail.
43. Run a jumper from D8 cathode at position 91 (any of 91A–91E) to the top
   `-` rail.
44. Run a jumper from D9 cathode at position 94 (any of 94A–94E) to the top
   `-` rail.
45. Run a jumper from D12 anode to D13 anode — position 102 (any of 102A–102E)
   to position 105 (any of 105A–105E).
46. Run a jumper from D13 anode to D6 anode — position 105 (any of 105A–105E)
   to position 43 (any of 43A–43E).
47. Run a jumper from D6 anode to R4 t1 — position 43 (any of 43A–43E) to
   position 61 (any of 61A–61E).
48. Run a jumper from R4 t1 to R4 t2 — position 61 (any of 61A–61E) to
   position 64 (any of 64A–64E).
49. Run a jumper from R4 t2 to U2 pin 10 — position 64 (any of 64A–64E) to
   position 16 (any of 16F–16J).
50. Run a jumper from D2 anode to D5 anode — position 31 (any of 31A–31E) to
   position 40 (any of 40A–40E).
51. Run a jumper from D5 anode to U2 pin 7 — position 40 (any of 40A–40E) to
   position 16 (any of 16A–16E).
52. Run a jumper from D3 anode to U2 pin 1 — position 34 (any of 34A–34E) to
   position 10 (any of 10A–10E).
53. Run a jumper from D4 anode to U2 pin 4 — position 37 (any of 37A–37E) to
   position 13 (any of 13A–13E).
54. Run a jumper from D8 anode to D9 anode — position 90 (any of 90A–90E) to
   position 93 (any of 93A–93E).
55. Run a jumper from D9 anode to R2 t1 — position 93 (any of 93A–93E) to
   position 51 (any of 51A–51E).
56. Run a jumper from R2 t1 to R2 t2 — position 51 (any of 51A–51E) to
   position 54 (any of 54A–54E).
57. Run a jumper from R2 t2 to U2 pin 12 — position 54 (any of 54A–54E) to
   position 14 (any of 14F–14J).
58. Run a jumper from U1 pin 4 at position 23 (any of 23A–23E) to the top `+`
   rail.
59. Run a jumper from U2 pin 15 to U2 pin 5 — position 11 (any of 11F–11J) to
   position 14 (any of 14A–14E).
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

- **Every pin must connect to something — never leave one floating.** Tie CE (pin 13, clock-enable) to ground with a jumper for normal counting, and tie RST (pin 15, reset) to ground too unless you want a permanently-reset chip. A floating CMOS input drifts unpredictably; the symptom is a chip that behaves differently when you wave your hand near it. This is *the* most common 'why doesn't my CMOS work?' problem.
- **The Q-output pins are scrambled — not in physical order.** Wire 'pin 1 to LED 1, pin 2 to LED 2 …' and you get a confused dance pattern, not a counter sweep. The actual mapping is: Q0 → pin 3, Q1 → pin 2, Q2 → pin 4, Q3 → pin 7, Q4 → pin 10, Q5 → pin 1, Q6 → pin 5, Q7 → pin 6, Q8 → pin 9, Q9 → pin 11. Keep the datasheet pin table open while wiring; reading 'pin 1' off the chip and assuming it's Q0 is the classic 4017 trap.
- **Pull RST HIGH and the counter restarts from zero.** Useful at power-on, or any time you want to start counting from the top. The neat trick: wire an output back to RST to make a counter that automatically restarts at a chosen number — wire Q3 → RST and the counter cycles 0, 1, 2, then snaps back to 0 the moment Q3 goes HIGH. One jumper turns the 4017 into any modulus you want (a 'mod-3 counter' here). (Advanced: the RST pulse must outlast the chip's ~150 ns response time at 5 V. Typical breadboard clock rates are slow enough that this is automatic; only matters if you're running the chip near its maximum clock rate.)
- **Electrolytic capacitors have a + and − end — always check which is which.** The longer lead is + (positive); the can has a stripe along the side near the − (negative) lead. Install one backwards and it heats up, vents boiling electrolyte, and sometimes pops loudly — this is the main reason 'always wear safety glasses' is a bench rule. Ceramic and film capacitors are not polarised and go in either way.
- **Always use a capacitor rated well above the voltage it will actually see.** Rule of thumb: pick a part rated for at least 1.5 times the highest steady-state voltage in your circuit. A 16 V cap on a 12 V rail will die early as the supply rings or sags; a 25 V cap shrugs the same conditions off. (The rated voltage is the *working* maximum, not a nominal indicator.)
- **Different capacitor types do different jobs — match the type to the role.** Big electrolytics (microfarads) sit on supply rails as bulk reservoirs; small ceramics (10–100 nF) go right next to chip supply pins as local decouplers; film and polypropylene caps handle precision timing where drift matters. Putting an electrolytic where a ceramic belongs (and vice versa) is the single most common 'why does this circuit oscillate?' bench mistake.
- **The black band marks the cathode (the − end).** Match the band to the bar in the schematic symbol — they're the same thing. Install it backwards and under normal bias the diode blocks current the wrong way (your circuit silently does nothing); under reverse bias it conducts and shorts whatever the diode was meant to protect.
- **Use the 1N4148 for small signal jobs — not for power.** It's rated for 200 mA average and 1 A peak, which suits logic-level steering, voltage clamping, level-shifting, and high-speed switching. It's the wrong choice for rectifying mains-derived AC or absorbing motor flyback current; reach for a 1N4001 or 1N4007 there.
- **LEDs have a + and − end — the long lead is +.** Get them the wrong way around and the LED simply doesn't light up; there's no spark or smoke, just a dark LED. If someone has already trimmed the leads, look at the rim of the plastic body: the flat spot marks the − (cathode) side. Both leads are valid wires as far as the framework is concerned, so it can't catch this mistake for you.
- **Always put a resistor in series with an LED — never connect an LED directly across a supply.** Without a resistor the LED draws too much current and burns out in a literal flash. 330 Ω works fine for most LEDs on a 5 V supply. (The formula, if you care: R = (V_supply − V_F) / I_target; 330 Ω drives about 10 mA through a typical red LED at 5 V, which is bright but not stressed.)
- **Put a capacitor across the supply pins, right at the chip.** A 100 nF ceramic from pin 8 (Vcc) to pin 1 (GND), leads under 5 mm long. The 555 draws a sharp current spike every time its output switches, and without a local cap the supply rail rings — making the oscillator's timing drift and coupling noise into anything else sharing the supply. If your 555 oscillator runs at the wrong frequency or jitters, this is the first thing to check.
- **Add a 10 nF cap from pin 5 to ground**, even if you're not using pin 5 for anything. Pin 5 (Control Voltage) is internally connected to the chip's reference divider, and without that little cap the pin acts as an antenna for nearby noise — your steady oscillator turns into a jittery one for no obvious reason. (The pin's high-impedance node picks up stray fields and modulates the comparator thresholds; the cap shorts that noise to ground.)
- **For battery-powered work, use a CMOS 555 instead** — the TLC555 or ICM7555 are drop-in replacements that draw ~100 µA versus the original NE555's 3–10 mA. Same pinout, same external circuit, ten to a hundred times the battery life. The classic bipolar NE555 has one advantage: its output can drive ~200 mA directly into a load — useful for small lamps or relays at the cost of rougher supply behaviour.
