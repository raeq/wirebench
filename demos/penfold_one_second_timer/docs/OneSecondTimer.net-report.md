# Net Report — OneSecondTimer

9 logical net(s) across 1 ground domain(s): ELECTRICAL.

## Net N0

Domain: ELECTRICAL

Readers (1):
- D2.anode (`LED red`, IN)

Other ports on this net (1):
- R7.t2 (`Resistor 510 Ω`, BIDIR)

Pull-up path: R7.t1 → + rail via R7 (510 Ω)

## Net N1

Domain: ELECTRICAL

Readers (1):
- D2.cathode (`LED red`, IN)

Other ports on this net (1):
- R8.t1 (`Resistor 510 Ω`, BIDIR)


## Net N2

Domain: ELECTRICAL

Drivers (1):
- U1.OUT (`LM741`, OUT)

Other ports on this net (3):
- R4.t2 (`Resistor 50 kΩ`, BIDIR)
- R6.t1 (`Resistor 220 kΩ`, BIDIR)
- R8.t2 (`Resistor 510 Ω`, BIDIR)


## Net N3 — + rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (1):
- U1.V_POS (`LM741`, IN)

Other ports on this net (3):
- C1.t1 (`Capacitor 100 µF`, BIDIR)
- R1.t1 (`Resistor 100 kΩ`, BIDIR)
- R7.t1 (`Resistor 510 Ω`, BIDIR)


## Net N4 — − rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (1):
- U1.V_NEG (`LM741`, IN)

Other ports on this net (3):
- C1.t2 (`Capacitor 100 µF`, BIDIR)
- C2.t2 (`Capacitor 100 nF`, BIDIR)
- R2.t2 (`Resistor 100 kΩ`, BIDIR)


## Net N5

Domain: ELECTRICAL

Readers (1):
- U1.IN_NEG (`LM741`, IN)

Other ports on this net (3):
- C2.t1 (`Capacitor 100 nF`, BIDIR)
- D1.anode (`D1N4148`, BIDIR)
- R5.t2 (`Resistor 10 MΩ`, BIDIR)


## Net N6

Domain: ELECTRICAL

Other ports on this net (3):
- D1.cathode (`D1N4148`, BIDIR)
- R5.t1 (`Resistor 10 MΩ`, BIDIR)
- R6.t2 (`Resistor 220 kΩ`, BIDIR)


## Net N7

Domain: ELECTRICAL

Other ports on this net (2):
- R3.t2 (`Resistor 4.7 kΩ`, BIDIR)
- R4.t1 (`Resistor 50 kΩ`, BIDIR)


## Net N8

Domain: ELECTRICAL

Readers (1):
- U1.IN_POS (`LM741`, IN)

Other ports on this net (3):
- R1.t2 (`Resistor 100 kΩ`, BIDIR)
- R2.t1 (`Resistor 100 kΩ`, BIDIR)
- R3.t1 (`Resistor 4.7 kΩ`, BIDIR)

Pull-up path: R1.t1 → + rail via R1 (100000 Ω)
