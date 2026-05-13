# Behavioural-cell audit

This table records the audit decision for every registered component
class.  The Phase-10 regression test
(`tests/framework/test_behavioural_completeness.py`) cross-references
it: every entry in the registry must construct cleanly in a minimal
topology.

**Categories** (per spec §5):

- **A** — Passive.  No OUT pins, or only OUT pins on conductor
  structures.  No behavioural cell needed.
- **B** — Behavioural-cell-driven.  Has OUT pins driven by a cell
  that's a function of input pins.
- **C** — Application-firmware-driven.  Has OUT pins driven by user
  code injected via subclassing.  `BARE_FIRMWARE_DRIVEN = True` on
  the class.

**Phase status**: every phase 2–10 has landed.  Construction-time
invariant (`Chip._assert_every_out_pin_is_internally_driven`) is
active in `framework/chip.py`; defective chip classes can no longer
be constructed.  The registry-wide regression test backs it up.

## Category A — passive (no cell on the class)

These classes have no OUT pins or only conductor-style OUTs.  No
behavioural cell is needed.

| Class group                            | Notes                                             |
|----------------------------------------|---------------------------------------------------|
| `Resistor`, `Capacitor`, `Inductor`    | 2-terminal passives; BIDIR ports                  |
| `LED`                                  | 2 IN pins; no driver                              |
| `Rail`, `Cell`                         | leaf drivers — already cells in their own right   |
| `D1N4001` / `D1N4007` / `D1N4148` / `D1N5817` | passive diodes; supply-chain role via `SeriesRectifier`, wired-OR via `DiodeOR` |
| `D1N4728A` / `D1N4733A` / `D1N4742A`   | passive Zeners; shunt-regulator role via `ZenerShunt` |
| All `Connector` subclasses             | built from `Pin`s; conductor-transparent in ERC   |
| `Relay_SPDT`                           | mechanical contact pair, conductor-transparent    |
| `MicroSDCard`, `SDCard`                | passive medium; slot drives the data path         |

## Category B — behavioural cell instantiated (Phase 1–7)

### Phase 1 — Linear regulators

| Class        | Cell              | Parameters                            |
|--------------|-------------------|---------------------------------------|
| `LM7805`     | `LinearRegulator` | output 5.0, dropout 2.0               |
| `LM7812`     | `LinearRegulator` | output 12.0, dropout 2.0              |
| `LM7905`     | `LinearRegulator` | output -5.0, dropout 2.0 (sign-aware) |
| `LM317`      | `LinearRegulator` | output configurable (default 5.0), dropout 2.0 |
| `LM337`      | `LinearRegulator` | output configurable (default -5.0), dropout 2.0 |
| `AMS1117_33` | `LinearRegulator` | output 3.3, dropout 1.1               |
| `AMS1117_50` | `LinearRegulator` | output 5.0, dropout 1.1               |
| `LP2950`     | `LinearRegulator` | output 5.0, dropout 0.4               |

### Phase 1 — Circuit-level diode companions

These cells are *circuit-level* (instantiated alongside a passive
diode in the parent design, not inside the diode class):

- `SeriesRectifier(v_f)` — drives `output = input − V_F` when the
  diode would be forward-biased; companion to a passive diode in a
  supply-chain role (canonical use: `5v_rail_power` demo D1).
- `ZenerShunt(v_z)` — drives `cathode = anode + V_Z` for the
  shunt-regulator role; companion to a passive Zener.
- `DiodeOR(input_names=...)` — pre-existing; OR-matrix role used by
  the `dice` demo.

### Phase 3 — Transistor circuit-level companions

Same pattern as the diode cells — transistors are Category A
passive; the role-specific behaviour is modelled at the circuit
level alongside the passive part:

- `BJTSwitch(polarity='npn'|'pnp', v_be_on=0.7)` — saturated
  common-emitter switch.  Pass `v_be_on=1.4` for Darlingtons
  (TIP120).
- `MOSFETSwitch(channel='n'|'p', v_gs_th=2.0)` — saturated
  low-side / high-side switch.

The transistor classes themselves stay passive — `BC547`, `BC548`,
`BC557`, `Q2N3904`, `Q2N3906`, `Q2N2222`, `TIP120` (BJTs); `BS170`,
`Q2N7000`, `IRLB8721`, `IRFZ44N` (MOSFETs).  Same precedent as
diodes (a transistor's role is a property of the circuit, not the
part).

### Phase 4 — Op-amps and comparators

| Class                  | Cell        | Channels | Supply pins        |
|------------------------|-------------|---------:|--------------------|
| `LM358`, `LMV358`      | `OpAmp`     | 2        | V_POS / V_GND      |
| `LM324`                | `OpAmp`     | 4        | V_POS / V_GND      |
| `TL072`, `OPA2134`     | `OpAmp`     | 2        | V_POS / V_NEG      |
| `TL074`                | `OpAmp`     | 4        | V_POS / V_NEG      |
| `LM741`                | `OpAmp`     | 1        | V_POS / V_NEG      |
| `MCP6002`              | `OpAmp`     | 2        | VDD / VSS          |
| `LM339`                | `OpAmp`     | 4        | VCC / GND (used as comparator) |
| `TLV3401`              | `OpAmp`     | 1        | VCC / GND          |
| `LM311`                | `OpAmp` × 2 | 1        | VCC_POS / VCC_NEG; dual COL_OUT + EMIT_OUT |
| `LM393`                | `Comparator` | 2       | (pre-existing)     |
| `SN74AHC1G14`          | `Inverter`  | 1        | (Schmitt-inverter) |

