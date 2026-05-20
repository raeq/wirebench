# Net Report — FuzzUnit

9 logical net(s) across 1 ground domain(s): ELECTRICAL.

## Net N0

Domain: ELECTRICAL

Other ports on this net (2):
- C3.t2 (`Capacitor 220 nF`, BIDIR)
- R6.t1 (`Resistor 50 kΩ`, BIDIR)


## Net N1

Domain: ELECTRICAL

Other ports on this net (2):
- J2.tip (`Audio3p5mmTRSJack`, BIDIR)
- R6.t2 (`Resistor 50 kΩ`, BIDIR)


## Net N2

Domain: ELECTRICAL

Drivers (1):
- U1.OUT (`LM741`, OUT)

Other ports on this net (4):
- C3.t1 (`Capacitor 220 nF`, BIDIR)
- D1.anode (`D1N4148`, BIDIR)
- D2.cathode (`D1N4148`, BIDIR)
- R3.t2 (`Resistor 470 kΩ`, BIDIR)


## Net N3 — − rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (1):
- U1.V_NEG (`LM741`, IN)

Other ports on this net (7):
- C2.t2 (`Capacitor 10 µF`, BIDIR)
- D1.cathode (`D1N4148`, BIDIR)
- D2.anode (`D1N4148`, BIDIR)
- J1.sleeve (`Audio3p5mmTRSJack`, BIDIR)
- J2.sleeve (`Audio3p5mmTRSJack`, BIDIR)
- R1.t2 (`Resistor 1 MΩ`, BIDIR)
- R5.t2 (`Resistor 100 kΩ`, BIDIR)


## Net N4

Domain: ELECTRICAL

Readers (1):
- U1.IN_POS (`LM741`, IN)

Other ports on this net (3):
- C2.t1 (`Capacitor 10 µF`, BIDIR)
- R4.t2 (`Resistor 100 kΩ`, BIDIR)
- R5.t1 (`Resistor 100 kΩ`, BIDIR)

Pull-up path: R4.t1 → + rail via R4 (100000 Ω)

## Net N5 — + rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (1):
- U1.V_POS (`LM741`, IN)

Other ports on this net (1):
- R4.t1 (`Resistor 100 kΩ`, BIDIR)


## Net N6

Domain: ELECTRICAL

Readers (1):
- U1.IN_NEG (`LM741`, IN)

Other ports on this net (2):
- R2.t2 (`Resistor 1 kΩ`, BIDIR)
- R3.t1 (`Resistor 470 kΩ`, BIDIR)


## Net N7

Domain: ELECTRICAL

Other ports on this net (3):
- C1.t2 (`Capacitor 100 nF`, BIDIR)
- R1.t1 (`Resistor 1 MΩ`, BIDIR)
- R2.t1 (`Resistor 1 kΩ`, BIDIR)


## Net N8

Domain: ELECTRICAL

Other ports on this net (2):
- C1.t1 (`Capacitor 100 nF`, BIDIR)
- J1.tip (`Audio3p5mmTRSJack`, BIDIR)
