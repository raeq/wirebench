# Interface Report — BatteryPackBoard

1 board(s) in this design: A1 (`BatteryPackBoard`).

## Board: `BatteryPackBoard` (A1)

name 'Li-Ion 1S Battery Pack', rev A.

Public connectors (1):

### J1 — `Header1xNFemale`, 4-pin @ 2.54 mm

| Pin | Name | Direction | Connects to (internal) | Notes |
|-----|------|-----------|------------------------|-------|
| 1 | p1 | BIDIR | R3.t1 + U1.SDA | open-drain bus (SDA) |
| 2 | p2 | BIDIR | R4.t1 + U1.SCL | open-drain bus (SCL) |
| 3 | p3 | BIDIR | R5.t1 + U1.HDQ | open-drain bus (HDQ) |
| 4 | p4 | BIDIR | BT1.neg + C1.t2 + C2.t2 + C3.t2 + R1.t1 + R1.t2 + R2.t2 + U1.SRN + U1.SRP + U1.VSS |  |