### Phase 5 — RS-232 driver / level shifter

| Class    | Cells                                              |
|----------|----------------------------------------------------|
| `MAX232` | 2 × `RS232Driver` + 2 × `ConstantVoltage` (V_POS / V_NEG) |

### Phase 6 — Sensors

| Class      | Cell(s)                                       | Notes |
|------------|-----------------------------------------------|-------|
| `TMP36`    | `AnalogTempSensor`                            | Python-state `temperature_c` setter |
| `MPU6050`  | 4 × `IdleDriver`                              | I²C-driven; outputs idle until prescribed |
| `HCSR04`   | `IdleDriver`                                  | echo pulse modelled as idle LOW |
| `DHT11`    | (no OUT pins — BIDIR only)                    | Category A passive |
| `BMP280`   | (no OUT pins — BIDIR only)                    | Category A passive |

### Phase 7 — Specialty IC placeholders (drive-idle pattern)

These chips use `wire_idle_drivers(pins, domain)` to attach an
`IdleDriver` to every declared OUT pin.  The drivers satisfy the
construction-time invariant; actual chip behaviour is protocol-
driven, bus-driven, or otherwise too complex to model at the
framework's voltage-only level.

| Class                                                  | Phase-7 notes                                  |
|--------------------------------------------------------|------------------------------------------------|
| `NE555`                                                | OUT / DISCH idle LOW                           |
| `LM386`                                                | audio output, idle 0 V                         |
| `DS1307`                                               | I²C RTC; SQW_OUT, X2 idle                      |
| `MAX7219`                                              | display driver; all digit / segment outputs idle LOW |
| `TLC5940`                                              | LED-PWM driver; all outputs idle               |
| `MOC3021`, `OPTO_4N25`, `OPTO_TLP521`                  | optos; emitter / collector / base idle         |
| `TRS3122E`                                             | (already cellled pre-audit)                    |
| `LM5002`, `LM5160`, `TPS2660`, `DRV8313`               | switchers / eFuses; SW / FLT_B / IMON idle     |
| `BQ27546G1`                                            | (already cellled pre-audit)                    |
| `Display5641AS`                                        | (already cellled pre-audit — `SegmentMatrix`)  |
| `TMP302`                                               | open-drain temp switch; OUT idle               |
| `SN74HC00`..`SN74HC595`                                | logic-family chips; outputs idle LOW           |

### Already-cellled before the audit

| Class                                | Cell(s)                                  |
|--------------------------------------|------------------------------------------|
| `ULN2003A`                           | 7 × `DarlingtonChannel`                  |
| `SN74HC04`, `CD4069`                 | 6 × `Inverter`                           |
| `CD4043`                             | 4 × `NORLatch` + `TriStateBuffer`s       |
| `CD4017`                             | `DecadeCounter`                          |
| `ISOW7841`                           | `IsolatedChannel`                        |

## Category C — application-firmware-driven (Phase 8)

These classes declare `BARE_FIRMWARE_DRIVEN = True` and legitimately
ship with `cells=[]`.  Users subclass and inject a firmware-as-cell
(see `Uno_ThermometerSketch`, `Uno_BLDCCommutator` for the pattern).

| Class                                | Notes              |
|--------------------------------------|--------------------|
| `ATmega328P`, `ATmega2560`, `ATmega32U4` | AVR microcontrollers |
| `ATtiny84`, `ATtiny85`               | small AVRs         |
| `STM32F103C8T6`, `STM32F411CEU6`     | ARM Cortex-M       |
| `RP2040`                             | RP2040 Cortex-M0+  |
| `ESP32_WROOM_32`, `ESP8266_12F`      | WiFi / BT MCUs     |

## Construction-time invariant (Phase 9)

Active in `framework/chip.py`.  Every `Chip` subclass must drive every
declared OUT pin via an internal cell, or set
`BARE_FIRMWARE_DRIVEN = True`.  Violations raise
`PartConfigurationError` at construction with a message naming the
offending pin.  Tests:
`tests/framework/test_chip_construction_invariant.py`.

The invariant accepts two patterns as "real driver":

1. A cell (FactorNode that's not a Pin) with an OUT port wired to
   the OUT pin's internal face — the typical behavioural-cell case.
2. Another Pin's internal face wired to the OUT pin's internal face
   (an OUT pin's internal face is IN direction; the OTHER pin's
   internal face — whose external is IN — is OUT-direction and
   counts as a driver) — valid for pure pass-through chips.

## Backup-power demo audit

See `docs/backup-power-audit.md`.  Passes by-design (the three
suspect chips are deliberately unwired; the design's behaviour is
in `BackupSupervisor`).

## Phase 10 — Registry regression test

`tests/framework/test_behavioural_completeness.py`.  Parametrised
over every registered class; each must construct cleanly via the
`_construct_any` helper.  Skips list is exactly one entry (`Board`,
which needs a parent assembly) — every other class must construct
in isolation.

## Maintenance

Re-run this audit any time a new component class is added.  The
phase-10 regression test will fail if a registered class can't be
constructed cleanly; the construction-time invariant will fail if a
new chip class is added with OUT pins and no driving cell.
