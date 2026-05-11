# Component Library Data

**Total parts catalogued**: 74
**Generated**: 2026-05-11
**Sources**: All data sourced from manufacturer datasheets cited per-part.
**Follow-on**: Implementation spec for these parts (TBD) will translate this catalogue into `src/components/...` classes.

## Summary table

| Class | Refdes | Primary package |
|-------|:------:|-----------------|
| ATmega328P | U | PDIP-28 |
| ATmega2560 | U | TQFP-100 |
| ATmega32U4 | U | TQFP-44 |
| ATtiny85 | U | PDIP-8 |
| ATtiny84 | U | PDIP-14 |
| STM32F103C8T6 | U | LQFP-48 |
| STM32F411CEU6 | U | UFQFPN-48 |
| RP2040 | U | QFN-56 |
| ESP32_WROOM_32 | U | SMD module (38-pad) |
| ESP8266_12F | U | SMD module (22-pad) |
| SN74HC00 | U | DIP-14 |
| SN74HC02 | U | DIP-14 |
| SN74HC08 | U | DIP-14 |
| SN74HC32 | U | DIP-14 |
| SN74HC74 | U | DIP-14 |
| SN74HC86 | U | DIP-14 |
| SN74HC138 | U | DIP-16 |
| SN74HC139 | U | DIP-16 |
| SN74HC151 | U | DIP-16 |
| SN74HC157 | U | DIP-16 |
| SN74HC165 | U | DIP-16 |
| SN74HC174 | U | DIP-16 |
| SN74HC273 | U | DIP-20 |
| SN74HC541 | U | DIP-20 |
| SN74HC595 | U | DIP-16 |
| LM358 | U | PDIP-8 |
| LM324 | U | PDIP-14 |
| TL072 | U | PDIP-8 |
| TL074 | U | PDIP-14 |
| LM741 | U | PDIP-8 |
| MCP6002 | U | PDIP-8 |
| OPA2134 | U | PDIP-8 |
| LMV358 | U | SOIC-8 |
| LM339 | U | PDIP-14 |
| TLV3401 | U | SOT-23-5 |
| LM311 | U | PDIP-8 |
| LM7805 | U | TO-220 |
| LM7812 | U | TO-220 |
| LM7905 | U | TO-220 |
| LM317 | U | TO-220 |
| LM337 | U | TO-220 |
| AMS1117_33 | U | SOT-223 |
| AMS1117_50 | U | SOT-223 |
| LP2950 | U | TO-92 |
| BC547 | Q | TO-92 |
| BC557 | Q | TO-92 |
| Q2N3904 | Q | TO-92 |
| Q2N3906 | Q | TO-92 |
| Q2N2222 | Q | TO-92 |
| Q2N7000 | Q | TO-92 |
| BS170 | Q | TO-92 |
| IRLB8721 | Q | TO-220 |
| IRFZ44N | Q | TO-220 |
| TIP120 | Q | TO-220 |
| D1N4148 | D | DO-35 |
| D1N4001 | D | DO-41 |
| D1N4007 | D | DO-41 |
| D1N5817 | D | DO-41 |
| D1N4733A | D | DO-41 |
| D1N4742A | D | DO-41 |
| NE555 | U | PDIP-8 |
| LM386 | U | PDIP-8 |
| DS18B20 | U | TO-92 |
| DS1307 | U | PDIP-8 |
| MAX7219 | U | PDIP-24W |
| TMP36 | U | TO-92 |
| BMP280 | U | LGA-8 |
| MPU6050 | U | QFN-24 |
| HCSR04 | U | 4-pin SIP module |
| MOC3021 | U | DIP-6 |
| OPTO_4N25 | U | DIP-6 |
| OPTO_TLP521 | U | DIP-4 |
| TLC5940 | U | DIP-28 |
| MAX232 | U | DIP-16 |

---

## Microcontrollers

### ATmega328P — 8-bit AVR microcontroller, 32 KB flash, 28-pin
- **Manufacturer(s)**: Microchip (formerly Atmel)
- **MFR P/N (primary)**: ATMEGA328P-PU
- **Refdes prefix**: U
- **Package(s)**: PDIP-28, TQFP-32, MLF/QFN-32
- **Pin map (primary package, PDIP-28)**:

| Pin | Name | Direction |
|----:|------|-----------|
| 1 | PC6 / /RESET | BIDIR (IN as /RESET) |
| 2 | PD0 / RXD | BIDIR |
| 3 | PD1 / TXD | BIDIR |
| 4 | PD2 / INT0 | BIDIR |
| 5 | PD3 / INT1 / OC2B | BIDIR |
| 6 | PD4 / T0 / XCK | BIDIR |
| 7 | VCC | power_in |
| 8 | GND | power_in |
| 9 | PB6 / XTAL1 / TOSC1 | BIDIR |
| 10 | PB7 / XTAL2 / TOSC2 | BIDIR |
| 11 | PD5 / T1 / OC0B | BIDIR |
| 12 | PD6 / AIN0 / OC0A | BIDIR |
| 13 | PD7 / AIN1 | BIDIR |
| 14 | PB0 / ICP1 / CLKO | BIDIR |
| 15 | PB1 / OC1A | BIDIR |
| 16 | PB2 / /SS / OC1B | BIDIR |
| 17 | PB3 / MOSI / OC2A | BIDIR |
| 18 | PB4 / MISO | BIDIR |
| 19 | PB5 / SCK | BIDIR |
| 20 | AVCC | power_in |
| 21 | AREF | power_in |
| 22 | GND | power_in |
| 23 | PC0 / ADC0 | BIDIR |
| 24 | PC1 / ADC1 | BIDIR |
| 25 | PC2 / ADC2 | BIDIR |
| 26 | PC3 / ADC3 | BIDIR |
| 27 | PC4 / ADC4 / SDA | BIDIR |
| 28 | PC5 / ADC5 / SCL | BIDIR |

- **KiCad footprint**: `Package_DIP:DIP-28_W7.62mm`
- **Description**: 8-bit AVR RISC microcontroller with 32 KB flash, 2 KB SRAM, 1 KB EEPROM. The chip at the heart of the Arduino Uno.
- **Operating voltage / current**: V_CC 1.8–5.5 V (full 20 MHz at 4.5–5.5 V); active ~0.2 mA/MHz @ 1.8 V, ~9 mA @ 16 MHz/5 V; power-down <1 µA; absolute max V_CC 6.0 V, per-pin I/O 40 mA, total I/O 200 mA.
- **Datasheet URL**: https://ww1.microchip.com/downloads/en/DeviceDoc/ATmega48A-PA-88A-PA-168A-PA-328-P-DS-DS40002061B.pdf
- **SPICE model**: (generic model required) — Microchip does not publish a SPICE model; use a digital I/O behavioural macro or vendor-supplied IBIS.
- **Notes**: Pin 1 must be pulled to V_CC through a 10 kΩ resistor for normal operation; tying it low resets the part. AVCC must be connected (within 0.3 V of VCC) even if ADC unused. Internal 8 MHz RC oscillator allows operation without a crystal; fuses select clock source.

### ATmega2560 — 8-bit AVR microcontroller, 256 KB flash, 100-pin
- **Manufacturer(s)**: Microchip (formerly Atmel)
- **MFR P/N (primary)**: ATMEGA2560-16AU
- **Refdes prefix**: U
- **Package(s)**: TQFP-100, CBGA-100
- **Pin map (primary package, TQFP-100)**:

| Pin | Name | Direction |
|----:|------|-----------|
| 1 | PG5 / OC0B | BIDIR |
| 2 | PE0 / RXD0 / PCINT8 | BIDIR |
| 3 | PE1 / TXD0 | BIDIR |
| 4 | PE2 / XCK0 / AIN0 | BIDIR |
| 5 | PE3 / OC3A / AIN1 | BIDIR |
| 6 | PE4 / OC3B / INT4 | BIDIR |
| 7 | PE5 / OC3C / INT5 | BIDIR |
| 8 | PE6 / T3 / INT6 | BIDIR |
| 9 | PE7 / CLKO / ICP3 / INT7 | BIDIR |
| 10 | VCC | power_in |
| 11 | GND | power_in |
| 12 | PH0 / RXD2 | BIDIR |
| 13 | PH1 / TXD2 | BIDIR |
| 14 | PH2 / XCK2 | BIDIR |
| 15 | PH3 / OC4A | BIDIR |
| 16 | PH4 / OC4B | BIDIR |
| 17 | PH5 / OC4C | BIDIR |
| 18 | PH6 / OC2B | BIDIR |
| 19 | PB0 / SS / PCINT0 | BIDIR |
| 20 | PB1 / SCK / PCINT1 | BIDIR |
| 21 | PB2 / MOSI / PCINT2 | BIDIR |
| 22 | PB3 / MISO / PCINT3 | BIDIR |
| 23 | PB4 / OC2A / PCINT4 | BIDIR |
| 24 | PB5 / OC1A / PCINT5 | BIDIR |
| 25 | PB6 / OC1B / PCINT6 | BIDIR |
| 26 | PB7 / OC0A / OC1C / PCINT7 | BIDIR |
| 27 | PH7 / T4 | BIDIR |
| 28 | PG3 / TOSC2 | BIDIR |
| 29 | PG4 / TOSC1 | BIDIR |
| 30 | /RESET | IN |
| 31 | VCC | power_in |
| 32 | GND | power_in |
| 33 | XTAL2 | BIDIR |
| 34 | XTAL1 | BIDIR |
| 35 | PL0 / ICP4 | BIDIR |
| 36 | PL1 / ICP5 | BIDIR |
| 37 | PL2 / T5 | BIDIR |
| 38 | PL3 / OC5A | BIDIR |
| 39 | PL4 / OC5B | BIDIR |
| 40 | PL5 / OC5C | BIDIR |
| 41 | PL6 | BIDIR |
| 42 | PL7 | BIDIR |
| 43 | PD0 / SCL / INT0 | BIDIR |
| 44 | PD1 / SDA / INT1 | BIDIR |
| 45 | PD2 / RXD1 / INT2 | BIDIR |
| 46 | PD3 / TXD1 / INT3 | BIDIR |
| 47 | PD4 / ICP1 | BIDIR |
| 48 | PD5 / XCK1 | BIDIR |
| 49 | PD6 / T1 | BIDIR |
| 50 | PD7 / T0 | BIDIR |
| 51 | PG0 / /WR | BIDIR |
| 52 | PG1 / /RD | BIDIR |
| 53 | PC0 / A8 | BIDIR |
| 54 | PC1 / A9 | BIDIR |
| 55 | PC2 / A10 | BIDIR |
| 56 | PC3 / A11 | BIDIR |
| 57 | PC4 / A12 | BIDIR |
| 58 | PC5 / A13 | BIDIR |
| 59 | PC6 / A14 | BIDIR |
| 60 | PC7 / A15 | BIDIR |
| 61 | VCC | power_in |
| 62 | GND | power_in |
| 63 | PJ0 / RXD3 / PCINT9 | BIDIR |
| 64 | PJ1 / TXD3 / PCINT10 | BIDIR |
| 65 | PJ2 / XCK3 / PCINT11 | BIDIR |
| 66 | PJ3 / PCINT12 | BIDIR |
| 67 | PJ4 / PCINT13 | BIDIR |
| 68 | PJ5 / PCINT14 | BIDIR |
| 69 | PJ6 / PCINT15 | BIDIR |
| 70 | PG2 / ALE | BIDIR |
| 71 | PA7 / AD7 | BIDIR |
| 72 | PA6 / AD6 | BIDIR |
| 73 | PA5 / AD5 | BIDIR |
| 74 | PA4 / AD4 | BIDIR |
| 75 | PA3 / AD3 | BIDIR |
| 76 | PA2 / AD2 | BIDIR |
| 77 | PA1 / AD1 | BIDIR |
| 78 | PA0 / AD0 | BIDIR |
| 79 | PJ7 | BIDIR |
| 80 | VCC | power_in |
| 81 | GND | power_in |
| 82 | PK7 / ADC15 / PCINT23 | BIDIR |
| 83 | PK6 / ADC14 / PCINT22 | BIDIR |
| 84 | PK5 / ADC13 / PCINT21 | BIDIR |
| 85 | PK4 / ADC12 / PCINT20 | BIDIR |
| 86 | PK3 / ADC11 / PCINT19 | BIDIR |
| 87 | PK2 / ADC10 / PCINT18 | BIDIR |
| 88 | PK1 / ADC9 / PCINT17 | BIDIR |
| 89 | PK0 / ADC8 / PCINT16 | BIDIR |
| 90 | PF7 / ADC7 / TDI | BIDIR |
| 91 | PF6 / ADC6 / TDO | BIDIR |
| 92 | PF5 / ADC5 / TMS | BIDIR |
| 93 | PF4 / ADC4 / TCK | BIDIR |
| 94 | PF3 / ADC3 | BIDIR |
| 95 | PF2 / ADC2 | BIDIR |
| 96 | PF1 / ADC1 | BIDIR |
| 97 | PF0 / ADC0 | BIDIR |
| 98 | AREF | power_in |
| 99 | GND | power_in |
| 100 | AVCC | power_in |

- **KiCad footprint**: `Package_QFP:TQFP-100_14x14mm_P0.5mm`
- **Description**: High-pin-count AVR with 256 KB flash, 8 KB SRAM, 4 KB EEPROM, 16 PWM channels, 4 UARTs. The Arduino Mega 2560 chip.
- **Operating voltage / current**: V_CC 4.5–5.5 V (16 MHz parts), 1.8–5.5 V (L variant, derated speed); active ~20 mA @ 16 MHz/5 V; power-down <1 µA; per-pin I/O 40 mA, V_CC absolute max 6.0 V.
- **Datasheet URL**: https://ww1.microchip.com/downloads/en/devicedoc/atmel-2549-8-bit-avr-microcontroller-atmega640-1280-1281-2560-2561_datasheet.pdf
- **SPICE model**: (generic model required)
- **Notes**: Five separate VCC/GND pairs must all be decoupled with 100 nF close to each pair. AVCC must be bridged to VCC through a ferrite/LC filter if ADC accuracy matters. /RESET requires 10 kΩ pull-up.

### ATmega32U4 — 8-bit AVR microcontroller with USB device, 32 KB flash, 44-pin
- **Manufacturer(s)**: Microchip (formerly Atmel)
- **MFR P/N (primary)**: ATMEGA32U4-AU
- **Refdes prefix**: U
- **Package(s)**: TQFP-44, VQFN-44
- **Pin map (primary package, TQFP-44)**:

| Pin | Name | Direction |
|----:|------|-----------|
| 1 | PE6 | BIDIR |
| 2 | UVCC | power_in |
| 3 | D_NEG | BIDIR |
| 4 | D_POS | BIDIR |
| 5 | UGND | power_in |
| 6 | UCAP | power_in |
| 7 | VBUS | power_in |
| 8 | PB0 | BIDIR |
| 9 | PB1 | BIDIR |
| 10 | PB2 | BIDIR |
| 11 | PB3 | BIDIR |
| 12 | PB7 | BIDIR |
| 13 | /RESET | IN |
| 14 | VCC | power_in |
| 15 | GND | power_in |
| 16 | XTAL2 | BIDIR |
| 17 | XTAL1 | BIDIR |
| 18 | PD0 | BIDIR |
| 19 | PD1 | BIDIR |
| 20 | PD2 | BIDIR |
| 21 | PD3 | BIDIR |
| 22 | PD5 | BIDIR |
| 23 | GND | power_in |
| 24 | VCC | power_in |
| 25 | PD4 | BIDIR |
| 26 | PD6 | BIDIR |
| 27 | PD7 | BIDIR |
| 28 | PB4 | BIDIR |
| 29 | PB5 | BIDIR |
| 30 | PB6 | BIDIR |
| 31 | PC6 | BIDIR |
| 32 | PC7 | BIDIR |
| 33 | PE2 (/HWB) | BIDIR |
| 34 | VCC | power_in |
| 35 | GND | power_in |
| 36 | PF7 | BIDIR |
| 37 | PF6 | BIDIR |
| 38 | PF5 | BIDIR |
| 39 | PF4 | BIDIR |
| 40 | PF1 | BIDIR |
| 41 | PF0 | BIDIR |
| 42 | AREF | power_in |
| 43 | GND | power_in |
| 44 | AVCC | power_in |

