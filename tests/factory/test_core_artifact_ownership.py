"""Producer and review contract test for the core list (ST-0347).

Rule: Factory maintainer finds exactly one producer for every core and seam
artifact (BR-056, BR-057, BR-058, BR-060). Each entry of
`rulebooks/core-artifacts.yaml` needs exactly one output declaration that
matches its sample path, and that declaration needs a non-empty
`reviewed_by:`. A declaration with `edits: wording` is no producer.

The real-catalog check reads only `rulebooks/core-artifacts.yaml` and
`INDEX.yaml`. Regenerate `INDEX.yaml` with `scripts/index-lint` after an
agent definition changes.
"""

from __future__ import annotations

import pytest
import yaml
from conftest import REPO_ROOT, load_script

il = load_script("index-lint")

FACTORY = REPO_ROOT / "packages" / "factory"

# Gaps that a named story still has to close. The list is strict: a listed
# entry that passes fails the test. No story adds an entry. It is empty now:
# every core list entry has one reviewed producer.
EXPECTED_FAILURES: dict[str, str] = {}


def producer_finding(agents: list[dict], entry: dict) -> str | None:
    """Return why a core list entry fails, or None when it passes."""
    sample = entry["sample_path"]
    producers = [
        (agent["name"], decl)
        for agent in agents
        for decl in (agent.get("outputs") or {}).get("declarations") or []
        if decl.get("edits") != "wording"
        and il.pattern_matches(str(decl.get("path_pattern", "")), sample)
    ]
    if not producers:
        return f"{sample}: no producer; no output declaration matches the sample path"
    if len(producers) > 1:
        named = ", ".join(
            f"{name} ({decl['path_pattern']})" for name, decl in producers
        )
        return f"{sample}: {len(producers)} producers: {named}"
    name, decl = producers[0]
    if not decl.get("reviewed_by"):
        return f"{sample}: no review; producer {name} ({decl['path_pattern']}) has no reviewed_by entry"
    return None


def producer_findings(agents: list[dict], core_list: list[dict]) -> dict[str, str]:
    """Map each failing entry's path pattern to its finding."""
    findings = {e["path_pattern"]: producer_finding(agents, e) for e in core_list}
    return {pattern: f for pattern, f in findings.items() if f is not None}


def expectation_error(path_pattern: str, finding: str | None) -> str | None:
    """Compare one real-catalog result with the expected-failure list."""
    if path_pattern in EXPECTED_FAILURES and finding is None:
        return (
            f"{path_pattern}: expected failure that now passes; remove it from "
            f"EXPECTED_FAILURES ({EXPECTED_FAILURES[path_pattern]})"
        )
    if path_pattern not in EXPECTED_FAILURES and finding is not None:
        return finding
    return None


def _agent(name: str, *declarations: dict, inputs: dict | None = None) -> dict:
    agent: dict = {"name": name, "outputs": {"declarations": list(declarations)}}
    if inputs is not None:
        agent["inputs"] = inputs
    return agent


def _entry(path_pattern: str, sample_path: str | None = None) -> dict:
    return {"path_pattern": path_pattern, "sample_path": sample_path or path_pattern}


GLOSSARY = _entry("docs/spec/glossary.md")


@pytest.mark.spec("CAO-01-CT-01")
class TestSt0347ProducerCount:
    def test_st_0347_one_reviewed_producer_passes(self):
        agents = [
            _agent(
                "domain-modeling-agent",
                {
                    "path_pattern": "docs/spec/entity-model.md",
                    "reviewed_by": ["spec-review-agent"],
                },
            )
        ]
        assert producer_findings(agents, [_entry("docs/spec/entity-model.md")]) == {}

    def test_st_0347_entry_without_producer_names_the_sample_path(self):
        agents = [
            _agent("architecture-agent", {"path_pattern": "docs/spec/architecture.dsl"})
        ]
        findings = producer_findings(agents, [_entry("docs/spec/dependency-rules.dsl")])
        assert list(findings) == ["docs/spec/dependency-rules.dsl"]
        assert (
            "docs/spec/dependency-rules.dsl: no producer"
            in findings["docs/spec/dependency-rules.dsl"]
        )

    def test_st_0347_wide_second_pattern_names_both_agents(self):
        agents = [
            _agent(
                "domain-modeling-agent",
                {
                    "path_pattern": "docs/spec/state-machines.md",
                    "reviewed_by": ["spec-review-agent"],
                },
            ),
            _agent("reconciliation-agent", {"path_pattern": "docs/spec/*.md"}),
        ]
        finding = producer_findings(agents, [_entry("docs/spec/state-machines.md")])[
            "docs/spec/state-machines.md"
        ]
        assert "2 producers" in finding
        assert "domain-modeling-agent" in finding
        assert "reconciliation-agent (docs/spec/*.md)" in finding

    def test_st_0347_double_star_pattern_counts_as_producer(self):
        agents = [
            _agent(
                "domain-modeling-agent",
                {
                    "path_pattern": "docs/spec/glossary.md",
                    "reviewed_by": ["spec-review-agent"],
                },
            ),
            _agent("developer-agent", {"path_pattern": "docs/spec/**/*.md"}),
        ]
        finding = producer_finding(agents, GLOSSARY)
        assert finding is not None
        assert "developer-agent (docs/spec/**/*.md)" in finding


