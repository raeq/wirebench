# Build Guide: DigitalThermometer

Single-board digital thermometer.

## Ingredients

| Refdes | Part | Value / Spec | Quantity | Notes |
|--------|------|--------------|----------|-------|
| R1 | Resistor | 220 Ω | 1 | ¼ W carbon film is fine |
| U1 | Uno_ThermometerSketch | Uno_ThermometerSketch | 1 |  |
| U2 | DHT11 | DHT11 | 1 |  |
| U3 | Display5641AS | Display5641AS | 1 |  |

Also: a standard 830-pin solderless breadboard, an assortment of jumper wires (red for the positive rail, black for ground rail, any colour for signals), and a 5 V supply.

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
6. Run a jumper from position 14 (any of 14A–14E) to position 26 (any of
   26F–26J).
7. Run a jumper from position 26 (any of 26F–26J) to position 40 (any of
   40A–40E).
8. Run a jumper from position 40 (any of 40A–40E) to position 43 (any of
   43A–43E).
9. Run a jumper from position 31 (any of 31A–31E) to the top `-` rail.
10. Run a jumper from position 23 (any of 23A–23E) to position 29 (any of
   29A–29E).
11. Run a jumper from position 23 (any of 23F–23J) to position 27 (any of
   27A–27E).
12. Run a jumper from position 22 (any of 22F–22J) to position 26 (any of
   26A–26E).
13. Run a jumper from position 21 (any of 21F–21J) to position 28 (any of
   28F–28J).
14. Run a jumper from position 20 (any of 20F–20J) to position 30 (any of
   30A–30E).
15. Run a jumper from position 19 (any of 19F–19J) to position 28 (any of
   28A–28E).
16. Run a jumper from position 13 (any of 13A–13E) to position 35 (any of
   35A–35E).
17. Run a jumper from position 15 (any of 15A–15E) to position 29 (any of
   29F–29J).
18. Run a jumper from position 20 (any of 20A–20E) to position 30 (any of
   30F–30J).
19. Run a jumper from position 21 (any of 21A–21E) to position 27 (any of
   27F–27J).
20. Run a jumper from position 22 (any of 22A–22E) to position 31 (any of
   31F–31J).
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

- **Don't poll faster than once per second.** The DHT11's internal sample rate is ~1 Hz; reading more often returns stale data and stresses the sensor's self-heating budget (which already biases the temperature reading by ~1°C). Schedule reads on a 1-second timer, not in your main loop.
- **Accuracy is mediocre by design.** ±2°C and ±5% RH are typical; the chip is a teaching-grade humidity sensor, not an instrument. For real measurement use a SHT3x / BME280 — double the cost, ten times the accuracy.
- **One-wire protocol is bit-banged with tight timing.** Many Arduino libraries disable interrupts during reads (~25 ms). If you're running PWM, software-serial, or an OS, the DHT11 read can corrupt other timing-sensitive operations.
- **4-pin TO-92-ish package: V+, DATA, NC, GND** from the screen side (the side with the metal grille). The NC pin really is no-connect; some tutorials show a pull-up resistor on it — that's wrong, the pull-up goes on DATA.
- **Common-cathode**: each digit's cathode goes low to enable that digit; segments are driven HIGH. The common-anode variant (5641AH) has the opposite polarity — wiring code written for one type into the other lights all the wrong digits.
- **Each segment needs its own current-limit resistor.** ~330 Ω per segment at 5 V drives ~10 mA, which is plenty bright. Don't share one resistor across multiple segments — when only one segment is on it gets full current; when seven are on each gets a seventh, and brightness changes with digit content.
- **Multiplex one digit at a time.** With four digits sharing seven segment wires, the firmware enables digit 0 → drives its pattern → 1 ms later enables digit 1 → drives *its* pattern → and so on. Persistence of vision fuses the four frames into one image. Refresh below ~50 Hz visibly flickers; above ~200 Hz needs careful PWM-vs-multiplex timing.
- **Drive currents add up.** During digit-on time, seven segments × 10 mA = 70 mA flows through the digit's cathode pin and back through the MCU. If your MCU pin is rated 20 mA absolute-max, use a transistor (NPN to ground for common-cathode) — not a direct MCU connection.
- **Decouple every Vcc pin separately.** The ATmega328P has VCC and AVCC (analogue Vcc) — both need a 100 nF cap to their respective ground pin, leads under 5 mm. AVCC should be tied to VCC through a ferrite bead or 10 Ω resistor with its own 100 nF + 10 µF on the chip side; without that, ADC readings pick up digital switching noise.
- **RESET pin must be pulled high.** A 10 kΩ pull-up from RESET (pin 1) to Vcc is mandatory — floating RESET drifts low and the chip cycles. Add a 100 nF cap from RESET to ground for noise immunity (an auto-reset arrangement for serial bootloaders also uses this capacitor).
- **Fuse settings persist across power cycles** and aren't visible in the program. The chip ships with the internal 8 MHz RC oscillator divided by 8 (so 1 MHz effective). If you wired an external crystal but forgot to update CKSEL fuses, the chip still runs from the internal oscillator and your timing is wrong. Worse: setting CKSEL to external crystal without one wired up bricks the chip until you apply an external clock via HVPP.
- **Don't drive RESET as an I/O.** PC6 doubles as the RESET pin but using it for I/O requires setting the RSTDISBL fuse — which disables ISP programming permanently. Only do this with HVPP available as a recovery path.
