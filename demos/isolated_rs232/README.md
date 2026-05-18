# isolated_rs232

A galvanically isolated RS-232 link reproduced from TIDA-01230. An ISOW7841 quad-channel digital isolator on the host-MCU side, a TRS3122E RS-232 transceiver behind the barrier, and two `Header1xNFemale` connectors — one in the logic-side `ELECTRICAL` ground domain, one in the line-side `ISOLATED` ground domain. The `IsolatedRS232Link` composite mates a host plug to the logic side and an RS-232 cable to the line side; the design's whole point is that no electrical conductor reaches across the barrier — every signal crosses the isolator's capacitive coupling instead.

## What this design is protected from

The framework refused these specific mistakes during this design's development. Each snippet is a near-miss — paste the broken lines into your own copy of the design and wirebench raises before the design can run, either at construction or at the first `evaluate()`.

### A cross-domain wire

```python
# In IsolatedRS232Board.__init__, perhaps an attempt to "share the
# decoupling cap to save BOM cost" ties the logic-side bypass to the
# iso-side bypass:
wire(self.c_vcc1.t1, self.c_viso.t1)

IsolatedRS232Board(refdes_number=1)
# DomainCrossingError: Cannot wire ports across ground domains: 't1' (electrical), 't1' (isolated_rs232)
```

`c_vcc1` is declared with `domain=ELECTRICAL`; `c_viso` with `domain=ISOLATED`. The two `GroundDomain`s are deliberately distinct so the isolator's purpose — keeping line-side faults from reaching the MCU side — actually holds. `wire()` consults each port's domain before merging nets and refuses any wire that would bridge two distinct domains. The bench equivalent is the design's whole reason for existing being silently undone: the iso barrier is bypassed by a single jumper, and the next time the RS-232 line catches a static discharge it goes straight into the host MCU.

### A cross-domain mate — host plug into the iso-side receptacle

```python
# In IsolatedRS232Link.__init__, perhaps the user mates the host's
# logic-side plug into J2 (the iso-side receptacle) by mistake — the
# two receptacles are the same model and on opposite ends of the
# same board:
mate(self.host.connectors[0], self.iso_rs232.connectors[1])  # was: [0]

IsolatedRS232Link()
# DomainCrossingError: Cannot wire ports across ground domains: 'p1' (electrical), 'p1' (isolated_rs232)
```

`mate()` doesn't have its own "wrong-domain" check — it propagates per-pin connections through `wire()`, and `wire()`'s domain guard fires on the first pin-pair. The framework happily accepts the connector classes as matching mates; it's only at the pin-level connection that the boundary violation surfaces. The bench equivalent is the user plugging a 4-pin cable into a physically-identical receptacle on the wrong side of the board — wirebench refuses the mate; in real hardware you'd plug it in, energise the host, and ride a fault current path through whatever's least resistant.

## Running it

```bash
python demos/isolated_rs232/isolated_rs232.py
```

## What comes out

The `docs/` folder beside this README has the design's pre-generated exports. The composed `IsolatedRS232Link` gets its own set, and the standalone `IsolatedRS232Board` plus the two mating boards (`ControllerSourceBoard`, `RS232CableBoard`) export as if they were complete designs:

- [`IsolatedRS232Link.bom.csv`](docs/IsolatedRS232Link.bom.csv), [`IsolatedRS232Link.svg`](docs/IsolatedRS232Link.svg), [`IsolatedRS232Link.md`](docs/IsolatedRS232Link.md), [`IsolatedRS232Link.net`](docs/IsolatedRS232Link.net), [`IsolatedRS232Link.cir`](docs/IsolatedRS232Link.cir), [`IsolatedRS232Link.dot`](docs/IsolatedRS232Link.dot), [`IsolatedRS232Link.mmd`](docs/IsolatedRS232Link.mmd), [`IsolatedRS232Link.yosys.json`](docs/IsolatedRS232Link.yosys.json), [`IsolatedRS232Link.net-report.md`](docs/IsolatedRS232Link.net-report.md), [`IsolatedRS232Link.domain-report.md`](docs/IsolatedRS232Link.domain-report.md), [`IsolatedRS232Link.interface-report.md`](docs/IsolatedRS232Link.interface-report.md) — composed assembly
- [`IsolatedRS232Board.bom.csv`](docs/IsolatedRS232Board.bom.csv), [`IsolatedRS232Board.svg`](docs/IsolatedRS232Board.svg), [`IsolatedRS232Board.md`](docs/IsolatedRS232Board.md), [`IsolatedRS232Board.net`](docs/IsolatedRS232Board.net), [`IsolatedRS232Board.cir`](docs/IsolatedRS232Board.cir), [`IsolatedRS232Board.dot`](docs/IsolatedRS232Board.dot), [`IsolatedRS232Board.mmd`](docs/IsolatedRS232Board.mmd), [`IsolatedRS232Board.yosys.json`](docs/IsolatedRS232Board.yosys.json), [`IsolatedRS232Board.net-report.md`](docs/IsolatedRS232Board.net-report.md), [`IsolatedRS232Board.domain-report.md`](docs/IsolatedRS232Board.domain-report.md), [`IsolatedRS232Board.interface-report.md`](docs/IsolatedRS232Board.interface-report.md) — isolator board
- [`ControllerSourceBoard.bom.csv`](docs/ControllerSourceBoard.bom.csv), [`ControllerSourceBoard.svg`](docs/ControllerSourceBoard.svg), [`ControllerSourceBoard.md`](docs/ControllerSourceBoard.md), [`ControllerSourceBoard.net`](docs/ControllerSourceBoard.net), [`ControllerSourceBoard.cir`](docs/ControllerSourceBoard.cir), [`ControllerSourceBoard.dot`](docs/ControllerSourceBoard.dot), [`ControllerSourceBoard.mmd`](docs/ControllerSourceBoard.mmd), [`ControllerSourceBoard.yosys.json`](docs/ControllerSourceBoard.yosys.json), [`ControllerSourceBoard.net-report.md`](docs/ControllerSourceBoard.net-report.md), [`ControllerSourceBoard.domain-report.md`](docs/ControllerSourceBoard.domain-report.md), [`ControllerSourceBoard.interface-report.md`](docs/ControllerSourceBoard.interface-report.md) — host source
- [`RS232CableBoard.bom.csv`](docs/RS232CableBoard.bom.csv), [`RS232CableBoard.svg`](docs/RS232CableBoard.svg), [`RS232CableBoard.md`](docs/RS232CableBoard.md), [`RS232CableBoard.net`](docs/RS232CableBoard.net), [`RS232CableBoard.cir`](docs/RS232CableBoard.cir), [`RS232CableBoard.dot`](docs/RS232CableBoard.dot), [`RS232CableBoard.mmd`](docs/RS232CableBoard.mmd), [`RS232CableBoard.yosys.json`](docs/RS232CableBoard.yosys.json), [`RS232CableBoard.net-report.md`](docs/RS232CableBoard.net-report.md), [`RS232CableBoard.domain-report.md`](docs/RS232CableBoard.domain-report.md), [`RS232CableBoard.interface-report.md`](docs/RS232CableBoard.interface-report.md) — cable stand-in

## Going further

- The source: [`isolated_rs232.py`](isolated_rs232.py)
- The full ordered list of all twelve demos: [`../../docs/learning-path.md`](../../docs/learning-path.md)
