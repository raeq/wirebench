# Net Report — FiveVoltRailPower

5 logical net(s) across 1 ground domain(s): ELECTRICAL.

## Net N0

Domain: ELECTRICAL

Readers (1):
- D3.anode (`LED green`, IN)

Other ports on this net (1):
- R1.t2 (`Resistor 470 Ω`, BIDIR)


## Net N1

Domain: ELECTRICAL

Drivers (1):
- BT1.neg (`CR2032Stack`, OUT)

Readers (2):
- D3.cathode (`LED green`, IN)
- U1.GND (`LM7805`, IN)

Other ports on this net (3):
- C1.t2 (`Capacitor 100 nF`, BIDIR)
- C2.t2 (`Capacitor 10 µF`, BIDIR)
- D2.anode (`D1N4733A`, BIDIR)


## Net N2

Domain: ELECTRICAL

Drivers (1):
- U1.OUTPUT (`LM7805`, OUT)

Other ports on this net (3):
- C2.t1 (`Capacitor 10 µF`, BIDIR)
- D2.cathode (`D1N4733A`, BIDIR)
- R1.t1 (`Resistor 470 Ω`, BIDIR)


## Net N3

Domain: ELECTRICAL

Drivers (1):
- SeriesRectifier.output (`SeriesRectifier`, OUT)

Readers (1):
- U1.INPUT (`LM7805`, IN)

Other ports on this net (2):
- C1.t1 (`Capacitor 100 nF`, BIDIR)
- D1.cathode (`D1N5817`, BIDIR)


## Net N4

Domain: ELECTRICAL

Drivers (1):
- BT1.pos (`CR2032Stack`, OUT)

Readers (1):
- SeriesRectifier.input (`SeriesRectifier`, IN)

Other ports on this net (3):
- D1.anode (`D1N5817`, BIDIR)
- P1.p1 (`Header1xNMale`, BIDIR)
- P1.p2 (`Header1xNMale`, BIDIR)
