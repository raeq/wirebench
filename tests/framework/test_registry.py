"""Component registry tests — per format spec §12 (#6-8)."""
import pytest

# Ensure components are imported so they register themselves.
import components.chips     # noqa: F401
import components.passives  # noqa: F401
import components.connectors  # noqa: F401
import framework.board  # noqa: F401

from framework.errors import DuplicateRegistrationError, UnknownPartError
from framework.factor import FactorNode
from framework.registry import lookup, register, registered_names

from components.passives.resistor import Resistor


def test_registered_components_looked_up():
    assert lookup("Resistor") is Resistor


def test_unknown_name_raises_keyerror():
    with pytest.raises(UnknownPartError, match="Unknown component type"):
        lookup("NonexistentChip")


def test_duplicate_registration_raises():
    class _Dummy(FactorNode):
        @property
        def ports(self):
            return {}
        def evaluate(self):
            pass

    register("DuplicateRegistrationTestDummy")(_Dummy)
    with pytest.raises(DuplicateRegistrationError, match="already registered"):
        # Different class with same name.
        class _AnotherDummy(FactorNode):
            @property
            def ports(self):
                return {}
            def evaluate(self):
                pass
        register("DuplicateRegistrationTestDummy")(_AnotherDummy)


def test_registry_idempotent_same_class():
    # Re-registering the *same* class with the *same* name is a no-op.
    register("Resistor")(Resistor)


def test_registered_names_covers_codebase():
    names = registered_names()
    expected = {
        'Resistor', 'LED', 'Rail', 'Board',
        'SN74HC04', 'CD4069', 'LM393', 'CD4043', 'ULN2003A',
        'Header2xNMale', 'Header2xNFemale', 'USBCReceptacle',
    }
    assert expected.issubset(set(names))
