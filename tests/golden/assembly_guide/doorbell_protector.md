# Build Guide: DoorbellProtector

Two-LM555 doorbell protector.

## Safety first

- **Put on safety glasses before powering anything up.** Electrolytic capacitors can vent boiling electrolyte if reverse-installed or over-volted; battery cells can flash violently on a short; small parts under tension (springs in switches, leads under a soldering iron) launch in unexpected directions. The glasses are cheap insurance against an afternoon you'd otherwise regret.
- **Discharge static before touching chips.** Touch a grounded metal surface (the bench frame, a radiator, the case of a mains-powered tool that's plugged in but switched off) before picking up MOSFETs or CMOS logic. A static spark you can't feel — under 100 V from walking across a carpet — punches through a gate oxide silently. The part still looks fine; it just doesn't work, and you spend two hours blaming your wiring. An ESD wrist strap clipped to a grounded surface is the permanent fix.
- **Wear insulating gloves when working above ~30 V or near mains.** Standard hobby breadboard work (3.3–24 V) doesn't need them; anything reaching into a wall-wart's primary side, a charged high-voltage capacitor, or a tube-amp B+ rail does. If the design includes a transformer, a switching supply's input stage, or a Cell pack above a few volts, treat it as hot until you've personally verified it's discharged.

## Parts

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

## Layout

Each part below is drawn the way it sits on the breadboard, with every pin labelled. Chips run left-to-right with the notch at the left; pin 1 is the top-left pin (closest to the notch). Sensors and modules are shown as a single horizontal row of pins. 2-lead passives are drawn axially with the value in line.

### C1 — Capacitor

```
t1 ─┤├─ t2   [100 nF]
```

### C2 — Capacitor

```
t1 ─┤├─ t2   [4.7 µF]
```

### C3 — Capacitor

```
t1 ─┤├─ t2   [100 nF]
```

### C4 — Capacitor

```
t1 ─┤├─ t2   [100 nF]
```

### C5 — Capacitor

```
t1 ─┤├─ t2   [47 µF]
```

### D1 — D1N4007

```
anode ─▶├─ cathode   [D1N4007]
```

### D2 — LED

```
anode (+, long lead) ─▶├─ cathode (−, short lead)   [red, 5 mm]
```

### K1 — Relay_SPDT

```
coil_plus ─┤▮ Relay_SPDT ▮├─ coil_minus
```

### Q1 — BC548

```
c ─┤▮ BC548 ▮├─ b
```

### Q2 — Q2N3904

```
c ─┤▮ Q2N3904 ▮├─ b
```

### R1 — Resistor

```
t1 ─┤▮ 1000 Ω ▮├─ t2
```

### R2 — Resistor

```
t1 ─┤▮ 1000000 Ω ▮├─ t2
```

### R3 — Resistor

```
t1 ─┤▮ 1000000 Ω ▮├─ t2
```

### R4 — Resistor

```
t1 ─┤▮ 1000 Ω ▮├─ t2
```

### R5 — Resistor

```
t1 ─┤▮ 10000 Ω ▮├─ t2
```

### R6 — Resistor

```
t1 ─┤▮ 1000000 Ω ▮├─ t2
```

### R7 — Resistor

```
t1 ─┤▮ 4700 Ω ▮├─ t2
```

### R8 — Resistor

```
t1 ─┤▮ 47000 Ω ▮├─ t2
```

### U1 — NE555_Monostable

```
        1      2      3      4   
       GND   TRIG    OUT   RESET 
    ┌────────────────────────────┐
  U │      NE555_Monostable      │
    └────────────────────────────┘
       VCC   DISCH  THRES  CONT  
        8      7      6      5   
```

### U2 — NE555_Monostable

```
        1      2      3      4   
       GND   TRIG    OUT   RESET 
    ┌────────────────────────────┐
  U │      NE555_Monostable      │
    └────────────────────────────┘
       VCC   DISCH  THRES  CONT  
        8      7      6      5   
```


## How to verify

Before you start wiring, take five minutes to confirm each part actually works. A multimeter on the diode-test and resistance settings catches most pre-install failures: dead LEDs, mis-bagged parts, transistors damaged in shipping, batteries below their safe-discharge limit. The checks below cover what you can verify with a basic multimeter; chips and complex modules generally need a working test rig instead, so they're not listed here.

- **Test as 'two diodes back-to-back sharing the base'.** Put the red probe on the base (middle pin) and touch the black probe to each of the other two pins in turn — both should read about 0.6 V forward (base-to-emitter, base-to-collector in forward bias). Reverse: red on one of the other pins, black on the base — both readings should be OL. Any 0 V or unexpected OL means the junction is damaged. (Mind the European C-B-E pinout: looking at the flat side with the leads down, the *middle* pin is the base for the BC548 the same as for the 2N3904, but the outer pins are swapped.)
- **For an electrolytic capacitor, use your multimeter's diode-test or continuity mode to confirm it charges.** Put the red probe on the + lead (longer / unmarked side) and the black on the − lead (the side with the stripe). A healthy cap shows a voltage that climbs over a second or two and then settles to OL — the meter is charging the cap through its internal current source. Reverse the leads briefly to discharge and repeat. A cap that immediately reads zero (continuous beep) is shorted; one that reads OL from the first touch is open or has lost its capacitance.
- **Confirm the printed value matches what the design calls for** — capacitor markings are easy to misread. Big electrolytics print the value directly (e.g. '100 µF 25 V'); smaller ceramics use a three-digit code where the first two digits are the value in pF and the third is the number of trailing zeros ('104' means 100,000 pF = 100 nF = 0.1 µF). A capacitance meter (built into many DMMs) confirms the value within ±10%.
- **Use the multimeter's diode-test mode.** Red probe on the anode (unmarked end), black probe on the cathode (banded end): the meter reads about 0.6 V forward. Reverse the probes: OL. Both directions showing 0.6 V means a shorted diode; both showing OL means an open diode. The body marking should read '1N4007' — the lower 1N400x variants look identical externally but have lower reverse-voltage ratings.
- **Set your multimeter to diode-test mode and probe the LED's leads.** Put the red probe on the long lead (anode +) and the black probe on the short lead (cathode −). A healthy LED lights up dimly — the meter is forcing a tiny current through it — and the reading shows the forward voltage (around 1.8 V for red, 2 V for yellow, 3.2 V for blue/white). Reverse the probes and the LED should stay dark with the meter reading OL. If both directions show OL the LED is open / dead; if both directions light the LED it has failed as a short. This also tells you which lead is the anode, useful if the leads were trimmed.
- **Test an NPN BJT with the diode-test mode as 'two diodes back-to-back, sharing the base'.** Put the red probe on the base (middle pin); touch the black probe to the emitter, then to the collector. Both readings should be about 0.6 V forward — base-to-emitter and base-to-collector junctions in forward bias. Now put red on the emitter or collector and black on the base: both should read OL (junctions in reverse). Any reading of 0 V (short) or unexpected OL means the part is damaged.
- **Measure the coil resistance with your multimeter.** Put the meter in resistance (Ω) mode and probe the two coil pins. A small hobby relay's coil typically reads between 50 Ω and a few hundred ohms; 0 Ω means the coil is shorted (don't apply power), OL means it's burned open. The package usually labels which pins are the coil.
- **Check the resting contact state.** Switch the meter to continuity / beep mode. Probe Common (COM) to Normally-Closed (NC): the meter should beep — these contacts are connected when the coil is *not* energised. Probe Common to Normally-Open (NO): OL — these contacts are not connected at rest. Now briefly apply the rated coil voltage and you should hear an audible click as the relay actuates; the readings flip (COM-NC opens, COM-NO closes). No click means the coil is dead or you've applied the wrong voltage.
- **Measure the resistance with your multimeter before installing.** Set the meter to the Ω (ohms) range, probe one lead, then the other; the reading should match the value printed on the part (or decoded from its colour bands) to within a few percent. A reading of OL (open / infinity) means the resistor is broken inside; a value wildly different from what's marked usually means someone has swapped parts in the bin and you've grabbed the wrong one.


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
22. Run a jumper from C4 t1 to C4 t2 — position 85 (any of 85A–85E) to
   position 86 (any of 86A–86E).
