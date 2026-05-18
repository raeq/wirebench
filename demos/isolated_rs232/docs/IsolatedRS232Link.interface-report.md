# Interface Report — IsolatedRS232Link

3 board(s) in this design: A1 (`ControllerSourceBoard`), A2 (`IsolatedRS232Board`), A3 (`RS232CableBoard`).

Mating pairs:
- A1.P1 mates with A2.J1
- A2.J2 mates with A3.P2

## Board: `ControllerSourceBoard` (A1)

name 'Controller Plug', rev A.

Public connectors (1):

### P1 — `Header1xNMale`, 4-pin @ 2.54 mm

| Pin | Name | Direction | Connects to (internal) | Notes |
|-----|------|-----------|------------------------|-------|
| 1 | p1 | BIDIR | Rail.out + J1.p1 | + supply |
| 2 | p2 | BIDIR | Rail.out + J1.p2 | − supply |
| 3 | p3 | BIDIR |  |  |
| 4 | p4 | BIDIR |  |  |


## Board: `IsolatedRS232Board` (A2)

name 'Isolated RS-232', rev A.

Public connectors (2):

### J1 — `Header1xNFemale`, 4-pin @ 2.54 mm

| Pin | Name | Direction | Connects to (internal) | Notes |
|-----|------|-----------|------------------------|-------|
| 1 | p1 | BIDIR |  |  |
| 2 | p2 | BIDIR |  |  |
| 3 | p3 | BIDIR | P1.p3 + U1.INA |  |
| 4 | p4 | BIDIR | P1.p4 + U1.OUTD |  |

### J2 — `Header1xNFemale`, 4-pin @ 2.54 mm

| Pin | Name | Direction | Connects to (internal) | Notes |
|-----|------|-----------|------------------------|-------|
| 1 | p1 | BIDIR | P2.p1 + U2.TOUT1 |  |
| 2 | p2 | BIDIR | P2.p2 + U2.RIN1 |  |
| 3 | p3 | BIDIR |  |  |
| 4 | p4 | BIDIR |  |  |


## Board: `RS232CableBoard` (A3)

name 'RS-232 Cable', rev A.

Public connectors (1):

### P2 — `Header1xNMale`, 4-pin @ 2.54 mm

| Pin | Name | Direction | Connects to (internal) | Notes |
|-----|------|-----------|------------------------|-------|
| 1 | p1 | BIDIR |  |  |
| 2 | p2 | BIDIR |  |  |
| 3 | p3 | BIDIR | Rail.out + J2.p3 | − supply |
| 4 | p4 | BIDIR |  |  |
