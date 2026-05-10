"""Day-1 connector library.

Every connector class in the library is re-exported here.  Mating-pair
declarations run at module import time (see each module's bottom).
"""
from .headers         import (Header1xNFemale, Header1xNMale,
                              Header2xNFemale, Header2xNMale)
from .idc             import IDC2xNMale, IDC2xNSocket
from .usb             import (USBAPlug, USBAReceptacle,
                              USBBPlug, USBBReceptacle,
                              USBMicroBPlug, USBMicroBReceptacle,
                              USBCPlug, USBCReceptacle)
from .network         import RJ45Jack, RJ45Plug
from .video           import HDMITypeAPlug, HDMITypeAReceptacle
from .audio           import (Audio3p5mmTRSJack, Audio3p5mmTRSPlug,
                              Audio3p5mmTRRSJack, Audio3p5mmTRRSPlug)
from .barrel          import (BarrelJack5p5x2p1, BarrelPlug5p5x2p1,
                              BarrelJack5p5x2p5, BarrelPlug5p5x2p5)
from .jst_ph          import JSTPHBoardSide, JSTPHCableHousing
from .jst_xh          import JSTXHBoardSide, JSTXHCableHousing
from .jst_sh          import JSTSHBoardSide, JSTSHCableHousing
from .jst_gh          import JSTGHBoardSide, JSTGHCableHousing
from .screw_terminal  import ScrewTerminalBlock
from .sd              import MicroSDCardSlot, MicroSDCard, SDCardSlot, SDCard

__all__ = [
    # headers
    'Header1xNFemale', 'Header1xNMale',
    'Header2xNFemale', 'Header2xNMale',
    # IDC
    'IDC2xNMale', 'IDC2xNSocket',
    # USB
    'USBAPlug', 'USBAReceptacle',
    'USBBPlug', 'USBBReceptacle',
    'USBMicroBPlug', 'USBMicroBReceptacle',
    'USBCPlug', 'USBCReceptacle',
    # network
    'RJ45Jack', 'RJ45Plug',
    # video
    'HDMITypeAPlug', 'HDMITypeAReceptacle',
    # audio
    'Audio3p5mmTRSJack', 'Audio3p5mmTRSPlug',
    'Audio3p5mmTRRSJack', 'Audio3p5mmTRRSPlug',
    # barrel
    'BarrelJack5p5x2p1', 'BarrelPlug5p5x2p1',
    'BarrelJack5p5x2p5', 'BarrelPlug5p5x2p5',
    # JST
    'JSTPHBoardSide', 'JSTPHCableHousing',
    'JSTXHBoardSide', 'JSTXHCableHousing',
    'JSTSHBoardSide', 'JSTSHCableHousing',
    'JSTGHBoardSide', 'JSTGHCableHousing',
    # screw terminal
    'ScrewTerminalBlock',
    # SD / microSD
    'MicroSDCardSlot', 'MicroSDCard', 'SDCardSlot', 'SDCard',
]
