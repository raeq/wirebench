"""Pydantic record types for the `.circuitry` file format.

Each registered FactorNode subclass has a corresponding record class
with a `type` Literal discriminator, refdes / id, and any class-
specific arguments.  Records are unioned through a `Discriminator("type")`.

Saving walks the in-memory model and produces records; loading
validates records and reconstructs live components via the registry.
"""
from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Discriminator, Field


# Pattern fragments shared across record families.
REFDES_U = r'^U\d+$'   # ICs
REFDES_J = r'^J\d+$'   # female / receptacle / chassis-side
REFDES_P = r'^P\d+$'   # male / plug / cable-side
REFDES_R = r'^R\d+$'   # resistors
REFDES_C = r'^C\d+$'   # capacitors
REFDES_L = r'^L\d+$'   # inductors
REFDES_D = r'^D\d+$'   # diodes (LEDs)
REFDES_Q = r'^Q\d+$'   # transistors (BJT / MOSFET)
REFDES_K = r'^K\d+$'   # relays
REFDES_A = r'^A\d+$'   # assemblies / boards
LOCAL_ID = r'^[A-Za-z][A-Za-z0-9_]*$'


# ---------------------------------------------------------------- base

class _Record(BaseModel):
    """Common record config: reject unknown fields outright."""
    model_config = ConfigDict(extra='forbid')


# --------------------------------------------------- passives & rails

class ResistorRecord(_Record):
    type:   Literal['Resistor'] = 'Resistor'
    refdes: Annotated[str,   Field(pattern=REFDES_R)]
    ohms:   Annotated[float, Field(gt=0)]


class CapacitorRecord(_Record):
    type:   Literal['Capacitor'] = 'Capacitor'
    refdes: Annotated[str,   Field(pattern=REFDES_C)]
    farads: Annotated[float, Field(gt=0)]


class InductorRecord(_Record):
    type:    Literal['Inductor'] = 'Inductor'
    refdes:  Annotated[str,   Field(pattern=REFDES_L)]
    henries: Annotated[float, Field(gt=0)]


class Relay_SPDTRecord(_Record):
    type:           Literal['Relay_SPDT'] = 'Relay_SPDT'
    refdes:         Annotated[str,   Field(pattern=REFDES_K)]
    pickup_voltage: Annotated[float, Field(gt=0)]


class LEDRecord(_Record):
    type:   Literal['LED'] = 'LED'
    refdes: Annotated[str, Field(pattern=REFDES_D)]
    color:  Annotated[str, Field(min_length=1)]


class RailRecord(_Record):
    type:  Literal['Rail'] = 'Rail'
    id:    Annotated[str, Field(pattern=LOCAL_ID)]
    level: bool


# --------------------------------------------------------------- chips

class _ChipRecord(_Record):
    """Bare chip record: just refdes (refdes prefix 'U')."""
    refdes: Annotated[str, Field(pattern=REFDES_U)]


class SN74HC04Record(_ChipRecord):
    type: Literal['SN74HC04'] = 'SN74HC04'

class CD4017Record(_ChipRecord):
    type: Literal['CD4017'] = 'CD4017'

class CD4069Record(_ChipRecord):
    type: Literal['CD4069'] = 'CD4069'

class LM393Record(_ChipRecord):
    type: Literal['LM393'] = 'LM393'

class CD4043Record(_ChipRecord):
    type: Literal['CD4043'] = 'CD4043'

class ULN2003ARecord(_ChipRecord):
    type: Literal['ULN2003A'] = 'ULN2003A'


# 74HC logic family.
class SN74HC00Record(_ChipRecord):  type: Literal['SN74HC00']  = 'SN74HC00'
class SN74HC02Record(_ChipRecord):  type: Literal['SN74HC02']  = 'SN74HC02'
class SN74HC08Record(_ChipRecord):  type: Literal['SN74HC08']  = 'SN74HC08'
class SN74HC32Record(_ChipRecord):  type: Literal['SN74HC32']  = 'SN74HC32'
class SN74HC74Record(_ChipRecord):  type: Literal['SN74HC74']  = 'SN74HC74'
class SN74HC86Record(_ChipRecord):  type: Literal['SN74HC86']  = 'SN74HC86'
class SN74HC138Record(_ChipRecord): type: Literal['SN74HC138'] = 'SN74HC138'
class SN74HC139Record(_ChipRecord): type: Literal['SN74HC139'] = 'SN74HC139'
class SN74HC151Record(_ChipRecord): type: Literal['SN74HC151'] = 'SN74HC151'
class SN74HC157Record(_ChipRecord): type: Literal['SN74HC157'] = 'SN74HC157'
class SN74HC165Record(_ChipRecord): type: Literal['SN74HC165'] = 'SN74HC165'
class SN74HC174Record(_ChipRecord): type: Literal['SN74HC174'] = 'SN74HC174'
class SN74HC273Record(_ChipRecord): type: Literal['SN74HC273'] = 'SN74HC273'
class SN74HC541Record(_ChipRecord): type: Literal['SN74HC541'] = 'SN74HC541'
class SN74HC595Record(_ChipRecord): type: Literal['SN74HC595'] = 'SN74HC595'