@pytest.mark.spec("CAO-01-CT-02")
class TestSt0347ProducerWithoutReview:
    @pytest.mark.parametrize(
        "declaration", [{}, {"reviewed_by": []}], ids=["no-field", "empty-list"]
    )
    def test_st_0347_missing_or_empty_review_fails(self, declaration):
        agents = [
            _agent(
                "domain-modeling-agent",
                {"path_pattern": "docs/spec/glossary.md", **declaration},
            )
        ]
        finding = producer_finding(agents, GLOSSARY)
        assert finding is not None
        assert finding.startswith("docs/spec/glossary.md: no review")


@pytest.mark.spec("CAO-02-CT-03")
class TestSt0347ReaderIsNoReview:
    def test_st_0347_empty_review_fails_while_another_agent_reads_the_artifact(self):
        reader_inputs = {
            "required": [{"type": "glossary", "path_pattern": "docs/spec/glossary.md"}]
        }
        agents = [
            _agent(
                "domain-modeling-agent",
                {"path_pattern": "docs/spec/glossary.md", "reviewed_by": []},
            ),
            _agent("spec-review-agent", inputs=reader_inputs),
        ]
        finding = producer_finding(agents, GLOSSARY)
        assert finding is not None
        assert "no review" in finding


@pytest.mark.spec("CAO-01-CT-03")
class TestSt0347WordingAndPlaceholder:
    def test_st_0347_wording_declaration_is_not_counted(self):
        agents = [
            _agent(
                "lector-agent", {"path_pattern": "docs/**/*.md", "edits": "wording"}
            ),
            _agent(
                "domain-modeling-agent",
                {
                    "path_pattern": "docs/spec/glossary.md",
                    "reviewed_by": ["spec-review-agent", "stakeholder"],
                },
            ),
        ]
        assert producer_finding(agents, GLOSSARY) is None

    def test_st_0347_name_placeholder_matches_the_sample_path(self):
        agents = [
            _agent(
                "requirements-agent",
                {
                    "path_pattern": "docs/spec/features/{name}.feature",
                    "reviewed_by": ["spec-review-agent"],
                },
            )
        ]
        entry = _entry(
            "docs/spec/features/*.feature", "docs/spec/features/example.feature"
        )
        assert producer_finding(agents, entry) is None


@pytest.mark.spec("CAO-17-CT-01")
class TestSt0347WorkingOutput:
    def test_st_0347_several_term_candidate_writers_give_no_finding(self):
        term_candidates = {"path_pattern": "docs/spec/work/term-candidates.md"}
        agents = [
            _agent("requirements-agent", term_candidates),
            _agent("architecture-agent", term_candidates),
            _agent(
                "domain-modeling-agent",
                {
                    "path_pattern": "docs/spec/glossary.md",
                    "reviewed_by": ["spec-review-agent", "stakeholder"],
                },
            ),
        ]
        assert producer_findings(agents, [GLOSSARY]) == {}


@pytest.mark.spec("CAO-01-LN-01")
class TestSt0347ExpectedFailureList:
    def test_st_0347_listed_entry_that_passes_is_named(self, monkeypatch):
        monkeypatch.setitem(EXPECTED_FAILURES, "docs/spec/glossary.md", "ST-0000")
        listed = "docs/spec/glossary.md"
        error = expectation_error(listed, None)
        assert error is not None
        assert error.startswith(f"{listed}: expected failure that now passes")

    def test_st_0347_unlisted_entry_that_fails_shows_its_finding(self):
        finding = "docs/spec/architecture.dsl: 2 producers: a (x), b (y)"
        assert expectation_error("docs/spec/architecture.dsl", finding) == finding

    def test_st_0347_listed_failure_and_unlisted_pass_give_no_error(
        self, monkeypatch
    ):
        monkeypatch.setitem(EXPECTED_FAILURES, "docs/spec/glossary.md", "ST-0000")
        assert (
            expectation_error(
                "docs/spec/glossary.md", "docs/spec/glossary.md: no review"
            )
            is None
        )
        assert expectation_error("docs/spec/architecture.dsl", None) is None


def _real_core_list() -> list[dict]:
    return il.load_core_list(FACTORY / "rulebooks")


def _real_agents() -> list[dict]:
    index = yaml.safe_load((FACTORY / "INDEX.yaml").read_text(encoding="utf-8"))
    return index.get("agents") or []


