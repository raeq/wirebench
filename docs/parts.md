# Components

Every part wirebench models — every chip, connector, passive,
diode, transistor, relay, and the `Board` base class.  Each row
shows the refdes prefix the framework assigns when you place
the part, the import path, the kind of component, and a
one-line description from the class docstring.

**142 parts** across 7 categories.

| Refdes | Class | Kind | Description | Footprint | Datasheet |
|--------|-------|------|-------------|-----------|-----------|
| `U` | `components.chips.ams1117_33.AMS1117_33` | chip | AMS1117-3.3 — fixed +3.3V 1A LDO regulator (SOT-223). | `Package_TO_SOT_SMD:SOT-223-3_TabPin2` | — |
| `U` | `components.chips.ams1117_50.AMS1117_50` | chip | AMS1117-5.0 — fixed +5V 1A LDO regulator (SOT-223). | `Package_TO_SOT_SMD:SOT-223-3_TabPin2` | — |
| `U` | `components.chips.atmega2560.ATmega2560` | chip | Microchip ATmega2560 — 8-bit AVR microcontroller, 256 KB flash (TQFP-100). | `Package_QFP:TQFP-100_14x14mm_P0.5mm` | — |
| `U` | `components.chips.atmega328p.ATmega328P` | chip | Microchip ATmega328P — 8-bit AVR microcontroller, 32 KB flash (PDIP-28). | `Package_DIP:DIP-28_W7.62mm` | — |
| `U` | `components.chips.atmega32u4.ATmega32U4` | chip | Microchip ATmega32U4 — 8-bit AVR microcontroller with USB device, 32 KB flash (TQFP-44). | `Package_QFP:TQFP-44_10x10mm_P0.8mm` | — |
| `U` | `components.chips.attiny84.ATtiny84` | chip | Microchip ATtiny84 — 8-bit AVR microcontroller, 8 KB flash (PDIP-14). | `Package_DIP:DIP-14_W7.62mm` | — |
| `U` | `components.chips.attiny85.ATtiny85` | chip | Microchip ATtiny85 — 8-bit AVR microcontroller, 8 KB flash (PDIP-8). | `Package_DIP:DIP-8_W7.62mm` | — |
| `J` | `components.connectors.audio.Audio3p5mmTRRSJack` | connector | 3.5 mm TRRS audio jack (4 contacts: tip/ring1/ring2/sleeve). | `Connector_Audio:Jack_3.5mm_TRRS_QingPu_WQP-PJ398SM_Vertical` | — |
| `P` | `components.connectors.audio.Audio3p5mmTRRSPlug` | connector | 3.5 mm TRRS audio plug. | `Connector_Audio:Jack_3.5mm_TRRS_QingPu_WQP-PJ398SM_Vertical` | — |
| `J` | `components.connectors.audio.Audio3p5mmTRSJack` | connector | 3.5 mm TRS audio jack (board-side). | `Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` | — |
| `P` | `components.connectors.audio.Audio3p5mmTRSPlug` | connector | 3.5 mm TRS audio plug (cable-side). | `Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` | — |
| `Q` | `components.transistors.bc547.BC547` | transistor | NPN BJT, general-purpose small-signal (100 mA, 45 V). | `Package_TO_SOT_THT:TO-92_Inline` | — |
| `Q` | `components.transistors.bc548.BC548` | transistor | NPN BJT, general-purpose small-signal (100 mA, 30 V). | `Package_TO_SOT_THT:TO-92_Inline` | — |
| `Q` | `components.transistors.bc557.BC557` | transistor | PNP BJT, general-purpose small-signal (100 mA, 45 V). | `Package_TO_SOT_THT:TO-92_Inline` | — |
| `U` | `components.chips.bmp280.BMP280` | chip | Bosch BMP280 — digital barometric pressure & temperature sensor (LGA-8). | `Package_LGA:Bosch_LGA-8_2x2.5mm_P0.65mm` | — |
| `U` | `components.chips.bq27546g1.BQ27546G1` | chip | Texas Instruments BQ27546-G1 — single-cell Li-Ion fuel gauge for | `Package_BGA:Texas_S-PVQFN-N15_2.61x1.96mm_DSBGA` | — |
| `Q` | `components.transistors.bs170.BS170` | transistor | N-channel enhancement-mode MOSFET, small-signal (500 mA, 60 V). | `Package_TO_SOT_THT:TO-92_Inline` | — |
| `J` | `components.connectors.barrel.BarrelJack5p5x2p1` | connector | 5.5 mm × 2.1 mm DC barrel jack (board-side). | `Connector_BarrelJack:BarrelJack_Horizontal` | — |
| `J` | `components.connectors.barrel.BarrelJack5p5x2p5` | connector | 5.5 mm × 2.5 mm DC barrel jack (board-side). | `Connector_BarrelJack:BarrelJack_2.5mm_Horizontal` | — |
| `P` | `components.connectors.barrel.BarrelPlug5p5x2p1` | connector | 5.5 mm × 2.1 mm DC barrel plug. | `Connector_BarrelJack:BarrelJack_Horizontal` | — |
| `P` | `components.connectors.barrel.BarrelPlug5p5x2p5` | connector | 5.5 mm × 2.5 mm DC barrel plug. | `Connector_BarrelJack:BarrelJack_2.5mm_Horizontal` | — |
| `A` | `framework.board.Board` | board | A printed circuit board: a populated PCB with name, revision, | various | — |
| `U` | `components.chips.cd4017.CD4017` | chip | RCA / Texas Instruments CD4017 — CMOS decade Johnson counter | `Package_DIP:DIP-16_W7.62mm` | — |
| `U` | `components.chips.cd4043.CD4043` | chip | Texas Instruments CD4043B — quad NOR-based RS latch with tri-state outputs. | `Package_DIP:DIP-16_W7.62mm` | — |
| `U` | `components.chips.cd4069.CD4069` | chip | Texas Instruments CD4069UB — hex unbuffered inverter. | `Package_DIP:DIP-14_W7.62mm` | — |
| `C` | `components.passives.capacitor.Capacitor` | passive | Ideal capacitor.  Charge accumulates: Q = C × V, I = C × dV/dt. | `Capacitor_SMD:C_0603_1608Metric` | — |
| `BT` | `components.passives.cell.Cell` | passive | Single-cell Li-Ion battery, modelled as a voltage source. | `Battery:BatteryHolder_Keystone_1042_1x18650` | — |
| `D` | `components.diodes.d1n4001.D1N4001` | diode | 1N4001 — 50 V / 1 A general-purpose silicon rectifier (DO-41). | `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal` | — |
| `D` | `components.diodes.d1n4007.D1N4007` | diode | 1N4007 — 1000 V / 1 A general-purpose silicon rectifier (DO-41). | `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal` | — |
| `D` | `components.diodes.d1n4148.D1N4148` | diode | 1N4148 — fast signal switching diode (100 V / 200 mA, DO-35). | `Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal` | — |
| `D` | `components.diodes.d1n4728a.D1N4728A` | diode | 1N4728A — 1 W Zener voltage reference / regulator at 3.3 V (DO-41). | `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal` | — |
| `D` | `components.diodes.d1n4733a.D1N4733A` | diode | 1N4733A — 1 W Zener voltage reference / regulator at 5.1 V (DO-41). | `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal` | — |
| `D` | `components.diodes.d1n4742a.D1N4742A` | diode | 1N4742A — 1 W Zener voltage reference / regulator at 12 V (DO-41). | `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal` | — |
| `D` | `components.diodes.d1n5817.D1N5817` | diode | 1N5817 — Schottky barrier rectifier (20 V / 1 A, low V_F, DO-41). | `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal` | — |
| `U` | `components.chips.dht11.DHT11` | chip | Aosong DHT11 — single-bus humidity and temperature sensor (4-pin | `Package_TO_SOT_THT:DHT11` | — |
| `U` | `components.chips.dht11_module.DHT11_Module` | chip | Aosong DHT11 breakout module — small PCB carrying a bare DHT11 | `Package_TO_SOT_THT:DHT11_Module` | — |
| `U` | `components.chips.drv8313.DRV8313` | chip | Texas Instruments DRV8313 — three-channel brushless-DC pre-driver | `Package_SO:HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP3.4x9.5mm` | — |
| `U` | `components.chips.ds1307.DS1307` | chip | Analog Devices (Maxim) DS1307 — I²C real-time clock with 56-byte | `Package_DIP:DIP-8_W7.62mm` | — |
| `U` | `components.chips.ds18b20.DS18B20` | chip | Analog Devices (Maxim) DS18B20 — 1-Wire programmable digital | `Package_TO_SOT_THT:TO-92_Inline` | — |
| `U` | `components.chips.display5641as.Display5641AS` | chip | 5641AS — 4-digit common-anode 7-segment LED display module | `Display_7Segment:Display_5641AS` | — |
| `U` | `components.chips.esp32_wroom_32.ESP32_WROOM_32` | chip | Espressif ESP32-WROOM-32 — Wi-Fi + Bluetooth SMD module with ESP32-D0WDQ6, 4 MB flash (38-pad). | `RF_Module:ESP32-WROOM-32` | — |
| `U` | `components.chips.esp8266_12f.ESP8266_12F` | chip | Ai-Thinker ESP-12F — Wi-Fi SMD module with ESP8266EX, 4 MB flash (22-pad). | `RF_Module:ESP-12E` | — |
| `U` | `components.chips.hcsr04.HCSR04` | chip | HC-SR04 — ultrasonic ranging breakout module (4-pin SIP, 2.54 mm). | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` | — |
| `P` | `components.connectors.video.HDMITypeAPlug` | connector | HDMI Type-A plug (cable-side). | `Connector_Video:HDMI_A_Amphenol_10029449-001RLF_Horizontal` | — |
| `J` | `components.connectors.video.HDMITypeAReceptacle` | connector | HDMI Type-A receptacle (board-side). | `Connector_Video:HDMI_A_Amphenol_10029449-001RLF_Horizontal` | — |
| `J` | `components.connectors.headers.Header1xNFemale` | connector | 1×N socket header strip — female counterpart to Header1xNMale. | various | — |
| `P` | `components.connectors.headers.Header1xNMale` | connector | 1×N pin header strip, snap-apart.  Common pitches: 2.54 mm (0.1"), | various | — |
| `J` | `components.connectors.headers.Header2xNFemale` | connector | 2×N dual-row socket header — female counterpart to Header2xNMale. | various | — |
| `P` | `components.connectors.headers.Header2xNMale` | connector | 2×N dual-row pin header strip.  `pin_count` here is the *total* pin | various | — |
| `P` | `components.connectors.idc.IDC2xNMale` | connector | 2×N shrouded male IDC header, board-side. | various | — |
| `J` | `components.connectors.idc.IDC2xNSocket` | connector | 2×N female IDC ribbon-cable socket. | various | — |
| `Q` | `components.transistors.irfz44n.IRFZ44N` | transistor | Standard-gate N-channel power MOSFET (49 A, 55 V). | `Package_TO_SOT_THT:TO-220-3_Vertical` | — |
| `Q` | `components.transistors.irlb8721.IRLB8721` | transistor | Logic-level N-channel power MOSFET (62 A, 30 V). | `Package_TO_SOT_THT:TO-220-3_Vertical` | — |
| `U` | `components.chips.isow7841.ISOW7841` | chip | Texas Instruments ISOW7841 — reinforced four-channel digital | `Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm` | — |
| `L` | `components.passives.inductor.Inductor` | passive | Ideal inductor.  Stores energy in a magnetic field: V = L × dI/dt. | `Inductor_SMD:L_0603_1608Metric` | — |
| — | `components.chips.concepts.inverter.Inverter` | cell | A single NOT gate cell. Pin a is input, pin y is output: y = NOT(a). | — | — |
| `P` | `components.connectors.jst_gh.JSTGHBoardSide` | connector | JST GH board-side male header (1.25 mm pitch). | various | — |
| `J` | `components.connectors.jst_gh.JSTGHCableHousing` | connector | JST GH cable-side female crimp housing (1.25 mm pitch). | various | — |
| `P` | `components.connectors.jst_ph.JSTPHBoardSide` | connector | JST PH board-side male header (2.0 mm pitch). | various | — |
| `J` | `components.connectors.jst_ph.JSTPHCableHousing` | connector | JST PH cable-side female crimp housing (2.0 mm pitch). | various | — |
| `P` | `components.connectors.jst_sh.JSTSHBoardSide` | connector | JST SH board-side male header (1.0 mm pitch). | various | — |
| `J` | `components.connectors.jst_sh.JSTSHCableHousing` | connector | JST SH cable-side female crimp housing (1.0 mm pitch). | various | — |
| `P` | `components.connectors.jst_xh.JSTXHBoardSide` | connector | JST XH board-side male header (2.5 mm pitch). | various | — |
| `J` | `components.connectors.jst_xh.JSTXHCableHousing` | connector | JST XH cable-side female crimp housing (2.5 mm pitch). | various | — |
| `D` | `components.passives.led.LED` | passive | Light-emitting diode. | `LED_SMD:LED_0805` | — |
| `U` | `components.chips.lm311.LM311` | chip | Texas Instruments LM311 — single high-speed open-collector comparator | `Package_DIP:DIP-8_W7.62mm` | — |
| `U` | `components.chips.lm317.LM317` | chip | Texas Instruments LM317 — adjustable +1.25V to +37V positive regulator (TO-220). | `Package_TO_SOT_THT:TO-220-3_Vertical` | — |
| `U` | `components.chips.lm324.LM324` | chip | Texas Instruments LM324 — quad single-supply low-power bipolar | `Package_DIP:DIP-14_W7.62mm` | — |
| `U` | `components.chips.lm337.LM337` | chip | Texas Instruments LM337 — adjustable -1.25V to -37V negative regulator (TO-220). | `Package_TO_SOT_THT:TO-220-3_Vertical` | — |
| `U` | `components.chips.lm339.LM339` | chip | Texas Instruments LM339 — quad open-collector differential comparator (PDIP-14). | `Package_DIP:DIP-14_W7.62mm` | — |
| `U` | `components.chips.lm358.LM358` | chip | Texas Instruments LM358 — dual single-supply low-power bipolar | `Package_DIP:DIP-8_W7.62mm` | — |
| `U` | `components.chips.lm386.LM386` | chip | Texas Instruments LM386 — low-voltage audio power amplifier (DIP-8). | `Package_DIP:DIP-8_W7.62mm` | — |
| `U` | `components.chips.lm393.LM393` | chip | Texas Instruments LM393 — dual differential voltage comparator. | `Package_DIP:DIP-8_W7.62mm` | — |
| `U` | `components.chips.lm5002.LM5002` | chip | Texas Instruments LM5002 — 3.1- to 75-V wide-Vin, 0.5-A | `Package_SO:VSSOP-8_3.0x3.0mm_P0.65mm` | — |
| `U` | `components.chips.lm5160.LM5160` | chip | Texas Instruments LM5160 — 65-V, 2-A synchronous step-down | `Package_SO:HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm` | — |
| `U` | `components.chips.lm741.LM741` | chip | Texas Instruments LM741 — classic single bipolar op-amp (DIP-8). | `Package_DIP:DIP-8_W7.62mm` | — |
| `U` | `components.chips.lm7805.LM7805` | chip | Texas Instruments LM7805 — fixed +5V positive linear regulator (TO-220). | `Package_TO_SOT_THT:TO-220-3_Vertical` | — |
| `U` | `components.chips.lm7812.LM7812` | chip | Texas Instruments LM7812 — fixed +12V positive linear regulator (TO-220). | `Package_TO_SOT_THT:TO-220-3_Vertical` | — |
| `U` | `components.chips.lm7905.LM7905` | chip | Texas Instruments LM7905 — fixed -5V negative linear regulator (TO-220). | `Package_TO_SOT_THT:TO-220-3_Vertical` | — |
| `U` | `components.chips.lmv358.LMV358` | chip | Texas Instruments LMV358 — dual low-voltage bipolar op-amp | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` | — |
| `U` | `components.chips.lp2950.LP2950` | chip | Texas Instruments LP2950 — micropower +5V LDO regulator, 100mA (TO-92). | `Package_TO_SOT_THT:TO-92_Inline` | — |
| `U` | `components.chips.max232.MAX232` | chip | Texas Instruments MAX232 — dual RS-232 driver/receiver with charge-pump (DIP-16). | `Package_DIP:DIP-16_W7.62mm` | — |
| `U` | `components.chips.max7219.MAX7219` | chip | Analog Devices (Maxim) MAX7219 — serial-input 8-digit common-cathode | `Package_DIP:DIP-24_W15.24mm` | — |
| `U` | `components.chips.mcp6002.MCP6002` | chip | Microchip MCP6002 — dual 1 MHz rail-to-rail CMOS op-amp (DIP-8). | `Package_DIP:DIP-8_W7.62mm` | — |
| `U` | `components.chips.moc3021.MOC3021` | chip | Vishay MOC3021 — non-zero-crossing triac driver optocoupler (DIP-6). | `Package_DIP:DIP-6_W7.62mm` | — |
| `U` | `components.chips.mpu6050.MPU6050` | chip | InvenSense / TDK MPU-6050 — 6-axis MEMS IMU (QFN-24). | `Sensor_Motion:InvenSense_QFN-24_4x4mm_P0.5mm` | — |
| `P` | `components.connectors.sd.MicroSDCard` | connector | A microSD card — modelled as a connector because the gold | various | — |
| `J` | `components.connectors.sd.MicroSDCardSlot` | connector | microSD card slot (board-side).  8 contacts. | `Connector_Card:microSD_HC_Hirose_DM3D-SF` | — |
| `U` | `components.chips.ne555.NE555` | chip | Texas Instruments NE555 — precision astable/monostable timer (DIP-8). | `Package_DIP:DIP-8_W7.62mm` | — |
| `U` | `components.chips.opa2134.OPA2134` | chip | Texas Instruments / Burr-Brown OPA2134 — dual audio FET-input | `Package_DIP:DIP-8_W7.62mm` | — |
| `U` | `components.chips.opto_4n25.OPTO_4N25` | chip | onsemi 4N25 — general-purpose phototransistor optocoupler with base pin (DIP-6). | `Package_DIP:DIP-6_W7.62mm` | — |
| `U` | `components.chips.opto_tlp521.OPTO_TLP521` | chip | Toshiba TLP521-1 — single-channel phototransistor optocoupler (DIP-4). | `Package_DIP:DIP-4_W7.62mm` | — |
| `Q` | `components.transistors.q2n2222.Q2N2222` | transistor | NPN BJT, medium-power switching (800 mA, 40 V). | `Package_TO_SOT_THT:TO-92_Inline` | — |
| `Q` | `components.transistors.q2n3904.Q2N3904` | transistor | NPN BJT, general-purpose small-signal (200 mA, 40 V). | `Package_TO_SOT_THT:TO-92_Inline` | — |
| `Q` | `components.transistors.q2n3906.Q2N3906` | transistor | PNP BJT, general-purpose small-signal (200 mA, 40 V). | `Package_TO_SOT_THT:TO-92_Inline` | — |
| `Q` | `components.transistors.q2n7000.Q2N7000` | transistor | N-channel enhancement-mode MOSFET, small-signal (200 mA, 60 V). | `Package_TO_SOT_THT:TO-92_Inline` | — |
| `J` | `components.connectors.network.RJ45Jack` | connector | RJ45 / 8P8C modular jack, board-side.  T568B pin labels. | `Connector_RJ:RJ45_Wuerth_7499010121A_Horizontal` | — |
| `P` | `components.connectors.network.RJ45Plug` | connector | RJ45 / 8P8C modular plug, cable-side. | `Connector_RJ:RJ45_Wuerth_7499010121A_Horizontal` | — |
| `U` | `components.chips.rp2040.RP2040` | chip | Raspberry Pi RP2040 — dual ARM Cortex-M0+ microcontroller, 264 KB SRAM (QFN-56). | `Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm` | — |
| — | `components.passives.rail.Rail` | passive | Constant logic rail.  Drives `out` to a fixed level (HIGH or LOW). | various | — |
| `K` | `components.relays.spdt.Relay_SPDT` | cell | SPDT electromechanical relay — single coil drives one common | `Relay_THT:Relay_SPDT_Generic` | — |
| `R` | `components.passives.resistor.Resistor` | passive | Ideal resistor. Ohm's law: V = I × R. | `Resistor_SMD:R_0603_1608Metric` | — |
| `P` | `components.connectors.sd.SDCard` | connector | A full-size SD card.  Modelled as a connector for the same | various | — |
| `J` | `components.connectors.sd.SDCardSlot` | connector | Full-size SD card slot (board-side).  9 contacts including | `Connector_Card:SD_TE_2041021` | — |
| `U` | `components.chips.sn74ahc1g14.SN74AHC1G14` | chip | Texas Instruments SN74AHC1G14 — single Schmitt-trigger inverter | `Package_TO_SOT_SMD:SOT-23-5` | — |
| `U` | `components.chips.sn74hc00.SN74HC00` | chip | Texas Instruments SN74HC00 — quad 2-input NAND gate (DIP-14). | `Package_DIP:DIP-14_W7.62mm` | — |
| `U` | `components.chips.sn74hc02.SN74HC02` | chip | Texas Instruments SN74HC02 — quad 2-input NOR gate (DIP-14). | `Package_DIP:DIP-14_W7.62mm` | — |
| `U` | `components.chips.sn74hc04.SN74HC04` | chip | Texas Instruments SN74HC04 — hex inverting buffer. | `Package_DIP:DIP-14_W7.62mm` | — |
| `U` | `components.chips.sn74hc08.SN74HC08` | chip | Texas Instruments SN74HC08 — quad 2-input AND gate (DIP-14). | `Package_DIP:DIP-14_W7.62mm` | — |
| `U` | `components.chips.sn74hc138.SN74HC138` | chip | Texas Instruments SN74HC138 — 3-to-8 line decoder/demultiplexer (DIP-16). | `Package_DIP:DIP-16_W7.62mm` | — |
| `U` | `components.chips.sn74hc139.SN74HC139` | chip | Texas Instruments SN74HC139 — dual 2-to-4 line decoder/demultiplexer (DIP-16). | `Package_DIP:DIP-16_W7.62mm` | — |
| `U` | `components.chips.sn74hc151.SN74HC151` | chip | Texas Instruments SN74HC151 — 8-to-1 data selector/multiplexer (DIP-16). | `Package_DIP:DIP-16_W7.62mm` | — |
| `U` | `components.chips.sn74hc157.SN74HC157` | chip | Texas Instruments SN74HC157 — quad 2-to-1 data selector/multiplexer (DIP-16). | `Package_DIP:DIP-16_W7.62mm` | — |
| `U` | `components.chips.sn74hc165.SN74HC165` | chip | Texas Instruments SN74HC165 — 8-bit parallel-load shift register (parallel-to-serial) (DIP-16). | `Package_DIP:DIP-16_W7.62mm` | — |
| `U` | `components.chips.sn74hc174.SN74HC174` | chip | Texas Instruments SN74HC174 — hex D-type flip-flop with common clock and clear (DIP-16). | `Package_DIP:DIP-16_W7.62mm` | — |
| `U` | `components.chips.sn74hc273.SN74HC273` | chip | Texas Instruments SN74HC273 — octal D-type flip-flop with common clock and clear (DIP-20). | `Package_DIP:DIP-20_W7.62mm` | — |
| `U` | `components.chips.sn74hc32.SN74HC32` | chip | Texas Instruments SN74HC32 — quad 2-input OR gate (DIP-14). | `Package_DIP:DIP-14_W7.62mm` | — |
| `U` | `components.chips.sn74hc541.SN74HC541` | chip | Texas Instruments SN74HC541 — octal buffer/line driver with 3-state outputs (DIP-20). | `Package_DIP:DIP-20_W7.62mm` | — |
| `U` | `components.chips.sn74hc595.SN74HC595` | chip | Texas Instruments SN74HC595 — 8-bit serial-in/parallel-out shift register with output latch (DIP-16). | `Package_DIP:DIP-16_W7.62mm` | — |
| `U` | `components.chips.sn74hc74.SN74HC74` | chip | Texas Instruments SN74HC74 — dual D-type flip-flop with preset and clear (DIP-14). | `Package_DIP:DIP-14_W7.62mm` | — |
| `U` | `components.chips.sn74hc86.SN74HC86` | chip | Texas Instruments SN74HC86 — quad 2-input XOR gate (DIP-14). | `Package_DIP:DIP-14_W7.62mm` | — |
| `U` | `components.chips.stm32f103c8t6.STM32F103C8T6` | chip | STMicroelectronics STM32F103C8T6 — ARM Cortex-M3 microcontroller, 64 KB flash (LQFP-48). | `Package_QFP:LQFP-48_7x7mm_P0.5mm` | — |
| `U` | `components.chips.stm32f411ceu6.STM32F411CEU6` | chip | STMicroelectronics STM32F411CEU6 — ARM Cortex-M4F microcontroller, 512 KB flash (UFQFPN-48). | `Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm` | — |
| `J` | `components.connectors.screw_terminal.ScrewTerminalBlock` | connector | PCB-mount screw terminal block. | various | — |
| `Q` | `components.transistors.tip120.TIP120` | transistor | NPN Darlington power transistor (5 A, 60 V). | `Package_TO_SOT_THT:TO-220-3_Vertical` | — |
| `U` | `components.chips.tl072.TL072` | chip | Texas Instruments TL072 — dual low-noise JFET-input op-amp | `Package_DIP:DIP-8_W7.62mm` | — |
| `U` | `components.chips.tl074.TL074` | chip | Texas Instruments TL074 — quad low-noise JFET-input op-amp | `Package_DIP:DIP-14_W7.62mm` | — |
| `U` | `components.chips.tlc5940.TLC5940` | chip | Texas Instruments TLC5940 — 16-channel constant-current sink LED driver (DIP-28). | `Package_DIP:DIP-28_W7.62mm` | — |
| `U` | `components.chips.tlv3401.TLV3401` | chip | Texas Instruments TLV3401 — single nanopower open-drain CMOS comparator (SOT-23-5). | `Package_TO_SOT_SMD:SOT-23-5` | — |
| `U` | `components.chips.tmp302.TMP302` | chip | Texas Instruments TMP302 — low-power resistor-programmable | `Package_SO:SOT-563_1.6x1.6mm_P0.5mm` | — |
| `U` | `components.chips.tmp36.TMP36` | chip | Analog Devices TMP36 — low-voltage analog temperature sensor (TO-92). | `Package_TO_SOT_THT:TO-92_Inline` | — |
| `U` | `components.chips.tps2660.TPS2660` | chip | Texas Instruments TPS2660 — 4.2-to-60-V, 150-mΩ industrial | `Package_SON:WSON-10-1EP_3x3mm_P0.5mm_EP1.6x2.4mm` | — |
| `U` | `components.chips.trs3122e.TRS3122E` | chip | Texas Instruments TRS3122E — full-duplex RS-232 line driver / | `Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm` | — |
| `U` | `components.chips.uln2003a.ULN2003A` | chip | Seven-channel NPN Darlington transistor array (TI ULN2003A). | `Package_DIP:DIP-16_W7.62mm` | — |
| `P` | `components.connectors.usb.USBAPlug` | connector | Standard USB-A plug (cable-side). | `Connector_USB:USB_A_Stewart_SS-52100-001_Horizontal` | — |
| `J` | `components.connectors.usb.USBAReceptacle` | connector | Standard USB-A receptacle (board-side). | `Connector_USB:USB_A_Stewart_SS-52100-001_Horizontal` | — |
| `P` | `components.connectors.usb.USBBPlug` | connector | USB Type-B plug. | `Connector_USB:USB_B_Wuerth_61400826021_Horizontal` | — |
| `J` | `components.connectors.usb.USBBReceptacle` | connector | USB Type-B receptacle (square printer-style). | `Connector_USB:USB_B_Wuerth_61400826021_Horizontal` | — |
| `P` | `components.connectors.usb.USBCPlug` | connector | USB Type-C plug (full 24-pin). | `Connector_USB:USB_C_Receptacle_GCT_USB4105-GF-A_16P_TopMnt_Horizontal` | — |
| `J` | `components.connectors.usb.USBCReceptacle` | connector | USB Type-C receptacle (full 24-pin). | `Connector_USB:USB_C_Receptacle_GCT_USB4105-GF-A_16P_TopMnt_Horizontal` | — |
| `P` | `components.connectors.usb.USBMicroBPlug` | connector | USB Micro-B plug. | `Connector_USB:USB_Micro-B_GCT_USB3076-30-A_Horizontal` | — |
| `J` | `components.connectors.usb.USBMicroBReceptacle` | connector | USB Micro-B receptacle. | `Connector_USB:USB_Micro-B_GCT_USB3076-30-A_Horizontal` | — |

## Filtering at the command line

The same catalogue is available locally via the `wirebench parts` CLI:

```bash
wirebench parts                    # every part, aligned text
wirebench parts --kind chip        # only chips
wirebench parts --prefix R         # only refdes-R parts (Resistor)
wirebench parts --has-footprint    # only parts with a fixed footprint
wirebench parts --pin-function POWER
wirebench parts --json             # structured JSON for tooling
```

Filters compose with AND — combine `--kind`, `--prefix`, `--has-cell`, `--has-footprint`, and `--pin-function` freely.
