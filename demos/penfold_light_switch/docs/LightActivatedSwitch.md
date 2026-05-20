# Build Guide: LightActivatedSwitch

LDR + comparator + transistor switch driving an indicator LED.

## Safety first

- **Put on safety glasses before powering anything up.** Electrolytic capacitors can vent boiling electrolyte if reverse-installed or over-volted; battery cells can flash violently on a short; small parts under tension (springs in switches, leads under a soldering iron) launch in unexpected directions. The glasses are cheap insurance against an afternoon you'd otherwise regret.
- **Discharge static before touching chips.** Touch a grounded metal surface (the bench frame, a radiator, the case of a mains-powered tool that's plugged in but switched off) before picking up MOSFETs or CMOS logic. A static spark you can't feel — under 100 V from walking across a carpet — punches through a gate oxide silently. The part still looks fine; it just doesn't work, and you spend two hours blaming your wiring. An ESD wrist strap clipped to a grounded surface is the permanent fix.
- **Wear insulating gloves when working above ~30 V or near mains.** Standard hobby breadboard work (3.3–24 V) doesn't need them; anything reaching into a wall-wart's primary side, a charged high-voltage capacitor, or a tube-amp B+ rail does. If the design includes a transformer, a switching supply's input stage, or a Cell pack above a few volts, treat it as hot until you've personally verified it's discharged.

## Parts

| Refdes | Part | Value / Spec | Quantity | Notes |
|--------|------|--------------|----------|-------|
| D1 | LED | red, 5 mm | 1 | Longer lead is the anode (+) |
| Q1 | BC547 | BC547 | 1 |  |
| R1 | Resistor | 10000 Ω | 1 | ¼ W carbon film is fine |
| R2 | Photoresistor | Photoresistor | 1 |  |
| R3 | Resistor | 10000 Ω | 1 | ¼ W carbon film is fine |
| R4 | Resistor | 5000 Ω | 1 | ¼ W carbon film is fine |
| R5 | Resistor | 4700 Ω | 1 | ¼ W carbon film is fine |
| R6 | Resistor | 470 Ω | 1 | ¼ W carbon film is fine |
| U1 | LM741 | LM741 | 1 |  |

Also: a standard 830-pin solderless breadboard, an assortment of jumper wires (red for the positive rail, black for ground rail, any colour for signals), and a 5 V supply.

## Layout

Each part below is drawn the way it sits on the breadboard, with every pin labelled. Chips run left-to-right with the notch at the left; pin 1 is the top-left pin (closest to the notch). Sensors and modules are shown as a single horizontal row of pins. 2-lead passives are drawn axially with the value in line.

### D1 — LED

```
anode (+, long lead) ─▶├─ cathode (−, short lead)   [red, 5 mm]
```

### Q1 — BC547

```
c ─┤▮ BC547 ▮├─ b
```

### R1 — Resistor

```
t1 ─┤▮ 10000 Ω ▮├─ t2
```

### R2 — Photoresistor

```
t1 ─┤▮ Photoresistor ▮├─ t2
```

### R3 — Resistor

```
t1 ─┤▮ 10000 Ω ▮├─ t2
```

### R4 — Resistor

```
t1 ─┤▮ 5000 Ω ▮├─ t2
```

### R5 — Resistor

```
t1 ─┤▮ 4700 Ω ▮├─ t2
```

### R6 — Resistor

```
t1 ─┤▮ 470 Ω ▮├─ t2
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

- **Set your multimeter to diode-test mode and probe the LED's leads.** Put the red probe on the long lead (anode +) and the black probe on the short lead (cathode −). A healthy LED lights up dimly — the meter is forcing a tiny current through it — and the reading shows the forward voltage (around 1.8 V for red, 2 V for yellow, 3.2 V for blue/white). Reverse the probes and the LED should stay dark with the meter reading OL. If both directions show OL the LED is open / dead; if both directions light the LED it has failed as a short. This also tells you which lead is the anode, useful if the leads were trimmed.
- **Measure the LDR's dark and light resistance with your multimeter before installing.** Set the meter to the kΩ or MΩ range, probe across the two leads, then cover the sensor with your finger — the reading should climb steeply (typical ORP12 specimens reach 100 kΩ–1 MΩ in shade). Uncover and shine a torch at it — the reading should fall to a few hundred ohms or less. A reading that doesn't move with light has either failed open (always OL) or is the wrong part. Photocells are not polarised; either lead goes in either hole.
- **Measure the resistance with your multimeter before installing.** Set the meter to the Ω (ohms) range, probe one lead, then the other; the reading should match the value printed on the part (or decoded from its colour bands) to within a few percent. A reading of OL (open / infinity) means the resistor is broken inside; a value wildly different from what's marked usually means someone has swapped parts in the bin and you've grabbed the wrong one.


## Method

1. Orient the breadboard with its long axis horizontal and the trough running
   left-to-right through the middle. Connect your 5 V supply: the positive
   lead to the top `+` rail (positive rail), the negative lead to the top `-`
   rail (ground rail).
2. Plug U1 (LM741, DIP-8) straddling the trough: pin 1 at 10E, pin 7 at 11F.
   The chip's notch / dot marks pin 1 — make sure it lines up.
3. Plug R2 (Photoresistor): one lead at position 18 (any of 18A–18E), the
   other at position 21 (any of 21A–21E).
4. Plug R1 (Resistor): one lead at position 23 (any of 23A–23E), the other at
   position 26 (any of 26A–26E).
5. Plug R3 (Resistor): one lead at position 28 (any of 28A–28E), the other at
   position 31 (any of 31A–31E).
6. Plug R4 (Resistor): one lead at position 33 (any of 33A–33E), the other at
   position 36 (any of 36A–36E).
7. Plug Q1 (BC547): one lead at position 38 (any of 38A–38E), the other at
   position 39 (any of 39A–39E).
8. Plug R5 (Resistor): one lead at position 41 (any of 41A–41E), the other at
   position 44 (any of 44A–44E).
9. Plug R6 (Resistor): one lead at position 46 (any of 46A–46E), the other at
   position 49 (any of 49A–49E).
10. Plug D1 (LED): one lead at position 51 (any of 51A–51E), the other at
   position 52 (any of 52A–52E).
11. Run a jumper from R3 t2 to R4 t1 — position 31 (any of 31A–31E) to
   position 33 (any of 33A–33E).
12. Run a jumper from R4 t1 to U1 pin 2 — position 33 (any of 33A–33E) to
   position 11 (any of 11A–11E).
13. Run a jumper from R1 t1 to R2 t2 — position 23 (any of 23A–23E) to
   position 21 (any of 21A–21E).
14. Run a jumper from R2 t2 to U1 pin 3 — position 21 (any of 21A–21E) to
   position 12 (any of 12A–12E).
15. Run a jumper from R1 t2 at position 26 (any of 26A–26E) to the top `-`
   rail.
16. Run a jumper from R4 t2 at position 36 (any of 36A–36E) to the top `-`
   rail.
17. Run a jumper from U1 pin 4 at position 13 (any of 13A–13E) to the top `-`
   rail.
18. Run a jumper from R5 t1 to U1 pin 6 — position 41 (any of 41A–41E) to
   position 12 (any of 12F–12J).
19. Run a jumper from R2 t1 at position 18 (any of 18A–18E) to the top `+`
   rail.
20. Run a jumper from R3 t1 at position 28 (any of 28A–28E) to the top `+`
   rail.
21. Run a jumper from R6 t1 at position 46 (any of 46A–46E) to the top `+`
   rail.
22. Run a jumper from U1 pin 7 at position 11 (any of 11F–11J) to the top `+`
   rail.
23. Run a jumper from D1 anode to R6 t2 — position 51 (any of 51A–51E) to
   position 49 (any of 49A–49E).
24. Run a jumper from D1 cathode to Q1 c — position 52 (any of 52A–52E) to
   position 38 (any of 38A–38E).
25. Run a jumper from Q1 b to R5 t2 — position 39 (any of 39A–39E) to position
   44 (any of 44A–44E).
26. Verify nothing is shorted by inspecting the rails with a multimeter
   (continuity beep between `+` and `-` means trouble). Then connect the
   supply and observe.

## Notes & Gotchas

### General

- **Double-check the supply voltage before powering up.** Most TTL / CMOS logic survives 3.3 V – 5.5 V; an accidental 12 V from a bench supply destroys every chip on the board in microseconds. Set the supply, measure it with a multimeter, and only then connect.
- **Resistor wattage matters.** Standard ¼-W carbon-film resistors are fine below ~60 V across the part. Power resistors (½ W, 1 W) are needed for current-sense or load-dump positions; the BOM lists value only, not wattage — confirm against the schematic's expected current.
- **Tie unused CMOS inputs.** Any input pin not driven by the circuit must be wired to VCC or GND. Floating CMOS inputs drift unpredictably and can cause oscillation, excess supply current, or random behaviour. If your design has unused gates on a multi-gate chip, ground their inputs explicitly with a jumper.
- **Power-rail continuity.** Some 830-pin breadboards split each power rail into two segments at the middle of the board, with a visible break in the colored stripe. If your circuit uses the full rail length, bridge the gap with a jumper before powering on.

### Per-component

- **LEDs have a + and − end — the long lead is +.** Get them the wrong way around and the LED simply doesn't light up; there's no spark or smoke, just a dark LED. If someone has already trimmed the leads, look at the rim of the plastic body: the flat spot marks the − (cathode) side. Both leads are valid wires as far as the framework is concerned, so it can't catch this mistake for you.
- **Always put a resistor in series with an LED — never connect an LED directly across a supply.** Without a resistor the LED draws too much current and burns out in a literal flash. 330 Ω works fine for most LEDs on a 5 V supply. (The formula, if you care: R = (V_supply − V_F) / I_target; 330 Ω drives about 10 mA through a typical red LED at 5 V, which is bright but not stressed.)
- **The LDR's resistance varies over orders of magnitude — pick the divider resistor to put the threshold where the scene's light level changes.** Size R_divider ≈ geometric mean of (R_LDR_dark, R_LDR_light): for an ORP12 this is roughly 10 kΩ for indoor twilight. Wrong divider values mean the trip point lives in the wrong part of the scene's range and the alarm / switch either fires continuously or never fires.
- **LDRs are slow.** Response time at full transitions is tens to hundreds of milliseconds (CdS is a slow photoeffect). Useful for ambient-light sensing, dawn/dusk switching, and burglar-alarm tripwires; useless for anything that needs to follow a flicker faster than ~10 Hz. Reach for a photodiode (BPW34, BPW21) or phototransistor (BPW77, BPX38) when you need optical bandwidth above audio frequencies.
- **Modern CdS-cell ban in the EU / RoHS regions** — newer designs reach for a photodiode + transimpedance amplifier instead. For hobby use and educational replication of vintage projects an ORP12 / GL5528 / VT93N2 is still the drop-in part; treat the bench supply as one-off and don't expect to find these in a current production parts catalogue.