# Op-amps.
class LM358Record(_ChipRecord):    type: Literal['LM358']    = 'LM358'
class LM324Record(_ChipRecord):    type: Literal['LM324']    = 'LM324'
class TL072Record(_ChipRecord):    type: Literal['TL072']    = 'TL072'
class TL074Record(_ChipRecord):    type: Literal['TL074']    = 'TL074'
class LM741Record(_ChipRecord):    type: Literal['LM741']    = 'LM741'
class MCP6002Record(_ChipRecord):  type: Literal['MCP6002']  = 'MCP6002'
class OPA2134Record(_ChipRecord):  type: Literal['OPA2134']  = 'OPA2134'
class LMV358Record(_ChipRecord):   type: Literal['LMV358']   = 'LMV358'

# Comparators.
class LM339Record(_ChipRecord):    type: Literal['LM339']    = 'LM339'
class TLV3401Record(_ChipRecord):  type: Literal['TLV3401']  = 'TLV3401'
class LM311Record(_ChipRecord):    type: Literal['LM311']    = 'LM311'

# Regulators.
class LM7805Record(_ChipRecord):     type: Literal['LM7805']     = 'LM7805'
class LM7812Record(_ChipRecord):     type: Literal['LM7812']     = 'LM7812'
class LM7905Record(_ChipRecord):     type: Literal['LM7905']     = 'LM7905'
class LM317Record(_ChipRecord):      type: Literal['LM317']      = 'LM317'
class LM337Record(_ChipRecord):      type: Literal['LM337']      = 'LM337'
class AMS1117_33Record(_ChipRecord): type: Literal['AMS1117_33'] = 'AMS1117_33'
class AMS1117_50Record(_ChipRecord): type: Literal['AMS1117_50'] = 'AMS1117_50'
class LP2950Record(_ChipRecord):     type: Literal['LP2950']     = 'LP2950'
class LM5002Record(_ChipRecord):     type: Literal['LM5002']     = 'LM5002'
class LM5160Record(_ChipRecord):     type: Literal['LM5160']     = 'LM5160'
class TPS2660Record(_ChipRecord):    type: Literal['TPS2660']    = 'TPS2660'
class TMP302Record(_ChipRecord):     type: Literal['TMP302']     = 'TMP302'
class SN74AHC1G14Record(_ChipRecord): type: Literal['SN74AHC1G14'] = 'SN74AHC1G14'
class DRV8313Record(_ChipRecord):    type: Literal['DRV8313']    = 'DRV8313'

# Specialty ICs.
class NE555Record(_ChipRecord):         type: Literal['NE555']         = 'NE555'
class LM386Record(_ChipRecord):         type: Literal['LM386']         = 'LM386'
class DS18B20Record(_ChipRecord):       type: Literal['DS18B20']       = 'DS18B20'
class DS1307Record(_ChipRecord):        type: Literal['DS1307']        = 'DS1307'
class MAX7219Record(_ChipRecord):       type: Literal['MAX7219']       = 'MAX7219'
class Display5641ASRecord(_ChipRecord): type: Literal['Display5641AS'] = 'Display5641AS'

# Sensors.
class TMP36Record(_ChipRecord):    type: Literal['TMP36']   = 'TMP36'
class BMP280Record(_ChipRecord):   type: Literal['BMP280']  = 'BMP280'
class MPU6050Record(_ChipRecord):  type: Literal['MPU6050'] = 'MPU6050'
class HCSR04Record(_ChipRecord):   type: Literal['HCSR04']  = 'HCSR04'
class DHT11Record(_ChipRecord):    type: Literal['DHT11']   = 'DHT11'