- **KiCad footprint**: `Package_QFP:TQFP-44_10x10mm_P0.8mm`
- **Description**: AVR with built-in USB 2.0 full-speed device controller. The Arduino Leonardo / Micro / Pro Micro chip.
- **Operating voltage / current**: V_CC 2.7–5.5 V (full 16 MHz at 4.5–5.5 V); UVCC 3.0–5.5 V; active ~10 mA @ 8 MHz/3.3 V, ~20 mA @ 16 MHz/5 V; absolute max V_CC 6.0 V.
- **Datasheet URL**: https://ww1.microchip.com/downloads/en/devicedoc/atmel-7766-8-bit-avr-atmega16u4-32u4_datasheet.pdf
- **SPICE model**: (generic model required)
- **Notes**: UCAP pin needs a 1 µF ceramic to GND for the internal USB 3.3 V regulator. UVCC and VBUS must both be powered for USB operation. /HWB (pin 44) held low at reset enters the USB DFU bootloader — critical for board-side recovery.

### ATtiny85 — 8-bit AVR microcontroller, 8 KB flash, 8-pin
- **Manufacturer(s)**: Microchip (formerly Atmel)
- **MFR P/N (primary)**: ATTINY85-20PU
- **Refdes prefix**: U
- **Package(s)**: PDIP-8, SOIC-8, TSSOP-8, VQFN-20 (rare)
- **Pin map (primary package, PDIP-8)**:

| Pin | Name | Direction |
|----:|------|-----------|
| 1 | PB5 / /RESET / ADC0 / dW | BIDIR (IN as /RESET) |
| 2 | PB3 / XTAL1 / CLKI / ADC3 | BIDIR |
| 3 | PB4 / XTAL2 / CLKO / ADC2 | BIDIR |
| 4 | GND | power_in |
| 5 | PB0 / MOSI / DI / SDA / AIN0 / OC0A | BIDIR |
| 6 | PB1 / MISO / DO / AIN1 / OC0B / OC1A | BIDIR |
| 7 | PB2 / SCK / SCL / ADC1 / T0 / INT0 | BIDIR |
| 8 | VCC | power_in |

- **KiCad footprint**: `Package_DIP:DIP-8_W7.62mm`
- **Description**: Tiny 8-pin AVR with 8 KB flash, 512 B SRAM, 512 B EEPROM, 4-channel 10-bit ADC. Common for one-shot embedded jobs and Digispark-class boards.
- **Operating voltage / current**: V_CC 2.7–5.5 V (20 MHz parts), 1.8–5.5 V (V variant); active ~0.3 mA @ 1 MHz/1.8 V, ~5 mA @ 8 MHz/5 V; power-down <0.5 µA; per-pin I/O 40 mA.
- **Datasheet URL**: https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-2586-AVR-8-bit-Microcontroller-ATtiny25-ATtiny45-ATtiny85_Datasheet.pdf
- **SPICE model**: (generic model required)
- **Notes**: PB5 is by default the /RESET pin; converting to GPIO requires burning the RSTDISBL fuse and thereafter the chip can only be reprogrammed with high-voltage serial programming. Internal 8 MHz RC oscillator + PLL gives 16 MHz without a crystal.

### ATtiny84 — 8-bit AVR microcontroller, 8 KB flash, 14-pin
- **Manufacturer(s)**: Microchip (formerly Atmel)
- **MFR P/N (primary)**: ATTINY84-20PU
- **Refdes prefix**: U
- **Package(s)**: PDIP-14, SOIC-14, TSSOP-14, VQFN-20
- **Pin map (primary package, PDIP-14)**:

| Pin | Name | Direction |
|----:|------|-----------|
| 1 | VCC | power_in |
| 2 | PB0 / XTAL1 / PCINT8 | BIDIR |
| 3 | PB1 / XTAL2 / PCINT9 | BIDIR |
| 4 | PB3 / /RESET / dW / PCINT11 | BIDIR (IN as /RESET) |
| 5 | PB2 / INT0 / OC0A / CKOUT / PCINT10 | BIDIR |
| 6 | PA7 / ICP / OC0B / ADC7 / PCINT7 | BIDIR |
| 7 | PA6 / MOSI / SDA / OC1A / ADC6 / PCINT6 | BIDIR |
| 8 | PA5 / MISO / DO / OC1B / ADC5 / PCINT5 | BIDIR |
| 9 | PA4 / SCK / SCL / T1 / ADC4 / PCINT4 | BIDIR |
| 10 | PA3 / T0 / ADC3 / PCINT3 | BIDIR |
| 11 | PA2 / AIN1 / ADC2 / PCINT2 | BIDIR |
| 12 | PA1 / AIN0 / ADC1 / PCINT1 | BIDIR |
| 13 | PA0 / AREF / ADC0 / PCINT0 | BIDIR |
| 14 | GND | power_in |

- **KiCad footprint**: `Package_DIP:DIP-14_W7.62mm`
- **Description**: 14-pin AVR with 8 KB flash, 512 B SRAM, 12 GPIO, 8-channel 10-bit ADC. Popular for small "smart sensor" projects needing more I/O than an ATtiny85.
- **Operating voltage / current**: V_CC 2.7–5.5 V (20 MHz parts), 1.8–5.5 V (V variant); active ~0.3 mA @ 1 MHz/1.8 V, ~5 mA @ 8 MHz/5 V; power-down <0.5 µA.
- **Datasheet URL**: https://ww1.microchip.com/downloads/en/devicedoc/atmel-7701_automotive-microcontrollers-attiny24-44-84_datasheet.pdf
- **SPICE model**: (generic model required)
- **Notes**: Like the ATtiny85, /RESET (PB3) can be repurposed as GPIO only by burning RSTDISBL — irreversible without HVSP. Use the internal RC oscillator (8 MHz/CKOUT) to free PB0/PB1 for GPIO.

### STM32F103C8T6 — ARM Cortex-M3 microcontroller, 64 KB flash, 48-pin
- **Manufacturer(s)**: STMicroelectronics
- **MFR P/N (primary)**: STM32F103C8T6
- **Refdes prefix**: U
- **Package(s)**: LQFP-48, LQFP-64, LQFP-100, LQFP-144, VFQFPN-36/-48
- **Pin map (primary package, LQFP-48)**:

| Pin | Name | Direction |
|----:|------|-----------|
| 1 | VBAT | power_in |
| 2 | PC13 | BIDIR |
| 3 | PC14 / OSC32_IN | BIDIR |
| 4 | PC15 / OSC32_OUT | BIDIR |
| 5 | PD0 / OSC_IN | BIDIR |
| 6 | PD1 / OSC_OUT | BIDIR |
| 7 | NRST | IN |
| 8 | VSSA | power_in |
| 9 | VDDA | power_in |
| 10 | PA0 | BIDIR |
| 11 | PA1 | BIDIR |
| 12 | PA2 | BIDIR |
| 13 | PA3 | BIDIR |
| 14 | PA4 | BIDIR |
| 15 | PA5 | BIDIR |
| 16 | PA6 | BIDIR |
| 17 | PA7 | BIDIR |
| 18 | PB0 | BIDIR |
| 19 | PB1 | BIDIR |
| 20 | VSS | power_in |
| 21 | VDD | power_in |
| 22 | PB2 / BOOT1 | BIDIR |
| 23 | PB10 | BIDIR |
| 24 | PB11 | BIDIR |
| 25 | VSS | power_in |
| 26 | VDD | power_in |
| 27 | PB12 | BIDIR |
| 28 | PB13 | BIDIR |
| 29 | PB14 | BIDIR |
| 30 | PB15 | BIDIR |
| 31 | PA8 | BIDIR |
| 32 | PA9 / USART1_TX | BIDIR |
| 33 | PA10 / USART1_RX | BIDIR |
| 34 | PA11 / USB D_NEG | BIDIR |
| 35 | PA12 / USB D_POS | BIDIR |
| 36 | PA13 / JTMS-SWDIO | BIDIR |
| 37 | VSS | power_in |
| 38 | VDD | power_in |
| 39 | PA14 / JTCK-SWCLK | BIDIR |
| 40 | PA15 / JTDI | BIDIR |
| 41 | PB3 / JTDO | BIDIR |
| 42 | PB4 / NJTRST | BIDIR |
| 43 | PB5 | BIDIR |
| 44 | PB6 | BIDIR |
| 45 | PB7 | BIDIR |
| 46 | BOOT0 | IN |
| 47 | PB8 | BIDIR |
| 48 | PB9 | BIDIR |

- **KiCad footprint**: `Package_QFP:LQFP-48_7x7mm_P0.5mm`
- **Description**: 72 MHz ARM Cortex-M3 with 64 KB flash, 20 KB SRAM, USB FS device, 2× I²C, 3× USART, 2× SPI, 2× 12-bit ADC. The "Blue Pill" board chip.
- **Operating voltage / current**: V_DD 2.0–3.6 V (full 72 MHz at 2.7–3.6 V); run ~36 mA @ 72 MHz, sleep ~2 mA, stop ~24 µA, standby ~3 µA; absolute max V_DD 4.0 V; per-pin I/O 25 mA, total 150 mA.
- **Datasheet URL**: https://www.st.com/resource/en/datasheet/stm32f103c8.pdf
- **SPICE model**: (generic model required) — IBIS published at the STM32F103C8 product page CAD resources.
- **Notes**: BOOT0 high + BOOT1 low at reset enters the built-in UART bootloader on PA9/PA10. Genuine STM32F103C8T6 has 64 KB flash but many parts in the wild are clones (CKS, CS32). USB pull-up is not internal — board must add a 1.5 kΩ pull-up on D+ (the "Blue Pill" gets this wrong; needs the R10 fix).

### STM32F411CEU6 — ARM Cortex-M4F microcontroller, 512 KB flash, 48-pin
- **Manufacturer(s)**: STMicroelectronics
- **MFR P/N (primary)**: STM32F411CEU6
- **Refdes prefix**: U
- **Package(s)**: UFQFPN-48, LQFP-64, LQFP-100, WLCSP-49
- **Pin map (primary package, UFQFPN-48)**:

| Pin | Name | Direction |
|----:|------|-----------|
| 1 | VBAT | power_in |
| 2 | PC13-ANTI_TAMP | BIDIR |
| 3 | PC14-OSC32_IN | BIDIR |
| 4 | PC15-OSC32_OUT | BIDIR |
| 5 | PH0-OSC_IN | BIDIR |
| 6 | PH1-OSC_OUT | BIDIR |
| 7 | NRST | IN |
| 8 | VSSA | power_in |
| 9 | VDDA | power_in |
| 10 | PA0-WKUP | BIDIR |
| 11 | PA1 | BIDIR |
| 12 | PA2 | BIDIR |
| 13 | PA3 | BIDIR |
| 14 | PA4 | BIDIR |
| 15 | PA5 | BIDIR |
| 16 | PA6 | BIDIR |
| 17 | PA7 | BIDIR |
| 18 | PB0 | BIDIR |
| 19 | PB1 | BIDIR |
| 20 | PB2 (BOOT1) | BIDIR |
| 21 | PB10 | BIDIR |
| 22 | VCAP_1 (2.2 µF to GND) | power_in |
| 23 | VSS | power_in |
| 24 | VDD | power_in |
| 25 | PB12 | BIDIR |
| 26 | PB13 | BIDIR |
| 27 | PB14 | BIDIR |
| 28 | PB15 | BIDIR |
| 29 | PA8 | BIDIR |
| 30 | PA9 | BIDIR |
| 31 | PA10 | BIDIR |
| 32 | PA11 (USB_OTG_FS_DM) | BIDIR |
| 33 | PA12 (USB_OTG_FS_DP) | BIDIR |
| 34 | PA13 (SWDIO) | BIDIR |
| 35 | VSS | power_in |
| 36 | VDD | power_in |
| 37 | PA14 (SWCLK) | BIDIR |
| 38 | PA15 | BIDIR |
| 39 | PB3 | BIDIR |
| 40 | PB4 | BIDIR |
| 41 | PB5 | BIDIR |
| 42 | PB6 | BIDIR |
| 43 | PB7 | BIDIR |
| 44 | BOOT0 | IN |
| 45 | PB8 | BIDIR |
| 46 | PB9 | BIDIR |
| 47 | VSS | power_in |
| 48 | VDD | power_in |

_Centre exposed pad: connect to GND (VSS)._

- **KiCad footprint**: `Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm` (VERIFY: closest match — also seen as `UFQFPN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm` in some KiCad library versions)
- **Description**: 100 MHz ARM Cortex-M4 with FPU, 512 KB flash, 128 KB SRAM, USB OTG FS, SDIO, 3× SPI, 3× I²C. The "Black Pill" board chip.
- **Operating voltage / current**: V_DD 1.7–3.6 V (BOR off; 1.8 V min otherwise); run ~30 mA @ 100 MHz, sleep ~10 mA, stop ~42 µA, standby ~2 µA; per-pin I/O 25 mA, absolute max V_DD 4.0 V.
- **Datasheet URL**: https://www.st.com/resource/en/datasheet/stm32f411ce.pdf
- **SPICE model**: (generic model required) — IBIS at the STM32F411CE product page.
- **Notes**: VCAP_1 (pin 22) needs a 2.2 µF low-ESR ceramic to GND for the internal LDO — omitting it will brick the chip's core supply. Bottom centre EP is GND and must be soldered. Boots from system bootloader when BOOT0=1 at reset (USB DFU available).

### RP2040 — Dual ARM Cortex-M0+ microcontroller, 264 KB SRAM, no internal flash, 56-pin
- **Manufacturer(s)**: Raspberry Pi
- **MFR P/N (primary)**: RP2040 (sole source: Raspberry Pi Ltd)
- **Refdes prefix**: U
- **Package(s)**: QFN-56 (7×7 mm, 0.4 mm pitch)
- **Pin map (primary package, QFN-56)**:

| Pin | Name | Direction |
|----:|------|-----------|
| 1 | IOVDD | power_in |
| 2 | GP0 | BIDIR |
| 3 | GP1 | BIDIR |
| 4 | GP2 | BIDIR |
| 5 | GP3 | BIDIR |
| 6 | GP4 | BIDIR |
| 7 | GP5 | BIDIR |
| 8 | GP6 | BIDIR |
| 9 | GP7 | BIDIR |
| 10 | IOVDD | power_in |
| 11 | GP8 | BIDIR |
| 12 | GP9 | BIDIR |
| 13 | GP10 | BIDIR |
| 14 | GP11 | BIDIR |
| 15 | GP12 | BIDIR |
| 16 | GP13 | BIDIR |
| 17 | GP14 | BIDIR |
| 18 | GP15 | BIDIR |
| 19 | TESTEN | IN |
| 20 | XIN | BIDIR |
| 21 | XOUT | BIDIR |
| 22 | IOVDD | power_in |
| 23 | DVDD | power_in |
| 24 | SWCLK | BIDIR |
| 25 | SWDIO | BIDIR |
| 26 | RUN | IN |
| 27 | GP16 | BIDIR |
| 28 | GP17 | BIDIR |
| 29 | GP18 | BIDIR |
| 30 | GP19 | BIDIR |
| 31 | GP20 | BIDIR |
| 32 | GP21 | BIDIR |
| 33 | IOVDD | power_in |
| 34 | GP22 | BIDIR |
| 35 | GP23 | BIDIR |
| 36 | GP24 | BIDIR |
| 37 | GP25 | BIDIR |
| 38 | GP26 / ADC0 | BIDIR |
| 39 | GP27 / ADC1 | BIDIR |
| 40 | GP28 / ADC2 | BIDIR |
| 41 | GP29 / ADC3 | BIDIR |
| 42 | IOVDD | power_in |
| 43 | ADC_AVDD | power_in |
| 44 | VREG_VIN | power_in |
| 45 | VREG_VOUT | power_out |
| 46 | USB_DM | BIDIR |
| 47 | USB_DP | BIDIR |
| 48 | USB_VDD | power_in |
| 49 | IOVDD | power_in |
| 50 | DVDD | power_in |
| 51 | QSPI_SD3 | BIDIR |
| 52 | QSPI_SCLK | BIDIR |
| 53 | QSPI_SD0 | BIDIR |
| 54 | QSPI_SD2 | BIDIR |
| 55 | QSPI_SD1 | BIDIR |
| 56 | QSPI_SS_N | BIDIR |

