# Behavioural-cell audit

This table records the audit decision for every registered component
class. It is the source of truth that
`docs/behavioural-cell-audit-spec.md` calls for; the regression test in
phase 10 will cross-reference it.

**Categories** (per spec §5):

- **A** — Passive. No OUT pins or only conductor-style OUTs. No
  behavioural cell needed.
- **B** — Behavioural-cell-needed. Has OUT pins whose values are a
  function of input pins. Needs a cell.
- **C** — Application-firmware-driven. Has OUT pins driven by user
  code, not by a function of input pins. Bare class legitimately ships
  with `cells=[]`; the user injects a firmware-as-cell when needed.
  `BARE_FIRMWARE_DRIVEN = True` declared on the class (phase 8).

**Audit status**:

- **pass** — class is correctly modelled today.
- **fix-needed** — class is defective per the audit; needs work in the
  named phase.
- **deferred-Px** — known-incomplete; scheduled for phase *x*.

## Phase 1 deliverables

The Phase-1 work landed in this same commit. All linear regulators
across the catalogue (positive fixed, negative fixed, adjustable
positive, adjustable negative, LDO) now wrap a private
`LinearRegulator` cell. The 1N5817 Schottky reverted to Category A
passive; its supply-chain role is now modelled at the circuit level by
a new `SeriesRectifier(FactorNode)` cell — same pattern as the
existing `DiodeOR` cell that handles wired-OR matrices.

## Category A — passive

These classes have no OUT pins, or only OUT pins on conductor
structures (Pins acting as transparent wires). No cell needed.

| Class | Audit status | Notes |
|-------|--------------|-------|
| `Resistor` | pass | 2 BIDIR terminals; no directional behaviour |
| `Capacitor` | pass | 2 BIDIR terminals; no directional behaviour |
| `Inductor` | pass | 2 BIDIR terminals; no directional behaviour |
| `LED` | pass | 2 IN pins (anode, cathode); no driver |
| `Rail` | pass | declared OUT, but *is* the driver — not a chip-with-cells case |
| `Cell` | pass | OCV-curve cell drives `pos`/`neg`; behavioural model already in place |
| `D1N4001` / `D1N4007` / `D1N4148` / `D1N5817` | pass | passive; supply-chain role via `SeriesRectifier`, OR-matrix role via `DiodeOR`, flyback/clamp roles need no cell |
| `D1N4728A` / `D1N4733A` / `D1N4742A` | pass | passive; shunt-regulator role via `ZenerShunt` (phase 2) |
| All `Connector` subclasses (USB, audio, HDMI, JST, headers, RJ45, barrel jacks, SD slots, screw terminals) | pass | built from `Pin`s; conductor-transparent in ERC |

## Category B — behavioural cell instantiated

These classes wrap a private behavioural cell that drives their OUT
pins from their input pins.

### Linear regulators (Phase 1 — done)

| Class | Cell | Parameters | Status |
|-------|------|------------|--------|
| `LM7805` | `LinearRegulator` | `output_voltage=5.0, dropout_v=2.0` | pass |
| `LM7812` | `LinearRegulator` | `output_voltage=12.0, dropout_v=2.0` | pass |
| `LM7905` | `LinearRegulator` | `output_voltage=-5.0, dropout_v=2.0` | pass (negative — cell sign-aware) |
| `LM317` | `LinearRegulator` | `output_voltage` configurable (default 5.0), `dropout_v=2.0` | pass |
| `LM337` | `LinearRegulator` | `output_voltage` configurable (default -5.0), `dropout_v=2.0` | pass (negative) |
| `AMS1117_33` | `LinearRegulator` | `output_voltage=3.3, dropout_v=1.1` | pass |
| `AMS1117_50` | `LinearRegulator` | `output_voltage=5.0, dropout_v=1.1` | pass |
| `LP2950` | `LinearRegulator` | `output_voltage=5.0, dropout_v=0.4` | pass |

### Already-cellled chips (pre-audit)

| Class | Cell(s) | Notes |
|-------|---------|-------|
| `ULN2003A` | 7 × `DarlingtonChannel` | one per channel; existing |
| `SN74HC04` | 6 × `Inverter` | one per gate; existing |
| `CD4069` | 6 × `Inverter` | one per gate; existing |
| `CD4043` | 4 × `NORLatch` + `TriStateBuffer`s | existing |
| `CD4017` | `DecadeCounter` | existing |
| `LM393` | 2 × `Comparator` | existing |
| `ISOW7841` | `IsolatedChannel` | existing |