# Power / interface.
class MOC3021Record(_ChipRecord):     type: Literal['MOC3021']     = 'MOC3021'
class OPTO_4N25Record(_ChipRecord):   type: Literal['OPTO_4N25']   = 'OPTO_4N25'
class OPTO_TLP521Record(_ChipRecord): type: Literal['OPTO_TLP521'] = 'OPTO_TLP521'
class TLC5940Record(_ChipRecord):     type: Literal['TLC5940']     = 'TLC5940'
class MAX232Record(_ChipRecord):      type: Literal['MAX232']      = 'MAX232'

# Microcontrollers.
class ATmega328PRecord(_ChipRecord):    type: Literal['ATmega328P']     = 'ATmega328P'
class ATmega2560Record(_ChipRecord):    type: Literal['ATmega2560']     = 'ATmega2560'
class ATmega32U4Record(_ChipRecord):    type: Literal['ATmega32U4']     = 'ATmega32U4'
class ATtiny85Record(_ChipRecord):      type: Literal['ATtiny85']       = 'ATtiny85'
class ATtiny84Record(_ChipRecord):      type: Literal['ATtiny84']       = 'ATtiny84'
class STM32F103C8T6Record(_ChipRecord): type: Literal['STM32F103C8T6']  = 'STM32F103C8T6'
class STM32F411CEU6Record(_ChipRecord): type: Literal['STM32F411CEU6']  = 'STM32F411CEU6'
class RP2040Record(_ChipRecord):        type: Literal['RP2040']         = 'RP2040'
class ESP32_WROOM_32Record(_ChipRecord): type: Literal['ESP32_WROOM_32'] = 'ESP32_WROOM_32'
class ESP8266_12FRecord(_ChipRecord):    type: Literal['ESP8266_12F']    = 'ESP8266_12F'


# -------------------------------------------------------- transistors

class _TransistorRecord(_Record):
    """Discrete BJT or MOSFET: refdes-only (refdes prefix 'Q')."""
    refdes: Annotated[str, Field(pattern=REFDES_Q)]


class BC547Record(_TransistorRecord):    type: Literal['BC547']    = 'BC547'
class BC548Record(_TransistorRecord):    type: Literal['BC548']    = 'BC548'
class BC557Record(_TransistorRecord):    type: Literal['BC557']    = 'BC557'
class Q2N3904Record(_TransistorRecord):  type: Literal['Q2N3904']  = 'Q2N3904'
class Q2N3906Record(_TransistorRecord):  type: Literal['Q2N3906']  = 'Q2N3906'
class Q2N2222Record(_TransistorRecord):  type: Literal['Q2N2222']  = 'Q2N2222'
class TIP120Record(_TransistorRecord):   type: Literal['TIP120']   = 'TIP120'
class Q2N7000Record(_TransistorRecord):  type: Literal['Q2N7000']  = 'Q2N7000'
class BS170Record(_TransistorRecord):    type: Literal['BS170']    = 'BS170'
class IRLB8721Record(_TransistorRecord): type: Literal['IRLB8721'] = 'IRLB8721'
class IRFZ44NRecord(_TransistorRecord):  type: Literal['IRFZ44N']  = 'IRFZ44N'


# -------------------------------------------------------------- diodes

class _DiodeRecord(_Record):
    """Discrete rectifier / Zener / Schottky: refdes-only (prefix 'D')."""
    refdes: Annotated[str, Field(pattern=REFDES_D)]


class D1N4148Record(_DiodeRecord):  type: Literal['D1N4148']  = 'D1N4148'
class D1N4001Record(_DiodeRecord):  type: Literal['D1N4001']  = 'D1N4001'
class D1N4007Record(_DiodeRecord):  type: Literal['D1N4007']  = 'D1N4007'
class D1N5817Record(_DiodeRecord):  type: Literal['D1N5817']  = 'D1N5817'
class D1N4728ARecord(_DiodeRecord): type: Literal['D1N4728A'] = 'D1N4728A'
class D1N4733ARecord(_DiodeRecord): type: Literal['D1N4733A'] = 'D1N4733A'
class D1N4742ARecord(_DiodeRecord): type: Literal['D1N4742A'] = 'D1N4742A'


# --------------------------- connectors: parameterised (pin_count + pitch)

class _ParamConnectorRecord(_Record):
    """Snap-apart header / IDC / screw terminal — pin_count and
    pitch_mm both supplied at construction."""
    pin_count: Annotated[int,   Field(gt=0)]
    pitch_mm:  Annotated[float, Field(gt=0)]


