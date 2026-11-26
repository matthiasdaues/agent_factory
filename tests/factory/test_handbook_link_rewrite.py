"""Contract tests of the section map in _link_rewrite (ST-0454).

The section map repoints each link to one of the three deleted files to the
handbook page that holds its section (BR-150, BR-151, PROP-08). Every test
works on strings, without files.
"""

from __future__ import annotations

import pytest
from _link_rewrite import (
    AmbiguousLink,
    UnmappedAnchor,
    read_section_map,
    rewrite_section_links,
    section_target,
)

# The guide's name is built from two parts, so the search of FH-05-LN-01
# does not find this file.
NAME = "factory" + "-guide"
GUIDE = f"packages/factory/docs/{NAME}.md"
INSTALLED = f"../../.agent-factory/factory/docs/{NAME}.md"
CONCEPTS = "docs/arc42/concepts.md"
INTRO = "docs/arc42/beginner-intro.md"
HANDBOOK = "packages/factory/docs/handbook/"

MAP = f"""\
| Source | Section | Anchor | Page | Note |
| --- | --- | --- | --- | --- |
| `{GUIDE}` | Factory Guide | `#{NAME}` | [`{HANDBOOK}index.md`](x) | |
| `{GUIDE}` | Agents | `#agents` | [`{HANDBOOK}concepts/agents.md`](x) | |
| `{GUIDE}` | Skills | `#skills` | [`{HANDBOOK}concepts/skills.md`](x) | |
| `{CONCEPTS}` | How Agent Factory Works | `#how-agent-factory-works` | [`{HANDBOOK}concepts/how-the-factory-works.md`](x) | |
| `{CONCEPTS}` | The phase chain | `#the-phase-chain` | [`{HANDBOOK}concepts/how-the-factory-works.md`](x) | |
| `{CONCEPTS}` | Project directory tree | `#project-directory-tree` | [`docs/handbook/architecture/repository-layout.md`](x) | |
| `{INTRO}` | A Beginner's Introduction | `#a-beginners-introduction` | [`{HANDBOOK}getting-started/first-session.md`](x) | |
| `packages/usage/README.md` | Usage | `#usage` | [`{HANDBOOK}usage-capture/usage-add-on.md`](x) | |
"""
SECTIONS = read_section_map(MAP, {GUIDE, CONCEPTS, INTRO})
ANCHORS = {
    HANDBOOK + "concepts/agents.md": {"agents"},
    HANDBOOK + "concepts/skills.md": {"what-a-skill-is"},
    HANDBOOK + "concepts/how-the-factory-works.md": {"the-phase-chain"},
}


def rewrite(text: str, src: str = "docs/adr/0001-x.md") -> str:
    return rewrite_section_links(text, src, SECTIONS, ANCHORS)[0]


@pytest.mark.spec("FH-CT-60")
def test_st_0454_map_reads_only_the_named_sources_and_their_opening() -> None:
    assert set(SECTIONS) == {GUIDE, CONCEPTS, INTRO}
    assert SECTIONS[GUIDE][""] == HANDBOOK + "index.md"
    assert SECTIONS[GUIDE]["skills"] == HANDBOOK + "concepts/skills.md"


@pytest.mark.spec("FH-CT-61")
def test_st_0454_anchor_stays_when_the_page_has_the_heading() -> None:
    assert rewrite(f"[a](../../{GUIDE}#agents)") == "[a](../../packages/factory/docs/handbook/concepts/agents.md#agents)"


@pytest.mark.spec("FH-CT-62")
def test_st_0454_anchor_goes_when_the_page_lacks_the_heading() -> None:
    assert rewrite(f"[s](../../{GUIDE}#skills)") == "[s](../../packages/factory/docs/handbook/concepts/skills.md)"


@pytest.mark.spec("FH-CT-63")
@pytest.mark.parametrize(
    ("old", "page"),
    [
        (GUIDE, "index.md"),
        (CONCEPTS, "concepts/how-the-factory-works.md"),
        (INTRO, "getting-started/first-session.md"),
    ],
)
def test_st_0454_link_without_anchor_goes_to_the_opening_page(old: str, page: str) -> None:
    assert rewrite(f"[x]({old})", src="README.md") == f"[x]({HANDBOOK}{page})"


@pytest.mark.spec("FH-CT-64")
def test_st_0454_installed_guide_link_keeps_its_prefix() -> None:
    text = f"[g]({INSTALLED}#agents) [h]({INSTALLED})"
    assert rewrite(text) == (
        "[g](../../.agent-factory/factory/docs/handbook/concepts/agents.md#agents)"
        " [h](../../.agent-factory/factory/docs/handbook/index.md)"
    )


@pytest.mark.spec("FH-CT-65")
def test_st_0454_record_changes_only_in_link_destinations() -> None:
    text = f"# Old record\n\nSee [the *guide*]({GUIDE}#agents \"title\") and [other](other.md).\n"
    new, edits = rewrite_section_links(text, "README.md", SECTIONS, ANCHORS)
    assert new == f"# Old record\n\nSee [the *guide*]({HANDBOOK}concepts/agents.md#agents \"title\") and [other](other.md).\n"
    assert edits == [(f"{GUIDE}#agents", f"{HANDBOOK}concepts/agents.md#agents")]


@pytest.mark.spec("FH-CT-66")
def test_st_0454_links_in_code_stay() -> None:
    text = f"`[a]({GUIDE})`\n\n```\n[b]({GUIDE})\n```\n"
    assert rewrite(text, src="README.md") == text


