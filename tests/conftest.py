import sys
import os
_HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(_HERE, '..', 'src'))
sys.path.insert(0, os.path.join(_HERE, '..', 'demos'))

import pytest

from components.passives.resistor import Resistor
from components.chips.concepts.comparator import Comparator
from components.chips.concepts.nor_latch import NORLatch
from components.passives.led import LED
from water_alarm import WaterAlarm


@pytest.fixture
def shunt():
    return Resistor(ohms=1, refdes_number=1)


@pytest.fixture
def comparator():
    return Comparator()


@pytest.fixture
def latch():
    return NORLatch()


@pytest.fixture
def red_led():
    return LED('red', refdes_number=1)


@pytest.fixture
def alarm():
    return WaterAlarm()