### Pending — to-do in later phases

| Class | Phase | Cell to write | Notes |
|-------|------:|---------------|-------|
| `D1N4733A`, `D1N4742A` | 2 | `ZenerShunt` (circuit-level, alongside passive Zener) | shunt-regulator / crowbar role |
| `BC547`/`BC548`/`BC557`/`Q2N2222`/`Q2N3904`/`Q2N3906`/`TIP120` | 3 | `BJTSwitch` | NPN / PNP / Darlington (V_BE ≈ 1.4 V for TIP120) |
| `Q2N7000`/`BS170`/`IRLB8721`/`IRFZ44N` | 3 | `MOSFETSwitch` | N-MOSFETs |
| `LM358`/`LM324`/`TL072`/`TL074`/`LM741`/`MCP6002`/`LMV358`/`OPA2134` | 4 | `OpAmp` | rail-to-rail saturation model |
| `LM339`/`LM311`/`TLV3401`/`SN74AHC1G14` | 4 | `Comparator` (existing) | audit-only: verify cell is wired |
| `MOC3021`/`OPTO_4N25`/`OPTO_TLP521` | 5 | `Optocoupler` / `TriacOptocoupler` | LED-input + photo-output stage |
| `MAX232`/`TRS3122E` | 5 | `RS232Driver` | inverting level-shifter |
| `TMP36` | 6 | `AnalogTempSensor` | Python-state driven |
| `BMP280`/`MPU6050`/`HCSR04` | 6 | `I2CPressureSensor` / `I2CIMU` / `UltrasonicRanger` | Python-state placeholder |
| `DHT11` | 6 | `OneWireSensor` (placeholder) | |
| `NE555` | 7 | `NE555Placeholder` (idle-low; Python override) | per §7.2.8 option (b) |
| `LM386`/`LM5002`/`LM5160`/`TPS2660`/`DRV8313`/`BQ27546G1`/`DS18B20`/`DS1307`/`MAX7219`/`TLC5940`/`SDCardSlot`/`MicroSDCardSlot` | 7 | per-IC placeholder | drive idle; Python-state override |
| `SN74HC*` family (00/02/08/32/74/86/138/139/151/157/165/174/273/541/595) | TBD | inspect existing cells; mark fix-needed if any has `cells=[]` | not in scope today |
| `MAX232`, `Relay_SPDT`, `Fan_3W*`, `Display5641AS` | TBD | inspect | |

## Category C — application-firmware-driven (Phase 8)

These classes have OUT pins whose values are determined by user
firmware, not by a function of their input pins. Bare class ships with
`cells=[]`; users subclass and inject a firmware-as-cell (per
`Uno_ThermometerSketch`, `Uno_BLDCCommutator`, etc.). The
`BARE_FIRMWARE_DRIVEN = True` class attribute (phase 8) is the explicit
marker.

| Class | Phase | Notes |
|-------|------:|-------|
| `ATmega328P` | 8 | Arduino Uno MCU |
| `ATmega2560` | 8 | Arduino Mega MCU |
| `ATmega32U4` | 8 | Arduino Leonardo / Pro Micro MCU |
| `ATtiny84` | 8 | small AVR MCU |
| `ATtiny85` | 8 | small AVR MCU |
| `STM32F103C8T6` | 8 | "Blue Pill" Cortex-M3 |
| `STM32F411CEU6` | 8 | "Black Pill" Cortex-M4 |
| `RP2040` | 8 | Raspberry Pi Pico MCU |
| `ESP32_WROOM_32` | 8 | dual-core WiFi+BT MCU module |
| `ESP8266_12F` | 8 | WiFi MCU module |

## Backup-power demo audit

See `docs/backup-power-audit.md`. The demo passes by-design: the three
suspect chips (`TPS2660`, `LM5002`, `LM5160`) are deliberately left
unwired so the framework's ERC walker never encounters their OUT pins,
and the design's actual behaviour is computed by the
`BackupSupervisor` cell whose ports become the composite's external
surface. Not a defect.

## Maintenance

Re-run this audit any time a new component class is added or an
existing class changes its directional surface. The phase-10
regression test (`tests/framework/test_behavioural_completeness.py`)
will cross-reference this table and fail if a registered class lacks
an entry.
