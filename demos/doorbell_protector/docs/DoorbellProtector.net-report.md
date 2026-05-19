# Net Report — DoorbellProtector

8 logical net(s) across 1 ground domain(s): ELECTRICAL.

## Net N0

Domain: ELECTRICAL

Drivers (1):
- U1.OUT (`NE555_Monostable`, OUT)

Readers (2):
- D2.anode (`LED red`, IN)
- U2.TRIG (`NE555_Monostable`, IN)

Other ports on this net (6):
- C4.t1 (`Capacitor 100 nF`, BIDIR)
- C4.t2 (`Capacitor 100 nF`, BIDIR)
- K1.coil_plus (`Relay_SPDT`, BIDIR)
- Q1.b (`BC548`, BIDIR)
- R1.t1 (`Resistor 1 kΩ`, BIDIR)
- R1.t2 (`Resistor 1 kΩ`, BIDIR)


## Net N1

Domain: ELECTRICAL

Other ports on this net (3):
- D1.anode (`D1N4007`, BIDIR)
- K1.coil_minus (`Relay_SPDT`, BIDIR)
- Q1.c (`BC548`, BIDIR)


## Net N2 — + rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (1):
- U2.RESET (`NE555_Monostable`, IN)

Other ports on this net (19):
- C1.t1 (`Capacitor 100 nF`, BIDIR)
- C1.t2 (`Capacitor 100 nF`, BIDIR)
- C2.t1 (`Capacitor 4.7 µF`, BIDIR)
- C2.t2 (`Capacitor 4.7 µF`, BIDIR)
- C3.t1 (`Capacitor 100 nF`, BIDIR)
- C3.t2 (`Capacitor 100 nF`, BIDIR)
- C5.t1 (`Capacitor 47 µF`, BIDIR)
- C5.t2 (`Capacitor 47 µF`, BIDIR)
- D1.cathode (`D1N4007`, BIDIR)
- R2.t1 (`Resistor 1 MΩ`, BIDIR)
- R2.t2 (`Resistor 1 MΩ`, BIDIR)
- R3.t1 (`Resistor 1 MΩ`, BIDIR)
- R3.t2 (`Resistor 1 MΩ`, BIDIR)
- R6.t1 (`Resistor 1 MΩ`, BIDIR)
- R6.t2 (`Resistor 1 MΩ`, BIDIR)
- R7.t1 (`Resistor 4.7 kΩ`, BIDIR)
- R7.t2 (`Resistor 4.7 kΩ`, BIDIR)
- R8.t1 (`Resistor 47 kΩ`, BIDIR)
- R8.t2 (`Resistor 47 kΩ`, BIDIR)

Pull-up path: R2.t2 → + rail via R2 (1e+06 Ω)

## Net N3

Domain: ELECTRICAL

Drivers (1):
- Inverter.y (`Inverter`, OUT)

Readers (1):
- U1.RESET (`NE555_Monostable`, IN)

Other ports on this net (3):
- Q2.c (`Q2N3904`, BIDIR)
- R5.t1 (`Resistor 10 kΩ`, BIDIR)
- R5.t2 (`Resistor 10 kΩ`, BIDIR)


## Net N4

Domain: ELECTRICAL

Drivers (1):
- U2.OUT (`NE555_Monostable`, OUT)

Readers (1):
- Inverter.a (`Inverter`, IN)

Other ports on this net (3):
- Q2.b (`Q2N3904`, BIDIR)
- R4.t1 (`Resistor 1 kΩ`, BIDIR)
- R4.t2 (`Resistor 1 kΩ`, BIDIR)


## Net N5 — − rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (1):
- D2.cathode (`LED red`, IN)

Other ports on this net (2):
- Q1.e (`BC548`, BIDIR)
- Q2.e (`Q2N3904`, BIDIR)


## Net N6 — − rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (2):
- U1.GND (`NE555_Monostable`, IN)
- U2.GND (`NE555_Monostable`, IN)


## Net N7 — + rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Readers (2):
- U1.VCC (`NE555_Monostable`, IN)
- U2.VCC (`NE555_Monostable`, IN)
