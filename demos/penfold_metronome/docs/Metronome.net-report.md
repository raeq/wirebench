# Net Report — Metronome

9 logical net(s) across 1 ground domain(s): ELECTRICAL.

## Net N0

Domain: ELECTRICAL

Other ports on this net (2):
- C3.t2 (`Capacitor 10 µF`, BIDIR)
- LS1.t1 (`Speaker`, BIDIR)


## Net N1 — − rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (1):
- U1.GND (`NE555`, IN)

Other ports on this net (3):
- C1.t2 (`Capacitor 100 nF`, BIDIR)
- C2.t2 (`Capacitor 10 nF`, BIDIR)
- LS1.t2 (`Speaker`, BIDIR)


## Net N2

Domain: ELECTRICAL

Other ports on this net (2):
- C3.t1 (`Capacitor 10 µF`, BIDIR)
- R3.t2 (`Resistor 100 Ω`, BIDIR)


## Net N3

Domain: ELECTRICAL

Drivers (1):
- U1.OUT (`NE555`, OUT)

Other ports on this net (1):
- R3.t1 (`Resistor 100 Ω`, BIDIR)


## Net N4

Domain: ELECTRICAL

Other ports on this net (2):
- C2.t1 (`Capacitor 10 nF`, BIDIR)
- U1.CONT (`NE555`, BIDIR)


## Net N5

Domain: ELECTRICAL

Readers (2):
- U1.THRES (`NE555`, IN)
- U1.TRIG (`NE555`, IN)

Other ports on this net (2):
- C1.t1 (`Capacitor 100 nF`, BIDIR)
- R2.t2 (`Resistor 50 kΩ`, BIDIR)


## Net N6

Domain: ELECTRICAL

Drivers (1):
- U1.DISCH (`NE555`, OUT)

Other ports on this net (2):
- R1.t2 (`Resistor 4.7 kΩ`, BIDIR)
- R2.t1 (`Resistor 50 kΩ`, BIDIR)

Pull-up path: R1.t1 → + rail via R1 (4700 Ω)

## Net N7 — + rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (1):
- U1.VCC (`NE555`, IN)

Other ports on this net (1):
- R1.t1 (`Resistor 4.7 kΩ`, BIDIR)


## Net N8 — + rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (1):
- U1.RESET (`NE555`, IN)
