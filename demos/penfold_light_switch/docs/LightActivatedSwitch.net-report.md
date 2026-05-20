# Net Report — LightActivatedSwitch

9 logical net(s) across 1 ground domain(s): ELECTRICAL.

## Net N0

Domain: ELECTRICAL

Readers (1):
- D1.anode (`LED red`, IN)

Other ports on this net (1):
- R6.t2 (`Resistor 470 Ω`, BIDIR)

Pull-up path: R6.t1 → + rail via R6 (470 Ω)

## Net N1

Domain: ELECTRICAL

Readers (1):
- D1.cathode (`LED red`, IN)

Other ports on this net (1):
- Q1.c (`BC547`, BIDIR)


## Net N2 — + rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (1):
- U1.V_POS (`LM741`, IN)

Other ports on this net (3):
- R2.t1 (`Photoresistor`, BIDIR)
- R3.t1 (`Resistor 10 kΩ`, BIDIR)
- R6.t1 (`Resistor 470 Ω`, BIDIR)


## Net N3

Domain: ELECTRICAL

Drivers (1):
- U1.OUT (`LM741`, OUT)

Other ports on this net (1):
- R5.t1 (`Resistor 4.7 kΩ`, BIDIR)


## Net N4

Domain: ELECTRICAL

Other ports on this net (2):
- Q1.b (`BC547`, BIDIR)
- R5.t2 (`Resistor 4.7 kΩ`, BIDIR)


## Net N5 — − rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Other ports on this net (1):
- Q1.e (`BC547`, BIDIR)


## Net N6

Domain: ELECTRICAL

Readers (1):
- U1.IN_NEG (`LM741`, IN)

Other ports on this net (2):
- R3.t2 (`Resistor 10 kΩ`, BIDIR)
- R4.t1 (`Resistor 5 kΩ`, BIDIR)

Pull-up path: R3.t1 → + rail via R3 (10000 Ω)

## Net N7 — − rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (1):
- U1.V_NEG (`LM741`, IN)

Other ports on this net (2):
- R1.t2 (`Resistor 10 kΩ`, BIDIR)
- R4.t2 (`Resistor 5 kΩ`, BIDIR)


## Net N8

Domain: ELECTRICAL

Readers (1):
- U1.IN_POS (`LM741`, IN)

Other ports on this net (2):
- R1.t1 (`Resistor 10 kΩ`, BIDIR)
- R2.t2 (`Photoresistor`, BIDIR)
