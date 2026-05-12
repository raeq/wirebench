# Substrate-Compatibility Audit

Generated from the live `is_*` properties on every registered component.  Re-generate with `uv run python scripts/generate_substrate_audit.py`.

Columns:

- **TH**: `is_through_hole` — leads pass through breadboard / perfboard holes
- **SMD**: `is_smd` — surface-mount pad geometry
- **BB**: `is_breadboard_compatible` — fits a standard 830-pin solderless breadboard
- **PB**: `is_perfboard_compatible` — fits standard 0.1" perfboard
- **PCB**: `is_pcb_compatible` — placeable on a custom PCB (THT or SMD)
- **DB**: `is_dead_bug_compatible` — wired point-to-point in dead-bug fashion

| Class | TH | SMD | BB | PB | PCB | DB | Footprint |
|-------|----|-----|----|----|-----|----|-----------|
| AMS1117_33 | N | Y | N | N | Y | N | `Package_TO_SOT_SMD:SOT-223-3_TabPin2` |
| AMS1117_50 | N | Y | N | N | Y | N | `Package_TO_SOT_SMD:SOT-223-3_TabPin2` |
| ATmega2560 | N | Y | N | N | Y | N | `Package_QFP:TQFP-100_14x14mm_P0.5mm` |
| ATmega328P | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-28_W7.62mm` |
| ATmega32U4 | N | Y | N | N | Y | N | `Package_QFP:TQFP-44_10x10mm_P0.8mm` |
| ATtiny84 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-14_W7.62mm` |
| ATtiny85 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-8_W7.62mm` |
| Audio3p5mmTRRSJack | N | Y | N | N | Y | N | `Connector_Audio:Jack_3.5mm_TRRS_QingPu_WQP-PJ398SM_Vertical` |
| Audio3p5mmTRRSPlug | N | Y | N | N | Y | N | `Connector_Audio:Jack_3.5mm_TRRS_QingPu_WQP-PJ398SM_Vertical` |
| Audio3p5mmTRSJack | N | Y | N | N | Y | N | `Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` |
| Audio3p5mmTRSPlug | N | Y | N | N | Y | N | `Connector_Audio:Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` |
| BC547 | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:TO-92_Inline` |
| BC548 | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:TO-92_Inline` |
| BC557 | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:TO-92_Inline` |
| BMP280 | N | Y | N | N | Y | N | `Package_LGA:Bosch_LGA-8_2x2.5mm_P0.65mm` |
| BQ27546G1 | N | Y | N | N | Y | N | `Package_BGA:Texas_S-PVQFN-N15_2.61x1.96mm_DSBGA` |
| BS170 | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:TO-92_Inline` |
| BarrelJack5p5x2p1 | Y | N | Y | Y | Y | Y | `Connector_BarrelJack:BarrelJack_Horizontal` |
| BarrelJack5p5x2p5 | Y | N | Y | Y | Y | Y | `Connector_BarrelJack:BarrelJack_2.5mm_Horizontal` |
| BarrelPlug5p5x2p1 | Y | N | Y | Y | Y | Y | `Connector_BarrelJack:BarrelJack_Horizontal` |
| BarrelPlug5p5x2p5 | Y | N | Y | Y | Y | Y | `Connector_BarrelJack:BarrelJack_2.5mm_Horizontal` |
| Board | ?  | ?  | ?  | ?  | ?  | ?  | (could not instantiate) |
| CD4017 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-16_W7.62mm` |
| CD4043 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-16_W7.62mm` |
| CD4069 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-14_W7.62mm` |
| Capacitor | Y | Y | Y | Y | Y | Y | `Capacitor_SMD:C_0603_1608Metric` |
| Cell | Y | N | Y | Y | Y | Y | `Battery:BatteryHolder_Keystone_1042_1x18650` |
| D1N4001 | Y | N | Y | Y | Y | Y | `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal` |
| D1N4007 | Y | N | Y | Y | Y | Y | `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal` |
| D1N4148 | Y | N | Y | Y | Y | Y | `Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal` |
| D1N4728A | Y | N | Y | Y | Y | Y | `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal` |
| D1N4733A | Y | N | Y | Y | Y | Y | `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal` |
| D1N4742A | Y | N | Y | Y | Y | Y | `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal` |
| D1N5817 | Y | N | Y | Y | Y | Y | `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal` |
| DHT11 | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:DHT11` |
| DRV8313 | N | Y | N | N | Y | N | `Package_SO:HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP3.4x9.5mm` |
| DS1307 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-8_W7.62mm` |
| DS18B20 | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:TO-92_Inline` |
| Display5641AS | Y | N | Y | Y | Y | Y | `Display_7Segment:Display_5641AS` |
| ESP32_WROOM_32 | N | Y | N | N | Y | N | `RF_Module:ESP32-WROOM-32` |
| ESP8266_12F | N | Y | N | N | Y | N | `RF_Module:ESP-12E` |
| HCSR04 | Y | N | Y | Y | Y | Y | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` |
| HDMITypeAPlug | N | Y | N | N | Y | N | `Connector_Video:HDMI_A_Amphenol_10029449-001RLF_Horizontal` |
| HDMITypeAReceptacle | N | Y | N | N | Y | N | `Connector_Video:HDMI_A_Amphenol_10029449-001RLF_Horizontal` |
| Header1xNFemale | Y | N | Y | Y | Y | Y | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` |
| Header1xNMale | Y | N | Y | Y | Y | Y | `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical` |
| Header2xNFemale | Y | N | Y | Y | Y | Y | `Connector_PinHeader_2.54mm:PinHeader_2x02_P2.54mm_Vertical` |
| Header2xNMale | Y | N | Y | Y | Y | Y | `Connector_PinHeader_2.54mm:PinHeader_2x02_P2.54mm_Vertical` |
| IDC2xNMale | Y | N | Y | Y | Y | Y | `Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical` |
| IDC2xNSocket | Y | N | Y | Y | Y | Y | `Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical` |
| IRFZ44N | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:TO-220-3_Vertical` |
| IRLB8721 | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:TO-220-3_Vertical` |
| ISOW7841 | N | Y | N | N | Y | N | `Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm` |
| Inductor | Y | Y | Y | Y | Y | Y | `Inductor_SMD:L_0603_1608Metric` |
| Inverter | N | N | Y | Y | Y | Y | `—` |
| JSTGHBoardSide | N | N | N | N | N | N | `Connector_JST:JST_GH_BM4B-GHS-TBT_1x04-1MP_P1.25mm_Vertical` |
| JSTGHCableHousing | N | N | N | N | N | N | `Connector_JST:JST_GH_BM4B-GHS-TBT_1x04-1MP_P1.25mm_Vertical` |
| JSTPHBoardSide | N | N | N | N | N | N | `Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical` |
| JSTPHCableHousing | N | N | N | N | N | N | `Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical` |
| JSTSHBoardSide | N | N | N | N | N | N | `Connector_JST:JST_SH_BM4B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal` |
| JSTSHCableHousing | N | N | N | N | N | N | `Connector_JST:JST_SH_BM4B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal` |
| JSTXHBoardSide | N | N | N | N | N | N | `Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical` |
| JSTXHCableHousing | N | N | N | N | N | N | `Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical` |
| LED | Y | Y | Y | Y | Y | Y | `LED_SMD:LED_0805` |
| LM311 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-8_W7.62mm` |
| LM317 | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:TO-220-3_Vertical` |
| LM324 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-14_W7.62mm` |
| LM337 | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:TO-220-3_Vertical` |
| LM339 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-14_W7.62mm` |
| LM358 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-8_W7.62mm` |
| LM386 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-8_W7.62mm` |
| LM393 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-8_W7.62mm` |
| LM5002 | N | Y | N | N | Y | N | `Package_SO:VSSOP-8_3.0x3.0mm_P0.65mm` |
| LM5160 | N | Y | N | N | Y | N | `Package_SO:HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm` |
| LM741 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-8_W7.62mm` |
| LM7805 | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:TO-220-3_Vertical` |
| LM7812 | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:TO-220-3_Vertical` |
| LM7905 | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:TO-220-3_Vertical` |
| LMV358 | N | Y | N | N | Y | N | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` |
| LP2950 | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:TO-92_Inline` |
| MAX232 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-16_W7.62mm` |
| MAX7219 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-24_W15.24mm` |
| MCP6002 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-8_W7.62mm` |
| MOC3021 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-6_W7.62mm` |
| MPU6050 | N | Y | N | N | Y | N | `Sensor_Motion:InvenSense_QFN-24_4x4mm_P0.5mm` |
| MicroSDCard | N | N | Y | Y | Y | Y | `—` |
| MicroSDCardSlot | N | Y | N | N | Y | N | `Connector_Card:microSD_HC_Hirose_DM3D-SF` |
| NE555 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-8_W7.62mm` |
| OPA2134 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-8_W7.62mm` |
| OPTO_4N25 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-6_W7.62mm` |
| OPTO_TLP521 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-4_W7.62mm` |
| Q2N2222 | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:TO-92_Inline` |
| Q2N3904 | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:TO-92_Inline` |
| Q2N3906 | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:TO-92_Inline` |
| Q2N7000 | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:TO-92_Inline` |
| RJ45Jack | N | Y | N | N | Y | N | `Connector_RJ:RJ45_Wuerth_7499010121A_Horizontal` |
| RJ45Plug | N | Y | N | N | Y | N | `Connector_RJ:RJ45_Wuerth_7499010121A_Horizontal` |
| RP2040 | N | Y | N | N | Y | N | `Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm` |
| Rail | N | N | Y | Y | Y | Y | `—` |
| Resistor | Y | Y | Y | Y | Y | Y | `Resistor_SMD:R_0603_1608Metric` |
| SDCard | N | N | Y | Y | Y | Y | `—` |
| SDCardSlot | N | Y | N | N | Y | N | `Connector_Card:SD_TE_2041021` |
| SN74AHC1G14 | N | Y | N | N | Y | N | `Package_TO_SOT_SMD:SOT-23-5` |
| SN74HC00 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-14_W7.62mm` |
| SN74HC02 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-14_W7.62mm` |
| SN74HC04 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-14_W7.62mm` |
| SN74HC08 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-14_W7.62mm` |
| SN74HC138 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-16_W7.62mm` |
| SN74HC139 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-16_W7.62mm` |
| SN74HC151 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-16_W7.62mm` |
| SN74HC157 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-16_W7.62mm` |
| SN74HC165 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-16_W7.62mm` |
| SN74HC174 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-16_W7.62mm` |
| SN74HC273 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-20_W7.62mm` |
| SN74HC32 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-14_W7.62mm` |
| SN74HC541 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-20_W7.62mm` |
| SN74HC595 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-16_W7.62mm` |
| SN74HC74 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-14_W7.62mm` |
| SN74HC86 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-14_W7.62mm` |
| STM32F103C8T6 | N | Y | N | N | Y | N | `Package_QFP:LQFP-48_7x7mm_P0.5mm` |
| STM32F411CEU6 | N | Y | N | N | Y | N | `Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm` |
| ScrewTerminalBlock | Y | N | Y | Y | Y | Y | `TerminalBlock:TerminalBlock_Phoenix_MPT-5.08mm_1x04_P5.08mm_Horizontal` |
| TIP120 | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:TO-220-3_Vertical` |
| TL072 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-8_W7.62mm` |
| TL074 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-14_W7.62mm` |
| TLC5940 | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-28_W7.62mm` |
| TLV3401 | N | Y | N | N | Y | N | `Package_TO_SOT_SMD:SOT-23-5` |
| TMP302 | N | Y | N | N | Y | N | `Package_SO:SOT-563_1.6x1.6mm_P0.5mm` |
| TMP36 | Y | N | Y | Y | Y | Y | `Package_TO_SOT_THT:TO-92_Inline` |
| TPS2660 | N | Y | N | N | Y | N | `Package_SON:WSON-10-1EP_3x3mm_P0.5mm_EP1.6x2.4mm` |
| TRS3122E | N | Y | N | N | Y | N | `Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm` |
| ULN2003A | Y | N | Y | Y | Y | Y | `Package_DIP:DIP-16_W7.62mm` |
| USBAPlug | N | Y | N | N | Y | N | `Connector_USB:USB_A_Stewart_SS-52100-001_Horizontal` |
| USBAReceptacle | N | Y | N | N | Y | N | `Connector_USB:USB_A_Stewart_SS-52100-001_Horizontal` |
| USBBPlug | N | Y | N | N | Y | N | `Connector_USB:USB_B_Wuerth_61400826021_Horizontal` |
| USBBReceptacle | N | Y | N | N | Y | N | `Connector_USB:USB_B_Wuerth_61400826021_Horizontal` |
| USBCPlug | N | Y | N | N | Y | N | `Connector_USB:USB_C_Receptacle_GCT_USB4105-GF-A_16P_TopMnt_Horizontal` |
| USBCReceptacle | N | Y | N | N | Y | N | `Connector_USB:USB_C_Receptacle_GCT_USB4105-GF-A_16P_TopMnt_Horizontal` |
| USBMicroBPlug | N | Y | N | N | Y | N | `Connector_USB:USB_Micro-B_GCT_USB3076-30-A_Horizontal` |
| USBMicroBReceptacle | N | Y | N | N | Y | N | `Connector_USB:USB_Micro-B_GCT_USB3076-30-A_Horizontal` |
