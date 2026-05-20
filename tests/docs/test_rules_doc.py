"""Consistency tests for `docs/the-rules.md`.

Keep the cumulative-rules narrative in sync with the exception
hierarchy: every user-facing rule exception is referenced in the doc,
every exception name mentioned in the doc resolves to a real class,
and every cross-link target (demo READMEs, `framework/errors.py`)
exists on disk.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from framework import errors as E


REPO_ROOT = Path(__file__).resolve().parents[2]
RULES_DOC = REPO_ROOT / 'docs' / 'the-rules.md'
LEARNING_PATH_DOC = REPO_ROOT / 'docs' / 'learning-path.md'
MKDOCS_YML = REPO_ROOT / 'mkdocs.yml'


# User-facing rule exceptions — those that represent a topology /
# physical-fidelity rule the framework enforces and that this doc is
# meant to teach.  FormatError / UsageError variants that aren't part
# of the rule narrative (SaveError, LoadError, AmbiguousPinNameError,
# OrphanWireError, etc.) are intentionally omitted; they're real
# framework errors but not *rules* in the user-facing sense.
RULE_EXCEPTIONS = (
    'ShortCircuitError',
    'FloatingNetError',
    'UnconnectedPinError',
    'NodeMergeError',
    'EmptyWireError',
    'SignalTypeMismatchError',
    'DomainCrossingError',
    'ForbiddenStateError',
    'RefdesError',
    'IncompatibleMateError',
    'PinCountMismatchError',
    'PitchMismatchError',
    'WiredChipCallError',
)


@pytest.fixture(scope='module')
def rules_doc_text() -> str:
    return RULES_DOC.read_text()


def test_the_rules_doc_exists() -> None:
    assert RULES_DOC.is_file(), f"{RULES_DOC} is missing"


@pytest.mark.parametrize('exception_name', RULE_EXCEPTIONS)
def test_every_rule_exception_is_named_in_the_doc(
    exception_name: str,
    rules_doc_text: str,
) -> None:
    """A new rule exception added to the framework must also be
    documented as a rule on the page — keeps the doc in sync as the
    exception hierarchy evolves."""
    assert exception_name in rules_doc_text, (
        f"{exception_name} is in the RULE_EXCEPTIONS curated list "
        f"but not mentioned in docs/the-rules.md.  Either add a rule "
        f"entry, or remove the class from the list if it's no longer "
        f"user-facing."
    )


@pytest.mark.parametrize('exception_name', RULE_EXCEPTIONS)
def test_every_rule_exception_class_exists_in_framework(
    exception_name: str,
) -> None:
    """The curated rule-exception list must reflect real classes — if
    a rename happened, the list and the doc both need updating."""
    cls = getattr(E, exception_name, None)
    assert cls is not None, (
        f"{exception_name} is documented as a rule but doesn't exist "
        f"in framework.errors — was it renamed?"
    )
    assert isinstance(cls, type) and issubclass(cls, E.WirebenchError)


def test_every_exception_name_in_the_doc_resolves_to_a_class(
    rules_doc_text: str,
) -> None:
    """Any class name shaped like `XxxError` in the doc must point at
    a real exception — catches typos like `ShortCircutError` (missing
    `i`)."""
    referenced = set(re.findall(r'\b([A-Z][A-Za-z0-9_]*Error)\b', rules_doc_text))
    for name in referenced:
        assert hasattr(E, name), (
            f"Doc references {name!r} but no such exception exists in "
            f"framework.errors — typo?"
        )


def test_every_demo_cross_link_resolves(rules_doc_text: str) -> None:
    """`../demos/<name>/` links must point at directories that
    actually exist."""
    demo_links = set(re.findall(r'\(\.\./demos/([a-z0-9_]+)/\)', rules_doc_text))
    assert demo_links, "No demo cross-links found — at minimum a few rules should anchor to demos"
    for slug in demo_links:
        path = REPO_ROOT / 'demos' / slug
        assert path.is_dir(), (
            f"Doc links to ../demos/{slug}/ but {path} doesn't exist"
        )


def test_doc_cross_link_to_errors_source_resolves(
    rules_doc_text: str,
) -> None:
    """The doc links to the GitHub source of `framework/errors.py` — at
    least the on-disk file it names must exist locally too, so the
    `framework/errors.py` reference stays meaningful even before the
    doc site is published."""
    assert 'src/framework/errors.py' in rules_doc_text
    assert (REPO_ROOT / 'src' / 'framework' / 'errors.py').is_file()


# --------------------------------------------------------- learning-path

def test_learning_path_cross_references_the_rules_doc() -> None:
    """`docs/learning-path.md` must name `the-rules.md` so the two
    pages cross-reference and the cumulative-rules property is
    discoverable from either direction."""
    text = LEARNING_PATH_DOC.read_text()
    assert 'the-rules.md' in text, (
        "learning-path.md must link to the-rules.md so the rule "
        "narrative is reachable from the demo path."
    )


# --------------------------------------------------------------- mkdocs

def test_the_rules_appears_in_mkdocs_navigation() -> None:
    """The rules doc must be in the site nav so users browsing the
    published docs can find it."""
    text = MKDOCS_YML.read_text()
    assert 'the-rules.md' in text, (
        "mkdocs.yml must include the-rules.md in `nav:`."
    )


def test_mkdocs_orders_design_principles_before_rules_before_learning() -> None:
    """The nav reads as a progression: abstract (Design principles) →
    concrete enforcement (The rules) → graduated exposure (Learning
    path).  Each must appear in that order in the nav block."""
    text = MKDOCS_YML.read_text()
    dp_pos = text.find('design-principles.md')
    tr_pos = text.find('the-rules.md')
    lp_pos = text.find('learning-path.md')
    assert dp_pos != -1 and tr_pos != -1 and lp_pos != -1
    assert dp_pos < tr_pos < lp_pos, (
        f"mkdocs.yml ordering wrong: design-principles ({dp_pos}), "
        f"the-rules ({tr_pos}), learning-path ({lp_pos}); expected "
        f"design-principles → the-rules → learning-path."
    )
