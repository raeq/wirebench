# Net Report — IsolatedRS232Link

10 logical net(s) across 2 ground domain(s): ELECTRICAL, ISOLATED_RS232.

## Net N0

Domain: ISOLATED_RS232

Drivers (1):
- U2.TOUT1 (`TRS3122E`, OUT)

Other ports on this net (2):
- J2.p1 (`Header1xNFemale`, BIDIR)
- P2.p1 (`Header1xNMale`, BIDIR)


## Net N1

Domain: ISOLATED_RS232

Readers (1):
- U2.RIN1 (`TRS3122E`, IN)

Other ports on this net (2):
- J2.p2 (`Header1xNFemale`, BIDIR)
- P2.p2 (`Header1xNMale`, BIDIR)


## Net N2 — − rail

Domain: ISOLATED_RS232

Drivers (1):
- Rail.out (`Rail`, OUT)

Other ports on this net (2):
- J2.p3 (`Header1xNFemale`, BIDIR)
- P2.p3 (`Header1xNMale`, BIDIR)


## Net N3

Domain: ISOLATED_RS232

Other ports on this net (2):
- J2.p4 (`Header1xNFemale`, BIDIR)
- P2.p4 (`Header1xNMale`, BIDIR)


## Net N4 — + rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Other ports on this net (2):
- J1.p1 (`Header1xNFemale`, BIDIR)
- P1.p1 (`Header1xNMale`, BIDIR)


## Net N5 — − rail

Domain: ELECTRICAL

Drivers (1):
- Rail.out (`Rail`, OUT)

Other ports on this net (2):
- J1.p2 (`Header1xNFemale`, BIDIR)
- P1.p2 (`Header1xNMale`, BIDIR)


## Net N6

Domain: ELECTRICAL

Readers (1):
- U1.INA (`ISOW7841`, IN)

Other ports on this net (2):
- J1.p3 (`Header1xNFemale`, BIDIR)
- P1.p3 (`Header1xNMale`, BIDIR)


## Net N7

Domain: ELECTRICAL

Drivers (1):
- U1.OUTD (`ISOW7841`, OUT)

Other ports on this net (2):
- J1.p4 (`Header1xNFemale`, BIDIR)
- P1.p4 (`Header1xNMale`, BIDIR)


## Net N8

Domain: ISOLATED_RS232

Drivers (1):
- U1.OUTA (`ISOW7841`, OUT)

Readers (1):
- U2.TIN1 (`TRS3122E`, IN)


## Net N9

Domain: ISOLATED_RS232

Drivers (1):
- U2.ROUT1 (`TRS3122E`, OUT)

Readers (1):
- U1.IND (`ISOW7841`, IN)
