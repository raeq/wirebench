# Build Guide: WaterAlarm

Water level alarm.

## Safety first

- **Put on safety glasses before powering anything up.** Electrolytic capacitors can vent boiling electrolyte if reverse-installed or over-volted; battery cells can flash violently on a short; small parts under tension (springs in switches, leads under a soldering iron) launch in unexpected directions. The glasses are cheap insurance against an afternoon you'd otherwise regret.
- **Discharge static before touching chips.** Touch a grounded metal surface (the bench frame, a radiator, the case of a mains-powered tool that's plugged in but switched off) before picking up MOSFETs or CMOS logic. A static spark you can't feel — under 100 V from walking across a carpet — punches through a gate oxide silently. The part still looks fine; it just doesn't work, and you spend two hours blaming your wiring. An ESD wrist strap clipped to a grounded surface is the permanent fix.
- **Wear insulating gloves when working above ~30 V or near mains.** Standard hobby breadboard work (3.3–24 V) doesn't need them; anything reaching into a wall-wart's primary side, a charged high-voltage capacitor, or a tube-amp B+ rail does. If the design includes a transformer, a switching supply's input stage, or a Cell pack above a few volts, treat it as hot until you've personally verified it's discharged.

## Parts

| Refdes | Part | Value / Spec | Quantity | Notes |
|--------|------|--------------|----------|-------|
| D1 | LED | red, 5 mm | 1 | Longer lead is the anode (+) |
| D2 | LED | green, 5 mm | 1 | Longer lead is the anode (+) |
| R1 | Resistor | 10000 Ω | 1 | ¼ W carbon film is fine |
| R2 | Resistor | 10000 Ω | 1 | ¼ W carbon film is fine |
| U1 | ULN2003A | ULN2003A | 1 |  |
| U2 | SN74HC04 | SN74HC04 | 1 |  |
| U3 | CD4069 | CD4069 | 1 |  |
| U4 | CD4043 | CD4043 | 1 |  |

Also: a standard 830-pin solderless breadboard, an assortment of jumper wires (red for the positive rail, black for ground rail, any colour for signals), and a 5 V supply.

## Layout

Each part below is drawn the way it sits on the breadboard, with every pin labelled. Chips run left-to-right with the notch at the left; pin 1 is the top-left pin (closest to the notch). Sensors and modules are shown as a single horizontal row of pins. 2-lead passives are drawn axially with the value in line.

### D1 — LED

```
anode (+, long lead) ─▶├─ cathode (−, short lead)   [red, 5 mm]
```

### D2 — LED

```
anode (+, long lead) ─▶├─ cathode (−, short lead)   [green, 5 mm]
```

### R1 — Resistor

```
t1 ─┤▮ 10000 Ω ▮├─ t2
```

### R2 — Resistor

```
t1 ─┤▮ 10000 Ω ▮├─ t2
```

### U1 — ULN2003A

```
        1      2      3      4      5      6      7      8   
      in_1   in_2   in_3   in_4   in_5   in_6   in_7    GND  
    ┌────────────────────────────────────────────────────────┐
  U │                        ULN2003A                        │
    └────────────────────────────────────────────────────────┘
      out_1  out_2  out_3  out_4  out_5  out_6  out_7    —   
       16     15     14     13     12     11     10      9   
```

### U2 — SN74HC04

```
       1    2    3    4    5    6    7  
      a_1  y_1  a_2  y_2  a_3  y_3  GND 
    ┌───────────────────────────────────┐
  U │              SN74HC04             │
    └───────────────────────────────────┘
      VCC  a_6  y_6  a_5  y_5  a_4  y_4 
      14   13   12   11   10    9    8  
```

### U3 — CD4069

```
       1    2    3    4    5    6    7  
      a_1  y_1  a_2  y_2  a_3  y_3  VSS 
    ┌───────────────────────────────────┐
  U │               CD4069              │
    └───────────────────────────────────┘
      VDD  a_6  y_6  a_5  y_5  a_4  y_4 
      14   13   12   11   10    9    8  
```

### U4 — CD4043

```
       1    2    3    4    5    6    7    8  
      q_1  r_1  s_1  q_2  s_2  r_2  oe   VSS 
    ┌────────────────────────────────────────┐
  U │                 CD4043                 │
    └────────────────────────────────────────┘
      VDD   —   q_4  r_4  s_4  q_3  s_3  r_3 
      16   15   14   13   12   11   10    9  
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
2. Plug U1 (ULN2003A, DIP-16) straddling the trough: pin 1 at 10E, pin 16 at
   10F. The chip's notch / dot marks pin 1 — make sure it lines up.
3. Plug U4 (CD4043, DIP-16) straddling the trough: pin 1 at 20E, pin 16 at
   20F. The chip's notch / dot marks pin 1 — make sure it lines up.
4. Plug U2 (SN74HC04, DIP-14) straddling the trough: pin 1 at 30E, pin 14 at
   30F. The chip's notch / dot marks pin 1 — make sure it lines up.
5. Plug U3 (CD4069, DIP-14) straddling the trough: pin 1 at 39E, pin 14 at
   39F. The chip's notch / dot marks pin 1 — make sure it lines up.
6. Plug D1 (LED): one lead at position 50 (any of 50A–50E), the other at
   position 51 (any of 51A–51E).
7. Plug D2 (LED): one lead at position 53 (any of 53A–53E), the other at
   position 54 (any of 54A–54E).
8. Plug R1 (Resistor): one lead at position 56 (any of 56A–56E), the other at
   position 59 (any of 59A–59E).
9. Plug R2 (Resistor): one lead at position 61 (any of 61A–61E), the other at
   position 64 (any of 64A–64E).
10. Run a jumper from U1 pin 8 at position 17 (any of 17A–17E) to the top `-`
   rail.
11. Run a jumper from U2 pin 7 at position 36 (any of 36A–36E) to the top `-`
   rail.
12. Run a jumper from U3 pin 7 at position 45 (any of 45A–45E) to the top `-`
   rail.
13. Run a jumper from U4 pin 8 at position 27 (any of 27A–27E) to the top `-`
   rail.
14. Run a jumper from R2 t1 to U1 pin 15 — position 61 (any of 61A–61E) to
   position 11 (any of 11F–11J).
15. Run a jumper from U1 pin 15 to U2 pin 1 — position 11 (any of 11F–11J) to
   position 30 (any of 30A–30E).
16. Run a jumper from R1 t1 to U1 pin 16 — position 56 (any of 56A–56E) to
   position 10 (any of 10F–10J).
17. Run a jumper from U1 pin 16 to U4 pin 3 — position 10 (any of 10F–10J) to
   position 22 (any of 22A–22E).
18. Run a jumper from U2 pin 2 to U4 pin 2 — position 31 (any of 31A–31E) to
   position 21 (any of 21A–21E).
19. Run a jumper from U2 pin 11 at position 33 (any of 33F–33J) to the top `-`
   rail.
20. Run a jumper from U2 pin 13 at position 31 (any of 31F–31J) to the top `-`
   rail.
21. Run a jumper from U2 pin 3 at position 32 (any of 32A–32E) to the top `-`
   rail.
22. Run a jumper from U2 pin 5 at position 34 (any of 34A–34E) to the top `-`
   rail.
23. Run a jumper from U2 pin 9 at position 35 (any of 35F–35J) to the top `-`
   rail.
24. Run a jumper from U3 pin 11 at position 42 (any of 42F–42J) to the top `-`
   rail.
25. Run a jumper from U3 pin 13 at position 40 (any of 40F–40J) to the top `-`
   rail.
26. Run a jumper from U3 pin 3 at position 41 (any of 41A–41E) to the top `-`
   rail.
27. Run a jumper from U3 pin 5 at position 43 (any of 43A–43E) to the top `-`
   rail.
28. Run a jumper from U3 pin 9 at position 44 (any of 44F–44J) to the top `-`
   rail.
29. Run a jumper from U4 pin 10 at position 26 (any of 26F–26J) to the top `-`
   rail.
30. Run a jumper from U4 pin 12 at position 24 (any of 24F–24J) to the top `-`
   rail.
31. Run a jumper from U4 pin 13 at position 23 (any of 23F–23J) to the top `-`
   rail.
32. Run a jumper from U4 pin 5 at position 24 (any of 24A–24E) to the top `-`
   rail.
33. Run a jumper from U4 pin 6 at position 25 (any of 25A–25E) to the top `-`
   rail.
34. Run a jumper from U4 pin 9 at position 27 (any of 27F–27J) to the top `-`
   rail.
35. Run a jumper from U2 pin 14 at position 30 (any of 30F–30J) to the top `+`
   rail.
36. Run a jumper from U3 pin 14 at position 39 (any of 39F–39J) to the top `+`
   rail.
37. Run a jumper from U4 pin 16 at position 20 (any of 20F–20J) to the top `+`
   rail.
38. Run a jumper from D1 anode to U3 pin 1 — position 50 (any of 50A–50E) to
   position 39 (any of 39A–39E).
39. Run a jumper from U3 pin 1 to U4 pin 1 — position 39 (any of 39A–39E) to
   position 20 (any of 20A–20E).
40. Run a jumper from D2 anode to U3 pin 2 — position 53 (any of 53A–53E) to
   position 40 (any of 40A–40E).
41. Run a jumper from R1 t2 at position 59 (any of 59A–59E) to the top `+`
   rail.
42. Run a jumper from R2 t2 at position 64 (any of 64A–64E) to the top `+`
   rail.
43. Run a jumper from U4 pin 7 at position 26 (any of 26A–26E) to the top `+`
   rail.
44. Verify nothing is shorted by inspecting the rails with a multimeter
   (continuity beep between `+` and `-` means trouble). Then connect the
   supply and observe.

## Notes & Gotchas

### General

- **Double-check the supply voltage before powering up.** Most TTL / CMOS logic survives 3.3 V – 5.5 V; an accidental 12 V from a bench supply destroys every chip on the board in microseconds. Set the supply, measure it with a multimeter, and only then connect.
- **Resistor wattage matters.** Standard ¼-W carbon-film resistors are fine below ~60 V across the part. Power resistors (½ W, 1 W) are needed for current-sense or load-dump positions; the BOM lists value only, not wattage — confirm against the schematic's expected current.
- **Tie unused CMOS inputs.** Any input pin not driven by the circuit must be wired to VCC or GND. Floating CMOS inputs drift unpredictably and can cause oscillation, excess supply current, or random behaviour. If your design has unused gates on a multi-gate chip, ground their inputs explicitly with a jumper.
- **Power-rail continuity.** Some 830-pin breadboards split each power rail into two segments at the middle of the board, with a visible break in the colored stripe. If your circuit uses the full rail length, bridge the gap with a jumper before powering on.

### Per-component

- **Jumper pin 5 (OE) to Vdd or the outputs do nothing.** OE is the Output Enable — when it's not pulled HIGH, all four latch outputs sit in high-impedance and the chip looks dead even though it's working internally. This is a one-second fix that wastes an evening if you miss it: a jumper from pin 5 to the + rail.
- **Ground the inputs of every latch you're not using.** Each latch has its own S (Set) and R (Reset) pin; for any latch you don't plan to use, tie both pins to ground. Floating CMOS inputs drift through their threshold and the noise can couple into neighbouring latches through the chip's silicon, occasionally flipping outputs you *are* using.
- **The /Q (NOT-Q) outputs aren't brought out to package pins.** The silicon has them internally, but the chip only exposes the four Q outputs. If your design needs the inverted signal, send Q through a separate inverter gate — a spare gate of a 74HC04 or CD4069 is the cheapest fix; software inversion downstream of the chip is the simplest if a microcontroller is reading the output.
- **Every input pin must connect somewhere — Vdd or ground, but never floating.** If you only use two of the six inverter gates, jumper the unused inputs straight to ground. A floating CMOS input misbehaves in odd ways: the chip can oscillate, draw extra supply current, and behave differently when you wave your hand near the board. (Technically the input high-impedance node drifts through the threshold; the output stage spends time in its linear region and radiates noise into the supply rail.)
- **This chip's gates make weak digital edges — that's by design.** The 'UB' in the part number means *unbuffered*: each gate is one transistor stage instead of three. If you need crisp digital outputs (a clock for another chip, a clean trigger), use a 74HC04 instead. The CD4069's weakness is actually its party trick — biased into the in-between region with feedback resistors, each gate becomes a small linear amplifier; that's how you build crystal oscillators and Schmitt-trigger-like circuits out of CMOS inverters.
- **LEDs have a + and − end — the long lead is +.** Get them the wrong way around and the LED simply doesn't light up; there's no spark or smoke, just a dark LED. If someone has already trimmed the leads, look at the rim of the plastic body: the flat spot marks the − (cathode) side. Both leads are valid wires as far as the framework is concerned, so it can't catch this mistake for you.
- **Always put a resistor in series with an LED — never connect an LED directly across a supply.** Without a resistor the LED draws too much current and burns out in a literal flash. 330 Ω works fine for most LEDs on a 5 V supply. (The formula, if you care: R = (V_supply − V_F) / I_target; 330 Ω drives about 10 mA through a typical red LED at 5 V, which is bright but not stressed.)
- **Jumper every unused input to Vcc or ground.** This is a CMOS family chip just like the 4xxx parts; floating inputs misbehave the same way (random oscillation, extra supply current, hand-wave-sensitive behaviour). If you only use one of the six inverters, ground the other five inputs.
- **Put a 100 nF decoupling capacitor right at the supply pin.** From pin 14 (Vcc) to pin 7 (GND), with the cap's leads under 5 mm long — close enough that you'd call it 'touching the chip'. This is the most-skipped step in CMOS hobby work, and the most common cause of 'sometimes it works, sometimes it doesn't' bugs. The chip's switching currents create supply ringing inside the package itself; the cap has to be millimetres away to suppress it. A cap on the other side of the breadboard does nothing.
- **Don't drive 5 V logic with a 3.3 V signal — at least not this family.** The HC variant has CMOS-style input thresholds (around half the supply, so ~2.5 V on a 5 V rail). A 3.3 V HIGH from an ESP32 or RPi might or might not register as HIGH depending on temperature and chip tolerance. Use a 74HCT04 instead (TTL-style ~1.4 V threshold, recognises 3.3 V cleanly) or insert a level-shifter chip between the two voltage domains.
- **Wire your load between the + rail and the output pin — not between the output pin and ground.** The ULN2003A *sinks* current to ground; it doesn't *source* current from a rail. Put your relay / motor / coil with one end on V+, the other end on the chip's output, and the chip pulls the output LOW to energise the load. Wiring it the way you'd wire a transistor to drive HIGH is the most common 'why is nothing happening?' mistake with this part.
- **Pin 9 (COMMON) goes to the load supply, not to logic Vcc.** If you're driving 12 V relays, pin 9 connects to the 12 V rail. The chip has built-in freewheel diodes (the things that catch the voltage spike when a relay turns off) and pin 9 is where their cathodes meet. Without pin 9 tied to the load supply, every switch-off pulse punches straight through the chip and eventually kills a channel.
- **Keep the ground wire from pin 8 short.** With seven channels each sinking up to 500 mA at once, this one ground pin can carry several amps in a tight switching loop. A long ground wire on a breadboard introduces enough inductance that the chip's internal reference shifts relative to system ground, and channels can start switching when you didn't ask them to. Run pin 8's wire directly to the rail, no detours.
