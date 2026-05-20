"""End-to-end tests for `wirebench validate`.

Each test invokes the CLI as a subprocess (so the JSON-on-stdout
contract is exercised exactly as a downstream consumer would see it)
and asserts on the parsed payload + exit code.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES  = Path(__file__).resolve().parent / 'fixtures'


def _invoke(*args: str) -> tuple[int, dict[str, object]]:
    """Run `wirebench validate ...` as a subprocess; return exit code
    and parsed stdout JSON."""
    cmd = [sys.executable, '-m', 'cli.main', 'validate', *args]
    result = subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert result.stdout.endswith('\n'), (
        f"stdout must end with a newline; got {result.stdout!r}"
    )
    payload = json.loads(result.stdout)
    return result.returncode, payload


# ---------------------------------------------------------- success cases


def test_constructed_demo() -> None:
    """A real demo validates cleanly."""
    code, out = _invoke('demos/hello_led/hello_led.py')
    assert code == 0
    assert out['status'] == 'constructed'
    assert out['design'] == 'HelloLED'
    assert isinstance(out['parts'], int)
    assert out['parts'] > 0
    assert out['warnings'] == []


def test_explicit_class_selects_target() -> None:
    """--class picks a specific Circuit subclass from a file with many."""
    code, out = _invoke(
        str(FIXTURES / 'multiple_circuits.py'), '--class', 'DesignA',
    )
    assert code == 0
    assert out['status'] == 'constructed'
    assert out['design'] == 'DesignA'


# ---------------------------------------------------------- failure cases
#
# One test per error class to verify the regex extractors do their job.


def test_short_circuit_wire_extracts_pins() -> None:
    code, out = _invoke(str(FIXTURES / 'short_circuit_wire.py'))
    assert code == 1
    assert out['status'] == 'failed'
    assert out['error_class'] == 'ShortCircuitError'
    details = out['details']
    assert details['pins'] == ['y_1', 'y_2']
    # Untouched fields stay defaulted.
    assert details['refdes'] is None
    assert details['parts'] == []
    # High-confidence remediation (two named drivers) → present.
    assert 'remediation' in details
    assert 'y_1' in details['remediation']
    assert 'y_2' in details['remediation']


def test_short_circuit_three_way_omits_remediation() -> None:
    """When the canonical two-driver shape doesn't apply, the
    `remediation` key is omitted entirely so the JSON shape stays
    minimal for the low-confidence case."""
    # Reuse the existing two-driver fixture's path machinery by
    # constructing inline; the unit test on the framework side
    # confirms three+ drivers return None.  Here we only confirm that
    # an exception whose remediation is None doesn't get a JSON entry.
    from cli.validate import _details_with_remediation
    from framework.errors import ShortCircuitError
    e = ShortCircuitError("three-way short", drivers=('a', 'b', 'c'))
    details = _details_with_remediation(e)
    assert 'remediation' not in details


def test_floating_net_extracts_parts_and_pins() -> None:
    code, out = _invoke(str(FIXTURES / 'floating_net.py'))
    assert code == 1
    assert out['status'] == 'failed'
    assert out['error_class'] == 'FloatingNetError'
    details = out['details']
    assert details['parts'] == ['Resistor', 'Resistor']
    assert details['pins']  == ['t1', 't1']


def test_incompatible_mate_extracts_both_parts() -> None:
    code, out = _invoke(str(FIXTURES / 'incompatible_mate.py'))
    assert code == 1
    assert out['status'] == 'failed'
    assert out['error_class'] == 'IncompatibleMateError'
    assert out['details']['parts'] == ['Header2xNMale', 'JSTPHCableHousing']


def test_part_configuration_extracts_pin_and_number() -> None:
    code, out = _invoke(
        str(FIXTURES / 'part_configuration.py'), '--class', 'BrokenDesign',
    )
    assert code == 1
    assert out['status'] == 'failed'
    assert out['error_class'] == 'PartConfigurationError'
    details = out['details']
    assert details['parts'] == ['PartiallyDriven']
    assert details['pin']        == 'y_2'
    assert details['pin_number'] == 3


def test_domain_crossing_extracts_pins_and_domain() -> None:
    code, out = _invoke(str(FIXTURES / 'domain_crossing.py'))
    assert code == 1
    assert out['status'] == 'failed'
    assert out['error_class'] == 'DomainCrossingError'
    details = out['details']
    assert details['pins']   == ['a', 'b']
    assert details['domain'] == 'ISOLATED_A'


def test_breadboard_incompatible_extracts_multi_bullet() -> None:
    code, out = _invoke(str(FIXTURES / 'breadboard_incompatible.py'))
    assert code == 1
    assert out['status'] == 'failed'
    assert out['error_class'] == 'BreadboardIncompatibleError'
    details = out['details']
    assert details['parts'] == ['U1']
    assert details['pins']  == ['VCC']


# ---------------------------------------------------------- error cases


def test_nonexistent_file_returns_error() -> None:
    code, out = _invoke('/nonexistent/path/that/does/not/exist.py')
    assert code == 2
    assert out['status'] == 'error'
    assert out['design'] is None
    assert out['error_class'] == 'FileNotFoundError'


def test_syntax_error_in_file_returns_error() -> None:
    code, out = _invoke(str(FIXTURES / 'syntax_error.py'))
    assert code == 2
    assert out['status'] == 'error'
    assert out['error_class'] == 'SyntaxError'


def test_no_circuit_subclass_returns_error() -> None:
    code, out = _invoke(str(FIXTURES / 'no_circuit.py'))
    assert code == 2
    assert out['status'] == 'error'
    assert 'No Circuit subclass' in out['message']  # type: ignore[operator]


def test_multiple_circuits_without_class_returns_error() -> None:
    code, out = _invoke(str(FIXTURES / 'multiple_circuits.py'))
    assert code == 2
    assert out['status'] == 'error'
    message = out['message']
    assert isinstance(message, str)
    assert 'Multiple Circuit subclasses' in message
    assert 'DesignA' in message
    assert 'DesignB' in message


def test_unknown_class_name_returns_error() -> None:
    code, out = _invoke(
        str(FIXTURES / 'multiple_circuits.py'), '--class', 'DesignZZZ',
    )
    assert code == 2
    assert out['status'] == 'error'
    message = out['message']
    assert isinstance(message, str)
    assert 'DesignZZZ' in message


def test_missing_positional_returns_json() -> None:
    """argparse usage errors emit a JSON payload, not the default
    stderr-only message — preserves the one-JSON-object-per-invocation
    contract for downstream consumers."""
    code, out = _invoke()
    assert code == 2
    assert out['status'] == 'error'
    assert out['error_class'] == 'UsageError'


def test_sibling_module_import_resolves() -> None:
    """A design that imports a sibling helper module from its own
    directory should resolve, matching how `python design.py` would
    behave when run from that directory."""
    code, out = _invoke(str(FIXTURES / 'sibling_import_design.py'))
    assert code == 0, f"expected success, got {out}"
    assert out['status'] == 'constructed'


# ---------------------------------------------------------- schema shape


_DETAIL_KEYS = {
    'refdes', 'pin', 'pins', 'parts', 'nets', 'domain', 'pin_number',
}


@pytest.mark.parametrize(
    'args',
    [
        (str(FIXTURES / 'short_circuit_wire.py'),),
        ('/nonexistent.py',),
    ],
)
def test_details_keys_always_present_on_failure_and_error(
    args: tuple[str, ...],
) -> None:
    """The `details` block has a fixed schema for failed/error statuses
    so consumers can read every key without per-error-class branching.

    `remediation` is the one exception: it's an *additive* key included
    only when the framework has a high-confidence fix to suggest, so
    the consumer must be tolerant of its presence or absence.
    """
    _, out = _invoke(*args)
    details = out['details']
    assert isinstance(details, dict)
    assert _DETAIL_KEYS.issubset(details.keys())
    assert set(details.keys()) - _DETAIL_KEYS <= {'remediation'}
    # List-typed fields are always lists, never None.
    assert isinstance(details['pins'],  list)
    assert isinstance(details['parts'], list)
    assert isinstance(details['nets'],  list)


def test_success_payload_shape() -> None:
    """Success payloads omit `details` and carry `parts` + `warnings`."""
    _, out = _invoke('demos/hello_led/hello_led.py')
    assert 'parts' in out
    assert out['warnings'] == []
    # `details` is reserved for failure / error payloads.
    assert 'details' not in out
