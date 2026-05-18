# Net Report — HelloLED

3 logical net(s) across 1 ground domain(s): ELECTRICAL.

## Net N0

Domain: ELECTRICAL

Readers (1):
- D1.anode (`LED red`, IN)

Other ports on this net (1):
- R1.t2 (`Resistor 330 Ω`, BIDIR)

Pull-up path: R1.t1 → + rail via R1 (330 Ω)

## Net N1 — − rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (1):
- D1.cathode (`LED red`, IN)


## Net N2 — + rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Other ports on this net (1):
- R1.t1 (`Resistor 330 Ω`, BIDIR)
