import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest

from components.passives.resistor import Resistor
from components.parts.concepts.comparator import Comparator
from components.parts.concepts.nor_latch import NORLatch
from components.passives.led import LED
from applications.water_alarm import WaterAlarm


@pytest.fixture
def shunt():
    return Resistor(ohms=1)


@pytest.fixture
def comparator():
    return Comparator()


@pytest.fixture
def latch():
    return NORLatch()


@pytest.fixture
def red_led():
    return LED('red')


@pytest.fixture
def alarm():
    return WaterAlarm()
