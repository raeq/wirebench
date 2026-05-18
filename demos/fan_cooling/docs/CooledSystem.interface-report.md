# Interface Report — CooledSystem

2 board(s) in this design: A1 (`PowerSourceBoard`), A2 (`FanCoolingBoard`).

Mating pairs:
- A1.P1 mates with A2.J1

## Board: `PowerSourceBoard` (A1)

name 'Power Source', rev A.

Public connectors (1):

### P1 — `Header1xNMale`, 2-pin @ 2.54 mm

| Pin | Name | Direction | Connects to (internal) | Notes |
|-----|------|-----------|------------------------|-------|
| 1 | p1 | BIDIR | Rail.out + J1.p1 | + supply |
| 2 | p2 | BIDIR | Rail.out + J1.p2 | − supply |


## Board: `FanCoolingBoard` (A2)

name 'Fan Cooling Module', rev A.

Public connectors (2):

### J1 — `Header1xNFemale`, 2-pin @ 2.54 mm

| Pin | Name | Direction | Connects to (internal) | Notes |
|-----|------|-----------|------------------------|-------|
| 1 | p1 | BIDIR | Rail.out + P1.p1 | + supply |
| 2 | p2 | BIDIR |  |  |

### J2 — `Header1xNFemale`, 2-pin @ 2.54 mm

| Pin | Name | Direction | Connects to (internal) | Notes |
|-----|------|-----------|------------------------|-------|
| 1 | p1 | BIDIR | Rail.out + J1.p1 + P1.p1 | + supply |
| 2 | p2 | BIDIR | FanController.fan_drive |  |