@pytest.mark.spec("CAO-01-LN-01")
class TestSt0347RealCatalog:
    @pytest.mark.parametrize(
        "entry", _real_core_list(), ids=lambda e: e["path_pattern"]
    )
    def test_st_0347_entry_has_one_reviewed_producer(self, entry):
        error = expectation_error(
            entry["path_pattern"], producer_finding(_real_agents(), entry)
        )
        assert error is None, error

    def test_st_0363_expected_failure_list_is_empty(self):
        assert EXPECTED_FAILURES == {}

    def test_st_0347_every_expected_failure_is_on_the_core_list(self):
        patterns = {e["path_pattern"] for e in _real_core_list()}
        assert set(EXPECTED_FAILURES) <= patterns, sorted(
            set(EXPECTED_FAILURES) - patterns
        )


# Configuration files of common mutation tools. The tool and its
# configuration belong to the project, so no agent declares them (DEC-36).
MUTATION_TOOL_CONFIG_SAMPLES = [
    "pyproject.toml",
    "setup.cfg",
    "mutmut_config.py",
    ".cosmic-ray.toml",
    "stryker.conf.json",
    "stryker.config.mjs",
    "pom.xml",
    "build.gradle",
    ".cargo-mutants.toml",
]


def _producers(agents: list[dict], sample: str) -> list[str]:
    return sorted(
        agent["name"]
        for agent in agents
        for decl in (agent.get("outputs") or {}).get("declarations") or []
        if decl.get("edits") != "wording"
        and il.pattern_matches(str(decl.get("path_pattern", "")), sample)
    )


@pytest.mark.spec("CAO-10-LN-02")
class TestSt0357TestPracticeHasOneProducer:
    @pytest.mark.parametrize(
        "sample",
        [
            "docs/testing.yaml",
            "docs/spec/work/payments-qa-strategy.md",
        ],
    )
    def test_st_0357_only_the_test_strategy_agent_declares(self, sample):
        assert _producers(_real_agents(), sample) == ["test-strategy-agent"]

    def test_st_0357_no_other_agent_declares_the_qa_strategy_by_name(self):
        named = sorted(
            agent["name"]
            for agent in _real_agents()
            for decl in (agent.get("outputs") or {}).get("declarations") or []
            if "qa-strategy" in str(decl.get("path_pattern", ""))
        )
        assert named == ["test-strategy-agent"]

    @pytest.mark.parametrize("sample", MUTATION_TOOL_CONFIG_SAMPLES)
    def test_st_0357_no_declaration_names_a_mutation_tool_config(self, sample):
        (agent,) = [a for a in _real_agents() if a["name"] == "test-strategy-agent"]
        patterns = [
            d["path_pattern"] for d in agent["outputs"]["declarations"]
        ]
        assert not [p for p in patterns if il.pattern_matches(p, sample)]


# The writer outline of "Each writer of a shared working-output file declares
# its path" (CAO-G11). Each pair names an agent and a path it must declare.
SPEC_FEEDBACK_REPORTS = "docs/spec/work/spec-feedback-*.md"
RECONCILIATION_REPORTS = "docs/reviews/reconciliation-*.md"
BUG_FINDINGS = "docs/findings/BUG-*.md"
REPORT_WRITERS = [
    "requirements-agent",
    "domain-modeling-agent",
    "architecture-agent",
    "test-strategy-agent",
    "virgil",
    "spec-review-agent",
    "architecture-review-agent",
]
BUG_WRITERS = [
    "spec-review-agent",
    "architecture-review-agent",
    "requirements-agent",
    "domain-modeling-agent",
    "test-strategy-agent",
    "virgil",
]
WRITER_OUTLINE = (
    [(a, "docs/spec/work/term-candidates.md") for a in
     ["requirements-agent", "virgil", "domain-modeling-agent"]]
    + [("developer-agent", SPEC_FEEDBACK_REPORTS)]
    + [(a, SPEC_FEEDBACK_REPORTS) for a in REPORT_WRITERS]
    + [("reconciliation-agent", RECONCILIATION_REPORTS)]
    + [(a, RECONCILIATION_REPORTS) for a in REPORT_WRITERS]
    + [(a, BUG_FINDINGS) for a in BUG_WRITERS]
)


def _index_declarations(name: str) -> dict[str, dict]:
    (agent,) = [a for a in _real_agents() if a["name"] == name]
    return {
        d["path_pattern"]: d for d in (agent.get("outputs") or {}).get("declarations") or []
    }


@pytest.mark.spec("CAO-17-LN-01")
class TestSt0362EveryWriterDeclaresItsPath:
    @pytest.mark.parametrize(
        ("agent", "path"), WRITER_OUTLINE, ids=lambda v: str(v)
    )
    def test_st_0362_writer_declares_the_working_output(self, agent, path):
        decl = _index_declarations(agent).get(path)
        assert decl is not None, f"{agent} does not declare {path} in INDEX.yaml"
        assert "reviewed_by" not in decl, f"{agent} {path}: working output has no reviewed_by"

    def test_st_0362_developer_agent_declares_no_adr(self):
        patterns = list(_index_declarations("developer-agent"))
        assert not [p for p in patterns if il.pattern_matches(p, "docs/adr/0012-x.md")]