23. Run a jumper from C4 t2 to D2 anode — position 86 (any of 86A–86E) to
   position 33 (any of 33A–33E).
24. Run a jumper from D2 anode to K1 coil_plus — position 33 (any of 33A–33E)
   to position 91 (any of 91A–91E).
25. Run a jumper from K1 coil_plus to Q1 b — position 91 (any of 91A–91E) to
   position 25 (any of 25A–25E).
26. Run a jumper from Q1 b to R1 t1 — position 25 (any of 25A–25E) to position
   36 (any of 36A–36E).
27. Run a jumper from R1 t1 to R1 t2 — position 36 (any of 36A–36E) to
   position 39 (any of 39A–39E).
28. Run a jumper from R1 t2 to U1 pin 3 — position 39 (any of 39A–39E) to
   position 12 (any of 12A–12E).
29. Run a jumper from U1 pin 3 to U2 pin 2 — position 12 (any of 12A–12E) to
   position 17 (any of 17A–17E).
30. Run a jumper from D1 cathode at position 31 (any of 31A–31E) to the top
   `+` rail.
31. Run a jumper from U2 pin 4 at position 19 (any of 19A–19E) to the top `+`
   rail.
32. Run a jumper from D2 cathode at position 34 (any of 34A–34E) to the top
   `-` rail.