class Header1xNMaleRecord(_ParamConnectorRecord):
    type:   Literal['Header1xNMale'] = 'Header1xNMale'
    refdes: Annotated[str, Field(pattern=REFDES_P)]

class Header1xNFemaleRecord(_ParamConnectorRecord):
    type:   Literal['Header1xNFemale'] = 'Header1xNFemale'
    refdes: Annotated[str, Field(pattern=REFDES_J)]

class Header2xNMaleRecord(_ParamConnectorRecord):
    type:   Literal['Header2xNMale'] = 'Header2xNMale'
    refdes: Annotated[str, Field(pattern=REFDES_P)]

class Header2xNFemaleRecord(_ParamConnectorRecord):
    type:   Literal['Header2xNFemale'] = 'Header2xNFemale'
    refdes: Annotated[str, Field(pattern=REFDES_J)]

class IDC2xNMaleRecord(_ParamConnectorRecord):
    type:   Literal['IDC2xNMale'] = 'IDC2xNMale'
    refdes: Annotated[str, Field(pattern=REFDES_P)]

class IDC2xNSocketRecord(_ParamConnectorRecord):
    type:   Literal['IDC2xNSocket'] = 'IDC2xNSocket'
    refdes: Annotated[str, Field(pattern=REFDES_J)]

class ScrewTerminalBlockRecord(_ParamConnectorRecord):
    type:   Literal['ScrewTerminalBlock'] = 'ScrewTerminalBlock'
    refdes: Annotated[str, Field(pattern=REFDES_J)]


# ------------------------------ JST families: pin_count, class-attr pitch

class _JSTRecord(_Record):
    """JST families have a class-attribute pitch; only pin_count is at
    construction."""
    pin_count: Annotated[int, Field(gt=0)]

class JSTPHBoardSideRecord(_JSTRecord):
    type:   Literal['JSTPHBoardSide'] = 'JSTPHBoardSide'
    refdes: Annotated[str, Field(pattern=REFDES_P)]

class JSTPHCableHousingRecord(_JSTRecord):
    type:   Literal['JSTPHCableHousing'] = 'JSTPHCableHousing'
    refdes: Annotated[str, Field(pattern=REFDES_J)]

class JSTXHBoardSideRecord(_JSTRecord):
    type:   Literal['JSTXHBoardSide'] = 'JSTXHBoardSide'
    refdes: Annotated[str, Field(pattern=REFDES_P)]

class JSTXHCableHousingRecord(_JSTRecord):
    type:   Literal['JSTXHCableHousing'] = 'JSTXHCableHousing'
    refdes: Annotated[str, Field(pattern=REFDES_J)]

class JSTSHBoardSideRecord(_JSTRecord):
    type:   Literal['JSTSHBoardSide'] = 'JSTSHBoardSide'
    refdes: Annotated[str, Field(pattern=REFDES_P)]

class JSTSHCableHousingRecord(_JSTRecord):
    type:   Literal['JSTSHCableHousing'] = 'JSTSHCableHousing'
    refdes: Annotated[str, Field(pattern=REFDES_J)]

class JSTGHBoardSideRecord(_JSTRecord):
    type:   Literal['JSTGHBoardSide'] = 'JSTGHBoardSide'
    refdes: Annotated[str, Field(pattern=REFDES_P)]

class JSTGHCableHousingRecord(_JSTRecord):
    type:   Literal['JSTGHCableHousing'] = 'JSTGHCableHousing'
    refdes: Annotated[str, Field(pattern=REFDES_J)]


# ----------------------- connectors: fixed geometry (refdes only)

class _FixedFemaleConnectorRecord(_Record):
    refdes: Annotated[str, Field(pattern=REFDES_J)]

class _FixedMaleConnectorRecord(_Record):
    refdes: Annotated[str, Field(pattern=REFDES_P)]


class USBAReceptacleRecord(_FixedFemaleConnectorRecord):
    type: Literal['USBAReceptacle'] = 'USBAReceptacle'
class USBAPlugRecord(_FixedMaleConnectorRecord):
    type: Literal['USBAPlug'] = 'USBAPlug'

class USBBReceptacleRecord(_FixedFemaleConnectorRecord):
    type: Literal['USBBReceptacle'] = 'USBBReceptacle'
class USBBPlugRecord(_FixedMaleConnectorRecord):
    type: Literal['USBBPlug'] = 'USBBPlug'