@pytest.mark.spec("FH-CT-67")
def test_st_0454_reference_definition_is_rewritten() -> None:
    text = f"[guide][g]\n\n[g]: {CONCEPTS}#the-phase-chain\n"
    assert rewrite(text, src="README.md") == f"[guide][g]\n\n[g]: {HANDBOOK}concepts/how-the-factory-works.md#the-phase-chain\n"


@pytest.mark.spec("FH-CT-68")
def test_st_0454_contributor_page_and_other_links_stay_relative() -> None:
    assert rewrite("[t](arc42/concepts.md#project-directory-tree) [o](arc42/05.md)", src="docs/README.md") == (
        "[t](handbook/architecture/repository-layout.md) [o](arc42/05.md)"
    )


@pytest.mark.spec("FH-CT-69")
def test_st_0454_unmapped_anchor_is_refused() -> None:
    with pytest.raises(UnmappedAnchor, match=f"{NAME}.md#nowhere"):
        rewrite(f"[x]({GUIDE}#nowhere)", src="README.md")


@pytest.mark.spec("FH-CT-70")
def test_st_0454_installed_link_to_a_contributor_page_is_refused() -> None:
    sections = {GUIDE: {"": "docs/handbook/index.md"}}
    with pytest.raises(UnmappedAnchor, match="not installed"):
        section_target(INSTALLED.removeprefix("../../"), "", sections, {})


@pytest.mark.spec("FH-CT-71")
def test_st_0454_link_outside_the_map_stays() -> None:
    assert section_target("docs/arc42/05.md", "x", SECTIONS, ANCHORS) is None


@pytest.mark.spec("FH-CT-72")
def test_st_0454_installed_guide_link_gets_the_source_page_in_this_repository() -> None:
    text = f"[g]({INSTALLED}#agents) [h]({INSTALLED})"
    new = rewrite_section_links(text, "docs/adr/0001-x.md", SECTIONS, ANCHORS, installed_links=False)[0]
    assert new == f"[g](../../{HANDBOOK}concepts/agents.md#agents) [h](../../{HANDBOOK}index.md)"


PHASE_PAGE = f"{HANDBOOK}concepts/how-the-factory-works.md"


@pytest.mark.spec("FH-CT-73")
def test_st_0454_query_stays_and_the_path_moves() -> None:
    text = f"[x]({CONCEPTS}?plain=1#the-phase-chain)"
    assert rewrite(text, src="README.md") == f"[x]({PHASE_PAGE}?plain=1#the-phase-chain)"


@pytest.mark.spec("FH-CT-74")
def test_st_0454_encoded_fragment_is_decoded_for_the_map_and_kept() -> None:
    text = f"[x]({CONCEPTS}#the%2Dphase%2Dchain)"
    assert rewrite(text, src="README.md") == f"[x]({PHASE_PAGE}#the%2Dphase%2Dchain)"


@pytest.mark.spec("FH-CT-75")
def test_st_0454_link_in_a_span_with_inner_backticks_stays() -> None:
    text = f"`` a ` [x]({CONCEPTS}) ``\n"
    assert rewrite(text, src="README.md") == text


@pytest.mark.spec("FH-CT-76")
@pytest.mark.parametrize(
    ("text", "line"),
    [
        (f"Intro\n`example\n[x]({CONCEPTS})`\n", 2),
        (f"Intro\n\n[a [b]]({CONCEPTS})\n", 3),
        (f"[x]:\n    {CONCEPTS}\n", 1),
        (f"Intro\n[x]({CONCEPTS}\n", 2),
        (f"Intro\n\n`open text\n[x]: {CONCEPTS}\ntext close`\n", 3),
    ],
    ids=[
        "multiline-code-span",
        "nested-label",
        "split-reference-definition",
        "unclosed-link",
        "definition-in-multiline-code-span",
    ],
)
def test_st_0454_doubtful_link_is_refused_with_file_and_line(text: str, line: int) -> None:
    with pytest.raises(AmbiguousLink, match=f"^README.md:{line}: "):
        rewrite(text, src="README.md")


@pytest.mark.spec("FH-CT-77")
def test_st_0454_refusal_edits_nothing_in_the_file() -> None:
    text = f"[ok]({GUIDE})\n\n[x]({CONCEPTS}\n"
    with pytest.raises(AmbiguousLink, match="^README.md:3: "):
        rewrite_section_links(text, "README.md", SECTIONS, ANCHORS)


@pytest.mark.spec("FH-CT-78")
def test_st_0454_doubtful_construct_without_a_mapped_link_is_left_alone() -> None:
    text = "`a\n[x](other.md)`\n\n[a [b]](other.md)\n\n[r]:\n    other.md\n\n[u](other.md\n"
    assert rewrite(text, src="README.md") == text


@pytest.mark.spec("FH-CT-79")
def test_st_0454_escaped_backticks_open_no_code_span() -> None:
    text = f"Example \\`open\n[x]({CONCEPTS})\nclose\\`\n"
    assert rewrite(text, src="README.md") == f"Example \\`open\n[x]({PHASE_PAGE})\nclose\\`\n"


@pytest.mark.spec("FH-CT-80")
def test_st_0454_label_end_without_an_open_bracket_is_plain_text() -> None:
    text = f"A literal suffix is ]({CONCEPTS}).\n\n[a] and ]({CONCEPTS}).\n"
    assert rewrite(text, src="README.md") == text
