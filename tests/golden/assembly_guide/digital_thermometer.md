# Build Guide: DigitalThermometer

Single-board digital thermometer.

## Safety first

- **Put on safety glasses before powering anything up.** Electrolytic capacitors can vent boiling electrolyte if reverse-installed or over-volted; battery cells can flash violently on a short; small parts under tension (springs in switches, leads under a soldering iron) launch in unexpected directions. The glasses are cheap insurance against an afternoon you'd otherwise regret.
- **Discharge static before touching chips.** Touch a grounded metal surface (the bench frame, a radiator, the case of a mains-powered tool that's plugged in but switched off) before picking up MOSFETs or CMOS logic. A static spark you can't feel — under 100 V from walking across a carpet — punches through a gate oxide silently. The part still looks fine; it just doesn't work, and you spend two hours blaming your wiring. An ESD wrist strap clipped to a grounded surface is the permanent fix.
- **Wear insulating gloves when working above ~30 V or near mains.** Standard hobby breadboard work (3.3–24 V) doesn't need them; anything reaching into a wall-wart's primary side, a charged high-voltage capacitor, or a tube-amp B+ rail does. If the design includes a transformer, a switching supply's input stage, or a Cell pack above a few volts, treat it as hot until you've personally verified it's discharged.

## Parts

| Refdes | Part | Value / Spec | Quantity | Notes |
|--------|------|--------------|----------|-------|
| R1 | Resistor | 220 Ω | 1 | ¼ W carbon film is fine |
| U1 | Uno_ThermometerSketch | Uno_ThermometerSketch | 1 |  |
| U2 | DHT11 | DHT11 | 1 |  |
| U3 | Display5641AS | Display5641AS | 1 |  |

Also: a standard 830-pin solderless breadboard, an assortment of jumper wires (red for the positive rail, black for ground rail, any colour for signals), and a 5 V supply.

## How to verify

Before you start wiring, take five minutes to confirm each part actually works. A multimeter on the diode-test and resistance settings catches most pre-install failures: dead LEDs, mis-bagged parts, transistors damaged in shipping, batteries below their safe-discharge limit. The checks below cover what you can verify with a basic multimeter; chips and complex modules generally need a working test rig instead, so they're not listed here.

- **Measure the resistance with your multimeter before installing.** Set the meter to the Ω (ohms) range, probe one lead, then the other; the reading should match the value printed on the part (or decoded from its colour bands) to within a few percent. A reading of OL (open / infinity) means the resistor is broken inside; a value wildly different from what's marked usually means someone has swapped parts in the bin and you've grabbed the wrong one.


## Method

1. Orient the breadboard with its long axis horizontal and the trough running
   left-to-right through the middle. Connect your 5 V supply: the positive
   lead to the top `+` rail (positive rail), the negative lead to the top `-`
   rail (ground rail).
2. Plug U1 (Uno_ThermometerSketch, DIP-28) straddling the trough: pin 1 at
   10E, pin 28 at 10F. The chip's notch / dot marks pin 1 — make sure it lines
   up.
3. Plug U3 (Display5641AS, DIP-12) straddling the trough: pin 1 at 26E, pin 12
   at 26F. The chip's notch / dot marks pin 1 — make sure it lines up.
4. Plug U2 (DHT11, DIP-4) straddling the trough: pin 1 at 34E, pin 4 at 34F.
   The chip's notch / dot marks pin 1 — make sure it lines up.
5. Plug R1 (Resistor): one lead at position 40 (any of 40A–40E), the other at
   position 43 (any of 43A–43E).
6. Run a jumper from R1 t1 to R1 t2 — position 40 (any of 40A–40E) to position
   43 (any of 43A–43E).
7. Run a jumper from R1 t2 to U1 PD3 — position 43 (any of 43A–43E) to
   position 14 (any of 14A–14E).
8. Run a jumper from U1 PD3 to U3 DIG_1 — position 14 (any of 14A–14E) to
   position 26 (any of 26F–26J).
9. Run a jumper from U3 DIG_4 at position 31 (any of 31A–31E) to the top `-`
   rail.
10. Run a jumper from U1 PB0 to U3 SEG_C — position 23 (any of 23A–23E) to
   position 29 (any of 29A–29E).
11. Run a jumper from U1 PB1 to U3 SEG_D — position 23 (any of 23F–23J) to
   position 27 (any of 27A–27E).
12. Run a jumper from U1 PB2 to U3 SEG_E — position 22 (any of 22F–22J) to
   position 26 (any of 26A–26E).
13. Run a jumper from U1 PB3 to U3 SEG_F — position 21 (any of 21F–21J) to
   position 28 (any of 28F–28J).
14. Run a jumper from U1 PB4 to U3 SEG_G — position 20 (any of 20F–20J) to
   position 30 (any of 30A–30E).
15. Run a jumper from U1 PB5 to U3 SEG_DP — position 19 (any of 19F–19J) to
   position 28 (any of 28A–28E).
16. Run a jumper from U1 PD2 to U2 DATA — position 13 (any of 13A–13E) to
   position 35 (any of 35A–35E).
17. Run a jumper from U1 PD4 to U3 DIG_2 — position 15 (any of 15A–15E) to
   position 29 (any of 29F–29J).
18. Run a jumper from U1 PD5 to U3 DIG_3 — position 20 (any of 20A–20E) to
   position 30 (any of 30F–30J).
19. Run a jumper from U1 PD6 to U3 SEG_A — position 21 (any of 21A–21E) to
   position 27 (any of 27F–27J).
20. Run a jumper from U1 PD7 to U3 SEG_B — position 22 (any of 22A–22E) to
   position 31 (any of 31F–31J).
21. Verify nothing is shorted by inspecting the rails with a multimeter
   (continuity beep between `+` and `-` means trouble). Then connect the
   supply and observe.

## Notes & Gotchas

### General

- **Double-check the supply voltage before powering up.** Most TTL / CMOS logic survives 3.3 V – 5.5 V; an accidental 12 V from a bench supply destroys every chip on the board in microseconds. Set the supply, measure it with a multimeter, and only then connect.
- **Resistor wattage matters.** Standard ¼-W carbon-film resistors are fine below ~60 V across the part. Power resistors (½ W, 1 W) are needed for current-sense or load-dump positions; the BOM lists value only, not wattage — confirm against the schematic's expected current.
- **Tie unused CMOS inputs.** Any input pin not driven by the circuit must be wired to VCC or GND. Floating CMOS inputs drift unpredictably and can cause oscillation, excess supply current, or random behaviour. If your design has unused gates on a multi-gate chip, ground their inputs explicitly with a jumper.
- **Power-rail continuity.** Some 830-pin breadboards split each power rail into two segments at the middle of the board, with a visible break in the colored stripe. If your circuit uses the full rail length, bridge the gap with a jumper before powering on.

### Per-component

- **Read the DHT11 at most once per second.** The sensor only updates its internal reading about that often; polling faster just gives you the same number back, while heating the chip and shifting its temperature reading by ~1°C. Put the read in a one-second timer, not in your main loop.
- **This is a teaching-grade sensor, not an instrument.** Expect ±2°C and ±5% relative humidity error — fine for 'is the room hot or humid?' projects, useless for anything that needs real accuracy. If your build cares about precision (a weather station, an HVAC monitor), swap in a BME280 or SHT31; both cost about twice as much and are ten times more accurate.
- **The pin labelled NC really has nothing inside.** Looking at the side with the grille, the pins are V+, DATA, NC, GND. Some online tutorials show a pull-up resistor going to NC — that's wrong; the pull-up belongs on DATA. The NC pin should stay completely unconnected.
- **The DHT11's protocol is timing-sensitive, and the standard library reads disable interrupts for ~25 ms.** If your sketch also runs PWM, software-serial, or an interrupt-driven task, the DHT11 read can disrupt those. On RTOS-class boards (ESP32, RP2040 under MicroPython) prefer the BME280 — its I²C protocol is interrupt-friendly.
- **This is the common-cathode version: pull a digit's cathode LOW to enable it, and drive segments HIGH to light them.** If you accidentally bought the 5641AH (common-anode), the polarity is reversed and code written for one will light all the wrong digits in the other. Check the part number on the device label before wiring.
- **One current-limit resistor per segment, never one shared across segments.** Use ~330 Ω on each of the seven segment lines for a 5 V supply. Sharing a single resistor sounds frugal but the brightness changes with the digit's content — a '1' (two segments lit) glows twice as bright as a '8' (seven segments) because each segment gets half the current when shared with a partner.
- **The MCU drives one digit at a time, very quickly, and your eye fuses them into one image.** The firmware loop is: enable digit 0 → drive its segment pattern → 1 ms later enable digit 1 → drive that pattern → ... and so on, cycling through all four digits about 100 times a second. Refresh slower than ~50 Hz and you see visible flicker; faster than ~200 Hz needs care with timer interrupts.
- **The digit's common pin can sink a lot of current — too much for an MCU to handle directly.** When all seven segments are on, ~70 mA flows through one digit's cathode pin (7 × 10 mA). Most MCU pins are rated for only ~20 mA. Put an NPN transistor or a low-side MOSFET between each digit's common pin and ground, and switch *that* with the MCU; never wire a digit common straight into a logic pin.
- **Put a 100 nF capacitor at each supply pin, leads under 5 mm long.** The ATmega328P has two supply pins (VCC and AVCC, the analogue Vcc) and each needs its own cap to ground. Without these caps the chip glitches under load and ADC readings drift. For clean ADC readings, also wire AVCC to VCC through a small ferrite bead or 10 Ω resistor, with a 10 µF cap on the AVCC side — this isolates the analogue supply from digital switching noise.
- **Add a 10 kΩ resistor from RESET (pin 1) to the + rail.** Without that pull-up, RESET drifts LOW and the chip resets itself in a loop. Add a 100 nF cap from RESET to ground too — it makes RESET noise-immune, and Arduino-style serial bootloaders also use that cap to auto-reset the board for uploads.
- **Don't try to use PC6 (pin 1) as a normal I/O pin** unless you have a high-voltage programmer (HVPP). PC6 doubles as the RESET pin; freeing it as I/O requires setting the RSTDISBL fuse, which permanently disables the standard ISP programming interface. If you ever need to update the firmware after that, your only path is HVPP — which most hobbyists don't have. Hardly worth it for one extra I/O pin.
- **'Fuse' settings persist across power cycles and aren't visible in your program.** They're a separate set of configuration bytes that control things like clock source, brown-out detection, and bootloader behaviour. New chips ship configured for the internal 8 MHz oscillator divided by 8 (so 1 MHz effective) — if you wired an external crystal but didn't update the CKSEL fuses, your code still runs from the internal oscillator and timing is wrong. Worse: setting CKSEL to 'external crystal' without one actually wired up bricks the chip until you apply an external clock via HVPP.
