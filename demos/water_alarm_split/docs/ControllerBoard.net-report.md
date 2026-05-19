# Net Report — ControllerBoard

7 logical net(s) across 1 ground domain(s): ELECTRICAL.

## Net N0

Domain: ELECTRICAL

Readers (1):
- U3.s_1 (`CD4043`, IN)


## Net N1

Domain: ELECTRICAL

Readers (1):
- U1.a_1 (`SN74HC04`, IN)


## Net N2 — + rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (1):
- U3.oe (`CD4043`, IN)


## Net N3 — − rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (18):
- D1.cathode (`LED red`, IN)
- D2.cathode (`LED green`, IN)
- U1.a_2 (`SN74HC04`, IN)
- U1.a_3 (`SN74HC04`, IN)
- U1.a_4 (`SN74HC04`, IN)
- U1.a_5 (`SN74HC04`, IN)
- U1.a_6 (`SN74HC04`, IN)
- U2.a_2 (`CD4069`, IN)
- U2.a_3 (`CD4069`, IN)
- U2.a_4 (`CD4069`, IN)
- U2.a_5 (`CD4069`, IN)
- U2.a_6 (`CD4069`, IN)
- U3.r_2 (`CD4043`, IN)
- U3.r_3 (`CD4043`, IN)
- U3.r_4 (`CD4043`, IN)
- U3.s_2 (`CD4043`, IN)
- U3.s_3 (`CD4043`, IN)
- U3.s_4 (`CD4043`, IN)


## Net N4

Domain: ELECTRICAL

Drivers (1):
- U2.y_1 (`CD4069`, OUT)

Readers (1):
- D2.anode (`LED green`, IN)


## Net N5

Domain: ELECTRICAL

Drivers (1):
- U3.q_1 (`CD4043`, OUT)

Readers (2):
- D1.anode (`LED red`, IN)
- U2.a_1 (`CD4069`, IN)


## Net N6

Domain: ELECTRICAL

Drivers (1):
- U1.y_1 (`SN74HC04`, OUT)

Readers (1):
- U3.r_1 (`CD4043`, IN)
