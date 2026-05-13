# Build Guide: Uno_ThermometerSketch

ATmega328P loaded with the digital-thermometer firmware.

## Safety first

- **Put on safety glasses before powering anything up.** Electrolytic capacitors can vent boiling electrolyte if reverse-installed or over-volted; battery cells can flash violently on a short; small parts under tension (springs in switches, leads under a soldering iron) launch in unexpected directions. The glasses are cheap insurance against an afternoon you'd otherwise regret.
- **Discharge static before touching chips.** Touch a grounded metal surface (the bench frame, a radiator, the case of a mains-powered tool that's plugged in but switched off) before picking up MOSFETs or CMOS logic. A static spark you can't feel — under 100 V from walking across a carpet — punches through a gate oxide silently. The part still looks fine; it just doesn't work, and you spend two hours blaming your wiring. An ESD wrist strap clipped to a grounded surface is the permanent fix.
- **Wear insulating gloves when working above ~30 V or near mains.** Standard hobby breadboard work (3.3–24 V) doesn't need them; anything reaching into a wall-wart's primary side, a charged high-voltage capacitor, or a tube-amp B+ rail does. If the design includes a transformer, a switching supply's input stage, or a Cell pack above a few volts, treat it as hot until you've personally verified it's discharged.

## Parts

| Refdes | Part | Value / Spec | Quantity | Notes |
|--------|------|--------------|----------|-------|
| U1 | Uno_ThermometerSketch | Uno_ThermometerSketch | 1 |  |

Also: a standard 830-pin solderless breadboard, an assortment of jumper wires (red for the positive rail, black for ground rail, any colour for signals), and a 5 V supply.

## How to verify

Before you start wiring, take five minutes to confirm each part actually works. A multimeter on the diode-test and resistance settings catches most pre-install failures: dead LEDs, mis-bagged parts, transistors damaged in shipping, batteries below their safe-discharge limit. The checks below cover what you can verify with a basic multimeter; chips and complex modules generally need a working test rig instead, so they're not listed here.

*(No standalone bench checks declared for the parts in this design — proceed directly to assembly and watch for trouble during the first power-up.)*


## Method

1. Orient the breadboard with its long axis horizontal and the trough running
   left-to-right through the middle. Connect your 5 V supply: the positive
   lead to the top `+` rail (positive rail), the negative lead to the top `-`
   rail (ground rail).
2. Plug U1 (Uno_ThermometerSketch, DIP-28) straddling the trough: pin 1 at
   10E, pin 28 at 10F. The chip's notch / dot marks pin 1 — make sure it lines
   up.
3. Verify nothing is shorted by inspecting the rails with a multimeter
   (continuity beep between `+` and `-` means trouble). Then connect the
   supply and observe.

## Notes & Gotchas

### General

- **Double-check the supply voltage before powering up.** Most TTL / CMOS logic survives 3.3 V – 5.5 V; an accidental 12 V from a bench supply destroys every chip on the board in microseconds. Set the supply, measure it with a multimeter, and only then connect.
- **Resistor wattage matters.** Standard ¼-W carbon-film resistors are fine below ~60 V across the part. Power resistors (½ W, 1 W) are needed for current-sense or load-dump positions; the BOM lists value only, not wattage — confirm against the schematic's expected current.
- **Tie unused CMOS inputs.** Any input pin not driven by the circuit must be wired to VCC or GND. Floating CMOS inputs drift unpredictably and can cause oscillation, excess supply current, or random behaviour. If your design has unused gates on a multi-gate chip, ground their inputs explicitly with a jumper.
- **Power-rail continuity.** Some 830-pin breadboards split each power rail into two segments at the middle of the board, with a visible break in the colored stripe. If your circuit uses the full rail length, bridge the gap with a jumper before powering on.

### Per-component

- **Put a 100 nF capacitor at each supply pin, leads under 5 mm long.** The ATmega328P has two supply pins (VCC and AVCC, the analogue Vcc) and each needs its own cap to ground. Without these caps the chip glitches under load and ADC readings drift. For clean ADC readings, also wire AVCC to VCC through a small ferrite bead or 10 Ω resistor, with a 10 µF cap on the AVCC side — this isolates the analogue supply from digital switching noise.
- **Add a 10 kΩ resistor from RESET (pin 1) to the + rail.** Without that pull-up, RESET drifts LOW and the chip resets itself in a loop. Add a 100 nF cap from RESET to ground too — it makes RESET noise-immune, and Arduino-style serial bootloaders also use that cap to auto-reset the board for uploads.
- **Don't try to use PC6 (pin 1) as a normal I/O pin** unless you have a high-voltage programmer (HVPP). PC6 doubles as the RESET pin; freeing it as I/O requires setting the RSTDISBL fuse, which permanently disables the standard ISP programming interface. If you ever need to update the firmware after that, your only path is HVPP — which most hobbyists don't have. Hardly worth it for one extra I/O pin.
- **'Fuse' settings persist across power cycles and aren't visible in your program.** They're a separate set of configuration bytes that control things like clock source, brown-out detection, and bootloader behaviour. New chips ship configured for the internal 8 MHz oscillator divided by 8 (so 1 MHz effective) — if you wired an external crystal but didn't update the CKSEL fuses, your code still runs from the internal oscillator and timing is wrong. Worse: setting CKSEL to 'external crystal' without one actually wired up bricks the chip until you apply an external clock via HVPP.
