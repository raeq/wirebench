"""Discrete diodes — rectifiers, Schottky, Zeners in DO-35/DO-41."""
from .d1n4148  import D1N4148
from .d1n4001  import D1N4001
from .d1n4007  import D1N4007
from .d1n5817  import D1N5817
from .d1n4728a import D1N4728A
from .d1n4733a import D1N4733A
from .d1n4742a import D1N4742A
from .oa90     import D_OA90

__all__ = [
    'D1N4148', 'D1N4001', 'D1N4007', 'D1N5817',
    'D1N4728A', 'D1N4733A', 'D1N4742A',
    'D_OA90',
]
