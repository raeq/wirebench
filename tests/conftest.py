import glob
import sys
import os
_HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(_HERE, '..', 'src'))
# Each demo now lives in its own subdirectory under demos/ (so that
# `demos/<name>/docs/` can hold the rendered export artefacts beside
# the demo source).  Add every demo subdirectory to sys.path so the
# existing `from <demo_name> import …` import style still works
# unchanged from test code.
for _demo_dir in sorted(glob.glob(os.path.join(_HERE, '..', 'demos', '*'))):
    if os.path.isdir(_demo_dir):
        sys.path.insert(0, _demo_dir)

import pytest

# Hypothesis profile — counterexamples persist in .hypothesis/ for
# replay across runs.  Hypothesis doesn't read TOML config; it reads
# settings registered here.
from hypothesis import Verbosity, settings

settings.register_profile(
    'default',
    deadline=500,                # ms per example; flag slow strategies
    max_examples=200,            # default budget; override per-test if needed
    derandomize=False,           # randomised exploration; counterexamples
                                 # persist via .hypothesis/examples
    suppress_health_check=[],    # do not silence slow/imbalanced strategies
    verbosity=Verbosity.normal,
)
settings.load_profile('default')

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