_Centre exposed pad: connect to GND._

- **KiCad footprint**: `Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm` (VERIFY: precise EP size depends on KiCad library version)
- **Description**: Dual-core Cortex-M0+ @ 133 MHz, 264 KB SRAM, no on-die flash (uses external QSPI flash via XIP), 8 programmable I/O state machines (PIO), USB 1.1 host/device. The Raspberry Pi Pico chip.
- **Operating voltage / current**: IOVDD 1.8–3.3 V, USB_VDD 3.3 V, DVDD 1.1 V (internally regulated); typical 25 mA active, 0.4 mA dormant, 180 µA sleep; absolute max IOVDD 3.63 V.
- **Datasheet URL**: https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf
- **SPICE model**: (generic model required)
- **Notes**: Six IOVDD pins must each be decoupled with a 100 nF cap. Two DVDD pins likewise each need 100 nF plus one 1 µF bulk. Internal VREG output (DVDD) must not be loaded externally. Boots into BOOTSEL mode if QSPI_SS_N is held low at reset — the standard Pico bootloader trick.

### ESP32_WROOM_32 — Wi-Fi + Bluetooth module with ESP32-D0WDQ6, 4 MB flash, 38-pad
- **Manufacturer(s)**: Espressif Systems
- **MFR P/N (primary)**: ESP32-WROOM-32E (current production)
- **Refdes prefix**: U
- **Package(s)**: SMD module, 18×25.5×3.1 mm, 38 castellated pads
- **Pin map (38-pin variant; see datasheet §2.2 / Table 3)**:

| Pin | Name | Direction |
|----:|------|-----------|
| 1 | GND | power_in |
| 2 | 3V3 | power_in |
| 3 | EN (CHIP_PU) | IN |
| 4 | SENSOR_VP / GPIO36 / ADC1_CH0 | IN (input-only) |
| 5 | SENSOR_VN / GPIO39 / ADC1_CH3 | IN (input-only) |
| 6 | GPIO34 / ADC1_CH6 | IN (input-only) |
| 7 | GPIO35 / ADC1_CH7 | IN (input-only) |
| 8 | GPIO32 / ADC1_CH4 / XTAL_32K_P | BIDIR |
| 9 | GPIO33 / ADC1_CH5 / XTAL_32K_N | BIDIR |
| 10 | GPIO25 / DAC_1 / ADC2_CH8 | BIDIR |
| 11 | GPIO26 / DAC_2 / ADC2_CH9 | BIDIR |
| 12 | GPIO27 / ADC2_CH7 | BIDIR |
| 13 | GPIO14 / ADC2_CH6 / MTMS | BIDIR |
| 14 | GPIO12 / ADC2_CH5 / MTDI | BIDIR |
| 15 | GND | power_in |
| 16 | GPIO13 / ADC2_CH4 / MTCK | BIDIR |
| 17 | SD2 / GPIO9 (internal flash) | BIDIR (avoid) |
| 18 | SD3 / GPIO10 (internal flash) | BIDIR (avoid) |
| 19 | CMD / GPIO11 (internal flash) | BIDIR (avoid) |
| 20 | CLK / GPIO6 (internal flash) | BIDIR (avoid) |
| 21 | SD0 / GPIO7 (internal flash) | BIDIR (avoid) |
| 22 | SD1 / GPIO8 (internal flash) | BIDIR (avoid) |
| 23 | GPIO15 / ADC2_CH3 / MTDO | BIDIR |
| 24 | GPIO2 / ADC2_CH2 | BIDIR |
| 25 | GPIO0 / ADC2_CH1 (boot strap) | BIDIR |
| 26 | GPIO4 / ADC2_CH0 | BIDIR |
| 27 | GPIO16 / U2_RXD | BIDIR |
| 28 | GPIO17 / U2_TXD | BIDIR |
| 29 | GPIO5 / VSPI_SS | BIDIR |
| 30 | GPIO18 / VSPI_SCK | BIDIR |
| 31 | GPIO19 / VSPI_MISO | BIDIR |
| 32 | NC | NC |
| 33 | GPIO21 / I2C_SDA | BIDIR |
| 34 | RXD0 / GPIO3 | BIDIR |
| 35 | TXD0 / GPIO1 | BIDIR |
| 36 | GPIO22 / I2C_SCL | BIDIR |
| 37 | GPIO23 / VSPI_MOSI | BIDIR |
| 38 | GND | power_in |

- **KiCad footprint**: `RF_Module:ESP32-WROOM-32`
- **Description**: 2.4 GHz Wi-Fi 802.11 b/g/n + Bluetooth 4.2 BR/EDR & BLE module built around the dual-core ESP32-D0WDQ6 SoC, with integrated 4 MB SPI flash and PCB antenna.
- **Operating voltage / current**: V_DD 3.0–3.6 V (3.3 V nominal); typical 80 mA continuous, Wi-Fi TX peak ~500 mA (need a supply rated ≥ 600 mA), deep sleep 10 µA.
- **Datasheet URL**: https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32_datasheet_en.pdf
- **SPICE model**: (generic model required)
- **Notes**: Pins 17–22 are wired to the internal SPI flash — do not route them out. GPIO0 must be high at boot for normal operation, low to enter the UART download bootloader. EN needs a 10 kΩ pull-up plus a 1 µF reset capacitor for reliable startup. Antenna keep-out is mandatory under the module antenna section.

### ESP8266_12F — Wi-Fi module with ESP8266EX, 4 MB flash, 22-pad
- **Manufacturer(s)**: Ai-Thinker (module); silicon by Espressif Systems
- **MFR P/N (primary)**: ESP-12F
- **Refdes prefix**: U
- **Package(s)**: SMD module, 16×24×3 mm, 22 castellated pads (2 mm pitch)
- **Pin map (22-pad module)**:

| Pin | Name | Direction |
|----:|------|-----------|
| 1 | RST | IN |
| 2 | ADC / TOUT | IN (input-only, 0–1.0 V) |
| 3 | EN / CH_PD | IN |
| 4 | GPIO16 / WAKE | BIDIR |
| 5 | GPIO14 / HSPI_CLK | BIDIR |
| 6 | GPIO12 / HSPI_MISO | BIDIR |
| 7 | GPIO13 / HSPI_MOSI / RXD2 | BIDIR |
| 8 | VCC (3.3 V) | power_in |
| 9 | CS0 / GPIO15 (boot strap, must be low) | BIDIR |
| 10 | MISO / GPIO2 (boot strap, must be high) | BIDIR |
| 11 | GPIO0 (boot strap: high=run, low=flash) | BIDIR |
| 12 | MOSI / GPIO4 | BIDIR |
| 13 | SCLK / GPIO5 | BIDIR |
| 14 | GND | power_in |
| 15 | GPIO10 / SDD3 (internal flash) | BIDIR (avoid) |
| 16 | GPIO9 / SDD2 (internal flash) | BIDIR (avoid) |
| 17 | GPIO11 / SDCMD (internal flash) | BIDIR (avoid) |
| 18 | GPIO6 / SDCLK (internal flash) | BIDIR (avoid) |
| 19 | GPIO7 / SDD0 (internal flash) | BIDIR (avoid) |
| 20 | GPIO8 / SDD1 (internal flash) | BIDIR (avoid) |
| 21 | RXD / GPIO3 | BIDIR |
| 22 | TXD / GPIO1 | BIDIR |

- **KiCad footprint**: `RF_Module:ESP-12E` (VERIFY: ESP-12F shares the ESP-12E pad layout; some KiCad library versions also expose `RF_Module:ESP-12F` directly)
- **Description**: 2.4 GHz Wi-Fi 802.11 b/g/n module built around the ESP8266EX SoC with 4 MB SPI flash and PCB antenna.
- **Operating voltage / current**: V_CC 3.0–3.6 V; typical 80 mA continuous, TX peak ~300 mA (provide ≥ 500 mA supply with bulk cap), deep sleep ~20 µA.
- **Datasheet URL**: https://www.ai-thinker.com/wp-content/uploads/2018/01/ESP-12F.pdf
- **SPICE model**: (generic model required)
- **Notes**: Boot straps are unforgiving — GPIO15 LOW, GPIO2 and GPIO0 HIGH at reset for normal operation. Pins 15–20 are bonded to internal SPI flash; never drive them. ADC input is 0–1.0 V (not 0–3.3 V) on the bare chip. Supply must withstand TX bursts.

---

## 74HC Logic Family

### SN74HC00 — Quad 2-input NAND gate
- **Manufacturer(s)**: TI primary, Nexperia/onsemi second-source
- **MFR P/N (primary)**: SN74HC00N (DIP-14)
- **Refdes prefix**: U
- **Package(s)**: DIP-14 (N), SOIC-14 (D), TSSOP-14 (PW)
- **Pin map (primary package)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1 | 1A | IN |
| 2 | 1B | IN |
| 3 | 1Y | OUT |
| 4 | 2A | IN |
| 5 | 2B | IN |
| 6 | 2Y | OUT |
| 7 | GND | power_in |
| 8 | 3Y | OUT |
| 9 | 3A | IN |
| 10 | 3B | IN |
| 11 | 4Y | OUT |
| 12 | 4A | IN |
| 13 | 4B | IN |
| 14 | VCC | power_in |

- **KiCad footprint**: `Package_DIP:DIP-14_W7.62mm`
- **Description**: Four independent 2-input NAND gates. Output is LOW only when both inputs are HIGH.
- **Operating voltage / current**: V_CC 2 V – 6 V; I_OH/I_OL ±5.2 mA at 4.5 V (±25 mA absolute max per output)
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/sn74hc00.pdf
- **SPICE model**: https://www.ti.com/product/SN74HC00 (TI PSpice model available)
- **Notes**: All unused inputs must be tied to V_CC or GND — floating CMOS inputs draw shoot-through current and oscillate.

### SN74HC02 — Quad 2-input NOR gate
- **Manufacturer(s)**: TI primary, Nexperia/onsemi second-source
- **MFR P/N (primary)**: SN74HC02N (DIP-14)
- **Refdes prefix**: U
- **Package(s)**: DIP-14 (N), SOIC-14 (D), TSSOP-14 (PW)
- **Pin map (primary package)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1 | 1Y | OUT |
| 2 | 1A | IN |
| 3 | 1B | IN |
| 4 | 2Y | OUT |
| 5 | 2A | IN |
| 6 | 2B | IN |
| 7 | GND | power_in |
| 8 | 3A | IN |
| 9 | 3B | IN |
| 10 | 3Y | OUT |
| 11 | 4A | IN |
| 12 | 4B | IN |
| 13 | 4Y | OUT |
| 14 | VCC | power_in |

- **KiCad footprint**: `Package_DIP:DIP-14_W7.62mm`
- **Description**: Four independent 2-input NOR gates. Output is HIGH only when both inputs are LOW.
- **Operating voltage / current**: V_CC 2 V – 6 V; I_OH/I_OL ±5.2 mA at 4.5 V
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/sn74hc02.pdf
- **SPICE model**: https://www.ti.com/product/SN74HC02
- **Notes**: Pinout differs from HC00 — outputs on pins 1/4/10/13, not 3/6/8/11. Tie unused inputs.

### SN74HC08 — Quad 2-input AND gate
- **Manufacturer(s)**: TI primary, Nexperia/onsemi second-source
- **MFR P/N (primary)**: SN74HC08N (DIP-14)
- **Refdes prefix**: U
- **Package(s)**: DIP-14 (N), SOIC-14 (D), TSSOP-14 (PW)
- **Pin map (primary package)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1 | 1A | IN |
| 2 | 1B | IN |
| 3 | 1Y | OUT |
| 4 | 2A | IN |
| 5 | 2B | IN |
| 6 | 2Y | OUT |
| 7 | GND | power_in |
| 8 | 3Y | OUT |
| 9 | 3A | IN |
| 10 | 3B | IN |
| 11 | 4Y | OUT |
| 12 | 4A | IN |
| 13 | 4B | IN |
| 14 | VCC | power_in |

- **KiCad footprint**: `Package_DIP:DIP-14_W7.62mm`
- **Description**: Four independent 2-input AND gates. Output is HIGH only when both inputs are HIGH.
- **Operating voltage / current**: V_CC 2 V – 6 V; I_OH/I_OL ±5.2 mA at 4.5 V
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/sn74hc08.pdf
- **SPICE model**: https://www.ti.com/product/SN74HC08
- **Notes**: Same pinout as HC00/HC32/HC86. Tie unused inputs.

### SN74HC32 — Quad 2-input OR gate
- **Manufacturer(s)**: TI primary, Nexperia/onsemi second-source
- **MFR P/N (primary)**: SN74HC32N (DIP-14)
- **Refdes prefix**: U
- **Package(s)**: DIP-14 (N), SOIC-14 (D), TSSOP-14 (PW)
- **Pin map (primary package)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1 | 1A | IN |
| 2 | 1B | IN |
| 3 | 1Y | OUT |
| 4 | 2A | IN |
| 5 | 2B | IN |
| 6 | 2Y | OUT |
| 7 | GND | power_in |
| 8 | 3Y | OUT |
| 9 | 3A | IN |
| 10 | 3B | IN |
| 11 | 4Y | OUT |
| 12 | 4A | IN |
| 13 | 4B | IN |
| 14 | VCC | power_in |

- **KiCad footprint**: `Package_DIP:DIP-14_W7.62mm`
- **Description**: Four independent 2-input OR gates. Output is HIGH when either input is HIGH.
- **Operating voltage / current**: V_CC 2 V – 6 V; I_OH/I_OL ±5.2 mA at 4.5 V
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/sn74hc32.pdf
- **SPICE model**: https://www.ti.com/product/SN74HC32
- **Notes**: Same pinout as HC00/HC08/HC86. Tie unused inputs.

### SN74HC74 — Dual D-type flip-flop with preset and clear
- **Manufacturer(s)**: TI primary, Nexperia/onsemi second-source
- **MFR P/N (primary)**: SN74HC74N (DIP-14)
- **Refdes prefix**: U
- **Package(s)**: DIP-14 (N), SOIC-14 (D), TSSOP-14 (PW)
- **Pin map (primary package)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1 | 1CLR | IN |
| 2 | 1D | IN |
| 3 | 1CLK | IN |
| 4 | 1PRE | IN |
| 5 | 1Q | OUT |
| 6 | 1Q_BAR | OUT |
| 7 | GND | power_in |
| 8 | 2Q_BAR | OUT |
| 9 | 2Q | OUT |
| 10 | 2PRE | IN |
| 11 | 2CLK | IN |
| 12 | 2D | IN |
| 13 | 2CLR | IN |
| 14 | VCC | power_in |

- **KiCad footprint**: `Package_DIP:DIP-14_W7.62mm`
- **Description**: Two positive-edge-triggered D flip-flops with asynchronous active-LOW preset and clear inputs.
- **Operating voltage / current**: V_CC 2 V – 6 V; I_OH/I_OL ±5.2 mA at 4.5 V
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/sn74hc74.pdf
- **SPICE model**: https://www.ti.com/product/SN74HC74
- **Notes**: PRE and CLR are active-LOW and asynchronous; asserting both simultaneously is a forbidden state. Tie unused PRE/CLR HIGH.

### SN74HC86 — Quad 2-input XOR gate
- **Manufacturer(s)**: TI primary, Nexperia/onsemi second-source
- **MFR P/N (primary)**: SN74HC86N (DIP-14)
- **Refdes prefix**: U
- **Package(s)**: DIP-14 (N), SOIC-14 (D), TSSOP-14 (PW)
- **Pin map (primary package)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1 | 1A | IN |
| 2 | 1B | IN |
| 3 | 1Y | OUT |
| 4 | 2A | IN |
| 5 | 2B | IN |
| 6 | 2Y | OUT |
| 7 | GND | power_in |
| 8 | 3Y | OUT |
| 9 | 3A | IN |
| 10 | 3B | IN |
| 11 | 4Y | OUT |
| 12 | 4A | IN |
| 13 | 4B | IN |
| 14 | VCC | power_in |

- **KiCad footprint**: `Package_DIP:DIP-14_W7.62mm`
- **Description**: Four independent 2-input exclusive-OR gates. Output is HIGH when inputs differ.
- **Operating voltage / current**: V_CC 2 V – 6 V; I_OH/I_OL ±5.2 mA at 4.5 V
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/sn74hc86.pdf
- **SPICE model**: https://www.ti.com/product/SN74HC86
- **Notes**: Useful as a controlled inverter (B=1 inverts A).

