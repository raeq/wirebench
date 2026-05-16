# Build Guide: HelloLED

A single LED with a current-limit resistor across the supply rails.

## Safety first

- **Put on safety glasses before powering anything up.** Electrolytic capacitors can vent boiling electrolyte if reverse-installed or over-volted; battery cells can flash violently on a short; small parts under tension (springs in switches, leads under a soldering iron) launch in unexpected directions. The glasses are cheap insurance against an afternoon you'd otherwise regret.
- **Discharge static before touching chips.** Touch a grounded metal surface (the bench frame, a radiator, the case of a mains-powered tool that's plugged in but switched off) before picking up MOSFETs or CMOS logic. A static spark you can't feel — under 100 V from walking across a carpet — punches through a gate oxide silently. The part still looks fine; it just doesn't work, and you spend two hours blaming your wiring. An ESD wrist strap clipped to a grounded surface is the permanent fix.
- **Wear insulating gloves when working above ~30 V or near mains.** Standard hobby breadboard work (3.3–24 V) doesn't need them; anything reaching into a wall-wart's primary side, a charged high-voltage capacitor, or a tube-amp B+ rail does. If the design includes a transformer, a switching supply's input stage, or a Cell pack above a few volts, treat it as hot until you've personally verified it's discharged.

## Parts

| Refdes | Part | Value / Spec | Quantity | Notes |
|--------|------|--------------|----------|-------|
| D1 | LED | red, 5 mm | 1 | Longer lead is the anode (+) |
| R1 | Resistor | 330 Ω | 1 | ¼ W carbon film is fine |

Also: a standard 830-pin solderless breadboard, an assortment of jumper wires (red for the positive rail, black for ground rail, any colour for signals), and a 5 V supply.

## Layout

Each part below is drawn the way it sits on the breadboard, with every pin labelled. Chips run left-to-right with the notch at the left; pin 1 is the top-left pin (closest to the notch). Sensors and modules are shown as a single horizontal row of pins. 2-lead passives are drawn axially with the value in line.

### D1 — LED

```
anode (+, long lead) ─▶├─ cathode (−, short lead)   [red, 5 mm]
```

### R1 — Resistor

```
t1 ─┤▮ 330 Ω ▮├─ t2
```


## How to verify

Before you start wiring, take five minutes to confirm each part actually works. A multimeter on the diode-test and resistance settings catches most pre-install failures: dead LEDs, mis-bagged parts, transistors damaged in shipping, batteries below their safe-discharge limit. The checks below cover what you can verify with a basic multimeter; chips and complex modules generally need a working test rig instead, so they're not listed here.

- **Set your multimeter to diode-test mode and probe the LED's leads.** Put the red probe on the long lead (anode +) and the black probe on the short lead (cathode −). A healthy LED lights up dimly — the meter is forcing a tiny current through it — and the reading shows the forward voltage (around 1.8 V for red, 2 V for yellow, 3.2 V for blue/white). Reverse the probes and the LED should stay dark with the meter reading OL. If both directions show OL the LED is open / dead; if both directions light the LED it has failed as a short. This also tells you which lead is the anode, useful if the leads were trimmed.
- **Measure the resistance with your multimeter before installing.** Set the meter to the Ω (ohms) range, probe one lead, then the other; the reading should match the value printed on the part (or decoded from its colour bands) to within a few percent. A reading of OL (open / infinity) means the resistor is broken inside; a value wildly different from what's marked usually means someone has swapped parts in the bin and you've grabbed the wrong one.


## Method

1. Orient the breadboard with its long axis horizontal and the trough running
   left-to-right through the middle. Connect your 5 V supply: the positive
   lead to the top `+` rail (positive rail), the negative lead to the top `-`
   rail (ground rail).
2. Plug R1 (Resistor): one lead at position 12 (any of 12A–12E), the other at
   position 15 (any of 15A–15E).
3. Plug D1 (LED): one lead at position 17 (any of 17A–17E), the other at
   position 18 (any of 18A–18E).
4. Run a jumper from D1 anode to R1 t2 — position 17 (any of 17A–17E) to
   position 15 (any of 15A–15E).
5. Run a jumper from D1 cathode at position 18 (any of 18A–18E) to the top `-`
   rail.
6. Run a jumper from R1 t1 at position 12 (any of 12A–12E) to the top `+`
   rail.
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

- **LEDs have a + and − end — the long lead is +.** Get them the wrong way around and the LED simply doesn't light up; there's no spark or smoke, just a dark LED. If someone has already trimmed the leads, look at the rim of the plastic body: the flat spot marks the − (cathode) side. Both leads are valid wires as far as the framework is concerned, so it can't catch this mistake for you.
- **Always put a resistor in series with an LED — never connect an LED directly across a supply.** Without a resistor the LED draws too much current and burns out in a literal flash. 330 Ω works fine for most LEDs on a 5 V supply. (The formula, if you care: R = (V_supply − V_F) / I_target; 330 Ω drives about 10 mA through a typical red LED at 5 V, which is bright but not stressed.)