33. Run a jumper from Q2 b to R4 t1 — position 28 (any of 28A–28E) to position
   51 (any of 51A–51E).
34. Run a jumper from R4 t1 to R4 t2 — position 51 (any of 51A–51E) to
   position 54 (any of 54A–54E).
35. Run a jumper from R4 t2 to U2 pin 3 — position 54 (any of 54A–54E) to
   position 18 (any of 18A–18E).
36. Run a jumper from Q2 c to R5 t1 — position 27 (any of 27A–27E) to position
   56 (any of 56A–56E).
37. Run a jumper from R5 t1 to R5 t2 — position 56 (any of 56A–56E) to
   position 59 (any of 59A–59E).
38. Run a jumper from R5 t2 to U1 pin 4 — position 59 (any of 59A–59E) to
   position 13 (any of 13A–13E).
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

- **Hold the BC548 with the flat side facing you, leads pointing down — the pins are then Collector, Base, Emitter from left to right.** This is the European pinout (the whole BC54x family). The Americans wired their TO-92 parts in the mirror order — a 2N3904 or 2N2222 in the same package has the pins in *reversed* order: E, B, C from left to right. Swapping a BC548 for a 2N3904 in a hurry without rotating the part puts the emitter where the collector should be; nothing visibly fails, the circuit just stops working.
- **Always put a resistor in series with the base when driving from a logic pin.** The base-emitter junction is a diode; wired directly to a 5 V MCU pin it draws whatever current the pin can supply — which is more than the BC548's base can handle, and the part cooks. A 1 kΩ resistor in series limits base current to ~4 mA, plenty for switching a small load.
- **Electrolytic capacitors have a + and − end — always check which is which.** The longer lead is + (positive); the can has a stripe along the side near the − (negative) lead. Install one backwards and it heats up, vents boiling electrolyte, and sometimes pops loudly — this is the main reason 'always wear safety glasses' is a bench rule. Ceramic and film capacitors are not polarised and go in either way.
- **Always use a capacitor rated well above the voltage it will actually see.** Rule of thumb: pick a part rated for at least 1.5 times the highest steady-state voltage in your circuit. A 16 V cap on a 12 V rail will die early as the supply rings or sags; a 25 V cap shrugs the same conditions off. (The rated voltage is the *working* maximum, not a nominal indicator.)
- **Different capacitor types do different jobs — match the type to the role.** Big electrolytics (microfarads) sit on supply rails as bulk reservoirs; small ceramics (10–100 nF) go right next to chip supply pins as local decouplers; film and polypropylene caps handle precision timing where drift matters. Putting an electrolytic where a ceramic belongs (and vice versa) is the single most common 'why does this circuit oscillate?' bench mistake.
- **The black band marks the cathode (− end).** Match the band to the bar in the schematic symbol; they mean the same thing. Reverse-installing a rectifier on a transformer secondary is one of the most reliable ways to pop both the diode and the fuse in the same switch-on event.
- **The 1N4007 is the workhorse mains rectifier and a great flyback diode for slow inductive loads.** It blocks 1000 V reverse, conducts 1 A continuous, and costs almost nothing. Use it for relay coils, solenoids, small motors at audio frequencies, and any AC rectification at line frequency. Slow recovery (~2 µs) means it's the wrong choice for switching power supplies above a few kHz; a Schottky like the 1N5817 handles those.
- **LEDs have a + and − end — the long lead is +.** Get them the wrong way around and the LED simply doesn't light up; there's no spark or smoke, just a dark LED. If someone has already trimmed the leads, look at the rim of the plastic body: the flat spot marks the − (cathode) side. Both leads are valid wires as far as the framework is concerned, so it can't catch this mistake for you.
- **Always put a resistor in series with an LED — never connect an LED directly across a supply.** Without a resistor the LED draws too much current and burns out in a literal flash. 330 Ω works fine for most LEDs on a 5 V supply. (The formula, if you care: R = (V_supply − V_F) / I_target; 330 Ω drives about 10 mA through a typical red LED at 5 V, which is bright but not stressed.)
- **Put a capacitor across the supply pins, right at the chip.** A 100 nF ceramic from pin 8 (Vcc) to pin 1 (GND), leads under 5 mm long. The 555 draws a sharp current spike every time its output switches, and without a local cap the supply rail rings — making the oscillator's timing drift and coupling noise into anything else sharing the supply. If your 555 oscillator runs at the wrong frequency or jitters, this is the first thing to check.
- **Add a 10 nF cap from pin 5 to ground**, even if you're not using pin 5 for anything. Pin 5 (Control Voltage) is internally connected to the chip's reference divider, and without that little cap the pin acts as an antenna for nearby noise — your steady oscillator turns into a jittery one for no obvious reason. (The pin's high-impedance node picks up stray fields and modulates the comparator thresholds; the cap shorts that noise to ground.)
- **For battery-powered work, use a CMOS 555 instead** — the TLC555 or ICM7555 are drop-in replacements that draw ~100 µA versus the original NE555's 3–10 mA. Same pinout, same external circuit, ten to a hundred times the battery life. The classic bipolar NE555 has one advantage: its output can drive ~200 mA directly into a load — useful for small lamps or relays at the cost of rougher supply behaviour.
- **Hold the 2N3904 with the flat side facing you, leads pointing down — the pins are Emitter, Base, Collector from left to right.** This is the American JEDEC convention. The European BC547 / BC548 in the same TO-92 package have the *opposite* pin order (C, B, E). Drop a BC547 into a 2N3904's spot without rotating it 180° and emitter ends up where collector should be — the part still conducts a little, but the circuit silently doesn't work.
- **Always put a resistor in series with the base when driving from a logic pin.** The base-emitter junction is a forward-biased diode; wired directly to a 5 V MCU pin it conducts whatever current the pin can deliver, which exceeds the transistor's absolute-max base rating and burns it out. A 1 kΩ resistor limits the base current to about 4 mA — plenty to switch the transistor fully on for any small collector load.
- **Put a diode across the relay's coil — the band toward the + supply side.** A 1N4001 or 1N4007 does the job. Without this 'flyback' diode, the moment you switch the coil off the collapsing magnetic field generates a +100 V spike that destroys whatever was driving the coil (your MCU pin, your transistor, or your MOSFET). This is the single most common relay-circuit mistake, and the failure happens silently — the driving transistor just stops working some time later.
- **The relay has two voltage ratings, and they're independent.** The coil voltage is what powers the electromagnet (5 V, 12 V, etc.); the contact voltage rating is what the relay can switch (often 250 V AC at several amps). A 5 V relay with 250 V contacts is normal. Don't tie the coil supply and the load supply together without checking both ratings — they're designed to be separate.
- **MCU pins can't power a relay coil directly — use a transistor in between.** Relay coils typically draw 50–100 mA continuously while energised; MCU pins are rated for about 20 mA absolute max. Drive the coil through an NPN transistor (or N-channel MOSFET) and switch *that* with the MCU. Also confirm your supply has the current to spare: a 9 V battery feeding a small regulator may already be near its limit when you add a relay.
- **Switching inductive AC loads (motors, transformer primaries) wears the contacts out fast.** Each switch-off arcs the contacts; over thousands of cycles the surfaces pit and eventually weld shut or fail to make contact. Add a 'snubber' (100 Ω resistor in series with a 100 nF capacitor, the pair wired across the contacts) to dissipate the arc energy. For fast or frequent switching, use a solid-state relay instead.