### SN74HC138 — 3-to-8 line decoder/demultiplexer
- **Manufacturer(s)**: TI primary, Nexperia/onsemi second-source
- **MFR P/N (primary)**: SN74HC138N (DIP-16)
- **Refdes prefix**: U
- **Package(s)**: DIP-16 (N), SOIC-16 (D), TSSOP-16 (PW)
- **Pin map (primary package)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1 | A | IN |
| 2 | B | IN |
| 3 | C | IN |
| 4 | G2A | IN |
| 5 | G2B | IN |
| 6 | G1 | IN |
| 7 | Y7 | OUT |
| 8 | GND | power_in |
| 9 | Y6 | OUT |
| 10 | Y5 | OUT |
| 11 | Y4 | OUT |
| 12 | Y3 | OUT |
| 13 | Y2 | OUT |
| 14 | Y1 | OUT |
| 15 | Y0 | OUT |
| 16 | VCC | power_in |

- **KiCad footprint**: `Package_DIP:DIP-16_W7.62mm`
- **Description**: 3-to-8 line decoder. Decodes a 3-bit address (A,B,C) to one of eight active-LOW outputs when enabled.
- **Operating voltage / current**: V_CC 2 V – 6 V; I_OH/I_OL ±6 mA at 4.5 V
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/sn74hc138.pdf
- **SPICE model**: https://www.ti.com/product/SN74HC138
- **Notes**: Outputs are active-LOW. Enable requires G1=HIGH AND G2A=G2B=LOW; otherwise all outputs HIGH.

### SN74HC139 — Dual 2-to-4 line decoder/demultiplexer
- **Manufacturer(s)**: TI primary, Nexperia/onsemi second-source
- **MFR P/N (primary)**: SN74HC139N (DIP-16)
- **Refdes prefix**: U
- **Package(s)**: DIP-16 (N), SOIC-16 (D), TSSOP-16 (PW)
- **Pin map (primary package)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1 | 1G | IN |
| 2 | 1A | IN |
| 3 | 1B | IN |
| 4 | 1Y0 | OUT |
| 5 | 1Y1 | OUT |
| 6 | 1Y2 | OUT |
| 7 | 1Y3 | OUT |
| 8 | GND | power_in |
| 9 | 2Y3 | OUT |
| 10 | 2Y2 | OUT |
| 11 | 2Y1 | OUT |
| 12 | 2Y0 | OUT |
| 13 | 2B | IN |
| 14 | 2A | IN |
| 15 | 2G | IN |
| 16 | VCC | power_in |

- **KiCad footprint**: `Package_DIP:DIP-16_W7.62mm`
- **Description**: Two independent 2-to-4 line decoders, each with active-LOW enable.
- **Operating voltage / current**: V_CC 2 V – 6 V; I_OH/I_OL ±6 mA at 4.5 V
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/sn74hc139.pdf
- **SPICE model**: https://www.ti.com/product/SN74HC139
- **Notes**: Outputs and enables active-LOW. When G is HIGH all four Y outputs are HIGH.

### SN74HC151 — 8-to-1 data selector/multiplexer
- **Manufacturer(s)**: TI primary, Nexperia/onsemi second-source
- **MFR P/N (primary)**: SN74HC151N (DIP-16)
- **Refdes prefix**: U
- **Package(s)**: DIP-16 (N), SOIC-16 (D), TSSOP-16 (PW)
- **Pin map (primary package)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1 | D3 | IN |
| 2 | D2 | IN |
| 3 | D1 | IN |
| 4 | D0 | IN |
| 5 | Y | OUT |
| 6 | W | OUT |
| 7 | G | IN |
| 8 | GND | power_in |
| 9 | C | IN |
| 10 | B | IN |
| 11 | A | IN |
| 12 | D7 | IN |
| 13 | D6 | IN |
| 14 | D5 | IN |
| 15 | D4 | IN |
| 16 | VCC | power_in |

- **KiCad footprint**: `Package_DIP:DIP-16_W7.62mm`
- **Description**: 8-input multiplexer with complementary outputs. Y is selected, W is inverted.
- **Operating voltage / current**: V_CC 2 V – 6 V; I_OH/I_OL ±6 mA at 4.5 V
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/sn74hc151.pdf
- **SPICE model**: https://www.ti.com/product/SN74HC151
- **Notes**: Enable G is active-LOW; when G=HIGH, Y is forced LOW and W is HIGH.

### SN74HC157 — Quad 2-to-1 data selector/multiplexer
- **Manufacturer(s)**: TI primary, Nexperia/onsemi second-source
- **MFR P/N (primary)**: SN74HC157N (DIP-16)
- **Refdes prefix**: U
- **Package(s)**: DIP-16 (N), SOIC-16 (D), TSSOP-16 (PW)
- **Pin map (primary package)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1 | A/B | IN |
| 2 | 1A | IN |
| 3 | 1B | IN |
| 4 | 1Y | OUT |
| 5 | 2A | IN |
| 6 | 2B | IN |
| 7 | 2Y | OUT |
| 8 | GND | power_in |
| 9 | 3Y | OUT |
| 10 | 3B | IN |
| 11 | 3A | IN |
| 12 | 4Y | OUT |
| 13 | 4B | IN |
| 14 | 4A | IN |
| 15 | G | IN |
| 16 | VCC | power_in |

- **KiCad footprint**: `Package_DIP:DIP-16_W7.62mm`
- **Description**: Four 2-input multiplexers with common select and active-LOW enable. Non-inverting (use HC158 for inverting).
- **Operating voltage / current**: V_CC 2 V – 6 V; I_OH/I_OL ±6 mA at 4.5 V
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/sn74hc157.pdf
- **SPICE model**: https://www.ti.com/product/SN74HC157
- **Notes**: Enable G is active-LOW; when G=HIGH all Y outputs are LOW.

### SN74HC165 — 8-bit parallel-load shift register (parallel-to-serial)
- **Manufacturer(s)**: TI primary, Nexperia/onsemi second-source
- **MFR P/N (primary)**: SN74HC165N (DIP-16)
- **Refdes prefix**: U
- **Package(s)**: DIP-16 (N), SOIC-16 (D), TSSOP-16 (PW)
- **Pin map (primary package)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1 | SH/LD | IN |
| 2 | CLK | IN |
| 3 | E | IN |
| 4 | F | IN |
| 5 | G | IN |
| 6 | H | IN |
| 7 | QH_BAR | OUT |
| 8 | GND | power_in |
| 9 | QH | OUT |
| 10 | SER | IN |
| 11 | A | IN |
| 12 | B | IN |
| 13 | C | IN |
| 14 | D | IN |
| 15 | CLK_INH | IN |
| 16 | VCC | power_in |

- **KiCad footprint**: `Package_DIP:DIP-16_W7.62mm`
- **Description**: 8-bit parallel-load shift register. SH/LD LOW loads A–H; HIGH shifts toward QH on each rising clock edge.
- **Operating voltage / current**: V_CC 2 V – 6 V; I_OH/I_OL ±6 mA at 4.5 V
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/sn74hc165.pdf
- **SPICE model**: https://www.ti.com/product/SN74HC165
- **Notes**: CLK_INH must be LOW to enable clocking. SH/LD is asynchronous parallel load — hold HIGH during shifting.

### SN74HC174 — Hex D-type flip-flop with common clock and clear
- **Manufacturer(s)**: TI primary, Nexperia/onsemi second-source
- **MFR P/N (primary)**: SN74HC174N (DIP-16)
- **Refdes prefix**: U
- **Package(s)**: DIP-16 (N), SOIC-16 (D), TSSOP-16 (PW)
- **Pin map (primary package)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1 | CLR | IN |
| 2 | 1Q | OUT |
| 3 | 1D | IN |
| 4 | 2D | IN |
| 5 | 2Q | OUT |
| 6 | 3D | IN |
| 7 | 3Q | OUT |
| 8 | GND | power_in |
| 9 | CLK | IN |
| 10 | 4Q | OUT |
| 11 | 4D | IN |
| 12 | 5Q | OUT |
| 13 | 5D | IN |
| 14 | 6D | IN |
| 15 | 6Q | OUT |
| 16 | VCC | power_in |

- **KiCad footprint**: `Package_DIP:DIP-16_W7.62mm`
- **Description**: Six positive-edge-triggered D flip-flops with common clock and common asynchronous active-LOW clear.
- **Operating voltage / current**: V_CC 2 V – 6 V; I_OH/I_OL ±6 mA at 4.5 V
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/sn74hc174.pdf
- **SPICE model**: https://www.ti.com/product/SN74HC174
- **Notes**: CLR active-LOW and asynchronous — tie HIGH if unused. No Q_bar outputs.

### SN74HC273 — Octal D-type flip-flop with common clock and clear
- **Manufacturer(s)**: TI primary, Nexperia/onsemi second-source
- **MFR P/N (primary)**: SN74HC273N (DIP-20)
- **Refdes prefix**: U
- **Package(s)**: DIP-20 (N), SOIC-20 (DW), TSSOP-20 (PW)
- **Pin map (primary package)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1 | CLR | IN |
| 2 | 1Q | OUT |
| 3 | 1D | IN |
| 4 | 2D | IN |
| 5 | 2Q | OUT |
| 6 | 3Q | OUT |
| 7 | 3D | IN |
| 8 | 4D | IN |
| 9 | 4Q | OUT |
| 10 | GND | power_in |
| 11 | CLK | IN |
| 12 | 5Q | OUT |
| 13 | 5D | IN |
| 14 | 6D | IN |
| 15 | 6Q | OUT |
| 16 | 7Q | OUT |
| 17 | 7D | IN |
| 18 | 8D | IN |
| 19 | 8Q | OUT |
| 20 | VCC | power_in |

- **KiCad footprint**: `Package_DIP:DIP-20_W7.62mm`
- **Description**: Eight D flip-flops sharing common clock and async active-LOW clear.
- **Operating voltage / current**: V_CC 2 V – 6 V; I_OH/I_OL ±6 mA at 4.5 V
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/sn74hc273.pdf
- **SPICE model**: https://www.ti.com/product/SN74HC273
- **Notes**: No output-enable — outputs always driven (not bus-compatible without external buffer).

### SN74HC541 — Octal buffer/line driver with 3-state outputs
- **Manufacturer(s)**: TI primary, Nexperia/onsemi second-source
- **MFR P/N (primary)**: SN74HC541N (DIP-20)
- **Refdes prefix**: U
- **Package(s)**: DIP-20 (N), SOIC-20 (DW), SSOP-20 (DB), TSSOP-20 (PW)
- **Pin map (primary package)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1 | OE1 | IN |
| 2 | A1 | IN |
| 3 | A2 | IN |
| 4 | A3 | IN |
| 5 | A4 | IN |
| 6 | A5 | IN |
| 7 | A6 | IN |
| 8 | A7 | IN |
| 9 | A8 | IN |
| 10 | GND | power_in |
| 11 | Y8 | OUT |
| 12 | Y7 | OUT |
| 13 | Y6 | OUT |
| 14 | Y5 | OUT |
| 15 | Y4 | OUT |
| 16 | Y3 | OUT |
| 17 | Y2 | OUT |
| 18 | Y1 | OUT |
| 19 | OE2 | IN |
| 20 | VCC | power_in |

- **KiCad footprint**: `Package_DIP:DIP-20_W7.62mm`
- **Description**: Octal non-inverting buffer with 3-state outputs. Drives Y=A when both active-LOW OEs are asserted; otherwise Hi-Z.
- **Operating voltage / current**: V_CC 2 V – 6 V; I_OH/I_OL ±7.8 mA at 4.5 V
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/sn74hc541.pdf
- **SPICE model**: https://www.ti.com/product/SN74HC541
- **Notes**: Both OE1 AND OE2 must be LOW to enable outputs. Inputs and outputs on opposite sides for clean PCB layout.

### SN74HC595 — 8-bit serial-in/parallel-out shift register with output latch
- **Manufacturer(s)**: TI primary, Nexperia/onsemi second-source
- **MFR P/N (primary)**: SN74HC595N (DIP-16)
- **Refdes prefix**: U
- **Package(s)**: DIP-16 (N), SOIC-16 (D), TSSOP-16 (PW)
- **Pin map (primary package)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1 | QB | OUT |
| 2 | QC | OUT |
| 3 | QD | OUT |
| 4 | QE | OUT |
| 5 | QF | OUT |
| 6 | QG | OUT |
| 7 | QH | OUT |
| 8 | GND | power_in |
| 9 | QH_PRIME | OUT |
| 10 | SRCLR | IN |
| 11 | SRCLK | IN |
| 12 | RCLK | IN |
| 13 | OE | IN |
| 14 | SER | IN |
| 15 | QA | OUT |
| 16 | VCC | power_in |

- **KiCad footprint**: `Package_DIP:DIP-16_W7.62mm`
- **Description**: 8-bit serial-in shift register feeding an 8-bit storage register with 3-state parallel outputs. Daisy-chainable via QH'.
- **Operating voltage / current**: V_CC 2 V – 6 V; I_OH/I_OL ±6 mA at 4.5 V (±35 mA absolute max per output)
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/sn74hc595.pdf
- **SPICE model**: https://www.ti.com/product/SN74HC595
- **Notes**: SRCLK shifts data; RCLK transfers shift→storage. SRCLR active-LOW (clears shift register only). OE active-LOW for parallel outputs. Tie SRCLR HIGH and OE LOW for typical use.

---

## Op-Amps

### LM358 — Dual single-supply low-power bipolar op-amp
- **Manufacturer(s)**: TI (primary), onsemi, STMicroelectronics, Diodes Inc.
- **MFR P/N (primary)**: LM358P (DIP-8)
- **Refdes prefix**: U
- **Package(s)**: PDIP-8, SOIC-8, TSSOP-8, VSSOP-8
- **Pin map (primary package — PDIP-8)**:

| Pin | Name   | Direction |
|-----|--------|-----------|
| 1   | OUT1   | OUT       |
| 2   | IN1_NEG   | IN        |
| 3   | IN1_POS   | IN        |
| 4   | V_GND | power_in  |
| 5   | IN2_POS   | IN        |
| 6   | IN2_NEG   | IN        |
| 7   | OUT2   | OUT       |
| 8   | V_POS     | power_in  |

- **KiCad footprint**: `Package_DIP:DIP-8_W7.62mm`
- **Description**: Dual bipolar op-amp for single-supply operation with inputs that include ground. GBW ~1.1 MHz, NOT rail-to-rail.
- **Operating voltage / current**: 3 V to 32 V single (or ±1.5 V to ±16 V split); Iq ~0.7 mA total; Vos ~2 mV typ, 7 mV max.
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/lm358.pdf
- **SPICE model**: https://www.ti.com/product/LM358 (TINA-TI model)
- **Notes**: Single-supply OK (input CM includes ground). NOT rail-to-rail. Crossover distortion in Class-B output stage — pull output to V- with resistor for audio.

### LM324 — Quad single-supply low-power bipolar op-amp
- **Manufacturer(s)**: TI (primary), onsemi, STMicroelectronics, Diodes Inc.
- **MFR P/N (primary)**: LM324N (DIP-14)
- **Refdes prefix**: U
- **Package(s)**: PDIP-14, SOIC-14, TSSOP-14
- **Pin map (primary package — PDIP-14)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1   | OUT1 | OUT       |
| 2   | IN1_NEG | IN        |
| 3   | IN1_POS | IN        |
| 4   | V_POS   | power_in  |
| 5   | IN2_POS | IN        |
| 6   | IN2_NEG | IN        |
| 7   | OUT2 | OUT       |
| 8   | OUT3 | OUT       |
| 9   | IN3_NEG | IN        |
| 10  | IN3_POS | IN        |
| 11  | V_GND | power_in |
| 12  | IN4_POS | IN        |
| 13  | IN4_NEG | IN        |
| 14  | OUT4 | OUT       |

- **KiCad footprint**: `Package_DIP:DIP-14_W7.62mm`
- **Description**: Quad version of LM358 — bipolar, single-supply-capable. GBW ~1.2 MHz, NOT rail-to-rail.
- **Operating voltage / current**: 3 V to 32 V single (or ±1.5 V to ±16 V split); Iq ~1.2 mA total; Vos ~2 mV typ, 7 mV max.
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/lm324.pdf
- **SPICE model**: https://www.ti.com/product/LM324
- **Notes**: V+ on pin 4, GND on pin 11 — opposite of TL074/quad-JFET pinout!

