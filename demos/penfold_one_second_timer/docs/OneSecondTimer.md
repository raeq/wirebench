# Build Guide: OneSecondTimer

Op-amp relaxation oscillator, ~1 Hz, brief LED flash per cycle.

## Safety first

- **Put on safety glasses before powering anything up.** Electrolytic capacitors can vent boiling electrolyte if reverse-installed or over-volted; battery cells can flash violently on a short; small parts under tension (springs in switches, leads under a soldering iron) launch in unexpected directions. The glasses are cheap insurance against an afternoon you'd otherwise regret.
- **Discharge static before touching chips.** Touch a grounded metal surface (the bench frame, a radiator, the case of a mains-powered tool that's plugged in but switched off) before picking up MOSFETs or CMOS logic. A static spark you can't feel — under 100 V from walking across a carpet — punches through a gate oxide silently. The part still looks fine; it just doesn't work, and you spend two hours blaming your wiring. An ESD wrist strap clipped to a grounded surface is the permanent fix.
- **Wear insulating gloves when working above ~30 V or near mains.** Standard hobby breadboard work (3.3–24 V) doesn't need them; anything reaching into a wall-wart's primary side, a charged high-voltage capacitor, or a tube-amp B+ rail does. If the design includes a transformer, a switching supply's input stage, or a Cell pack above a few volts, treat it as hot until you've personally verified it's discharged.

## Parts

| Refdes | Part | Value / Spec | Quantity | Notes |
|--------|------|--------------|----------|-------|
| C1 | Capacitor | 100 µF | 1 |  |
| C2 | Capacitor | 100 nF | 1 |  |
| D1 | D1N4148 | D1N4148 | 1 |  |
| D2 | LED | red, 5 mm | 1 | Longer lead is the anode (+) |
| R1 | Resistor | 100000 Ω | 1 | ¼ W carbon film is fine |
| R2 | Resistor | 100000 Ω | 1 | ¼ W carbon film is fine |
| R3 | Resistor | 4700 Ω | 1 | ¼ W carbon film is fine |
| R4 | Resistor | 50000 Ω | 1 | ¼ W carbon film is fine |
| R5 | Resistor | 10000000 Ω | 1 | ¼ W carbon film is fine |
| R6 | Resistor | 220000 Ω | 1 | ¼ W carbon film is fine |
| R7 | Resistor | 510 Ω | 1 | ¼ W carbon film is fine |
| R8 | Resistor | 510 Ω | 1 | ¼ W carbon film is fine |
| U1 | LM741 | LM741 | 1 |  |

Also: a standard 830-pin solderless breadboard, an assortment of jumper wires (red for the positive rail, black for ground rail, any colour for signals), and a 5 V supply.

## Layout

Each part below is drawn the way it sits on the breadboard, with every pin labelled. Chips run left-to-right with the notch at the left; pin 1 is the top-left pin (closest to the notch). Sensors and modules are shown as a single horizontal row of pins. 2-lead passives are drawn axially with the value in line.

### C1 — Capacitor

```
t1 ─┤├─ t2   [100 µF]
```

### C2 — Capacitor

```
t1 ─┤├─ t2   [100 nF]
```

### D1 — D1N4148

```
anode ─▶├─ cathode   [D1N4148]
```

### D2 — LED

```
anode (+, long lead) ─▶├─ cathode (−, short lead)   [red, 5 mm]
```

### R1 — Resistor

```
t1 ─┤▮ 100000 Ω ▮├─ t2
```

### R2 — Resistor

```
t1 ─┤▮ 100000 Ω ▮├─ t2
```

### R3 — Resistor

```
t1 ─┤▮ 4700 Ω ▮├─ t2
```

### R4 — Resistor

```
t1 ─┤▮ 50000 Ω ▮├─ t2
```

### R5 — Resistor

```
t1 ─┤▮ 10000000 Ω ▮├─ t2
```

### R6 — Resistor

```
t1 ─┤▮ 220000 Ω ▮├─ t2
```

### R7 — Resistor

```
t1 ─┤▮ 510 Ω ▮├─ t2
```

### R8 — Resistor

```
t1 ─┤▮ 510 Ω ▮├─ t2
```

### U1 — LM741

```
          1          2          3          4     
      OFFSET_N1   IN_NEG     IN_POS      V_NEG   
    ┌────────────────────────────────────────────┐
  U │                   LM741                    │
    └────────────────────────────────────────────┘
          —        V_POS       OUT     OFFSET_N2 
          8          7          6          5     
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
2. Plug U1 (LM741, DIP-8) straddling the trough: pin 1 at 10E, pin 7 at 11F.
   The chip's notch / dot marks pin 1 — make sure it lines up.
3. Plug R1 (Resistor): one lead at position 18 (any of 18A–18E), the other at
   position 21 (any of 21A–21E).
4. Plug R2 (Resistor): one lead at position 23 (any of 23A–23E), the other at
   position 26 (any of 26A–26E).
5. Plug R3 (Resistor): one lead at position 28 (any of 28A–28E), the other at
   position 31 (any of 31A–31E).
6. Plug R4 (Resistor): one lead at position 33 (any of 33A–33E), the other at
   position 36 (any of 36A–36E).
7. Plug R5 (Resistor): one lead at position 38 (any of 38A–38E), the other at
   position 41 (any of 41A–41E).
8. Plug R6 (Resistor): one lead at position 43 (any of 43A–43E), the other at
   position 46 (any of 46A–46E).
9. Plug C2 (Capacitor): one lead at position 48 (any of 48A–48E), the other at
   position 49 (any of 49A–49E).
10. Plug D1 (D1N4148): one lead at position 51 (any of 51A–51E), the other at
   position 52 (any of 52A–52E).
11. Plug C1 (Capacitor): one lead at position 54 (any of 54A–54E), the other
   at position 55 (any of 55A–55E).
12. Plug R7 (Resistor): one lead at position 57 (any of 57A–57E), the other at
   position 60 (any of 60A–60E).
13. Plug R8 (Resistor): one lead at position 62 (any of 62A–62E), the other at
   position 65 (any of 65A–65E).
14. Plug D2 (LED): one lead at position 67 (any of 67A–67E), the other at
   position 68 (any of 68A–68E).
15. Run a jumper from C2 t1 to D1 anode — position 48 (any of 48A–48E) to
   position 51 (any of 51A–51E).
16. Run a jumper from D1 anode to R5 t2 — position 51 (any of 51A–51E) to
   position 41 (any of 41A–41E).
17. Run a jumper from R5 t2 to U1 pin 2 — position 41 (any of 41A–41E) to
   position 11 (any of 11A–11E).
18. Run a jumper from R1 t2 to R2 t1 — position 21 (any of 21A–21E) to
   position 23 (any of 23A–23E).
19. Run a jumper from R2 t1 to R3 t1 — position 23 (any of 23A–23E) to
   position 28 (any of 28A–28E).
20. Run a jumper from R3 t1 to U1 pin 3 — position 28 (any of 28A–28E) to
   position 12 (any of 12A–12E).
21. Run a jumper from C1 t2 at position 55 (any of 55A–55E) to the top `-`
   rail.
22. Run a jumper from C2 t2 at position 49 (any of 49A–49E) to the top `-`
   rail.
23. Run a jumper from R2 t2 at position 26 (any of 26A–26E) to the top `-`
   rail.
24. Run a jumper from U1 pin 4 at position 13 (any of 13A–13E) to the top `-`
   rail.
25. Run a jumper from R4 t2 to R6 t1 — position 36 (any of 36A–36E) to
   position 43 (any of 43A–43E).
26. Run a jumper from R6 t1 to R8 t2 — position 43 (any of 43A–43E) to
   position 65 (any of 65A–65E).
27. Run a jumper from R8 t2 to U1 pin 6 — position 65 (any of 65A–65E) to
   position 12 (any of 12F–12J).
28. Run a jumper from C1 t1 at position 54 (any of 54A–54E) to the top `+`
   rail.
29. Run a jumper from R1 t1 at position 18 (any of 18A–18E) to the top `+`
   rail.
30. Run a jumper from R7 t1 at position 57 (any of 57A–57E) to the top `+`
   rail.
31. Run a jumper from U1 pin 7 at position 11 (any of 11F–11J) to the top `+`
   rail.
32. Run a jumper from D1 cathode to R5 t1 — position 52 (any of 52A–52E) to
   position 38 (any of 38A–38E).
33. Run a jumper from R5 t1 to R6 t2 — position 38 (any of 38A–38E) to
   position 46 (any of 46A–46E).
34. Run a jumper from D2 anode to R7 t2 — position 67 (any of 67A–67E) to
   position 60 (any of 60A–60E).
35. Run a jumper from D2 cathode to R8 t1 — position 68 (any of 68A–68E) to
   position 62 (any of 62A–62E).
36. Run a jumper from R3 t2 to R4 t1 — position 31 (any of 31A–31E) to
   position 33 (any of 33A–33E).
37. Verify nothing is shorted by inspecting the rails with a multimeter
   (continuity beep between `+` and `-` means trouble). Then connect the
   supply and observe.

## Notes & Gotchas

### General

- **Double-check the supply voltage before powering up.** Most TTL / CMOS logic survives 3.3 V – 5.5 V; an accidental 12 V from a bench supply destroys every chip on the board in microseconds. Set the supply, measure it with a multimeter, and only then connect.
- **Resistor wattage matters.** Standard ¼-W carbon-film resistors are fine below ~60 V across the part. Power resistors (½ W, 1 W) are needed for current-sense or load-dump positions; the BOM lists value only, not wattage — confirm against the schematic's expected current.
- **Tie unused CMOS inputs.** Any input pin not driven by the circuit must be wired to VCC or GND. Floating CMOS inputs drift unpredictably and can cause oscillation, excess supply current, or random behaviour. If your design has unused gates on a multi-gate chip, ground their inputs explicitly with a jumper.
- **Power-rail continuity.** Some 830-pin breadboards split each power rail into two segments at the middle of the board, with a visible break in the colored stripe. If your circuit uses the full rail length, bridge the gap with a jumper before powering on.

### Per-component

- **Electrolytic capacitors have a + and − end — always check which is which.** The longer lead is + (positive); the can has a stripe along the side near the − (negative) lead. Install one backwards and it heats up, vents boiling electrolyte, and sometimes pops loudly — this is the main reason 'always wear safety glasses' is a bench rule. Ceramic and film capacitors are not polarised and go in either way.
- **Always use a capacitor rated well above the voltage it will actually see.** Rule of thumb: pick a part rated for at least 1.5 times the highest steady-state voltage in your circuit. A 16 V cap on a 12 V rail will die early as the supply rings or sags; a 25 V cap shrugs the same conditions off. (The rated voltage is the *working* maximum, not a nominal indicator.)
- **Different capacitor types do different jobs — match the type to the role.** Big electrolytics (microfarads) sit on supply rails as bulk reservoirs; small ceramics (10–100 nF) go right next to chip supply pins as local decouplers; film and polypropylene caps handle precision timing where drift matters. Putting an electrolytic where a ceramic belongs (and vice versa) is the single most common 'why does this circuit oscillate?' bench mistake.
- **The black band marks the cathode (the − end).** Match the band to the bar in the schematic symbol — they're the same thing. Install it backwards and under normal bias the diode blocks current the wrong way (your circuit silently does nothing); under reverse bias it conducts and shorts whatever the diode was meant to protect.
- **Use the 1N4148 for small signal jobs — not for power.** It's rated for 200 mA average and 1 A peak, which suits logic-level steering, voltage clamping, level-shifting, and high-speed switching. It's the wrong choice for rectifying mains-derived AC or absorbing motor flyback current; reach for a 1N4001 or 1N4007 there.
- **LEDs have a + and − end — the long lead is +.** Get them the wrong way around and the LED simply doesn't light up; there's no spark or smoke, just a dark LED. If someone has already trimmed the leads, look at the rim of the plastic body: the flat spot marks the − (cathode) side. Both leads are valid wires as far as the framework is concerned, so it can't catch this mistake for you.
- **Always put a resistor in series with an LED — never connect an LED directly across a supply.** Without a resistor the LED draws too much current and burns out in a literal flash. 330 Ω works fine for most LEDs on a 5 V supply. (The formula, if you care: R = (V_supply − V_F) / I_target; 330 Ω drives about 10 mA through a typical red LED at 5 V, which is bright but not stressed.)
