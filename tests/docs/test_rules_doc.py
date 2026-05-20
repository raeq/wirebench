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


def _github_anchor(heading: str) -> str:
    """Mimic GitHub's heading-anchor algorithm so the test can compare
    a link's `#anchor` fragment against a heading text taken from a
    demo README.

    Rules (matching GitHub's behaviour for our use cases):
      - lowercase
      - keep word characters, spaces, and hyphens; drop everything else
        (em-dashes, periods, parentheses, apostrophes all drop)
      - replace each space with a hyphen
    Consecutive hyphens are preserved (e.g. `order — wrong` becomes
    `order--wrong`).
    """
    text = heading.strip().lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = text.replace(' ', '-')
    return text


def _readme_anchors(readme_path: Path) -> set[str]:
    """Every GitHub-style anchor produced by an `## …` / `### …`
    heading in the given README."""
    anchors: set[str] = set()
    for line in readme_path.read_text().splitlines():
        m = re.match(r'^#{2,6}\s+(.+?)\s*$', line)
        if m:
            anchors.add(_github_anchor(m.group(1)))
    return anchors


def test_every_demo_cross_link_resolves(rules_doc_text: str) -> None:
    """Absolute GitHub URLs of the form
    `https://github.com/raeq/wirebench/blob/main/demos/<slug>/README.md#<anchor>`
    must resolve: the README file exists and the anchor matches a
    heading in it.

    mkdocs strict mode rejects relative links to files outside the
    `docs/` tree (the README lives under `demos/`, which isn't part
    of the published site), so the demo cross-links use the absolute
    GitHub URL — same pattern this doc uses for the
    `src/framework/errors.py` source link.
    """
    readme_links = re.findall(
        r'https://github\.com/raeq/wirebench/blob/main/demos/'
        r'([a-z0-9_]+)/README\.md#([a-z0-9-]+)',
        rules_doc_text,
    )
    assert readme_links, (
        "the-rules.md should link to demo README sections (the "
        "*what this design is protected from* near-miss snippets) — "
        "that's what gives rule entries their first-caught "
        "traceability."
    )
    for slug, anchor in readme_links:
        readme = REPO_ROOT / 'demos' / slug / 'README.md'
        assert readme.is_file(), (
            f"Doc links to demos/{slug}/README.md but {readme} "
            f"doesn't exist"
        )
        anchors = _readme_anchors(readme)
        assert anchor in anchors, (
            f"Doc links to {readme.name}#{anchor} but no heading in "
            f"that README produces that GitHub anchor.  Available "
            f"anchors: {sorted(anchors)}"
        )