class USBMicroBReceptacleRecord(_FixedFemaleConnectorRecord):
    type: Literal['USBMicroBReceptacle'] = 'USBMicroBReceptacle'
class USBMicroBPlugRecord(_FixedMaleConnectorRecord):
    type: Literal['USBMicroBPlug'] = 'USBMicroBPlug'

class USBCReceptacleRecord(_FixedFemaleConnectorRecord):
    type: Literal['USBCReceptacle'] = 'USBCReceptacle'
class USBCPlugRecord(_FixedMaleConnectorRecord):
    type: Literal['USBCPlug'] = 'USBCPlug'

class RJ45JackRecord(_FixedFemaleConnectorRecord):
    type: Literal['RJ45Jack'] = 'RJ45Jack'
class RJ45PlugRecord(_FixedMaleConnectorRecord):
    type: Literal['RJ45Plug'] = 'RJ45Plug'

class HDMITypeAReceptacleRecord(_FixedFemaleConnectorRecord):
    type: Literal['HDMITypeAReceptacle'] = 'HDMITypeAReceptacle'
class HDMITypeAPlugRecord(_FixedMaleConnectorRecord):
    type: Literal['HDMITypeAPlug'] = 'HDMITypeAPlug'

class Audio3p5mmTRSJackRecord(_FixedFemaleConnectorRecord):
    type: Literal['Audio3p5mmTRSJack'] = 'Audio3p5mmTRSJack'
class Audio3p5mmTRSPlugRecord(_FixedMaleConnectorRecord):
    type: Literal['Audio3p5mmTRSPlug'] = 'Audio3p5mmTRSPlug'

class Audio3p5mmTRRSJackRecord(_FixedFemaleConnectorRecord):
    type: Literal['Audio3p5mmTRRSJack'] = 'Audio3p5mmTRRSJack'
class Audio3p5mmTRRSPlugRecord(_FixedMaleConnectorRecord):
    type: Literal['Audio3p5mmTRRSPlug'] = 'Audio3p5mmTRRSPlug'

class BarrelJack5p5x2p1Record(_FixedFemaleConnectorRecord):
    type: Literal['BarrelJack5p5x2p1'] = 'BarrelJack5p5x2p1'
class BarrelPlug5p5x2p1Record(_FixedMaleConnectorRecord):
    type: Literal['BarrelPlug5p5x2p1'] = 'BarrelPlug5p5x2p1'

class BarrelJack5p5x2p5Record(_FixedFemaleConnectorRecord):
    type: Literal['BarrelJack5p5x2p5'] = 'BarrelJack5p5x2p5'
class BarrelPlug5p5x2p5Record(_FixedMaleConnectorRecord):
    type: Literal['BarrelPlug5p5x2p5'] = 'BarrelPlug5p5x2p5'

class MicroSDCardSlotRecord(_FixedFemaleConnectorRecord):
    type: Literal['MicroSDCardSlot'] = 'MicroSDCardSlot'
class MicroSDCardRecord(_FixedMaleConnectorRecord):
    type: Literal['MicroSDCard'] = 'MicroSDCard'

class SDCardSlotRecord(_FixedFemaleConnectorRecord):
    type: Literal['SDCardSlot'] = 'SDCardSlot'
class SDCardRecord(_FixedMaleConnectorRecord):
    type: Literal['SDCard'] = 'SDCard'


# --------------------------------------------------------- component union