### TL072 — Dual low-noise JFET-input op-amp
- **Manufacturer(s)**: TI (primary), onsemi, STMicroelectronics
- **MFR P/N (primary)**: TL072CP (DIP-8)
- **Refdes prefix**: U
- **Package(s)**: PDIP-8, SOIC-8, TSSOP-8
- **Pin map (primary package — PDIP-8)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1   | OUT1 | OUT       |
| 2   | IN1_NEG | IN        |
| 3   | IN1_POS | IN        |
| 4   | V_NEG   | power_in  |
| 5   | IN2_POS | IN        |
| 6   | IN2_NEG | IN        |
| 7   | OUT2 | OUT       |
| 8   | V_POS   | power_in  |

- **KiCad footprint**: `Package_DIP:DIP-8_W7.62mm`
- **Description**: Dual JFET-input op-amp, low noise, popular for audio. GBW ~3 MHz, slew rate 13 V/µs.
- **Operating voltage / current**: ±2.25 V to ±18 V split, or 4.5 V to 36 V single; Iq ~1.4 mA/ch; Vos ~3 mV typ, 10 mV max.
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/tl072.pdf
- **SPICE model**: https://www.ti.com/product/TL072
- **Notes**: JFET inputs — ultra-high Zin (~10¹² Ω), low bias (~30 pA). Output cannot reach rails (~1.5 V headroom). Watch for phase reversal if input exceeds CM range (TL072H is phase-reversal-free).

### TL074 — Quad low-noise JFET-input op-amp
- **Manufacturer(s)**: TI (primary), onsemi, STMicroelectronics
- **MFR P/N (primary)**: TL074CN (DIP-14)
- **Refdes prefix**: U
- **Package(s)**: PDIP-14, SOIC-14, TSSOP-14
- **Pin map (primary package — PDIP-14)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1   | OUT1 | OUT       |
| 2   | IN1_NEG | IN        |
| 3   | IN1_POS | IN        |
| 4   | V_POS   | power_in  |
| 5   | IN2_POS | IN        |
| 6   | IN2_NEG | IN        |
| 7   | OUT2 | OUT       |
| 8   | OUT3 | OUT       |
| 9   | IN3_NEG | IN        |
| 10  | IN3_POS | IN        |
| 11  | V_NEG   | power_in  |
| 12  | IN4_POS | IN        |
| 13  | IN4_NEG | IN        |
| 14  | OUT4 | OUT       |

- **KiCad footprint**: `Package_DIP:DIP-14_W7.62mm`
- **Description**: Quad version of TL072 — JFET-input, audio-grade. GBW ~3 MHz, slew rate 13 V/µs.
- **Operating voltage / current**: ±2.25 V to ±18 V split or 4.5–36 V single; Iq ~1.4 mA/ch (~5.6 mA total); Vos ~3 mV typ.
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/tl074.pdf
- **SPICE model**: https://www.ti.com/product/TL074
- **Notes**: Standard quad pinout (V+ pin 4, V- pin 11). Use TL074H variant for phase-reversal-free operation.

### LM741 — Classic single bipolar op-amp
- **Manufacturer(s)**: TI (primary), onsemi, STMicroelectronics
- **MFR P/N (primary)**: LM741CN (DIP-8)
- **Refdes prefix**: U
- **Package(s)**: PDIP-8, CDIP-8, TO-99 metal can
- **Pin map (primary package — PDIP-8)**:

| Pin | Name        | Direction |
|-----|-------------|-----------|
| 1   | OFFSET_N1   | IN        |
| 2   | IN_NEG         | IN        |
| 3   | IN_POS         | IN        |
| 4   | V_NEG          | power_in  |
| 5   | OFFSET_N2   | IN        |
| 6   | OUT         | OUT       |
| 7   | V_POS          | power_in  |
| 8   | NC          | —         |

- **KiCad footprint**: `Package_DIP:DIP-8_W7.62mm`
- **Description**: Classic 1968 single bipolar op-amp. GBW ~1 MHz, slew 0.5 V/µs. Split-supply only.
- **Operating voltage / current**: ±5 V to ±18 V; Iq ~1.7 mA; Vos ~1 mV typ, 6 mV max.
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/lm741.pdf
- **SPICE model**: https://www.ti.com/product/LM741 (generic 741 macromodel widely available)
- **Notes**: Legacy / educational. Avoid for new designs; choose TL07x or LM358.

### MCP6002 — Dual 1 MHz rail-to-rail CMOS op-amp
- **Manufacturer(s)**: Microchip (sole source)
- **MFR P/N (primary)**: MCP6002-I/P (DIP-8)
- **Refdes prefix**: U
- **Package(s)**: PDIP-8, SOIC-8, MSOP-8, TDFN-8
- **Pin map (primary package — PDIP-8)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1   | OUT1 | OUT       |
| 2   | IN1_NEG | IN        |
| 3   | IN1_POS | IN        |
| 4   | VSS  | power_in  |
| 5   | IN2_POS | IN        |
| 6   | IN2_NEG | IN        |
| 7   | OUT2 | OUT       |
| 8   | VDD  | power_in  |

- **KiCad footprint**: `Package_DIP:DIP-8_W7.62mm`
- **Description**: Dual CMOS rail-to-rail input AND output op-amp. GBW 1 MHz, slew 0.6 V/µs.
- **Operating voltage / current**: 1.8 V to 6.0 V single; Iq ~100 µA/ch; Vos ±4.5 mV max.
- **Datasheet URL**: https://ww1.microchip.com/downloads/en/DeviceDoc/MCP6001-1R-1U-2-4-1.3-MHz-Low-Power-Op-Amp-DS20001733L.pdf
- **SPICE model**: https://www.microchip.com/en-us/product/MCP6002 (Mindi/SPICE model)
- **Notes**: True rail-to-rail in & out. Pin-compatible with LM358 footprint.

### OPA2134 — Dual audio FET-input op-amp
- **Manufacturer(s)**: TI / Burr-Brown (primary, sole source)
- **MFR P/N (primary)**: OPA2134PA (DIP-8)
- **Refdes prefix**: U
- **Package(s)**: PDIP-8, SOIC-8
- **Pin map (primary package — PDIP-8)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1   | OUT1 | OUT       |
| 2   | IN1_NEG | IN        |
| 3   | IN1_POS | IN        |
| 4   | V_NEG   | power_in  |
| 5   | IN2_POS | IN        |
| 6   | IN2_NEG | IN        |
| 7   | OUT2 | OUT       |
| 8   | V_POS   | power_in  |

- **KiCad footprint**: `Package_DIP:DIP-8_W7.62mm`
- **Description**: Premium dual FET-input audio op-amp. GBW 8 MHz, slew 20 V/µs, THD+N 0.00008%.
- **Operating voltage / current**: ±2.5 V to ±18 V split; Iq ~4 mA/ch; Vos ±0.5 mV typ, ±2 mV max.
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/opa2134.pdf
- **SPICE model**: https://www.ti.com/product/OPA2134
- **Notes**: Audiophile-grade — extremely low THD. Phase-reversal-free input stage. Pin-compatible with TL072/NE5532.

### LMV358 — Dual low-voltage bipolar op-amp
- **Manufacturer(s)**: TI (primary), onsemi, STMicroelectronics, Diodes Inc.
- **MFR P/N (primary)**: LMV358IDR (SOIC-8)
- **Refdes prefix**: U
- **Package(s)**: SOIC-8, VSSOP-8, TSSOP-8 (no current PDIP-8 from TI)
- **Pin map (primary package — SOIC-8)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1   | OUT1 | OUT       |
| 2   | IN1_NEG | IN        |
| 3   | IN1_POS | IN        |
| 4   | V_GND | power_in |
| 5   | IN2_POS | IN        |
| 6   | IN2_NEG | IN        |
| 7   | OUT2 | OUT       |
| 8   | V_POS   | power_in  |

- **KiCad footprint**: `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` (VERIFY: no through-hole variant stocked by TI; DIP-8 footprint can be used with compatible second-source if needed)
- **Description**: Low-voltage single-supply variant of LM358 family. GBW ~1 MHz.
- **Operating voltage / current**: 2.7 V to 5.5 V single; Iq ~210 µA/ch; Vos ±1.7 mV typ.
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/lmv358.pdf
- **SPICE model**: https://www.ti.com/product/LMV358
- **Notes**: NOT true rail-to-rail (within ~50 mV of V- only). Same pinout as LM358 — drop-in for low-voltage designs.

---

## Comparators

### LM339 — Quad open-collector differential comparator, single-supply
- **Manufacturer(s)**: Texas Instruments (primary); onsemi, STMicroelectronics (second-source)
- **MFR P/N (primary)**: LM339N
- **Refdes prefix**: U
- **Package(s)**: PDIP-14, SOIC-14, TSSOP-14, SSOP-14, WQFN-16
- **Pin map (primary package)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1   | OUT2 | OUT       |
| 2   | OUT1 | OUT       |
| 3   | VCC  | power_in  |
| 4   | IN1_NEG | IN        |
| 5   | IN1_POS | IN        |
| 6   | IN2_NEG | IN        |
| 7   | IN2_POS | IN        |
| 8   | IN3_NEG | IN        |
| 9   | IN3_POS | IN        |
| 10  | IN4_NEG | IN        |
| 11  | IN4_POS | IN        |
| 12  | GND  | power_in  |
| 13  | OUT4 | OUT       |
| 14  | OUT3 | OUT       |

- **KiCad footprint**: `Package_DIP:DIP-14_W7.62mm`
- **Description**: Quad differential comparator with open-collector outputs. Input CM range includes ground.
- **Operating voltage / current**: VCC 2 V to 30 V single or ±1 V to ±15 V split; output sink up to 16 mA typ; supply current ~1 mA @ 5 V.
- **Datasheet URL**: https://www.ti.com/lit/gpn/lm339
- **SPICE model**: https://www.ti.com/lit/zip/slcj010 (PSpice)
- **Notes**: Open-collector — **requires external pull-up**. Outputs wire-OR-able.

### TLV3401 — Single nanopower open-drain CMOS comparator, rail-to-rail input
- **Manufacturer(s)**: Texas Instruments (primary; sole source)
- **MFR P/N (primary)**: TLV3401IDBVR
- **Refdes prefix**: U
- **Package(s)**: SOT-23-5 (DBV), SOIC-8 (D), PDIP-8 (P)
- **Pin map (primary package — SOT-23-5)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1   | OUT  | OUT       |
| 2   | GND  | power_in  |
| 3   | IN_POS  | IN        |
| 4   | IN_NEG  | IN        |
| 5   | VCC  | power_in  |

- **KiCad footprint**: `Package_TO_SOT_SMD:SOT-23-5`
- **Description**: Single nanopower comparator with open-drain CMOS output. Inputs tolerate VCC+5 V above the positive rail.
- **Operating voltage / current**: VCC 2.5 V to 16 V (2.7 V min over industrial); 470 nA typ; open-drain output.
- **Datasheet URL**: https://www.ti.com/lit/gpn/tlv3401
- **SPICE model**: https://www.ti.com/lit/zip/sbom412
- **Notes**: **Requires external pull-up resistor** on output. Rail-to-rail (and beyond) input CM.

### LM311 — Single high-speed open-collector comparator with strobe and balance
- **Manufacturer(s)**: Texas Instruments (primary); onsemi, STMicroelectronics (second-source)
- **MFR P/N (primary)**: LM311P
- **Refdes prefix**: U
- **Package(s)**: PDIP-8, SOIC-8, TSSOP-8
- **Pin map (primary package — PDIP-8)**:

| Pin | Name     | Direction |
|-----|----------|-----------|
| 1   | EMIT_OUT | OUT       |
| 2   | IN_POS      | IN        |
| 3   | IN_NEG      | IN        |
| 4   | VCC_NEG     | power_in  |
| 5   | BALANCE  | IN        |
| 6   | BAL/STRB | IN        |
| 7   | COL_OUT  | OUT       |
| 8   | VCC_POS     | power_in  |

- **KiCad footprint**: `Package_DIP:DIP-8_W7.62mm`
- **Description**: Single high-speed (165 ns) differential comparator with independently accessible open-collector and emitter outputs, plus strobe.
- **Operating voltage / current**: VCC+ − VCC- = 3.5 V to 30 V; output sink **50 mA at up to 50 V** at COL OUT; supply ~5.4 mA typ.
- **Datasheet URL**: https://www.ti.com/lit/gpn/lm311
- **SPICE model**: https://www.ti.com/lit/zip/slcm011
- **Notes**: Open-collector COL OUT — **requires external pull-up**. Pull BAL/STRB low to disable output. Inputs limited to within ±15 V of supply midpoint.

---

## Voltage Regulators

### LM7805 — Fixed +5V positive linear regulator, 1A
- **Manufacturer(s)**: Texas Instruments (primary), STMicroelectronics, onsemi
- **MFR P/N (primary)**: LM7805CT (TI, TO-220) / L7805CV (ST)
- **Refdes prefix**: U
- **Package(s)**: TO-220 (3-pin), TO-263 (D2PAK), TO-252 (DPAK)
- **Pin map (primary package — TO-220)**:

| Pin | Name   | Direction  |
|-----|--------|------------|
| 1   | INPUT  | power_in   |
| 2   | GND    | power_in   |
| 3   | OUTPUT | power_out  |

- **KiCad footprint**: `Package_TO_SOT_THT:TO-220-3_Vertical`
- **Description**: Classic fixed positive linear regulator. Non-LDO (~2V dropout).
- **Operating voltage / current**: V_in max 35V, V_out 5.0V ±4%, I_out max 1.5A (typ. 1A continuous), dropout ~2.0V.
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/lm340.pdf
- **SPICE model**: https://www.ti.com/product/LM340
- **Notes**: Requires 0.33µF input and 0.1µF output cap close to pins. Heatsink above ~500mA. Tab is GND.

### LM7812 — Fixed +12V positive linear regulator, 1A
- **Manufacturer(s)**: Texas Instruments, STMicroelectronics, onsemi
- **MFR P/N (primary)**: LM7812CT (TI, TO-220) / L7812CV (ST)
- **Refdes prefix**: U
- **Package(s)**: TO-220 (3-pin), TO-263, TO-252
- **Pin map (primary package — TO-220)**:

| Pin | Name   | Direction  |
|-----|--------|------------|
| 1   | INPUT  | power_in   |
| 2   | GND    | power_in   |
| 3   | OUTPUT | power_out  |

- **KiCad footprint**: `Package_TO_SOT_THT:TO-220-3_Vertical`
- **Description**: Fixed positive linear regulator, +12V variant of 78xx. Non-LDO.
- **Operating voltage / current**: V_in max 35V, V_out 12.0V ±4%, I_out max 1.5A, dropout ~2.0V (V_in ≥ ~14.5V).
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/lm340.pdf
- **SPICE model**: https://www.ti.com/product/LM340
- **Notes**: Tab is GND.

### LM7905 — Fixed -5V NEGATIVE linear regulator, 1A
- **Manufacturer(s)**: Texas Instruments, STMicroelectronics, onsemi
- **MFR P/N (primary)**: LM7905CT (TI, TO-220) / L7905CV (ST)
- **Refdes prefix**: U
- **Package(s)**: TO-220 (3-pin), TO-263
- **Pin map (primary package — TO-220)** — *different from 78xx*:

| Pin | Name   | Direction  |
|-----|--------|------------|
| 1   | GND    | power_in   |
| 2   | INPUT  | power_in   |
| 3   | OUTPUT | power_out  |

- **KiCad footprint**: `Package_TO_SOT_THT:TO-220-3_Vertical`
- **Description**: Fixed negative linear regulator (79xx family). Non-LDO. **Pinout differs from 78xx**.
- **Operating voltage / current**: V_in max -35V, V_out -5.0V ±4%, I_out max 1.5A, dropout ~1.1V typ.
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/lm7905.pdf
- **SPICE model**: https://www.ti.com/product/LM7905
- **Notes**: **DO NOT swap footprints with 78xx**. Requires 2.2µF tantalum input and 1µF tantalum output. Tab is INPUT (not GND).

