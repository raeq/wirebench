import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest

from components.resistor import Resistor
from components.lm393 import LM393
from components.cd4043 import CD4043
from components.led import LED
from applications.water_alarm import WaterAlarm


@pytest.fixture
def shunt():
    return Resistor(ohms=1)


@pytest.fixture
def comp_low():
    return LM393(vref=100, ref_on_plus=True)


@pytest.fixture
def comp_high():
    return LM393(vref=150, ref_on_plus=False)


@pytest.fixture
def latch():
    return CD4043()


@pytest.fixture
def red_led():
    return LED('red')


@pytest.fixture
def alarm():
    return WaterAlarm()
