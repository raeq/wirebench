# Net Report — WaterAlarm

9 logical net(s) across 1 ground domain(s): ELECTRICAL.

## Net N0 — − rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (4):
- U1.GND (`ULN2003A`, IN)
- U2.GND (`SN74HC04`, IN)
- U3.VSS (`CD4069`, IN)
- U4.VSS (`CD4043`, IN)


## Net N1 — + rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (3):
- U2.VCC (`SN74HC04`, IN)
- U3.VDD (`CD4069`, IN)
- U4.VDD (`CD4043`, IN)


## Net N2 — + rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (1):
- U4.oe (`CD4043`, IN)

Other ports on this net (2):
- R1.t2 (`Resistor 10 kΩ`, BIDIR)
- R2.t2 (`Resistor 10 kΩ`, BIDIR)


## Net N3 — − rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (16):
- U2.a_2 (`SN74HC04`, IN)
- U2.a_3 (`SN74HC04`, IN)
- U2.a_4 (`SN74HC04`, IN)
- U2.a_5 (`SN74HC04`, IN)
- U2.a_6 (`SN74HC04`, IN)
- U3.a_2 (`CD4069`, IN)
- U3.a_3 (`CD4069`, IN)
- U3.a_4 (`CD4069`, IN)
- U3.a_5 (`CD4069`, IN)
- U3.a_6 (`CD4069`, IN)
- U4.r_2 (`CD4043`, IN)
- U4.r_3 (`CD4043`, IN)
- U4.r_4 (`CD4043`, IN)
- U4.s_2 (`CD4043`, IN)
- U4.s_3 (`CD4043`, IN)
- U4.s_4 (`CD4043`, IN)


## Net N4

Domain: ELECTRICAL

Drivers (1):
- U1.out_2 (`ULN2003A`, OUT + OPEN_COLLECTOR)

Readers (1):
- U2.a_1 (`SN74HC04`, IN)

Other ports on this net (1):
- R2.t1 (`Resistor 10 kΩ`, BIDIR)

Pull-up path: R2.t2 → + rail via R2 (10000 Ω)

## Net N5

Domain: ELECTRICAL

Drivers (1):
- U1.out_1 (`ULN2003A`, OUT + OPEN_COLLECTOR)

Readers (1):
- U4.s_1 (`CD4043`, IN)

Other ports on this net (1):
- R1.t1 (`Resistor 10 kΩ`, BIDIR)

Pull-up path: R1.t2 → + rail via R1 (10000 Ω)

## Net N6

Domain: ELECTRICAL

Drivers (1):
- U3.y_1 (`CD4069`, OUT)

Readers (1):
- D2.anode (`LED green`, IN)


## Net N7

Domain: ELECTRICAL

Drivers (1):
- U4.q_1 (`CD4043`, OUT)

Readers (2):
- D1.anode (`LED red`, IN)
- U3.a_1 (`CD4069`, IN)


## Net N8

Domain: ELECTRICAL

Drivers (1):
- U2.y_1 (`SN74HC04`, OUT)

Readers (1):
- U4.r_1 (`CD4043`, IN)