ComponentRecord = Annotated[
    Union[
        ResistorRecord, CapacitorRecord, InductorRecord, Relay_SPDTRecord,
        LEDRecord, RailRecord,
        SN74HC04Record, CD4017Record, CD4069Record, LM393Record, CD4043Record,
        ULN2003ARecord,
        # 74HC logic
        SN74HC00Record, SN74HC02Record, SN74HC08Record, SN74HC32Record,
        SN74HC74Record, SN74HC86Record, SN74HC138Record, SN74HC139Record,
        SN74HC151Record, SN74HC157Record, SN74HC165Record, SN74HC174Record,
        SN74HC273Record, SN74HC541Record, SN74HC595Record,
        # Op-amps
        LM358Record, LM324Record, TL072Record, TL074Record, LM741Record,
        MCP6002Record, OPA2134Record, LMV358Record,
        # Comparators
        LM339Record, TLV3401Record, LM311Record,
        # Regulators
        LM7805Record, LM7812Record, LM7905Record, LM317Record, LM337Record,
        AMS1117_33Record, AMS1117_50Record, LP2950Record,
        LM5002Record, LM5160Record, TPS2660Record,
        TMP302Record, SN74AHC1G14Record, DRV8313Record,
        # Specialty ICs
        NE555Record, LM386Record, DS18B20Record, DS1307Record, MAX7219Record,
        Display5641ASRecord,
        # Sensors
        TMP36Record, BMP280Record, MPU6050Record, HCSR04Record, DHT11Record,
        # Power / interface
        MOC3021Record, OPTO_4N25Record, OPTO_TLP521Record, TLC5940Record,
        MAX232Record,
        # MCUs
        ATmega328PRecord, ATmega2560Record, ATmega32U4Record,
        ATtiny85Record, ATtiny84Record,
        STM32F103C8T6Record, STM32F411CEU6Record, RP2040Record,
        ESP32_WROOM_32Record, ESP8266_12FRecord,
        # Transistors
        BC547Record, BC548Record, BC557Record, Q2N3904Record, Q2N3906Record,
        Q2N2222Record, TIP120Record,
        Q2N7000Record, BS170Record, IRLB8721Record, IRFZ44NRecord,
        # Diodes
        D1N4148Record, D1N4001Record, D1N4007Record, D1N5817Record,
        D1N4728ARecord, D1N4733ARecord, D1N4742ARecord,
        Header1xNMaleRecord, Header1xNFemaleRecord,
        Header2xNMaleRecord, Header2xNFemaleRecord,
        IDC2xNMaleRecord, IDC2xNSocketRecord,
        ScrewTerminalBlockRecord,
        JSTPHBoardSideRecord, JSTPHCableHousingRecord,
        JSTXHBoardSideRecord, JSTXHCableHousingRecord,
        JSTSHBoardSideRecord, JSTSHCableHousingRecord,
        JSTGHBoardSideRecord, JSTGHCableHousingRecord,
        USBAReceptacleRecord,    USBAPlugRecord,
        USBBReceptacleRecord,    USBBPlugRecord,
        USBMicroBReceptacleRecord, USBMicroBPlugRecord,
        USBCReceptacleRecord,    USBCPlugRecord,
        RJ45JackRecord,          RJ45PlugRecord,
        HDMITypeAReceptacleRecord, HDMITypeAPlugRecord,
        Audio3p5mmTRSJackRecord,   Audio3p5mmTRSPlugRecord,
        Audio3p5mmTRRSJackRecord,  Audio3p5mmTRRSPlugRecord,
        BarrelJack5p5x2p1Record,   BarrelPlug5p5x2p1Record,
        BarrelJack5p5x2p5Record,   BarrelPlug5p5x2p5Record,
        MicroSDCardSlotRecord,     MicroSDCardRecord,
        SDCardSlotRecord,          SDCardRecord,
    ],
    Discriminator('type'),
]


# ---------------------------------------------------------- wires & mates

class WireRecord(_Record):
    ports: Annotated[
        list[Annotated[str, Field(min_length=1)]],
        Field(min_length=2),
    ]


class MateRecord(_Record):
    a: Annotated[str, Field(min_length=1)]
    b: Annotated[str, Field(min_length=1)]


# ---------------------------------------------------------- compositions

class CircuitRecord(_Record):
    type:          Literal['Circuit'] = 'Circuit'
    components:    list[ComponentRecord]
    wires:         list[WireRecord]
    surface_ports: dict[str, str] = Field(default_factory=dict)


class BoardRecord(_Record):
    type:       Literal['Board'] = 'Board'
    refdes:     Annotated[str, Field(pattern=REFDES_A)]
    name:       Annotated[str, Field(min_length=1)]
    revision:   Annotated[str, Field(min_length=1)]
    components: list[ComponentRecord]
    wires:      list[WireRecord]


class AssemblyRecord(_Record):
    type:          Literal['Assembly'] = 'Assembly'
    boards:        list[BoardRecord]
    mates:         list[MateRecord]
    surface_ports: dict[str, str] = Field(default_factory=dict)


# -------------------------------------------------------------- envelope

RootRecord = Annotated[
    Union[AssemblyRecord, BoardRecord, CircuitRecord],
    Discriminator('type'),
]


class CircuitryFile(_Record):
    format_version: Annotated[str, Field(pattern=r'^\d+\.\d+\.\d+$')]
    name:           str | None = None
    root:           RootRecord
