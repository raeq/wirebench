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
REFDES_D = r'^D\d+$'   # diodes (LEDs)
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

class CD4069Record(_ChipRecord):
    type: Literal['CD4069'] = 'CD4069'

class LM393Record(_ChipRecord):
    type: Literal['LM393'] = 'LM393'

class CD4043Record(_ChipRecord):
    type: Literal['CD4043'] = 'CD4043'

class ULN2003ARecord(_ChipRecord):
    type: Literal['ULN2003A'] = 'ULN2003A'


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
        ResistorRecord, LEDRecord, RailRecord,
        SN74HC04Record, CD4069Record, LM393Record, CD4043Record, ULN2003ARecord,
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