### LM317 — Adjustable +1.25V to +37V positive regulator, 1.5A
- **Manufacturer(s)**: Texas Instruments, STMicroelectronics, onsemi
- **MFR P/N (primary)**: LM317T (TI, TO-220)
- **Refdes prefix**: U
- **Package(s)**: TO-220, TO-263, TO-252, SOT-223 (LM317L variants)
- **Pin map (primary package — TO-220)**:

| Pin | Name   | Direction  |
|-----|--------|------------|
| 1   | ADJ    | IN         |
| 2   | OUTPUT | power_out  |
| 3   | INPUT  | power_in   |

- **KiCad footprint**: `Package_TO_SOT_THT:TO-220-3_Vertical`
- **Description**: Three-terminal adjustable positive regulator. V_out = 1.25V × (1 + R2/R1) + I_ADJ × R2.
- **Operating voltage / current**: V_in − V_out max 40V, V_out 1.25–37V, I_out max 1.5A, dropout ~2.0V.
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/lm317.pdf
- **SPICE model**: https://www.ti.com/product/LM317
- **Notes**: R1 typically 240Ω; min load ~10mA. Tab is OUTPUT — isolation required when heatsinking.

### LM337 — Adjustable -1.25V to -37V NEGATIVE regulator, 1.5A
- **Manufacturer(s)**: Texas Instruments, STMicroelectronics, onsemi
- **MFR P/N (primary)**: LM337T (TI, TO-220)
- **Refdes prefix**: U
- **Package(s)**: TO-220, TO-263
- **Pin map (primary package — TO-220)** — *different from LM317*:

| Pin | Name   | Direction  |
|-----|--------|------------|
| 1   | ADJ    | IN         |
| 2   | INPUT  | power_in   |
| 3   | OUTPUT | power_out  |

- **KiCad footprint**: `Package_TO_SOT_THT:TO-220-3_Vertical`
- **Description**: Three-terminal adjustable negative regulator — counterpart to LM317.
- **Operating voltage / current**: |V_in − V_out| max 40V, V_out -1.25 to -37V, I_out max 1.5A, dropout ~2.0V.
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/lm337.pdf
- **SPICE model**: https://www.ti.com/product/LM337
- **Notes**: **Pin 2 = INPUT, pin 3 = OUTPUT — opposite of LM317**. R1 typically 120Ω. Tab is INPUT.

### AMS1117_33 — Fixed +3.3V 1A LDO regulator (SOT-223)
- **Manufacturer(s)**: Advanced Monolithic Systems (primary), Diodes Inc. (AP1117), HTC Korea
- **MFR P/N (primary)**: AMS1117-3.3 (SOT-223)
- **Refdes prefix**: U
- **Package(s)**: SOT-223 (3-pin + tab), TO-252 (DPAK)
- **Pin map (primary package — SOT-223)**:

| Pin     | Name   | Direction  |
|---------|--------|------------|
| 1       | GND    | power_in   |
| 2       | OUTPUT | power_out  |
| 3       | INPUT  | power_in   |
| 4 (tab) | OUTPUT | power_out  |

- **KiCad footprint**: `Package_TO_SOT_SMD:SOT-223-3_TabPin2`
- **Description**: LDO fixed +3.3V positive linear regulator. Popular in 5V→3.3V level conversion for MCU/Wi-Fi modules.
- **Operating voltage / current**: V_in max 15V, V_out 3.3V ±1.5%, I_out max 1A, dropout 1.1V typ @ 800mA.
- **Datasheet URL**: http://www.advanced-monolithic.com/pdf/ds1117.pdf
- **SPICE model**: (generic LDO model required)
- **Notes**: Requires 10µF tantalum (or 22µF ceramic) on both input and output. Tab is OUTPUT — large copper pour required.

### AMS1117_50 — Fixed +5V 1A LDO regulator (SOT-223)
- **Manufacturer(s)**: Advanced Monolithic Systems (primary), Diodes Inc., HTC Korea
- **MFR P/N (primary)**: AMS1117-5.0 (SOT-223)
- **Refdes prefix**: U
- **Package(s)**: SOT-223, TO-252
- **Pin map (primary package — SOT-223)**:

| Pin     | Name   | Direction  |
|---------|--------|------------|
| 1       | GND    | power_in   |
| 2       | OUTPUT | power_out  |
| 3       | INPUT  | power_in   |
| 4 (tab) | OUTPUT | power_out  |

- **KiCad footprint**: `Package_TO_SOT_SMD:SOT-223-3_TabPin2`
- **Description**: LDO fixed +5V positive linear regulator.
- **Operating voltage / current**: V_in max 15V (V_in ≥ ~6.1V for regulation), V_out 5.0V ±1.5%, I_out max 1A, dropout 1.1V typ @ 800mA.
- **Datasheet URL**: http://www.advanced-monolithic.com/pdf/ds1117.pdf
- **SPICE model**: (generic LDO model required)
- **Notes**: Same caveats as AMS1117_33. Tab tied to OUTPUT.

### LP2950 — Micropower +5V (fixed) LDO regulator, 100mA
- **Manufacturer(s)**: Texas Instruments (primary, ex-National Semiconductor), onsemi
- **MFR P/N (primary)**: LP2950ACZ-5.0 (TO-92)
- **Refdes prefix**: U
- **Package(s)**: TO-92, TO-252/DPAK, SO-8 (LP2951 adj.)
- **Pin map (primary package — TO-92)**:

| Pin | Name   | Direction  |
|-----|--------|------------|
| 1   | INPUT  | power_in   |
| 2   | GND    | power_in   |
| 3   | OUTPUT | power_out  |

- **KiCad footprint**: `Package_TO_SOT_THT:TO-92_Inline`
- **Description**: Micropower fixed +5V LDO with ~75µA quiescent. Designed for battery-powered applications.
- **Operating voltage / current**: V_in max 30V, V_out 5.0V ±0.5% (A-grade), I_out max 100mA, dropout 380mV typ @ 100mA, I_q ~75µA.
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/lp2950.pdf
- **SPICE model**: https://www.ti.com/product/LP2950
- **Notes**: Requires 1µF tantalum (or ≥2.2µF ceramic with ESR 0.1–6Ω) on output for stability — ESR-sensitive. For adjustable variant use LP2951.

---

## Transistors

### BC547 — NPN BJT, general-purpose small-signal, 100 mA, 45 V
- **Manufacturer(s)**: onsemi (primary); Diotec, Nexperia
- **MFR P/N (primary)**: BC547B
- **Refdes prefix**: Q
- **Package(s)**: TO-92 (3-pin); SMD equivalent BC847 (SOT-23)
- **Pin map (primary package — TO-92, viewed from flat side)**:

| Pin | Name      | Direction |
|-----|-----------|-----------|
| 1   | Collector | IN        |
| 2   | Base      | IN        |
| 3   | Emitter   | OUT       |

- **KiCad footprint**: `Package_TO_SOT_THT:TO-92_Inline`
- **Description**: General-purpose NPN BJT for low-power switching and audio-frequency amplification. European CBE pinout.
- **Operating voltage / current**: V_CEO 45 V, V_CBO 50 V, I_C 100 mA, P_tot 500 mW; h_FE 200–450 (B grade), f_T 300 MHz.
- **Datasheet URL**: https://www.onsemi.com/pdf/datasheet/bc547-d.pdf
- **SPICE model**: onsemi PSpice library
- **Notes**: CBE pinout — opposite of 2N3904 (EBC). Complementary PNP is BC557.

### BC557 — PNP BJT, general-purpose small-signal, 100 mA, 45 V
- **Manufacturer(s)**: onsemi (primary); Diotec, Nexperia
- **MFR P/N (primary)**: BC557B
- **Refdes prefix**: Q
- **Package(s)**: TO-92; SMD equivalent BC857 (SOT-23)
- **Pin map (primary package — TO-92, from flat)**:

| Pin | Name      | Direction |
|-----|-----------|-----------|
| 1   | Collector | OUT       |
| 2   | Base      | IN        |
| 3   | Emitter   | IN        |

- **KiCad footprint**: `Package_TO_SOT_THT:TO-92_Inline`
- **Description**: General-purpose PNP BJT, complementary to BC547.
- **Operating voltage / current**: V_CEO −45 V, V_CBO −50 V, V_EBO −5 V, I_C −100 mA, P_tot 500 mW; h_FE 200–450, f_T 150 MHz.
- **Datasheet URL**: https://www.onsemi.com/pdf/datasheet/bc556bta-d.pdf
- **SPICE model**: onsemi PSpice library
- **Notes**: Same CBE pinout as BC547.

### Q2N3904 — NPN BJT, general-purpose small-signal, 200 mA, 40 V
- **Manufacturer(s)**: onsemi (primary); Diodes Inc., Central Semiconductor
- **MFR P/N (primary)**: 2N3904BU
- **Refdes prefix**: Q
- **Package(s)**: TO-92; SMD equivalent MMBT3904 (SOT-23)
- **Pin map (primary package — TO-92, from flat)**:

| Pin | Name      | Direction |
|-----|-----------|-----------|
| 1   | Emitter   | OUT       |
| 2   | Base      | IN        |
| 3   | Collector | IN        |

- **KiCad footprint**: `Package_TO_SOT_THT:TO-92_Inline`
- **Description**: Industry-standard small-signal NPN. JEDEC EBC pinout from flat.
- **Operating voltage / current**: V_CEO 40 V, V_CBO 60 V, I_C 200 mA, P_tot 625 mW; h_FE 100–300, f_T 300 MHz.
- **Datasheet URL**: https://www.onsemi.com/download/data-sheet/pdf/2n3903-d.pdf
- **SPICE model**: onsemi PSpice library
- **Notes**: EBC pinout — NOT pin-compatible with BC547 (CBE).

### Q2N3906 — PNP BJT, general-purpose small-signal, 200 mA, 40 V
- **Manufacturer(s)**: onsemi (primary); Diodes Inc., Central Semiconductor
- **MFR P/N (primary)**: 2N3906BU
- **Refdes prefix**: Q
- **Package(s)**: TO-92; SMD equivalent MMBT3906 (SOT-23)
- **Pin map (primary package — TO-92, from flat)**:

| Pin | Name      | Direction |
|-----|-----------|-----------|
| 1   | Emitter   | IN        |
| 2   | Base      | IN        |
| 3   | Collector | OUT       |

- **KiCad footprint**: `Package_TO_SOT_THT:TO-92_Inline`
- **Description**: Industry-standard small-signal PNP, complementary to 2N3904. JEDEC EBC.
- **Operating voltage / current**: V_CEO −40 V, V_CBO −40 V, V_EBO −5 V, I_C −200 mA, P_tot 625 mW; h_FE 100–300, f_T 250 MHz.
- **Datasheet URL**: https://www.onsemi.com/download/data-sheet/pdf/2n3906-d.pdf
- **SPICE model**: onsemi PSpice library
- **Notes**: Same EBC pinout as 2N3904.

### Q2N2222 — NPN BJT, medium-power switching, 800 mA, 40 V
- **Manufacturer(s)**: onsemi (P2N2222A in TO-92); Central Semiconductor (2N2222A in TO-18 metal can)
- **MFR P/N (primary)**: P2N2222A (TO-92) / 2N2222A (TO-18)
- **Refdes prefix**: Q
- **Package(s)**: TO-92 (P2N2222A); TO-18 metal can (original); SMD PMBT2222A (SOT-23)
- **Pin map (P2N2222A TO-92, from flat)**:

| Pin | Name      | Direction |
|-----|-----------|-----------|
| 1   | Emitter   | OUT       |
| 2   | Base      | IN        |
| 3   | Collector | IN        |

- **KiCad footprint**: `Package_TO_SOT_THT:TO-92_Inline` (P2N2222A); `Package_TO_SOT_THT:TO-18-3` (original TO-18 can)
- **Description**: Classic medium-power NPN switching transistor.
- **Operating voltage / current**: V_CEO 40 V, V_CBO 75 V, I_C 800 mA continuous (1 A peak), P_tot 625 mW (TO-92); h_FE 50–300, f_T 300 MHz.
- **Datasheet URL**: https://www.onsemi.com/pdf/datasheet/p2n2222a-d.pdf
- **SPICE model**: onsemi PSpice library
- **Notes**: TO-92 P2N2222A is EBC; original TO-18 can has its own pin order — verify package variant.

### Q2N7000 — N-channel MOSFET, small-signal, 200 mA, 60 V
- **Manufacturer(s)**: onsemi (primary); Diodes Inc., Microchip
- **MFR P/N (primary)**: 2N7000
- **Refdes prefix**: Q
- **Package(s)**: TO-92; SMD equivalent 2N7002 (SOT-23)
- **Pin map (primary package — TO-92, from flat)**:

| Pin | Name   | Direction |
|-----|--------|-----------|
| 1   | Source | OUT       |
| 2   | Gate   | IN        |
| 3   | Drain  | IN        |

- **KiCad footprint**: `Package_TO_SOT_THT:TO-92_Inline`
- **Description**: Small-signal N-channel enhancement-mode MOSFET for logic-level switching.
- **Operating voltage / current**: V_DS 60 V, V_GS ±20 V, I_D 200 mA continuous, R_DS(on) 5 Ω @ V_GS=10 V; V_GS(th) 0.8–3.0 V; P_D 400 mW.
- **Datasheet URL**: https://www.onsemi.com/download/data-sheet/pdf/2n7000-d.pdf
- **SPICE model**: onsemi PSpice library
- **Notes**: Logic-level gate. ESD-sensitive — no internal gate protection.

### BS170 — N-channel MOSFET, small-signal, 500 mA, 60 V
- **Manufacturer(s)**: onsemi (primary); Diodes Inc.
- **MFR P/N (primary)**: BS170
- **Refdes prefix**: Q
- **Package(s)**: TO-92; SMD equivalent MMBF170 (SOT-23)
- **Pin map (primary package — TO-92, from flat)**:

| Pin | Name   | Direction |
|-----|--------|-----------|
| 1   | Drain  | IN        |
| 2   | Gate   | IN        |
| 3   | Source | OUT       |

- **KiCad footprint**: `Package_TO_SOT_THT:TO-92_Inline`
- **Description**: Small-signal N-channel MOSFET, similar to 2N7000 but **mirrored pinout** (D-G-S vs S-G-D).
- **Operating voltage / current**: V_DS 60 V, V_GS ±20 V, I_D 500 mA continuous, R_DS(on) 5 Ω @ V_GS=10 V; V_GS(th) 0.8–3.0 V (typ 2.0 V); P_D 830 mW.
- **Datasheet URL**: https://www.mouser.com/datasheet/2/308/BS170_D-1803008.pdf
- **SPICE model**: onsemi PSpice library
- **Notes**: NOT pin-compatible with 2N7000 despite similar specs. ESD-sensitive.

### IRLB8721 — Logic-level N-channel power MOSFET, 62 A, 30 V
- **Manufacturer(s)**: Infineon (primary)
- **MFR P/N (primary)**: IRLB8721PBF
- **Refdes prefix**: Q
- **Package(s)**: TO-220AB (3 pin + tab)
- **Pin map (primary package — TO-220, front view)**:

| Pin | Name           | Direction |
|-----|----------------|-----------|
| 1   | Gate           | IN        |
| 2   | Drain (= tab)  | IN        |
| 3   | Source         | OUT       |
| tab | Drain          | IN        |

- **KiCad footprint**: `Package_TO_SOT_THT:TO-220-3_Vertical` (or `TO-220-3_Horizontal_TabDown` for heatsinked)
- **Description**: Logic-level HEXFET — fully enhanced at V_GS=4.5V, directly drivable from 5V or 3.3V MCU pins.
- **Operating voltage / current**: V_DS 30V, V_GS ±20V, I_D 62A @ T_C=25°C, R_DS(on) 8.7mΩ max @ V_GS=4.5V (6.5mΩ typ); V_GS(th) 1.35–2.35V; P_D 65W.
- **Datasheet URL**: https://www.infineon.com/dgdl/irlb8721pbf.pdf?fileId=5546d462533600a40153566056732591
- **SPICE model**: https://www.infineon.com/cms/en/product/power/mosfet/n-channel/irlb8721pbf/
- **Notes**: Tab is Drain — isolate from grounded heatsinks. Logic-level gate.

