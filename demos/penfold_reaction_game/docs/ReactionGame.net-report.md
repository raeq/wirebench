# Net Report — ReactionGame

24 logical net(s) across 1 ground domain(s): ELECTRICAL.

## Net N0 — + rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (1):
- U1.RESET (`NE555`, IN)

Other ports on this net (10):
- C1.t1 (`Capacitor 100 nF`, BIDIR)
- C1.t2 (`Capacitor 100 nF`, BIDIR)
- C2.t1 (`Capacitor 10 nF`, BIDIR)
- C2.t2 (`Capacitor 10 nF`, BIDIR)
- R11.t1 (`Resistor 47 kΩ`, BIDIR)
- R11.t2 (`Resistor 47 kΩ`, BIDIR)
- R12.t1 (`Resistor 4.7 kΩ`, BIDIR)
- R12.t2 (`Resistor 4.7 kΩ`, BIDIR)
- R13.t1 (`Resistor 10 kΩ`, BIDIR)
- R13.t2 (`Resistor 10 kΩ`, BIDIR)

Pull-up path: R11.t2 → + rail via R11 (47000 Ω)

## Net N1

Domain: ELECTRICAL

Readers (1):
- D10.cathode (`LED red`, IN)

Other ports on this net (1):
- R10.t1 (`Resistor 470 Ω`, BIDIR)


## Net N2 — − rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Other ports on this net (10):
- R1.t2 (`Resistor 470 Ω`, BIDIR)
- R10.t2 (`Resistor 470 Ω`, BIDIR)
- R2.t2 (`Resistor 470 Ω`, BIDIR)
- R3.t2 (`Resistor 470 Ω`, BIDIR)
- R4.t2 (`Resistor 470 Ω`, BIDIR)
- R5.t2 (`Resistor 470 Ω`, BIDIR)
- R6.t2 (`Resistor 470 Ω`, BIDIR)
- R7.t2 (`Resistor 470 Ω`, BIDIR)
- R8.t2 (`Resistor 470 Ω`, BIDIR)
- R9.t2 (`Resistor 470 Ω`, BIDIR)


## Net N3

Domain: ELECTRICAL

Readers (1):
- D9.cathode (`LED red`, IN)

Other ports on this net (1):
- R9.t1 (`Resistor 470 Ω`, BIDIR)


## Net N4

Domain: ELECTRICAL

Readers (1):
- D8.cathode (`LED red`, IN)

Other ports on this net (1):
- R8.t1 (`Resistor 470 Ω`, BIDIR)


## Net N5

Domain: ELECTRICAL

Readers (1):
- D7.cathode (`LED red`, IN)

Other ports on this net (1):
- R7.t1 (`Resistor 470 Ω`, BIDIR)


## Net N6

Domain: ELECTRICAL

Readers (1):
- D6.cathode (`LED red`, IN)

Other ports on this net (1):
- R6.t1 (`Resistor 470 Ω`, BIDIR)


## Net N7

Domain: ELECTRICAL

Readers (1):
- D5.cathode (`LED red`, IN)

Other ports on this net (1):
- R5.t1 (`Resistor 470 Ω`, BIDIR)


## Net N8

Domain: ELECTRICAL

Readers (1):
- D4.cathode (`LED red`, IN)

Other ports on this net (1):
- R4.t1 (`Resistor 470 Ω`, BIDIR)


## Net N9

Domain: ELECTRICAL

Readers (1):
- D3.cathode (`LED red`, IN)

Other ports on this net (1):
- R3.t1 (`Resistor 470 Ω`, BIDIR)


## Net N10

Domain: ELECTRICAL

Readers (1):
- D2.cathode (`LED red`, IN)

Other ports on this net (1):
- R2.t1 (`Resistor 470 Ω`, BIDIR)


## Net N11

Domain: ELECTRICAL

Readers (1):
- D1.cathode (`LED red`, IN)

Other ports on this net (1):
- R1.t1 (`Resistor 470 Ω`, BIDIR)


## Net N12

Domain: ELECTRICAL

Drivers (1):
- U2.Q9 (`CD4017`, OUT)

Readers (1):
- D10.anode (`LED red`, IN)


## Net N13

Domain: ELECTRICAL

Drivers (1):
- U2.Q8 (`CD4017`, OUT)

Readers (1):
- D9.anode (`LED red`, IN)


## Net N14

Domain: ELECTRICAL

Drivers (1):
- U2.Q7 (`CD4017`, OUT)

Readers (1):
- D8.anode (`LED red`, IN)


## Net N15

Domain: ELECTRICAL

Drivers (1):
- U2.Q6 (`CD4017`, OUT)

Readers (1):
- D7.anode (`LED red`, IN)


## Net N16

Domain: ELECTRICAL

Drivers (1):
- U2.Q5 (`CD4017`, OUT)

Readers (1):
- D6.anode (`LED red`, IN)


## Net N17

Domain: ELECTRICAL

Drivers (1):
- U2.Q4 (`CD4017`, OUT)

Readers (1):
- D5.anode (`LED red`, IN)


## Net N18

Domain: ELECTRICAL

Drivers (1):
- U2.Q3 (`CD4017`, OUT)

Readers (1):
- D4.anode (`LED red`, IN)


## Net N19

Domain: ELECTRICAL

Drivers (1):
- U2.Q2 (`CD4017`, OUT)

Readers (1):
- D3.anode (`LED red`, IN)


## Net N20

Domain: ELECTRICAL

Drivers (1):
- U2.Q1 (`CD4017`, OUT)

Readers (1):
- D2.anode (`LED red`, IN)


## Net N21

Domain: ELECTRICAL

Drivers (1):
- U2.Q0 (`CD4017`, OUT)

Readers (1):
- D1.anode (`LED red`, IN)


## Net N22 — − rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (2):
- U1.GND (`NE555`, IN)
- U2.VSS (`CD4017`, IN)


## Net N23 — + rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (2):
- U1.VCC (`NE555`, IN)
- U2.VDD (`CD4017`, IN)
