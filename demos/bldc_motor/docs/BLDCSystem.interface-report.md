# Interface Report — BLDCSystem

2 board(s) in this design: A1 (`BLDCSupplyBoard`), A2 (`BLDCControllerBoard`).

Mating pairs:
- A1.P1 mates with A2.J1

## Board: `BLDCSupplyBoard` (A1)

name 'Power Source', rev A.

Public connectors (1):

### P1 — `Header1xNMale`, 2-pin @ 2.54 mm

| Pin | Name | Direction | Connects to (internal) | Notes |
|-----|------|-----------|------------------------|-------|
| 1 | p1 | BIDIR | Rail.out + J1.p1 | + supply |
| 2 | p2 | BIDIR | Rail.out + J1.p2 | − supply |


## Board: `BLDCControllerBoard` (A2)

name 'BLDC Controller', rev A.

Public connectors (3):

### J1 — `Header1xNFemale`, 2-pin @ 2.54 mm

| Pin | Name | Direction | Connects to (internal) | Notes |
|-----|------|-----------|------------------------|-------|
| 1 | p1 | BIDIR |  |  |
| 2 | p2 | BIDIR |  |  |

### J2 — `Header1xNFemale`, 3-pin @ 2.54 mm

| Pin | Name | Direction | Connects to (internal) | Notes |
|-----|------|-----------|------------------------|-------|
| 1 | p1 | BIDIR | P3.p1 + U2.OUT1 |  |
| 2 | p2 | BIDIR | P3.p2 + U2.OUT2 |  |
| 3 | p3 | BIDIR | P3.p3 + U2.OUT3 |  |

### J3 — `Header1xNFemale`, 3-pin @ 2.54 mm

| Pin | Name | Direction | Connects to (internal) | Notes |
|-----|------|-----------|------------------------|-------|
| 1 | p1 | BIDIR | BLDCMotor.ha + P2.p1 + U1.PC0 |  |
| 2 | p2 | BIDIR | BLDCMotor.hb + P2.p2 + U1.PC1 |  |
| 3 | p3 | BIDIR | BLDCMotor.hc + P2.p3 + U1.PC2 |  |
