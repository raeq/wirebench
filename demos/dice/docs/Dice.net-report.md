# Net Report — Dice

13 logical net(s) across 1 ground domain(s): ELECTRICAL.

## Net N0

Domain: ELECTRICAL

Drivers (1):
- U2.Q4 (`CD4017`, OUT)

Readers (3):
- DiodeOR.q4 (`DiodeOR`, IN)
- D12.anode (`LED red`, IN)
- D13.anode (`LED red`, IN)

Other ports on this net (3):
- D6.anode (`D1N4148`, BIDIR)
- R4.t1 (`Resistor 330 Ω`, BIDIR)
- R4.t2 (`Resistor 330 Ω`, BIDIR)


## Net N1 — − rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (7):
- D10.cathode (`LED red`, IN)
- D11.cathode (`LED red`, IN)
- D12.cathode (`LED red`, IN)
- D13.cathode (`LED red`, IN)
- D7.cathode (`LED red`, IN)
- D8.cathode (`LED red`, IN)
- D9.cathode (`LED red`, IN)


## Net N2

Domain: ELECTRICAL

Drivers (1):
- DiodeOR.out (`DiodeOR`, OUT)

Readers (2):
- D10.anode (`LED red`, IN)
- D11.anode (`LED red`, IN)

Other ports on this net (5):
- D4.cathode (`D1N4148`, BIDIR)
- D5.cathode (`D1N4148`, BIDIR)
- D6.cathode (`D1N4148`, BIDIR)
- R3.t1 (`Resistor 330 Ω`, BIDIR)
- R3.t2 (`Resistor 330 Ω`, BIDIR)


## Net N3

Domain: ELECTRICAL

Drivers (1):
- U2.CO (`CD4017`, OUT)

Readers (2):
- D8.anode (`LED red`, IN)
- D9.anode (`LED red`, IN)

Other ports on this net (2):
- R2.t1 (`Resistor 330 Ω`, BIDIR)
- R2.t2 (`Resistor 330 Ω`, BIDIR)


## Net N4

Domain: ELECTRICAL

Drivers (1):
- DiodeOR.out (`DiodeOR`, OUT)

Readers (1):
- D7.anode (`LED red`, IN)

Other ports on this net (5):
- D1.cathode (`D1N4148`, BIDIR)
- D2.cathode (`D1N4148`, BIDIR)
- D3.cathode (`D1N4148`, BIDIR)
- R1.t1 (`Resistor 470 Ω`, BIDIR)
- R1.t2 (`Resistor 470 Ω`, BIDIR)


## Net N5

Domain: ELECTRICAL

Drivers (1):
- U2.Q3 (`CD4017`, OUT)

Readers (2):
- DiodeOR.q3 (`DiodeOR`, IN)
- DiodeOR.q3 (`DiodeOR`, IN)

Other ports on this net (2):
- D2.anode (`D1N4148`, BIDIR)
- D5.anode (`D1N4148`, BIDIR)


## Net N6

Domain: ELECTRICAL

Drivers (1):
- U2.Q2 (`CD4017`, OUT)

Readers (1):
- DiodeOR.q2 (`DiodeOR`, IN)

Other ports on this net (1):
- D4.anode (`D1N4148`, BIDIR)


## Net N7

Domain: ELECTRICAL

Drivers (1):
- U2.Q5 (`CD4017`, OUT)

Readers (1):
- DiodeOR.q5 (`DiodeOR`, IN)

Other ports on this net (1):
- D3.anode (`D1N4148`, BIDIR)


## Net N8

Domain: ELECTRICAL

Drivers (1):
- U2.Q1 (`CD4017`, OUT)

Readers (1):
- DiodeOR.q1 (`DiodeOR`, IN)

Other ports on this net (1):
- D1.anode (`D1N4148`, BIDIR)


## Net N9

Domain: ELECTRICAL

Drivers (1):
- U2.Q6 (`CD4017`, OUT)

Readers (1):
- U2.RST (`CD4017`, IN)


## Net N10 — − rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (2):
- U1.GND (`NE555`, IN)
- U2.VSS (`CD4017`, IN)


## Net N11 — + rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (2):
- U1.VCC (`NE555`, IN)
- U2.VDD (`CD4017`, IN)


## Net N18 — + rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (1):
- U1.RESET (`NE555`, IN)
