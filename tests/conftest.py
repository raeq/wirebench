import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest

from components.resistor import Resistor
from components.comparator import Comparator
from components.nor_latch import NORLatch
from components.led import LED
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
