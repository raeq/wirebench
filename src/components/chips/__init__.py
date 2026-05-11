"""Integrated circuits — what you'd find on a BOM.

Concepts (the cells used to implement these chips) are deliberately not
re-exported. Import them only from `components.chips.concepts.<name>`
when you genuinely need to peek inside a chip — and that should be rare.
"""
# Original library (decomposed chips with internal cells).
from .cd4043   import CD4043
from .cd4069   import CD4069
from .lm393    import LM393
from .sn74hc04 import SN74HC04
from .uln2003a import ULN2003A

# 74HC logic family (black-box).
from .sn74hc00  import SN74HC00
from .sn74hc02  import SN74HC02
from .sn74hc08  import SN74HC08
from .sn74hc32  import SN74HC32
from .sn74hc74  import SN74HC74
from .sn74hc86  import SN74HC86
from .sn74hc138 import SN74HC138
from .sn74hc139 import SN74HC139
from .sn74hc151 import SN74HC151
from .sn74hc157 import SN74HC157
from .sn74hc165 import SN74HC165
from .sn74hc174 import SN74HC174
from .sn74hc273 import SN74HC273
from .sn74hc541 import SN74HC541
from .sn74hc595 import SN74HC595

# Op-amps.
from .lm358   import LM358
from .lm324   import LM324
from .tl072   import TL072
from .tl074   import TL074
from .lm741   import LM741
from .mcp6002 import MCP6002
from .opa2134 import OPA2134
from .lmv358  import LMV358

# Comparators.
from .lm339   import LM339
from .tlv3401 import TLV3401
from .lm311   import LM311

# Regulators.
from .lm7805     import LM7805
from .lm7812     import LM7812
from .lm7905     import LM7905
from .lm317      import LM317
from .lm337      import LM337
from .ams1117_33 import AMS1117_33
from .ams1117_50 import AMS1117_50
from .lp2950     import LP2950

# Specialty ICs.
from .ne555   import NE555
from .lm386   import LM386
from .ds18b20 import DS18B20
from .ds1307  import DS1307
from .max7219 import MAX7219

# Sensors.
from .tmp36   import TMP36
from .bmp280  import BMP280
from .mpu6050 import MPU6050
from .hcsr04  import HCSR04

# Power / interface.
from .moc3021      import MOC3021
from .opto_4n25    import OPTO_4N25
from .opto_tlp521  import OPTO_TLP521
from .tlc5940      import TLC5940
from .max232       import MAX232

# Microcontrollers.
from .atmega328p     import ATmega328P
from .atmega2560     import ATmega2560
from .atmega32u4     import ATmega32U4
from .attiny85       import ATtiny85
from .attiny84       import ATtiny84
from .stm32f103c8t6  import STM32F103C8T6
from .stm32f411ceu6  import STM32F411CEU6
from .rp2040         import RP2040
from .esp32_wroom_32 import ESP32_WROOM_32
from .esp8266_12f    import ESP8266_12F

__all__ = [
    # Original
    'CD4043', 'CD4069', 'LM393', 'SN74HC04', 'ULN2003A',
    # 74HC
    'SN74HC00', 'SN74HC02', 'SN74HC08', 'SN74HC32', 'SN74HC74', 'SN74HC86',
    'SN74HC138', 'SN74HC139', 'SN74HC151', 'SN74HC157', 'SN74HC165',
    'SN74HC174', 'SN74HC273', 'SN74HC541', 'SN74HC595',
    # Op-amps
    'LM358', 'LM324', 'TL072', 'TL074', 'LM741', 'MCP6002', 'OPA2134', 'LMV358',
    # Comparators
    'LM339', 'TLV3401', 'LM311',
    # Regulators
    'LM7805', 'LM7812', 'LM7905', 'LM317', 'LM337',
    'AMS1117_33', 'AMS1117_50', 'LP2950',
    # Specialty
    'NE555', 'LM386', 'DS18B20', 'DS1307', 'MAX7219',
    # Sensors
    'TMP36', 'BMP280', 'MPU6050', 'HCSR04',
    # Power/interface
    'MOC3021', 'OPTO_4N25', 'OPTO_TLP521', 'TLC5940', 'MAX232',
    # MCUs
    'ATmega328P', 'ATmega2560', 'ATmega32U4', 'ATtiny85', 'ATtiny84',
    'STM32F103C8T6', 'STM32F411CEU6', 'RP2040', 'ESP32_WROOM_32', 'ESP8266_12F',
]