### IRFZ44N — Standard-gate N-channel power MOSFET, 49 A, 55 V
- **Manufacturer(s)**: Infineon (primary); Vishay
- **MFR P/N (primary)**: IRFZ44NPBF
- **Refdes prefix**: Q
- **Package(s)**: TO-220AB
- **Pin map (primary package — TO-220, front view)**:

| Pin | Name           | Direction |
|-----|----------------|-----------|
| 1   | Gate           | IN        |
| 2   | Drain (= tab)  | IN        |
| 3   | Source         | OUT       |
| tab | Drain          | IN        |

- **KiCad footprint**: `Package_TO_SOT_THT:TO-220-3_Vertical`
- **Description**: Workhorse standard-threshold N-channel HEXFET for medium-voltage power switching.
- **Operating voltage / current**: V_DS 55V, V_GS ±20V, I_D 49A @ T_C=25°C, R_DS(on) 17.5mΩ max @ V_GS=10V; V_GS(th) 2.0–4.0V; P_D 94W.
- **Datasheet URL**: https://www.infineon.com/dgdl/Infineon-IRFZ44N-DataSheet-v01_01-EN.pdf?fileId=5546d462533600a40153563b3a9f220d
- **SPICE model**: Infineon "Simulation Models" tab
- **Notes**: **NOT logic-level** — V_GS(th) up to 4V; cannot be driven from 3.3V MCU. Use a gate driver or pick IRLB8721/IRLZ44N.

### TIP120 — NPN Darlington power transistor, 5 A, 60 V
- **Manufacturer(s)**: onsemi (primary); STMicroelectronics, Diotec
- **MFR P/N (primary)**: TIP120
- **Refdes prefix**: Q
- **Package(s)**: TO-220AB
- **Pin map (primary package — TO-220, front view)**:

| Pin | Name              | Direction |
|-----|-------------------|-----------|
| 1   | Base              | IN        |
| 2   | Collector (= tab) | IN        |
| 3   | Emitter           | OUT       |
| tab | Collector         | IN        |

- **KiCad footprint**: `Package_TO_SOT_THT:TO-220-3_Vertical`
- **Description**: Monolithic NPN Darlington with integrated B-E shunt resistors. Drives inductive loads from logic-level signals.
- **Operating voltage / current**: V_CEO 60V, V_CBO 60V, V_EBO 5V, I_C 5A continuous (8A peak), P_D 65W; h_FE 1000 min @ I_C=3A, V_CE(sat) 2V typ / 4V max @ I_C=5A.
- **Datasheet URL**: https://www.onsemi.com/pdf/datasheet/tip120-d.pdf
- **SPICE model**: onsemi PSpice library
- **Notes**: High V_CE(sat) — heatsink required above ~1A. TIP121/122 are pin-compatible higher-V versions; PNP complement TIP125/126/127.

---

## Diodes

### D1N4148 — Fast signal switching diode (100V / 200mA, DO-35)
- **Manufacturer(s)**: onsemi (primary), Vishay, Diotec, NXP
- **MFR P/N (primary)**: 1N4148 (DO-35)
- **Refdes prefix**: D
- **Package(s)**: DO-35 (glass axial)
- **Pin map (primary package)**:

| Pin | Name    | Direction |
|-----|---------|-----------|
| 1   | Anode   | IN        |
| 2   | Cathode | OUT       |

- **KiCad footprint**: `Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal`
- **Description**: Small-signal, high-speed switching diode. Industry-standard general-purpose signal diode.
- **Operating voltage / current**: V_R max = 100V; I_F avg = 200mA; V_F typ ≈ 0.7V @ 10mA; t_rr ≈ 4ns.
- **Datasheet URL**: https://www.onsemi.com/pdf/datasheet/1n4148-d.pdf
- **SPICE model**: generic 1N4148 SPICE model widely available
- **Notes**: Cathode marked with band. Not for power rectification.

### D1N4001 — 50V / 1A general-purpose rectifier (DO-41)
- **Manufacturer(s)**: onsemi (primary), Vishay, Diotec
- **MFR P/N (primary)**: 1N4001 (DO-41)
- **Refdes prefix**: D
- **Package(s)**: DO-41 (axial)
- **Pin map (primary package)**:

| Pin | Name    | Direction |
|-----|---------|-----------|
| 1   | Anode   | IN        |
| 2   | Cathode | OUT       |

- **KiCad footprint**: `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal`
- **Description**: Low-voltage general-purpose silicon rectifier.
- **Operating voltage / current**: V_R max = 50V; I_F avg = 1A; V_F typ ≈ 1.0V @ 1A; I_FSM = 30A.
- **Datasheet URL**: https://www.onsemi.com/pdf/datasheet/1n4001-d.pdf
- **SPICE model**: generic 1N4001 SPICE model widely available
- **Notes**: Same DO-41 package as 1N4007 but only 50V reverse — do not substitute upward without checking. Slow recovery (~30µs).

### D1N4007 — 1000V / 1A general-purpose rectifier (DO-41)
- **Manufacturer(s)**: onsemi (primary), Vishay, Diotec
- **MFR P/N (primary)**: 1N4007 (DO-41)
- **Refdes prefix**: D
- **Package(s)**: DO-41
- **Pin map (primary package)**:

| Pin | Name    | Direction |
|-----|---------|-----------|
| 1   | Anode   | IN        |
| 2   | Cathode | OUT       |

- **KiCad footprint**: `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal`
- **Description**: High-voltage general-purpose silicon rectifier — default choice for mains rectification.
- **Operating voltage / current**: V_R max = 1000V; I_F avg = 1A; V_F typ ≈ 1.0V @ 1A; I_FSM = 30A.
- **Datasheet URL**: https://www.onsemi.com/pdf/datasheet/1n4007-d.pdf
- **SPICE model**: generic 1N4007 SPICE model widely available
- **Notes**: Safe upward substitute for any 1N400x. Slow, not for SMPS.

### D1N5817 — Schottky rectifier (20V / 1A, low V_F, DO-41)
- **Manufacturer(s)**: onsemi (primary), Vishay, Diotec
- **MFR P/N (primary)**: 1N5817 (DO-41)
- **Refdes prefix**: D
- **Package(s)**: DO-41
- **Pin map (primary package)**:

| Pin | Name    | Direction |
|-----|---------|-----------|
| 1   | Anode   | IN        |
| 2   | Cathode | OUT       |

- **KiCad footprint**: `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal`
- **Description**: Schottky barrier rectifier with low V_F and fast switching.
- **Operating voltage / current**: V_R max = 20V; I_F avg = 1A; V_F typ ≈ 0.45V @ 1A; I_FSM = 25A.
- **Datasheet URL**: https://www.onsemi.com/pdf/datasheet/1n5817-d.pdf
- **SPICE model**: generic 1N5817 Schottky SPICE model widely available
- **Notes**: Higher reverse leakage than silicon. For 30/40V use 1N5818/1N5819.

### D1N4733A — Zener diode, 5.1V 1W (DO-41)
- **Manufacturer(s)**: onsemi (primary), Vishay, Diotec
- **MFR P/N (primary)**: 1N4733A (DO-41)
- **Refdes prefix**: D
- **Package(s)**: DO-41
- **Pin map (primary package)**:

| Pin | Name    | Direction |
|-----|---------|-----------|
| 1   | Anode   | IN        |
| 2   | Cathode | OUT       |

- **KiCad footprint**: `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal`
- **Description**: 1W Zener voltage reference / regulator at 5.1V.
- **Operating voltage / current**: V_Z = 5.1V @ I_ZT = 49mA; P_D = 1W; I_ZM ≈ 178mA; tolerance ±5% (A suffix).
- **Datasheet URL**: https://www.onsemi.com/pdf/datasheet/1n4728a-d.pdf
- **SPICE model**: generic 1N4733A Zener SPICE model widely available
- **Notes**: Reverse-biased operation — cathode (band) to higher potential.

### D1N4742A — Zener diode, 12V 1W (DO-41)
- **Manufacturer(s)**: onsemi (primary), Vishay, Diotec
- **MFR P/N (primary)**: 1N4742A (DO-41)
- **Refdes prefix**: D
- **Package(s)**: DO-41
- **Pin map (primary package)**:

| Pin | Name    | Direction |
|-----|---------|-----------|
| 1   | Anode   | IN        |
| 2   | Cathode | OUT       |

- **KiCad footprint**: `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal`
- **Description**: 1W Zener voltage reference / regulator at 12V.
- **Operating voltage / current**: V_Z = 12V @ I_ZT = 21mA; P_D = 1W; I_ZM ≈ 76mA; tolerance ±5%.
- **Datasheet URL**: https://www.onsemi.com/pdf/datasheet/1n4728a-d.pdf
- **SPICE model**: generic 1N4742A Zener SPICE model widely available
- **Notes**: Avalanche-dominated above ~5.6V — sharper knee than low-V Zeners.

---

## Specialty ICs

### NE555 — Precision astable/monostable timer IC
- **Manufacturer(s)**: Texas Instruments (primary); ON Semiconductor, ST, Diodes Inc.
- **MFR P/N (primary)**: NE555P (TI, PDIP-8)
- **Refdes prefix**: U
- **Package(s)**: PDIP-8 (P), SOIC-8 (D), SO-8 (PS), TSSOP-8 (PW)
- **Pin map (primary package)**:

| Pin | Name  | Direction    |
|-----|-------|--------------|
| 1   | GND   | power_in     |
| 2   | TRIG  | IN           |
| 3   | OUT   | OUT          |
| 4   | RESET | IN           |
| 5   | CONT  | IN/OUT       |
| 6   | THRES | IN           |
| 7   | DISCH | OUT (OC)     |
| 8   | VCC   | power_in     |

- **KiCad footprint**: `Package_DIP:DIP-8_W7.62mm`
- **Description**: Classic bipolar precision timer. Output sinks/sources up to 200 mA.
- **Operating voltage / current**: VCC 4.5 V to 16 V (SE555: up to 18 V); supply ~3 mA @ 5 V.
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/ne555.pdf
- **SPICE model**: https://www.ti.com/product/NE555 (TI PSpice model: NE555.TSC)
- **Notes**: Pin 5 (CONT) should be bypassed to GND with 10 nF when unused. Output not rail-to-rail. CMOS variants (TLC555/LMC555) for low power.

### LM386 — Low-voltage audio power amplifier
- **Manufacturer(s)**: Texas Instruments (primary); JRC (NJM386), onsemi
- **MFR P/N (primary)**: LM386N-1 (TI, PDIP-8)
- **Refdes prefix**: U
- **Package(s)**: PDIP-8 (N), SOIC-8 (M), VSSOP-8 (MM)
- **Pin map (primary package)**:

| Pin | Name   | Direction |
|-----|--------|-----------|
| 1   | GAIN   | Passive   |
| 2   | INPUT_NEG | IN        |
| 3   | INPUT_POS | IN        |
| 4   | GND    | power_in  |
| 5   | VOUT   | OUT       |
| 6   | VS     | power_in  |
| 7   | BYPASS | OUT       |
| 8   | GAIN   | Passive   |

- **KiCad footprint**: `Package_DIP:DIP-8_W7.62mm`
- **Description**: Low-voltage class-AB audio power amplifier. Fixed gain 20 (extendable to 200 by 10 µF between pins 1 and 8).
- **Operating voltage / current**: VS 4 V to 12 V (LM386N-1/-3), 5 V to 18 V (LM386N-4); Iq ~4 mA.
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/lm386.pdf
- **SPICE model**: https://www.ti.com/product/LM386
- **Notes**: Add Zobel network (10 Ω + 50 nF) on VOUT. Pin 7 (BYPASS) decouple 10 µF. Notorious for oscillation if PCB layout is poor.

### DS18B20 — 1-Wire programmable digital thermometer
- **Manufacturer(s)**: Analog Devices (Maxim Integrated, primary)
- **MFR P/N (primary)**: DS18B20+ (TO-92)
- **Refdes prefix**: U
- **Package(s)**: TO-92 (3-pin), SO-8, µSOP-8
- **Pin map (primary package, TO-92, flat side facing you)**:

| Pin | Name | Direction    |
|-----|------|--------------|
| 1   | GND  | power_in     |
| 2   | DQ   | BIDIR        |
| 3   | VDD  | power_in     |

- **KiCad footprint**: `Package_TO_SOT_THT:TO-92_Inline`
- **Description**: 1-Wire digital thermometer, -55 to +125 °C with ±0.5 °C accuracy from -10 to +85 °C; user-selectable 9–12-bit resolution. Each chip has unique 64-bit ROM ID.
- **Operating voltage / current**: VDD 3.0 V to 5.5 V; active 1.0 mA typ, standby 750 nA typ.
- **Datasheet URL**: https://www.analog.com/media/en/technical-documentation/data-sheets/DS18B20.pdf
- **SPICE model**: (generic model required)
- **Notes**: DQ requires a 4.7 kΩ pull-up to VDD. Conversion up to 750 ms at 12-bit. Counterfeits widespread; genuine parts have "+" suffix.

### DS1307 — I²C real-time clock with 56-byte NV RAM
- **Manufacturer(s)**: Analog Devices (Maxim Integrated, primary)
- **MFR P/N (primary)**: DS1307+ (PDIP-8)
- **Refdes prefix**: U
- **Package(s)**: PDIP-8, SO-8
- **Pin map (primary package)**:

| Pin | Name     | Direction        |
|-----|----------|------------------|
| 1   | X1       | IN (xtal)        |
| 2   | X2       | OUT (xtal)       |
| 3   | VBAT     | power_in         |
| 4   | GND      | power_in         |
| 5   | SDA      | BIDIR            |
| 6   | SCL      | IN               |
| 7   | SQW/OUT  | OUT (OD)         |
| 8   | VCC      | power_in         |

- **KiCad footprint**: `Package_DIP:DIP-8_W7.62mm`
- **Description**: BCD real-time clock/calendar with 56 bytes of battery-backed SRAM. I²C up to 100 kHz, fixed address 0x68.
- **Operating voltage / current**: VCC 4.5–5.5 V; VBAT 2.0–3.5 V; active 1.5 mA max; timekeeping on VBAT 500 nA typ.
- **Datasheet URL**: https://www.analog.com/media/en/technical-documentation/data-sheets/DS1307.pdf
- **SPICE model**: (generic model required)
- **Notes**: External 32.768 kHz crystal with 12.5 pF load; do NOT add loading caps. SDA/SCL need external pull-ups (~4.7 kΩ). DS3231 is the recommended upgrade. SQW/OUT is open-drain.

### MAX7219 — Serial-input 8-digit common-cathode LED display driver
- **Manufacturer(s)**: Analog Devices (Maxim Integrated, primary)
- **MFR P/N (primary)**: MAX7219CNG+ (PDIP-24 wide)
- **Refdes prefix**: U
- **Package(s)**: PDIP-24 wide (15.24 mm row spacing), SO-24 wide (WG), SSOP-24 (EWG)
- **Pin map (primary package)**:

| Pin | Name   | Direction |
|-----|--------|-----------|
| 1   | DIN    | IN        |
| 2   | DIG 0  | OUT       |
| 3   | DIG 4  | OUT       |
| 4   | GND    | power_in  |
| 5   | DIG 6  | OUT       |
| 6   | DIG 2  | OUT       |
| 7   | DIG 3  | OUT       |
| 8   | DIG 7  | OUT       |
| 9   | GND    | power_in  |
| 10  | DIG 5  | OUT       |
| 11  | DIG 1  | OUT       |
| 12  | LOAD   | IN        |
| 13  | CLK    | IN        |
| 14  | SEG A  | OUT       |
| 15  | SEG F  | OUT       |
| 16  | SEG B  | OUT       |
| 17  | SEG G  | OUT       |
| 18  | ISET   | IN        |
| 19  | V_POS     | power_in  |
| 20  | SEG C  | OUT       |
| 21  | SEG E  | OUT       |
| 22  | SEG DP | OUT       |
| 23  | SEG D  | OUT       |
| 24  | DOUT   | OUT       |

- **KiCad footprint**: `Package_DIP:DIP-24_W15.24mm`
- **Description**: Serial-input common-cathode 7-segment LED driver multiplexing up to 8 digits (or an 8×8 matrix). Includes BCD decoder and 8×8 SRAM.
- **Operating voltage / current**: V+ 4.0–5.5 V; up to 330 mA with all segments on; shutdown ~150 µA typ.
- **Datasheet URL**: https://www.analog.com/media/en/technical-documentation/data-sheets/MAX7219-MAX7221.pdf
- **SPICE model**: (generic model required)
- **Notes**: Peak segment current set by R_SET between ISET and V+ (9.53 kΩ ≈ 40 mA/seg). Place 10 µF + 0.1 µF at V+. Daisy-chain via DOUT→DIN. Use MAX7221 for clean SPI buses.

