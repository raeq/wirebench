# Build Guide: WarblingDoorbuzzer

Two NE555 astables; slow modulates fast via the RESET pin.

## Safety first

- **Put on safety glasses before powering anything up.** Electrolytic capacitors can vent boiling electrolyte if reverse-installed or over-volted; battery cells can flash violently on a short; small parts under tension (springs in switches, leads under a soldering iron) launch in unexpected directions. The glasses are cheap insurance against an afternoon you'd otherwise regret.
- **Discharge static before touching chips.** Touch a grounded metal surface (the bench frame, a radiator, the case of a mains-powered tool that's plugged in but switched off) before picking up MOSFETs or CMOS logic. A static spark you can't feel — under 100 V from walking across a carpet — punches through a gate oxide silently. The part still looks fine; it just doesn't work, and you spend two hours blaming your wiring. An ESD wrist strap clipped to a grounded surface is the permanent fix.
- **Wear insulating gloves when working above ~30 V or near mains.** Standard hobby breadboard work (3.3–24 V) doesn't need them; anything reaching into a wall-wart's primary side, a charged high-voltage capacitor, or a tube-amp B+ rail does. If the design includes a transformer, a switching supply's input stage, or a Cell pack above a few volts, treat it as hot until you've personally verified it's discharged.

## Parts

| Refdes | Part | Value / Spec | Quantity | Notes |
|--------|------|--------------|----------|-------|
| C1 | Capacitor | 2.2 µF | 1 |  |
| C2 | Capacitor | 10 nF | 1 |  |
| C3 | Capacitor | 100 nF | 1 |  |
| C4 | Capacitor | 10 nF | 1 |  |
| C5 | Capacitor | 10 µF | 1 |  |
| LS1 | Speaker | Speaker | 1 |  |
| R1 | Resistor | 47000 Ω | 1 | ¼ W carbon film is fine |
| R2 | Resistor | 47000 Ω | 1 | ¼ W carbon film is fine |
| R3 | Resistor | 4700 Ω | 1 | ¼ W carbon film is fine |
| R4 | Resistor | 4700 Ω | 1 | ¼ W carbon film is fine |
| R5 | Resistor | 100 Ω | 1 | ¼ W carbon film is fine |
| U1 | NE555 | NE555 | 1 |  |
| U2 | NE555 | NE555 | 1 |  |

Also: a standard 830-pin solderless breadboard, an assortment of jumper wires (red for the positive rail, black for ground rail, any colour for signals), and a 5 V supply.

## Layout

Each part below is drawn the way it sits on the breadboard, with every pin labelled. Chips run left-to-right with the notch at the left; pin 1 is the top-left pin (closest to the notch). Sensors and modules are shown as a single horizontal row of pins. 2-lead passives are drawn axially with the value in line.

### C1 — Capacitor

```
t1 ─┤├─ t2   [2.2 µF]
```

### C2 — Capacitor

```
t1 ─┤├─ t2   [10 nF]
```

### C3 — Capacitor

```
t1 ─┤├─ t2   [100 nF]
```

### C4 — Capacitor

```
t1 ─┤├─ t2   [10 nF]
```

### C5 — Capacitor

```
t1 ─┤├─ t2   [10 µF]
```

### LS1 — Speaker

```
t1 ─┤▮ Speaker ▮├─ t2
```

### R1 — Resistor

```
t1 ─┤▮ 47000 Ω ▮├─ t2
```

### R2 — Resistor

```
t1 ─┤▮ 47000 Ω ▮├─ t2
```

### R3 — Resistor

```
t1 ─┤▮ 4700 Ω ▮├─ t2
```

### R4 — Resistor

```
t1 ─┤▮ 4700 Ω ▮├─ t2
```

### R5 — Resistor

```
t1 ─┤▮ 100 Ω ▮├─ t2
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

### U2 — NE555

```
        1      2      3      4   
       GND   TRIG    OUT   RESET 
    ┌────────────────────────────┐
  U │           NE555            │
    └────────────────────────────┘
       VCC   DISCH  THRES  CONT  
        8      7      6      5   
```


## How to verify

Before you start wiring, take five minutes to confirm each part actually works. A multimeter on the diode-test and resistance settings catches most pre-install failures: dead LEDs, mis-bagged parts, transistors damaged in shipping, batteries below their safe-discharge limit. The checks below cover what you can verify with a basic multimeter; chips and complex modules generally need a working test rig instead, so they're not listed here.

- **For an electrolytic capacitor, use your multimeter's diode-test or continuity mode to confirm it charges.** Put the red probe on the + lead (longer / unmarked side) and the black on the − lead (the side with the stripe). A healthy cap shows a voltage that climbs over a second or two and then settles to OL — the meter is charging the cap through its internal current source. Reverse the leads briefly to discharge and repeat. A cap that immediately reads zero (continuous beep) is shorted; one that reads OL from the first touch is open or has lost its capacitance.
- **Confirm the printed value matches what the design calls for** — capacitor markings are easy to misread. Big electrolytics print the value directly (e.g. '100 µF 25 V'); smaller ceramics use a three-digit code where the first two digits are the value in pF and the third is the number of trailing zeros ('104' means 100,000 pF = 100 nF = 0.1 µF). A capacitance meter (built into many DMMs) confirms the value within ±10%.
- **Measure the resistance with your multimeter before installing.** Set the meter to the Ω (ohms) range, probe one lead, then the other; the reading should match the value printed on the part (or decoded from its colour bands) to within a few percent. A reading of OL (open / infinity) means the resistor is broken inside; a value wildly different from what's marked usually means someone has swapped parts in the bin and you've grabbed the wrong one.
- **Measure the speaker's DC resistance with your multimeter.** Set the meter to the Ω range, probe across the two leads — a healthy moving-coil speaker reads slightly *less* than its nominal impedance (an '8 Ω speaker' typically reads around 6.5 Ω DC; the difference is reactive at the rated audio frequency).  A reading of OL means the voice coil has burnt out; a reading at 0 Ω means it's shorted.  Touch the leads to a 1.5 V cell briefly — a working speaker emits a faint click as the cone moves and the DC current sets up.


## Method

1. Orient the breadboard with its long axis horizontal and the trough running
   left-to-right through the middle. Connect your 5 V supply: the positive
   lead to the top `+` rail (positive rail), the negative lead to the top `-`
   rail (ground rail).
2. Plug U1 (NE555, DIP-8) straddling the trough: pin 1 at 10E, pin 8 at 10F.
   The chip's notch / dot marks pin 1 — make sure it lines up.
3. Plug U2 (NE555, DIP-8) straddling the trough: pin 1 at 16E, pin 8 at 16F.
   The chip's notch / dot marks pin 1 — make sure it lines up.
4. Plug R1 (Resistor): one lead at position 24 (any of 24A–24E), the other at
   position 27 (any of 27A–27E).
5. Plug R2 (Resistor): one lead at position 29 (any of 29A–29E), the other at
   position 32 (any of 32A–32E).
6. Plug C1 (Capacitor): one lead at position 34 (any of 34A–34E), the other at
   position 35 (any of 35A–35E).
7. Plug C2 (Capacitor): one lead at position 37 (any of 37A–37E), the other at
   position 38 (any of 38A–38E).
8. Plug R3 (Resistor): one lead at position 40 (any of 40A–40E), the other at
   position 43 (any of 43A–43E).
9. Plug R4 (Resistor): one lead at position 45 (any of 45A–45E), the other at
   position 48 (any of 48A–48E).
10. Plug C3 (Capacitor): one lead at position 50 (any of 50A–50E), the other
   at position 51 (any of 51A–51E).
11. Plug C4 (Capacitor): one lead at position 53 (any of 53A–53E), the other
   at position 54 (any of 54A–54E).
12. Plug R5 (Resistor): one lead at position 56 (any of 56A–56E), the other at
   position 59 (any of 59A–59E).
13. Plug C5 (Capacitor): one lead at position 61 (any of 61A–61E), the other
   at position 62 (any of 62A–62E).
14. Plug LS1 (Speaker): one lead at position 64 (any of 64A–64E), the other at
   position 66 (any of 66A–66E).
15. Run a jumper from C1 t2 at position 35 (any of 35A–35E) to the top `-`
   rail.
16. Run a jumper from C2 t2 at position 38 (any of 38A–38E) to the top `-`
   rail.
17. Run a jumper from C3 t2 at position 51 (any of 51A–51E) to the top `-`
   rail.
18. Run a jumper from C4 t2 at position 54 (any of 54A–54E) to the top `-`
   rail.
19. Run a jumper from LS1 t2 at position 66 (any of 66A–66E) to the top `-`
   rail.
20. Run a jumper from U1 pin 1 at position 10 (any of 10A–10E) to the top `-`
   rail.
21. Run a jumper from U2 pin 1 at position 16 (any of 16A–16E) to the top `-`
   rail.
22. Run a jumper from C1 t1 to R2 t2 — position 34 (any of 34A–34E) to
   position 32 (any of 32A–32E).
23. Run a jumper from R2 t2 to U1 pin 2 — position 32 (any of 32A–32E) to
   position 11 (any of 11A–11E).
24. Run a jumper from U1 pin 2 to U1 pin 6 — position 11 (any of 11A–11E) to
   position 12 (any of 12F–12J).
25. Run a jumper from U1 pin 3 to U2 pin 4 — position 12 (any of 12A–12E) to
   position 19 (any of 19A–19E).
26. Run a jumper from U1 pin 4 at position 13 (any of 13A–13E) to the top `+`
   rail.
27. Run a jumper from C2 t1 to U1 pin 5 — position 37 (any of 37A–37E) to
   position 13 (any of 13F–13J).
28. Run a jumper from R1 t2 to R2 t1 — position 27 (any of 27A–27E) to
   position 29 (any of 29A–29E).
29. Run a jumper from R2 t1 to U1 pin 7 — position 29 (any of 29A–29E) to
   position 11 (any of 11F–11J).
30. Run a jumper from R1 t1 at position 24 (any of 24A–24E) to the top `+`
   rail.
31. Run a jumper from R3 t1 at position 40 (any of 40A–40E) to the top `+`
   rail.
32. Run a jumper from U1 pin 8 at position 10 (any of 10F–10J) to the top `+`
   rail.
33. Run a jumper from U2 pin 8 at position 16 (any of 16F–16J) to the top `+`
   rail.
34. Run a jumper from C3 t1 to R4 t2 — position 50 (any of 50A–50E) to
   position 48 (any of 48A–48E).
35. Run a jumper from R4 t2 to U2 pin 2 — position 48 (any of 48A–48E) to
   position 17 (any of 17A–17E).
36. Run a jumper from U2 pin 2 to U2 pin 6 — position 17 (any of 17A–17E) to
   position 18 (any of 18F–18J).
37. Run a jumper from R5 t1 to U2 pin 3 — position 56 (any of 56A–56E) to
   position 18 (any of 18A–18E).
38. Run a jumper from C4 t1 to U2 pin 5 — position 53 (any of 53A–53E) to
   position 19 (any of 19F–19J).
39. Run a jumper from R3 t2 to R4 t1 — position 43 (any of 43A–43E) to
   position 45 (any of 45A–45E).
40. Run a jumper from R4 t1 to U2 pin 7 — position 45 (any of 45A–45E) to
   position 17 (any of 17F–17J).
41. Run a jumper from C5 t1 to R5 t2 — position 61 (any of 61A–61E) to
   position 59 (any of 59A–59E).
42. Run a jumper from C5 t2 to LS1 t1 — position 62 (any of 62A–62E) to
   position 64 (any of 64A–64E).
43. Verify nothing is shorted by inspecting the rails with a multimeter
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
- **Put a capacitor across the supply pins, right at the chip.** A 100 nF ceramic from pin 8 (Vcc) to pin 1 (GND), leads under 5 mm long. The 555 draws a sharp current spike every time its output switches, and without a local cap the supply rail rings — making the oscillator's timing drift and coupling noise into anything else sharing the supply. If your 555 oscillator runs at the wrong frequency or jitters, this is the first thing to check.
- **Add a 10 nF cap from pin 5 to ground**, even if you're not using pin 5 for anything. Pin 5 (Control Voltage) is internally connected to the chip's reference divider, and without that little cap the pin acts as an antenna for nearby noise — your steady oscillator turns into a jittery one for no obvious reason. (The pin's high-impedance node picks up stray fields and modulates the comparator thresholds; the cap shorts that noise to ground.)
- **For battery-powered work, use a CMOS 555 instead** — the TLC555 or ICM7555 are drop-in replacements that draw ~100 µA versus the original NE555's 3–10 mA. Same pinout, same external circuit, ten to a hundred times the battery life. The classic bipolar NE555 has one advantage: its output can drive ~200 mA directly into a load — useful for small lamps or relays at the cost of rougher supply behaviour.
- **Don't drive a speaker directly from a CMOS output — the chip can't source enough current.** A typical 4xxx-series or 74HC output is good for about 5 mA; a small speaker wants tens of milliamps to be audible.  Buffer the output with an NPN emitter-follower or a dedicated audio chip like the LM386, or use a piezo transducer (which is essentially a capacitive load that needs only a fraction of a milliamp of drive current).
- **AC-couple the speaker to any DC-biased signal stage.** The 555's output sits at half-supply on average; wiring it directly to a speaker means a continuous DC current through the voice coil, which heats the speaker and shifts the cone off centre (eventually damaging it).  Add a series capacitor (10–100 µF electrolytic for hobby work) so only the AC swing reaches the coil.  This is *the* most common 555-astable / speaker mistake.