def test_no_relative_demo_links_remain(rules_doc_text: str) -> None:
    """Relative links into `../demos/` would be rejected by mkdocs
    strict mode (the demo READMEs aren't part of the mkdocs site
    tree).  Pin the absolute-URL convention so a future edit doesn't
    silently re-introduce the failure."""
    relative = re.findall(r'\]\(\.\./demos/[^)]*\)', rules_doc_text)
    assert not relative, (
        f"Relative `../demos/...` links break mkdocs strict mode — "
        f"use absolute GitHub URLs.  Offenders: {relative}"
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

INDEX_DOC = REPO_ROOT / 'docs' / 'index.md'
DEMOS_DIR = REPO_ROOT / 'demos'


@pytest.fixture(scope='module')
def learning_path_text() -> str:
    return LEARNING_PATH_DOC.read_text()


@pytest.fixture(scope='module')
def index_text() -> str:
    return INDEX_DOC.read_text()


def _demos_in_repo() -> set[str]:
    """Every directory under `demos/` that holds an actual demo —
    identified by the presence of at least one `*.py` source file
    (skip strays like a docs-only or assets-only directory).  We don't
    require `README.md` because not every demo has one yet."""
    return {
        d.name for d in DEMOS_DIR.iterdir()
        if d.is_dir() and any(d.glob('*.py'))
    }


def test_learning_path_cross_references_the_rules_doc(
    learning_path_text: str,
) -> None:
    """`docs/learning-path.md` must name `the-rules.md` so the two
    pages cross-reference and the cumulative-rules property is
    discoverable from either direction."""
    assert 'the-rules.md' in learning_path_text, (
        "learning-path.md must link to the-rules.md so the rule "
        "narrative is reachable from the demo path."
    )


def test_learning_path_demo_links_use_github_urls(
    learning_path_text: str,
) -> None:
    """The demo links must point at GitHub folders, not
    `https://raeq.github.io/wirebench/demos/...` or relative
    `../demos/...` — both shapes produce broken pages on the published
    docs site (demos aren't republished as MkDocs pages).

    Pin the GitHub-URL convention so the failure mode the original
    Phase 2b.2 deploy hit (silent blank pages) can't return.
    """
    # No relative `../demos/...` links anywhere on the page.
    relative = re.findall(
        r'\]\(\.\./demos/[^)]*\)', learning_path_text,
    )
    assert not relative, (
        f"Relative `../demos/...` links resolve to nothing on the "
        f"published site.  Offenders: {relative}"
    )
    # No raeq.github.io/wirebench/demos/... links either.
    site_demos = re.findall(
        r'https://raeq\.github\.io/wirebench/demos/[^)\s]+',
        learning_path_text,
    )
    assert not site_demos, (
        f"Links to `raeq.github.io/wirebench/demos/...` produce empty "
        f"body content — demos aren't published as MkDocs pages.  "
        f"Use GitHub tree URLs instead.  Offenders: {site_demos}"
    )


def test_every_learning_path_demo_link_resolves_to_a_real_demo(
    learning_path_text: str,
) -> None:
    """Every `github.com/raeq/wirebench/tree/main/demos/<slug>/` link
    on Learning Path must correspond to a real demo directory in the
    repo.  Catches typos in the URL and demos that have been removed
    without the table being updated."""
    demo_links = re.findall(
        r'https://github\.com/raeq/wirebench/tree/main/demos/([a-z0-9_]+)/?',
        learning_path_text,
    )
    assert demo_links, (
        "No github.com demo links found on Learning Path — the demo "
        "table must use the canonical GitHub-tree URLs."
    )
    existing = _demos_in_repo()
    for slug in demo_links:
        assert slug in existing, (
            f"Learning Path links to demos/{slug}/ but that directory "
            f"doesn't exist (or has no README.md).  Known demos: "
            f"{sorted(existing)}"
        )


def test_learning_path_table_covers_every_demo(
    learning_path_text: str,
) -> None:
    """The Learning Path table must have one row per demo directory —
    a new demo added to `demos/` without a table row would silently
    fall off the published learning order."""
    listed = set(re.findall(
        r'https://github\.com/raeq/wirebench/tree/main/demos/([a-z0-9_]+)/?',
        learning_path_text,
    ))
    expected = _demos_in_repo()
    missing = expected - listed
    assert not missing, (
        f"Demos exist in the repo but aren't listed on Learning Path: "
        f"{sorted(missing)}.  Add a table row for each."
    )


# --------------------------------------------------------------- index

def test_index_links_to_the_rules(index_text: str) -> None:
    """Findings 1 + 5 of the site remediation: the homepage's *Where
    to go* surface must include the rules narrative and link to it."""
    assert 'the-rules.md' in index_text, (
        "docs/index.md must link to the-rules.md — it's the most "
        "distinctive Phase 2b.2 artefact and must be reachable from "
        "the landing page."
    )


def test_index_does_not_hardcode_demo_count(index_text: str) -> None:
    """The homepage must not embed a literal demo count — the count
    will stale every time a demo is added.  Phrasings like *every
    wirebench demo* delegate to the Learning Path table (which is
    authoritative and auto-survives demo additions)."""
    # Reject "twelve demos", "12 demos", "18 demos", etc.  Allow the
    # word `demo` / `demos` as a noun without a counting modifier.
    bad = re.findall(
        r'(?i)\b(?:'
        r'twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|'
        r'nineteen|twenty|\d+'
        r')\s+demos\b',
        index_text,
    )
    assert not bad, (
        f"docs/index.md hardcodes a demo count ({bad}) — every demo "
        f"addition would re-stale this line.  Use *every wirebench "
        f"demo* (or equivalent) and let Learning Path own the count."
    )


def test_index_shows_a_concrete_error_message(index_text: str) -> None:
    """Finding 5: the homepage must preview the four-paragraph
    error-message shape — *what / why / where / try* — concretely.
    Pinned by checking for the four labels in a fenced text block."""
    # All four labels must appear in the doc.  We don't assert order
    # or formatting since the rendered output is what visitors see.
    for label in ('Why:', 'Wired at:', 'Try:'):
        assert label in index_text, (
            f"docs/index.md should preview the error-message shape "
            f"with a `{label}` line — that's the Phase 2b user-facing "
            f"win this homepage callout exists to surface."
        )


def test_index_see_also_links_to_a_concrete_demo_readme(
    index_text: str,
) -> None:
    """Finding 7: the *See also* surface should be one click from the
    landing page to a real demo's *what this design is protected from*
    sidebar — not just the demos folder root."""
    assert re.search(
        r'https://github\.com/raeq/wirebench/blob/main/demos/'
        r'[a-z0-9_]+/README\.md',
        index_text,
    ), (
        "docs/index.md *See also* should link to a specific demo's "
        "README so the discipline-in-action is one click away — not "
        "just the demos folder root."
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


def test_mkdocs_keeps_the_two_component_pages_adjacent() -> None:
    """Finding 6: the auto-generated `parts.md` index and the
    hand-curated `component-library-data.md` narrative serve distinct
    purposes; the navigation orders them adjacent so the auto/curated
    distinction reads as one cluster rather than two scattered pages."""
    text = MKDOCS_YML.read_text()
    parts_pos = text.find('parts.md')
    notes_pos = text.find('component-library-data.md')
    assert parts_pos != -1 and notes_pos != -1
    # Adjacent in nav order — find the lines containing each entry and
    # confirm there's nothing else between them.
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    parts_line = next(
        (i for i, l in enumerate(lines) if 'parts.md' in l), None,
    )
    notes_line = next(
        (i for i, l in enumerate(lines) if 'component-library-data.md' in l),
        None,
    )
    assert parts_line is not None and notes_line is not None
    assert abs(parts_line - notes_line) == 1, (
        f"mkdocs.yml: the two component pages should be adjacent so "
        f"the auto/curated distinction reads as one cluster.  Currently "
        f"separated by {abs(parts_line - notes_line) - 1} nav entries."
    )