---

## Sensors

### TMP36 — Low-voltage analog temperature sensor (10 mV/°C)
- **Manufacturer(s)**: Analog Devices (primary)
- **MFR P/N (primary)**: TMP36GT9Z
- **Refdes prefix**: U
- **Package(s)**: TO-92 (3-pin), SOIC-8 (TMP36GSZ), SOT-23-5 (TMP36GRT)
- **Pin map (primary package)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1   | +Vs  | power_in  |
| 2   | VOUT | OUT       |
| 3   | GND  | power_in  |

- **KiCad footprint**: `Package_TO_SOT_THT:TO-92_Inline`
- **Description**: Precision centigrade temperature sensor — linear analog output (10 mV/°C, 750 mV at 25 °C). No calibration required.
- **Operating voltage / current**: V_S 2.7–5.5 V; ~50 µA quiescent; analog 0.1–2.0 V over −40 to +125 °C.
- **Datasheet URL**: https://www.analog.com/media/en/technical-documentation/data-sheets/TMP35_36_37.pdf
- **SPICE model**: (generic model required)
- **Notes**: 500 mV offset enables sub-zero on unipolar ADCs. Add 0.1 µF bypass close to +Vs.

### BMP280 — Digital barometric pressure & temperature sensor (I²C/SPI)
- **Manufacturer(s)**: Bosch Sensortec (sole source)
- **MFR P/N (primary)**: BMP280
- **Refdes prefix**: U
- **Package(s)**: LGA-8, 2.0 × 2.5 × 0.95 mm, 0.65 mm pitch
- **Pin map (primary package)**:

| Pin | Name       | Direction |
|-----|------------|-----------|
| 1   | GND        | power_in  |
| 2   | CSB        | IN        |
| 3   | SDI / SDA  | BIDIR     |
| 4   | SCK / SCL  | IN        |
| 5   | SDO / ADDR | BIDIR     |
| 6   | VDDIO      | power_in  |
| 7   | GND        | power_in  |
| 8   | VDD        | power_in  |

- **KiCad footprint**: `Package_LGA:Bosch_LGA-8_2x2.5mm_P0.65mm`
- **Description**: Absolute barometric pressure (300–1100 hPa) + integrated temperature. Selectable I²C (3.4 MHz) or SPI (10 MHz).
- **Operating voltage / current**: VDD 1.71–3.6 V, VDDIO 1.2–3.6 V; ~2.7 µA @ 1 Hz typ.
- **Datasheet URL**: https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp280-ds001.pdf
- **SPICE model**: (generic model required)
- **Notes**: 3.3 V part — do not connect to 5 V logic without level shifting. I²C address 0x76 (SDO=GND) or 0x77 (SDO=VDDIO). Tie CSB to VDDIO for I²C.

### MPU6050 — 6-axis MEMS IMU (3-axis gyro + 3-axis accelerometer) with DMP
- **Manufacturer(s)**: InvenSense / TDK (sole source; NRND — see ICM-20602 / ICM-42688)
- **MFR P/N (primary)**: MPU-6050
- **Refdes prefix**: U
- **Package(s)**: QFN-24, 4 × 4 × 0.9 mm, 0.5 mm pitch
- **Pin map (primary package, headline pins)**:

| Pin | Name     | Direction |
|-----|----------|-----------|
| 1   | CLKIN    | IN        |
| 6   | AUX_DA   | BIDIR     |
| 7   | AUX_CL   | OUT       |
| 8   | VLOGIC   | power_in  |
| 9   | AD0      | IN        |
| 10  | REGOUT   | OUT       |
| 11  | FSYNC    | IN        |
| 12  | INT      | OUT       |
| 13  | VDD      | power_in  |
| 18  | GND      | power_in  |
| 20  | CPOUT    | OUT       |
| 23  | SCL      | IN        |
| 24  | SDA      | BIDIR     |

(Pins 2–5, 14–17, 19, 21, 22 are NC/reserved — leave per datasheet.)

- **KiCad footprint**: `Sensor_Motion:InvenSense_QFN-24_4x4mm_P0.5mm`
- **Description**: 6-DOF MotionTracking — 3-axis gyro + 3-axis accelerometer with on-chip Digital Motion Processor (DMP) over I²C.
- **Operating voltage / current**: VDD 2.375–3.46 V, VLOGIC 1.71 V–VDD; ~3.9 mA active.
- **Datasheet URL**: https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf
- **SPICE model**: (generic model required)
- **Notes**: 3.3 V part — do NOT drive directly from 5 V logic. I²C address 0x68 (AD0=GND) / 0x69 (AD0=VDD). Required: 10 nF on CPOUT, 100 nF on REGOUT/VDD/VLOGIC. SDA/SCL pull-ups (2.2–10 kΩ).

### HCSR04 — Ultrasonic ranging breakout module (2–400 cm, 40 kHz)
- **Manufacturer(s)**: Generic Chinese (Cytron, Elec Freaks, ITead, no-name vendors)
- **MFR P/N (primary)**: HC-SR04
- **Refdes prefix**: U
- **Package(s)**: 4-pin SIP module, 2.54 mm pitch
- **Pin map (primary package)**:

| Pin | Name | Direction |
|-----|------|-----------|
| 1   | VCC  | power_in  |
| 2   | TRIG | IN        |
| 3   | ECHO | OUT       |
| 4   | GND  | power_in  |

- **KiCad footprint**: VERIFY — not in stock KiCad library. Use `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` or import a community footprint such as `Sensor:HC-SR04`.
- **Description**: Self-contained ultrasonic distance sensor module. TRIG ≥10 µs pulse → 8-cycle 40 kHz burst → ECHO width proportional to time-of-flight (~58 µs/cm).
- **Operating voltage / current**: VCC 5.0 V ±0.25 V; ~15 mA active, <2 mA idle; ECHO 5 V logic.
- **Datasheet URL**: https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf
- **SPICE model**: (generic model required)
- **Notes**: **5 V part** — divide ECHO for 3.3 V MCUs. Min trigger pulse 10 µs; ≥60 ms between measurements. HC-SR04P / RCWL-1601 accept 3–5 V supply.

---

## Power and Interface

### MOC3021 — Non-zero-crossing triac driver optocoupler
- **Manufacturer(s)**: Vishay (primary), Lite-On, Fairchild/onsemi
- **MFR P/N (primary)**: MOC3021M
- **Refdes prefix**: U
- **Package(s)**: DIP-6
- **Pin map (primary package)**:

| Pin | Name      | Direction |
|-----|-----------|-----------|
| 1   | ANODE     | IN        |
| 2   | CATHODE   | IN        |
| 3   | NC        | NC        |
| 4   | MT1       | OUT       |
| 5   | SUBSTRATE | NC        |
| 6   | MT2       | OUT       |

- **KiCad footprint**: `Package_DIP:DIP-6_W7.62mm`
- **Description**: Optically isolated non-zero-crossing triac driver for gating a larger power triac controlling AC mains loads. 7500 V (peak) isolation.
- **Operating voltage / current**: LED I_F(typ) 15 mA, I_FT(max) 15 mA; output triac V_DRM 400 V, I_TSM 1 A peak; isolation 7500 V_pk (5300 V_RMS).
- **Datasheet URL**: https://www.vishay.com/docs/83648/moc3021m.pdf
- **SPICE model**: (generic model required)
- **Notes**: Random-phase (NON zero-crossing) — use MOC3041/3061/3081 for zero-crossing. Drive a separate power triac through a current-limiting resistor (~360 Ω). Pin 5 leave floating.

### OPTO_4N25 — General-purpose phototransistor optocoupler with base pin
- **Manufacturer(s)**: onsemi (primary), Vishay, Lite-On
- **MFR P/N (primary)**: 4N25
- **Refdes prefix**: U
- **Package(s)**: DIP-6
- **Pin map (primary package)**:

| Pin | Name      | Direction |
|-----|-----------|-----------|
| 1   | ANODE     | IN        |
| 2   | CATHODE   | IN        |
| 3   | NC        | NC        |
| 4   | EMITTER   | OUT       |
| 5   | COLLECTOR | OUT       |
| 6   | BASE      | OUT       |

- **KiCad footprint**: `Package_DIP:DIP-6_W7.62mm`
- **Description**: Single-channel phototransistor optocoupler with accessible base pin. 5300 V_RMS isolation.
- **Operating voltage / current**: LED I_F max 60 mA, V_F ≈ 1.15 V; V_CEO 30 V, I_C max 50 mA, CTR(min) 20%; isolation 5300 V_RMS.
- **Datasheet URL**: https://www.onsemi.com/pdf/datasheet/4n25-d.pdf
- **SPICE model**: onsemi PSpice library
- **Notes**: Base pin (6) usually left floating. Slow (~2–5 µs) — use 6N137 for digital signalling.

### OPTO_TLP521 — Single-channel phototransistor optocoupler (DIP-4)
- **Manufacturer(s)**: Toshiba (primary); Isocom, Lite-On (second-source equivalents)
- **MFR P/N (primary)**: TLP521-1
- **Refdes prefix**: U
- **Package(s)**: DIP-4 (single, primary); DIP-8 dual (TLP521-2); DIP-16 quad (TLP521-4)
- **Pin map (primary package)**:

| Pin | Name      | Direction |
|-----|-----------|-----------|
| 1   | ANODE     | IN        |
| 2   | CATHODE   | IN        |
| 3   | EMITTER   | OUT       |
| 4   | COLLECTOR | OUT       |

- **KiCad footprint**: `Package_DIP:DIP-4_W7.62mm`
- **Description**: Compact single-channel phototransistor optocoupler in DIP-4 — no base pin.
- **Operating voltage / current**: LED I_F max 50 mA, V_F ≈ 1.15 V; V_CEO 55 V, I_C max 50 mA, CTR 50%–600% (rank-dependent); isolation 5000 V_RMS.
- **Datasheet URL**: https://toshiba.semicon-storage.com/info/TLP521-1_datasheet_en_20200924.pdf
- **SPICE model**: (generic model required)
- **Notes**: Officially obsolete in some regions — TLP281 / TLP293 are recommended modern replacements (same pinout).

### TLC5940 — 16-channel constant-current sink LED driver with PWM
- **Manufacturer(s)**: Texas Instruments (primary, sole source)
- **MFR P/N (primary)**: TLC5940NT (DIP-28)
- **Refdes prefix**: U
- **Package(s)**: DIP-28 (NT, primary); HTSSOP-28 (PWP); TSSOP-28 (PW); VQFN-32 (RHB)
- **Pin map (primary package)**:

| Pin | Name   | Direction |
|-----|--------|-----------|
| 1   | OUT1   | OUT       |
| 2   | OUT0   | OUT       |
| 3   | VPRG   | IN        |
| 4   | SIN    | IN        |
| 5   | SCLK   | IN        |
| 6   | XLAT   | IN        |
| 7   | BLANK  | IN        |
| 8   | GND    | power_in  |
| 9   | VCC    | power_in  |
| 10  | IREF   | IN        |
| 11  | DCPRG  | IN        |
| 12  | GSCLK  | IN        |
| 13  | SOUT   | OUT       |
| 14  | XERR   | OUT (OD)  |
| 15  | OUT15  | OUT       |
| 16  | OUT14  | OUT       |
| 17  | OUT13  | OUT       |
| 18  | OUT12  | OUT       |
| 19  | OUT11  | OUT       |
| 20  | OUT10  | OUT       |
| 21  | OUT9   | OUT       |
| 22  | OUT8   | OUT       |
| 23  | OUT7   | OUT       |
| 24  | OUT6   | OUT       |
| 25  | OUT5   | OUT       |
| 26  | OUT4   | OUT       |
| 27  | OUT3   | OUT       |
| 28  | OUT2   | OUT       |

- **KiCad footprint**: `Package_DIP:DIP-28_W7.62mm`
- **Description**: 16-channel constant-current sink LED driver with 12-bit grayscale PWM and 6-bit dot-correction per channel, daisy-chainable.
- **Operating voltage / current**: V_CC 3.0–5.5 V; per-channel sink 0–120 mA programmable (typ max 80 mA continuous), V_OUT max 17 V.
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/tlc5940.pdf
- **SPICE model**: (generic model required)
- **Notes**: NRND — TLC5947/TLC5948A are successors. Requires R_IREF (~2 kΩ for 20 mA/ch). GSCLK & BLANK must be host-toggled; chip does not free-run PWM.

### MAX232 — Dual RS-232 driver/receiver with on-chip charge-pump
- **Manufacturer(s)**: Texas Instruments (primary), Maxim/ADI (originator), Intersil/Renesas
- **MFR P/N (primary)**: MAX232CPE (DIP-16)
- **Refdes prefix**: U
- **Package(s)**: DIP-16, SOIC-16
- **Pin map (primary package)**:

| Pin | Name   | Direction       |
|-----|--------|-----------------|
| 1   | C1_POS    | passive (cap)   |
| 2   | V_POS     | OUT (≈ +10 V)   |
| 3   | C1_NEG    | passive (cap)   |
| 4   | C2_POS    | passive (cap)   |
| 5   | C2_NEG    | passive (cap)   |
| 6   | V_NEG     | OUT (≈ -10 V)   |
| 7   | T2OUT  | OUT (RS-232)    |
| 8   | R2IN   | IN (RS-232)     |
| 9   | R2OUT  | OUT (TTL)       |
| 10  | T2IN   | IN (TTL)        |
| 11  | T1IN   | IN (TTL)        |
| 12  | R1OUT  | OUT (TTL)       |
| 13  | R1IN   | IN (RS-232)     |
| 14  | T1OUT  | OUT (RS-232)    |
| 15  | GND    | power_in        |
| 16  | VCC    | power_in        |

- **KiCad footprint**: `Package_DIP:DIP-16_W7.62mm`
- **Description**: Dual RS-232 line driver/receiver using on-chip dual charge-pump to convert 5 V logic to ±10 V RS-232 from a single 5 V supply.
- **Operating voltage / current**: V_CC 4.5–5.5 V; I_CC ~8 mA typ; driver swing ±7.5 V loaded; receiver inputs ±30 V tolerant; up to 120 kbit/s.
- **Datasheet URL**: https://www.ti.com/lit/ds/symlink/max232.pdf
- **SPICE model**: https://www.ti.com/product/MAX232
- **Notes**: Requires 4 external charge-pump capacitors + VCC bypass. MAX232 specifies 1 µF; MAX232A allows 100 nF. Receivers have internal 5 kΩ pull-down.

---

## Needs Review (VERIFY flags)

The following entries carry `(VERIFY: ...)` flags that should be double-checked against the live KiCad 7+ library before the implementation pass:

- **STM32F411CEU6** — UFQFPN-48 footprint string varies between KiCad library versions (`QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm` vs `UFQFPN-48-1EP_...`).
- **RP2040** — QFN-56 EP size suffix depends on KiCad library version.
- **ESP8266_12F** — `RF_Module:ESP-12F` may not exist in all KiCad library versions; `RF_Module:ESP-12E` shares the same pad pattern.
- **LMV358** — No through-hole part stocked by TI; primary footprint is SOIC-8. Use a compatible second-source DIP-8 if through-hole is required.
- **HCSR04** — Not in the stock KiCad library at all; a 4-pin 2.54 mm header footprint or a community-supplied module footprint must be selected.
All chips in this catalogue now carry full per-pin tables, including the seven previously-abbreviated high-pin-count MCUs (ATmega2560, ATmega32U4, STM32F103C8T6, STM32F411CEU6, RP2040, ESP32_WROOM_32, ESP8266_12F).

Class names for `2N...` transistors and `1N...` diodes are prefixed with their IEEE 315 refdes letter (`Q2N3904`, `Q2N3906`, `Q2N2222`, `Q2N7000`; `D1N4148`, `D1N4001`, `D1N4007`, `D1N5817`, `D1N4733A`, `D1N4742A`) — both legal Python identifiers and faithful to the real-world refdes-plus-part-number naming on schematics and BOMs (Q1 is a transistor; per the BOM, Q1 is a 2N3904).
