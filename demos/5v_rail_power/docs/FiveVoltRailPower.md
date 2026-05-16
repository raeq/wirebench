# Build Guide: FiveVoltRailPower

5 V breadboard rail supply from a 3× CR2032 stack.

## Safety first

- **Put on safety glasses before powering anything up.** Electrolytic capacitors can vent boiling electrolyte if reverse-installed or over-volted; battery cells can flash violently on a short; small parts under tension (springs in switches, leads under a soldering iron) launch in unexpected directions. The glasses are cheap insurance against an afternoon you'd otherwise regret.
- **Discharge static before touching chips.** Touch a grounded metal surface (the bench frame, a radiator, the case of a mains-powered tool that's plugged in but switched off) before picking up MOSFETs or CMOS logic. A static spark you can't feel — under 100 V from walking across a carpet — punches through a gate oxide silently. The part still looks fine; it just doesn't work, and you spend two hours blaming your wiring. An ESD wrist strap clipped to a grounded surface is the permanent fix.
- **Wear insulating gloves when working above ~30 V or near mains.** Standard hobby breadboard work (3.3–24 V) doesn't need them; anything reaching into a wall-wart's primary side, a charged high-voltage capacitor, or a tube-amp B+ rail does. If the design includes a transformer, a switching supply's input stage, or a Cell pack above a few volts, treat it as hot until you've personally verified it's discharged.

## Parts

| Refdes | Part | Value / Spec | Quantity | Notes |
|--------|------|--------------|----------|-------|
| BT1 | CR2032Stack | CR2032Stack | 1 |  |
| C1 | Capacitor | 100 nF | 1 |  |
| C2 | Capacitor | 10 µF | 1 |  |
| D1 | D1N5817 | D1N5817 | 1 |  |
| D2 | D1N4733A | D1N4733A | 1 |  |
| D3 | LED | green, 5 mm | 1 | Longer lead is the anode (+) |
| P1 | Header1xNMale | Header1xNMale | 1 |  |
| R1 | Resistor | 470 Ω | 1 | ¼ W carbon film is fine |
| U1 | LM7805 | LM7805 | 1 |  |

Also: a standard 830-pin solderless breadboard, an assortment of jumper wires (red for the positive rail, black for ground rail, any colour for signals), and a 5 V supply.

## Layout

Each part below is drawn the way it sits on the breadboard, with every pin labelled. Chips run left-to-right with the notch at the left; pin 1 is the top-left pin (closest to the notch). Sensors and modules are shown as a single horizontal row of pins. 2-lead passives are drawn axially with the value in line.

### BT1 — CR2032Stack

```
pos ─┤▮ CR2032Stack ▮├─ neg
```

### C1 — Capacitor

```
t1 ─┤├─ t2   [100 nF]
```

### C2 — Capacitor

```
t1 ─┤├─ t2   [10 µF]
```

### D1 — D1N5817

```
anode ─▶├─ cathode   [D1N5817]
```

### D2 — D1N4733A

```
anode ─▶├─ cathode   [D1N4733A]
```

### D3 — LED

```
anode (+, long lead) ─▶├─ cathode (−, short lead)   [green, 5 mm]
```

### P1 — Header1xNMale

```
p1 ─┤▮ Header1xNMale ▮├─ p1_inner
```

### R1 — Resistor

```
t1 ─┤▮ 470 Ω ▮├─ t2
```

### U1 — LM7805

```
┌────────────────────────┐
│         LM7805         │
└┬───────┬───────┬───────┘
 1       2       3
NPUT    GND   OUTPUT
```


## How to verify

Before you start wiring, take five minutes to confirm each part actually works. A multimeter on the diode-test and resistance settings catches most pre-install failures: dead LEDs, mis-bagged parts, transistors damaged in shipping, batteries below their safe-discharge limit. The checks below cover what you can verify with a basic multimeter; chips and complex modules generally need a working test rig instead, so they're not listed here.

- **For an electrolytic capacitor, use your multimeter's diode-test or continuity mode to confirm it charges.** Put the red probe on the + lead (longer / unmarked side) and the black on the − lead (the side with the stripe). A healthy cap shows a voltage that climbs over a second or two and then settles to OL — the meter is charging the cap through its internal current source. Reverse the leads briefly to discharge and repeat. A cap that immediately reads zero (continuous beep) is shorted; one that reads OL from the first touch is open or has lost its capacitance.
- **Confirm the printed value matches what the design calls for** — capacitor markings are easy to misread. Big electrolytics print the value directly (e.g. '100 µF 25 V'); smaller ceramics use a three-digit code where the first two digits are the value in pF and the third is the number of trailing zeros ('104' means 100,000 pF = 100 nF = 0.1 µF). A capacitance meter (built into many DMMs) confirms the value within ±10%.
- **A Schottky reads a lower forward voltage than a silicon diode on the multimeter's diode test.** Red probe on the anode (unmarked end), black on the cathode (banded end): a healthy 1N5817 reads about 0.2–0.3 V forward, not the 0.6 V you'd see from a 1N4001 — the low drop is the Schottky's defining feature. Reverse the probes and the meter reads OL. If you read 0.6 V forward, somebody put a silicon diode in the Schottky bin.
- **Set your multimeter to diode-test mode and probe the LED's leads.** Put the red probe on the long lead (anode +) and the black probe on the short lead (cathode −). A healthy LED lights up dimly — the meter is forcing a tiny current through it — and the reading shows the forward voltage (around 1.8 V for red, 2 V for yellow, 3.2 V for blue/white). Reverse the probes and the LED should stay dark with the meter reading OL. If both directions show OL the LED is open / dead; if both directions light the LED it has failed as a short. This also tells you which lead is the anode, useful if the leads were trimmed.
- **Measure the resistance with your multimeter before installing.** Set the meter to the Ω (ohms) range, probe one lead, then the other; the reading should match the value printed on the part (or decoded from its colour bands) to within a few percent. A reading of OL (open / infinity) means the resistor is broken inside; a value wildly different from what's marked usually means someone has swapped parts in the bin and you've grabbed the wrong one.


## Method

1. Orient the breadboard with its long axis horizontal and the trough running
   left-to-right through the middle. Connect your 5 V supply: the positive
   lead to the top `+` rail (positive rail), the negative lead to the top `-`
   rail (ground rail).
2. Plug U1 (LM7805, DIP-3) straddling the trough: pin 1 at 10E, pin 3 at 11F.
   The chip's notch / dot marks pin 1 — make sure it lines up.
3. Plug BT1 (CR2032Stack): one lead at position 15 (any of 15A–15E), the other
   at position 16 (any of 16A–16E).
4. Plug P1 (Header1xNMale): one lead at position 18 (any of 18A–18E), the
   other at position 19 (any of 19A–19E).
5. Plug D1 (D1N5817): one lead at position 21 (any of 21A–21E), the other at
   position 22 (any of 22A–22E).
6. Plug C1 (Capacitor): one lead at position 24 (any of 24A–24E), the other at
   position 25 (any of 25A–25E).
7. Plug C2 (Capacitor): one lead at position 27 (any of 27A–27E), the other at
   position 28 (any of 28A–28E).
8. Plug D2 (D1N4733A): one lead at position 30 (any of 30A–30E), the other at
   position 31 (any of 31A–31E).
9. Plug R1 (Resistor): one lead at position 33 (any of 33A–33E), the other at
   position 36 (any of 36A–36E).
10. Plug D3 (LED): one lead at position 38 (any of 38A–38E), the other at
   position 39 (any of 39A–39E).
11. Run a jumper from BT1 neg to C1 t2 — position 16 (any of 16A–16E) to
   position 25 (any of 25A–25E).
12. Run a jumper from C1 t2 to C2 t2 — position 25 (any of 25A–25E) to
   position 28 (any of 28A–28E).
13. Run a jumper from C2 t2 to D2 anode — position 28 (any of 28A–28E) to
   position 30 (any of 30A–30E).
14. Run a jumper from D2 anode to D3 cathode — position 30 (any of 30A–30E) to
   position 39 (any of 39A–39E).
15. Run a jumper from D3 cathode to U1 GND — position 39 (any of 39A–39E) to
   position 11 (any of 11A–11E).
16. Run a jumper from BT1 pos to P1 p1_inner — position 15 (any of 15A–15E) to
   position 19 (any of 19A–19E).
17. Run a jumper from C1 t1 to D1 cathode — position 24 (any of 24A–24E) to
   position 22 (any of 22A–22E).
18. Run a jumper from D1 cathode to U1 INPUT — position 22 (any of 22A–22E) to
   position 10 (any of 10A–10E).
19. Run a jumper from C2 t1 to D2 cathode — position 27 (any of 27A–27E) to
   position 31 (any of 31A–31E).
20. Run a jumper from D2 cathode to R1 t1 — position 31 (any of 31A–31E) to
   position 33 (any of 33A–33E).
21. Run a jumper from R1 t1 to U1 OUTPUT — position 33 (any of 33A–33E) to
   position 11 (any of 11F–11J).
22. Run a jumper from D3 anode to R1 t2 — position 38 (any of 38A–38E) to
   position 36 (any of 36A–36E).
23. Verify nothing is shorted by inspecting the rails with a multimeter
   (continuity beep between `+` and `-` means trouble). Then connect the
   supply and observe.

## Notes & Gotchas

### General

- **Double-check the supply voltage before powering up.** Most TTL / CMOS logic survives 3.3 V – 5.5 V; an accidental 12 V from a bench supply destroys every chip on the board in microseconds. Set the supply, measure it with a multimeter, and only then connect.
- **Resistor wattage matters.** Standard ¼-W carbon-film resistors are fine below ~60 V across the part. Power resistors (½ W, 1 W) are needed for current-sense or load-dump positions; the BOM lists value only, not wattage — confirm against the schematic's expected current.
- **Tie unused CMOS inputs.** Any input pin not driven by the circuit must be wired to VCC or GND. Floating CMOS inputs drift unpredictably and can cause oscillation, excess supply current, or random behaviour. If your design has unused gates on a multi-gate chip, ground their inputs explicitly with a jumper.
- **Power-rail continuity.** Some 830-pin breadboards split each power rail into two segments at the middle of the board, with a visible break in the colored stripe. If your circuit uses the full rail length, bridge the gap with a jumper before powering on.

### Per-component

- **Three coin cells stacked in series carry 9 V at hundreds of milliamps short-circuit current.** A dropped paperclip across the stack will weld itself to the cells, ignite, and start a fire. Install the batteries last, after the rest of the circuit is built and the switch jumper is *not* installed.
- **CR2032 cells are non-rechargeable.** Don't try to charge them — they vent and can rupture. If a cell gets warm during use, remove it immediately and dispose of it at a battery-recycling drop-off (most hardware stores have one).
- **Polarity is counter-intuitive on coin cells.** The flat side with the engraved markings (`CR2032`, `+`, manufacturer logo) is the **positive** terminal. The smooth metal cup on the back is **negative**. Most coin-cell holders are marked with `+` on the contact that touches the flat marked face. Always verify with a multimeter on a known-good cell before powering up.
- **Series cells need to match.** Use three fresh cells from the same package. Mixing a fresh cell with two depleted ones makes the depleted ones charge in reverse, which is unsafe for primary cells.
- **Electrolytic capacitors have a + and − end — always check which is which.** The longer lead is + (positive); the can has a stripe along the side near the − (negative) lead. Install one backwards and it heats up, vents boiling electrolyte, and sometimes pops loudly — this is the main reason 'always wear safety glasses' is a bench rule. Ceramic and film capacitors are not polarised and go in either way.
- **Always use a capacitor rated well above the voltage it will actually see.** Rule of thumb: pick a part rated for at least 1.5 times the highest steady-state voltage in your circuit. A 16 V cap on a 12 V rail will die early as the supply rings or sags; a 25 V cap shrugs the same conditions off. (The rated voltage is the *working* maximum, not a nominal indicator.)
- **Different capacitor types do different jobs — match the type to the role.** Big electrolytics (microfarads) sit on supply rails as bulk reservoirs; small ceramics (10–100 nF) go right next to chip supply pins as local decouplers; film and polypropylene caps handle precision timing where drift matters. Putting an electrolytic where a ceramic belongs (and vice versa) is the single most common 'why does this circuit oscillate?' bench mistake.
- **The black band marks the cathode (− end)** — same convention as silicon diodes. The Schottky's marking matches the bar in the schematic symbol.
- **Use the 1N5817 wherever you'd use a 1N4001 but need lower voltage drop or faster switching.** Schottkys drop only ~0.3 V in forward bias (versus ~0.7 V for a silicon diode), so a switching-supply rectifier or a battery-OR diode loses less power as heat. The trade-off: Schottkys leak a small reverse current even when 'off' — over weeks they slowly drain the lower of two OR'd batteries, so don't use them for long-term battery backup arrangements.
- **This part only blocks 20 V reverse — don't use it where voltages exceed that.** A mains-rectifier transformer secondary, a 24 V motor flyback path, or anywhere ringing transients might exceed 20 V will pop the 1N5817. The 1N5819 (same package, 40 V reverse) handles more; above that, use a silicon diode like the 1N4007 instead.
- **LEDs have a + and − end — the long lead is +.** Get them the wrong way around and the LED simply doesn't light up; there's no spark or smoke, just a dark LED. If someone has already trimmed the leads, look at the rim of the plastic body: the flat spot marks the − (cathode) side. Both leads are valid wires as far as the framework is concerned, so it can't catch this mistake for you.
- **Always put a resistor in series with an LED — never connect an LED directly across a supply.** Without a resistor the LED draws too much current and burns out in a literal flash. 330 Ω works fine for most LEDs on a 5 V supply. (The formula, if you care: R = (V_supply − V_F) / I_target; 330 Ω drives about 10 mA through a typical red LED at 5 V, which is bright but not stressed.)
- **Put a capacitor on each side of the regulator, close to its pins.** A 0.33 µF capacitor from input (pin 1) to ground, and a 0.1 µF from output (pin 3) to ground, with the leads under 5 mm long. Skip these and the 7805 misbehaves — it can oscillate (audible whine, ringing on a scope) or overshoot when the load changes suddenly. This step seems optional but isn't.
- **Feed the input at least 7 V — anything lower and the output drops with it.** The 7805 needs about 2 V of headroom between input and output to hold regulation. A 9 V battery slowly sagging under load eventually crosses that line and the regulator's output sags too. For battery-powered work, use an LDO regulator (LP2950, AMS1117-5.0) — they only need a few hundred millivolts of headroom.
- **Add a heatsink whenever the load draws more than ~250 mA.** Whatever voltage the regulator is dropping (input minus 5 V) becomes heat — a 12 V input dropping to 5 V at 500 mA dissipates 3.5 W, enough to thermal-shutdown the chip in seconds without a heatsink. If the heat is more than a watt or two, switch to a switching regulator instead.
- **The TO-220's metal tab is internally tied to ground** (pin 2). That makes mounting easy — you can bolt it straight to a grounded heatsink without an insulator. The flip side: the tab and pin 2 are the same node, so don't mount the tab to anything that isn't at ground potential.
