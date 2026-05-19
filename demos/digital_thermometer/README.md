# digital_thermometer

An ATmega328P-based digital thermometer with a four-digit seven-segment display: the firmware reads a DHT11 temperature/humidity module on one GPIO and multiplexes the temperature across the display's four common-cathode digits. The Arduino sketch is modelled as a `Sketch` cell on the ATmega — the framework treats the firmware as a logical-cell inside the chip, so the display, the DHT11, and the firmware all participate in the same evaluation graph.

## What this design is protected from

The framework refused these specific mistakes during this design's development. Each snippet is a near-miss — paste the broken lines into your own copy of the design and wirebench raises before the design can run, either at construction or at the first `evaluate()`.

### A board that doesn't power up — DHT11 ground forgotten

```python
# In DigitalThermometer.__init__, drop the DHT11's GND wire — easy
# typo when you've already wired VCC and DATA and the GND looks like
# "the breadboard's GND rail, I'll get to it":
wire(self.vcc_a.out, self.dht11.VCC)
# missing: wire(self.gnd_a.out, self.dht11.GND)
wire(self.dht11.DATA, self.arduino.PD2)

# When the assembly-guide ERC runs:
export_to_string(DigitalThermometer(), 'assembly_guide')
# BreadboardIncompatibleError: Chips have unwired supply pins — the assembled circuit won't power up.
#   - U2 pin 3 (GND) [ground] — wire to the − rail
```

The DHT11_Module declares its `GND` pin as `PinFunction.GROUND` and `Direction.IN`; the assembly-guide ERC's `_make_rail_predicate` walks every Chip's ground pin and requires a path to a `−` rail. The bench equivalent is plugging in the module, applying power, and seeing the display flicker but report nonsense — the DHT11 isn't grounded and its data line drifts. Hours of "is the firmware reading the wrong pin?" before someone spots the missing jumper.

### Two rails shorted

```python
# In DigitalThermometer.__init__, a tempting consolidation:  the
# digital ground (self.gnd) and the analog ground (self.gnd_a) go to
# the same breadboard − rail anyway, so why not just merge them?
wire(self.gnd.out, self.gnd_a.out)

DigitalThermometer()
# ShortCircuitError: wire() has multiple drivers ('out', 'out') — short circuit
```

The design declares two GND `Rail`s — `self.gnd` (`Digital`) for the SN74-family tie-offs, and `self.gnd_a` (`Analog`) for the DHT11's supply pins. Each Rail has a single `out` port at `Direction.OUT`, and tying two `OUT`s together puts two drivers on one net. The framework keeps the digital and analog rails distinct because their `signal_type` differs; merging them is a category error the framework catches before it can be soldered. The bench equivalent is two bench-supply outputs accidentally bonded — whichever supply's regulator is weaker shuts down first.

## Running it

```bash
python demos/digital_thermometer/digital_thermometer.py
```

## What comes out

The `docs/` folder beside this README has the design's pre-generated exports. The composed `DigitalThermometer` gets its own set, and the `Uno_ThermometerSketch` (the Arduino-as-chip subassembly) gets a separate set so the firmware's surface is documented as a netlist component:

- [`DigitalThermometer.bom.csv`](docs/DigitalThermometer.bom.csv), [`DigitalThermometer.svg`](docs/DigitalThermometer.svg), [`DigitalThermometer.breadboard.svg`](docs/DigitalThermometer.breadboard.svg), [`DigitalThermometer.md`](docs/DigitalThermometer.md), [`DigitalThermometer.net`](docs/DigitalThermometer.net), [`DigitalThermometer.kicad_sch`](docs/DigitalThermometer.kicad_sch), [`DigitalThermometer.cir`](docs/DigitalThermometer.cir), [`DigitalThermometer.dot`](docs/DigitalThermometer.dot), [`DigitalThermometer.mmd`](docs/DigitalThermometer.mmd), [`DigitalThermometer.yosys.json`](docs/DigitalThermometer.yosys.json), [`DigitalThermometer.net-report.md`](docs/DigitalThermometer.net-report.md), [`DigitalThermometer.domain-report.md`](docs/DigitalThermometer.domain-report.md), [`DigitalThermometer.interface-report.md`](docs/DigitalThermometer.interface-report.md) — the assembly
- [`Uno_ThermometerSketch.bom.csv`](docs/Uno_ThermometerSketch.bom.csv), [`Uno_ThermometerSketch.svg`](docs/Uno_ThermometerSketch.svg), [`Uno_ThermometerSketch.breadboard.svg`](docs/Uno_ThermometerSketch.breadboard.svg), [`Uno_ThermometerSketch.md`](docs/Uno_ThermometerSketch.md), [`Uno_ThermometerSketch.net`](docs/Uno_ThermometerSketch.net), [`Uno_ThermometerSketch.kicad_sch`](docs/Uno_ThermometerSketch.kicad_sch), [`Uno_ThermometerSketch.cir`](docs/Uno_ThermometerSketch.cir), [`Uno_ThermometerSketch.dot`](docs/Uno_ThermometerSketch.dot), [`Uno_ThermometerSketch.mmd`](docs/Uno_ThermometerSketch.mmd), [`Uno_ThermometerSketch.yosys.json`](docs/Uno_ThermometerSketch.yosys.json), [`Uno_ThermometerSketch.net-report.md`](docs/Uno_ThermometerSketch.net-report.md), [`Uno_ThermometerSketch.domain-report.md`](docs/Uno_ThermometerSketch.domain-report.md), [`Uno_ThermometerSketch.interface-report.md`](docs/Uno_ThermometerSketch.interface-report.md) — the Arduino subassembly

## Going further

- The source: [`digital_thermometer.py`](digital_thermometer.py)
- The full ordered list of all twelve demos: [`../../docs/learning-path.md`](../../docs/learning-path.md)
