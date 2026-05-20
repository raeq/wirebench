# Net Report — WarblingDoorbuzzer

13 logical net(s) across 1 ground domain(s): ELECTRICAL.

## Net N0

Domain: ELECTRICAL

Other ports on this net (2):
- C5.t2 (`Capacitor 10 µF`, BIDIR)
- LS1.t1 (`Speaker`, BIDIR)


## Net N1 — − rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (2):
- U1.GND (`NE555`, IN)
- U2.GND (`NE555`, IN)

Other ports on this net (5):
- C1.t2 (`Capacitor 2.2 µF`, BIDIR)
- C2.t2 (`Capacitor 10 nF`, BIDIR)
- C3.t2 (`Capacitor 100 nF`, BIDIR)
- C4.t2 (`Capacitor 10 nF`, BIDIR)
- LS1.t2 (`Speaker`, BIDIR)


## Net N2

Domain: ELECTRICAL

Other ports on this net (2):
- C5.t1 (`Capacitor 10 µF`, BIDIR)
- R5.t2 (`Resistor 100 Ω`, BIDIR)


## Net N3

Domain: ELECTRICAL

Drivers (1):
- U2.OUT (`NE555`, OUT)

Other ports on this net (1):
- R5.t1 (`Resistor 100 Ω`, BIDIR)


## Net N4

Domain: ELECTRICAL

Other ports on this net (2):
- C4.t1 (`Capacitor 10 nF`, BIDIR)
- U2.CONT (`NE555`, BIDIR)


## Net N5

Domain: ELECTRICAL

Readers (2):
- U2.THRES (`NE555`, IN)
- U2.TRIG (`NE555`, IN)

Other ports on this net (2):
- C3.t1 (`Capacitor 100 nF`, BIDIR)
- R4.t2 (`Resistor 4.7 kΩ`, BIDIR)


## Net N6

Domain: ELECTRICAL

Drivers (1):
- U2.DISCH (`NE555`, OUT)

Other ports on this net (2):
- R3.t2 (`Resistor 4.7 kΩ`, BIDIR)
- R4.t1 (`Resistor 4.7 kΩ`, BIDIR)

Pull-up path: R3.t1 → + rail via R3 (4700 Ω)

## Net N7 — + rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (2):
- U1.VCC (`NE555`, IN)
- U2.VCC (`NE555`, IN)

Other ports on this net (2):
- R1.t1 (`Resistor 47 kΩ`, BIDIR)
- R3.t1 (`Resistor 4.7 kΩ`, BIDIR)


## Net N8

Domain: ELECTRICAL

Other ports on this net (2):
- C2.t1 (`Capacitor 10 nF`, BIDIR)
- U1.CONT (`NE555`, BIDIR)


## Net N9

Domain: ELECTRICAL

Readers (2):
- U1.THRES (`NE555`, IN)
- U1.TRIG (`NE555`, IN)

Other ports on this net (2):
- C1.t1 (`Capacitor 2.2 µF`, BIDIR)
- R2.t2 (`Resistor 47 kΩ`, BIDIR)


## Net N10

Domain: ELECTRICAL

Drivers (1):
- U1.DISCH (`NE555`, OUT)

Other ports on this net (2):
- R1.t2 (`Resistor 47 kΩ`, BIDIR)
- R2.t1 (`Resistor 47 kΩ`, BIDIR)

Pull-up path: R1.t1 → + rail via R1 (47000 Ω)

## Net N11

Domain: ELECTRICAL

Drivers (1):
- U1.OUT (`NE555`, OUT)

Readers (1):
- U2.RESET (`NE555`, IN)


## Net N12 — + rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (1):
- U1.RESET (`NE555`, IN)
