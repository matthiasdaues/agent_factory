"""Text checks for the core-artifact-ownership rulebook changes.

CAO-16 (Rule: Owner receives every finding it acts on next): the finding
format defines `owner:`, lists the ARCH and QA tags, drops RECON, and routes
each open finding to its owner or, without one, to the artifact's producer.
"""

from __future__ import annotations

import re

import pytest
from conftest import REPO_ROOT, load_script

RULEBOOKS = REPO_ROOT / "packages" / "factory" / "rulebooks"
FINDING_FORMAT = RULEBOOKS / "conventions" / "finding-format.md"
FINDING_TEMPLATE = RULEBOOKS / "templates" / "finding.md"


def _section(text: str, heading: str) -> str:
    """Return the body of the `## <heading>` section, up to the next `## `."""
    match = re.search(
        rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.M | re.S
    )
    assert match, f"section '## {heading}' missing"
    return match.group(1)


def _tag_table_tags(text: str) -> set[str]:
    section = _section(text, "File location and name")
    return set(re.findall(r"^\|[^|\n]+\|\s*`([A-Z]+)`\s*\|$", section, re.M))


@pytest.mark.spec("CAO-16-LN-01")
class TestSt0352FindingFormatDefinesOwner:
    """CAO-16-LN-01: owner field, its definition, tags, routing."""

    def test_st_0352_template_frontmatter_has_owner_line(self):
        template = FINDING_TEMPLATE.read_text(encoding="utf-8")
        frontmatter = _section(template, "Frontmatter")
        assert re.search(r"^owner: \S+", frontmatter, re.M)

    def test_st_0352_format_defines_owner_as_next_actor(self):
        text = FINDING_FORMAT.read_text(encoding="utf-8")
        owner = _section(text, "Owner")
        assert "`owner:`" in owner
        assert "the agent that acts on the finding next" in owner

    def test_st_0352_tag_table_lists_arch_and_qa(self):
        tags = _tag_table_tags(FINDING_FORMAT.read_text(encoding="utf-8"))
        assert {"ARCH", "QA"} <= tags

    def test_st_0352_tag_table_drops_recon(self):
        tags = _tag_table_tags(FINDING_FORMAT.read_text(encoding="utf-8"))
        assert "SPEC" in tags, "tag table not parsed"
        assert "RECON" not in tags

    def test_st_0352_orchestrator_sends_open_finding_to_owner(self):
        text = FINDING_FORMAT.read_text(encoding="utf-8")
        routing = _section(text, "How the orchestrator reads findings")
        assert "sends each open finding to the agent in `owner:`" in routing
        assert "not to the author of the reviewed phase" in routing


@pytest.mark.spec("CAO-16-LN-02")
class TestSt0352FindingWithoutOwnerGoesToProducer:
    """CAO-16-LN-02: fallback to the producer from the output declarations."""

    def test_st_0352_finding_without_owner_goes_to_producer(self):
        text = FINDING_FORMAT.read_text(encoding="utf-8")
        routing = _section(text, "How the orchestrator reads findings")
        assert "without `owner:`" in routing
        assert "producer of the artifact" in routing
        assert "output declarations" in routing


@pytest.mark.spec
class TestSt0346IndexLintHookWatchesCoreList:
    """A commit that changes only the core list still runs index-lint (BR-059)."""

    def test_st_0346_index_lint_hook_matches_core_list(self):
        import yaml

        config = yaml.safe_load(
            (REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
        )
        hooks = [h for repo in config["repos"] for h in repo.get("hooks", [])]
        (hook,) = [h for h in hooks if h["id"] == "index-lint"]
        assert re.search(hook["files"], "packages/factory/rulebooks/core-artifacts.yaml")


AGENTS = REPO_ROOT / "packages" / "factory" / "agents"
DOMAIN_MODELING_AGENT = AGENTS / "domain-modeling-agent.md"
SPEC_REVIEW_AGENT = AGENTS / "spec-review-agent.md"

GLOSSARY = "docs/spec/glossary.md"
ENTITY_MODEL = "docs/spec/entity-model.md"
OPTIONAL_STRUCTURE = [
    "docs/spec/state-machines.md",
    "docs/spec/validation-rules.md",
    "docs/spec/interface-contracts.md",
    "docs/spec/schemas/*",
]


def _frontmatter(path) -> dict:
    import yaml

    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert match, f"{path.name}: no frontmatter"
    return yaml.safe_load(match.group(1))


def _declarations(agent: dict) -> dict[str, dict]:
    return {d["path_pattern"]: d for d in agent["outputs"]["declarations"]}


@pytest.mark.spec("CAO-04-LN-01")
class TestSt0348DomainModelingAgentDefinition:
    """CAO-04-LN-01: tier, inputs, six outputs, optional files, schema step, handoff."""

    def test_st_0348_tier_is_strong(self):
        assert _frontmatter(DOMAIN_MODELING_AGENT)["tier"] == "strong"

    def test_st_0348_required_inputs_are_scope_map_and_feature_files(self):
        required = _frontmatter(DOMAIN_MODELING_AGENT)["inputs"]["required"]
        assert {r["path_pattern"] for r in required} == {
            "docs/spec/scope-map.md",
            "docs/spec/features/*.feature",
        }

    def test_st_0348_context_inputs(self):
        context = _frontmatter(DOMAIN_MODELING_AGENT)["inputs"]["context"]
        assert {
            GLOSSARY,
            "docs/spec/work/term-candidates.md",
            "src/**/*",
            "docs/agent-context.md",
        } <= set(context)

    def test_st_0348_glossary_and_entity_model_are_required_outputs(self):
        decls = _declarations(_frontmatter(DOMAIN_MODELING_AGENT))
        assert decls[GLOSSARY]["required"] is True
        assert decls[GLOSSARY]["reviewed_by"] == ["spec-review-agent", "stakeholder"]
        assert decls[ENTITY_MODEL]["required"] is True
        assert decls[ENTITY_MODEL]["reviewed_by"] == ["spec-review-agent"]

    @pytest.mark.parametrize("pattern", OPTIONAL_STRUCTURE)
    def test_st_0348_optional_structure_output_is_reviewed(self, pattern):
        decl = _declarations(_frontmatter(DOMAIN_MODELING_AGENT))[pattern]
        assert decl["required"] is False
        assert decl["reviewed_by"] == ["spec-review-agent"]

    def test_st_0348_optional_files_only_when_the_domain_needs_them(self):
        text = DOMAIN_MODELING_AGENT.read_text(encoding="utf-8")
        assert (
            "only when the domain has state machines, rules, contracts, "
            "or structured payloads" in " ".join(text.split())
        )

    def test_st_0348_workflow_has_schema_step(self):
        workflow = _section(
            DOMAIN_MODELING_AGENT.read_text(encoding="utf-8"), "Workflow"
        )
        step = re.search(r"^\d+\. \*\*Write schemas\*\*.*$", workflow, re.M)
        assert step, "no schema step"
        assert "`docs/spec/schemas/`" in step.group(0)
        assert "payload column" in step.group(0)

    def test_st_0348_workflow_has_state_machine_step(self):
        workflow = _section(
            DOMAIN_MODELING_AGENT.read_text(encoding="utf-8"), "Workflow"
        )
        step = re.search(r"^\d+\. \*\*Write state machines\*\*.*$", workflow, re.M)
        assert step, "no state machine step"
        assert "pseudocode" in step.group(0)
        assert "statemachine-lint" in step.group(0)

    def test_st_0348_handoff_names_spec_review_in_a_new_session(self):
        handoff = _section(DOMAIN_MODELING_AGENT.read_text(encoding="utf-8"), "Handoff")
        assert "spec-review-agent" in handoff
        assert "new session" in handoff

    def test_st_0348_handoff_names_architecture_only_after_its_files_change(self):
        handoff = " ".join(
            _section(DOMAIN_MODELING_AGENT.read_text(encoding="utf-8"), "Handoff").split()
        )
        assert (
            "only when this run wrote or changed `docs/spec/entity-model.md` "
            "or `docs/spec/state-machines.md`" in handoff
        )
        assert "architecture-agent" in handoff

    def test_st_0348_handoff_targets_in_frontmatter(self):
        assert _frontmatter(DOMAIN_MODELING_AGENT)["handoff-to"] == [
            "spec-review-agent",
            "architecture-agent",
        ]


@pytest.mark.spec("CAO-04-LN-01")
class TestSt0348SpecReviewReadsTheStructureFamily:
    """The spec-review agent reads every file it reviews (BR-059)."""

    def test_st_0348_glossary_and_entity_model_are_required_inputs(self):
        required = _frontmatter(SPEC_REVIEW_AGENT)["inputs"]["required"]
        assert {GLOSSARY, ENTITY_MODEL} <= {r["path_pattern"] for r in required}

    def test_st_0348_optional_structure_files_are_context_inputs(self):
        context = _frontmatter(SPEC_REVIEW_AGENT)["inputs"]["context"]
        assert set(OPTIONAL_STRUCTURE) <= set(context)
        assert GLOSSARY not in context


TEST_STRATEGY_AGENT = AGENTS / "test-strategy-agent.md"
REQUIREMENTS_AGENT = AGENTS / "requirements-agent.md"
VIRGIL = AGENTS / "virgil.md"
PLANNING_AGENT = AGENTS / "planning-agent.md"
SKILLS = REPO_ROOT / "packages" / "factory" / "skills"

TESTING_YAML = "docs/testing.yaml"
QA_STRATEGY = "docs/spec/work/{name}-qa-strategy.md"


def _flat(text: str) -> str:
    return " ".join(text.split())


def _subsection(text: str, heading: str) -> str:
    """Return the body of the `### <heading>` section, up to the next heading."""
    match = re.search(
        rf"^### {re.escape(heading)}\n(.*?)(?=^##+ |\Z)", text, re.M | re.S
    )
    assert match, f"section '### {heading}' missing"
    return match.group(1)


@pytest.mark.spec("CAO-10-LN-01")
class TestSt0357TestStrategyAgentDefinition:
    """CAO-10-LN-01: tier, skills, inputs, outputs, workflow, handoff."""

    def test_st_0357_tier_is_strong(self):
        assert _frontmatter(TEST_STRATEGY_AGENT)["tier"] == "strong"

    def test_st_0357_skills_are_the_four_test_practice_skills(self):
        assert _frontmatter(TEST_STRATEGY_AGENT)["skills"] == [
            "detect-test-regime",
            "qa-strategy-from-spec",
            "crap-score",
            "mutation-testing",
        ]

    def test_st_0357_declares_no_required_input(self):
        inputs = _frontmatter(TEST_STRATEGY_AGENT)["inputs"]
        assert not inputs.get("required")

    def test_st_0357_context_inputs(self):
        context = _frontmatter(TEST_STRATEGY_AGENT)["inputs"]["context"]
        assert {
            "docs/spec/features/*.feature",
            "docs/spec/interface-contracts.md",
            ENTITY_MODEL,
            TESTING_YAML,
        } <= set(context)

    def test_st_0357_outputs_are_testing_yaml_and_qa_strategies(self):
        decls = _declarations(_frontmatter(TEST_STRATEGY_AGENT))
        assert decls[TESTING_YAML]["reviewed_by"] == ["stakeholder"]
        assert QA_STRATEGY in decls

    def test_st_0357_writes_testing_yaml_without_a_feature_file(self):
        workflow = _flat(_section(TEST_STRATEGY_AGENT.read_text(encoding="utf-8"), "Workflow"))
        assert "also in a project without a feature file" in workflow

    def test_st_0357_qa_strategy_only_when_its_inputs_exist(self):
        workflow = _flat(_section(TEST_STRATEGY_AGENT.read_text(encoding="utf-8"), "Workflow"))
        assert (
            "only when the feature file, `docs/spec/interface-contracts.md`, "
            "and `docs/spec/entity-model.md` exist" in workflow
        )
        assert "names the missing input" in workflow

    def test_st_0357_every_testing_yaml_change_waits_for_the_stakeholder(self):
        workflow = _flat(_section(TEST_STRATEGY_AGENT.read_text(encoding="utf-8"), "Workflow"))
        assert (
            "**Pause point:** every change to `docs/testing.yaml` waits for "
            "the stakeholder's confirmation" in workflow
        )
        assert "writes nothing before the stakeholder confirms" in workflow

    def test_st_0357_mutation_testing_records_only_enabled_and_command(self):
        workflow = _flat(_section(TEST_STRATEGY_AGENT.read_text(encoding="utf-8"), "Workflow"))
        assert (
            "only `gates.mutation_testing.enabled` and "
            "`gates.mutation_testing.command`" in workflow
        )
        assert "writes no configuration file of the mutation tool" in workflow

    def test_st_0357_never_runs_a_gate(self):
        text = _flat(TEST_STRATEGY_AGENT.read_text(encoding="utf-8"))
        assert "The agent never runs a gate." in text

    def test_st_0357_handoff_names_the_planning_agent(self):
        assert _frontmatter(TEST_STRATEGY_AGENT)["handoff-to"] == ["planning-agent"]
        handoff = _section(TEST_STRATEGY_AGENT.read_text(encoding="utf-8"), "Handoff")
        assert "planning-agent" in handoff


@pytest.mark.spec("CAO-10-LN-01")
class TestSt0357OtherAgentsGiveUpTheTestPractice:
    """CAO-10-LN-01: requirements agent, Virgil, and planning agent."""

    def test_st_0357_requirements_agent_drops_the_qa_strategy(self):
        agent = _frontmatter(REQUIREMENTS_AGENT)
        assert "qa-strategy-from-spec" not in agent["skills"]
        assert QA_STRATEGY not in _declarations(agent)
        assert "qa-strategy-from-spec" not in REQUIREMENTS_AGENT.read_text(
            encoding="utf-8"
        )

    def test_st_0357_virgil_declares_no_testing_yaml(self):
        assert TESTING_YAML not in _declarations(_frontmatter(VIRGIL))

    def test_st_0357_fitting_step_2b_takes_the_test_strategy_role(self):
        step = _flat(
            _subsection(VIRGIL.read_text(encoding="utf-8"), "2b. Detect test regime")
        )
        assert "the session takes the test-strategy agent's role" in step
        assert "test-strategy-agent.md" in step

    def test_st_0357_planning_preflight_stops_and_names_the_test_strategy_agent(self):
        preflight = _flat(
            _subsection(
                PLANNING_AGENT.read_text(encoding="utf-8"),
                "Pre-flight — Concern registry and testing regime",
            )
        )
        assert "stop the pre-flight" in preflight
        assert "test-strategy-agent" in preflight

    def test_st_0357_planning_agent_does_not_run_detect_test_regime(self):
        assert "detect-test-regime" not in PLANNING_AGENT.read_text(encoding="utf-8")


@pytest.mark.spec("CAO-10-LN-01")
class TestSt0357SkillsNameTheirCaller:
    """The two test practice skills name the test-strategy agent and the pause point."""

    def test_st_0357_detect_test_regime_names_caller_and_pause_point(self):
        text = _flat((SKILLS / "detect-test-regime" / "SKILL.md").read_text(encoding="utf-8"))
        assert "The test-strategy agent invokes this skill" in text
        assert "Write nothing before the stakeholder confirms" in text
        assert "planning agent detects" not in text

    def test_st_0357_qa_strategy_from_spec_names_its_caller(self):
        text = _flat(
            (SKILLS / "qa-strategy-from-spec" / "SKILL.md").read_text(encoding="utf-8")
        )
        assert "The test-strategy agent invokes this skill" in text


ARCHITECTURE_AGENT = AGENTS / "architecture-agent.md"
MAINTAIN_ARCHITECTURE = SKILLS / "maintain-architecture" / "SKILL.md"
RUN_STEP = SKILLS / "run-step" / "SKILL.md"

DEPENDENCY_RULES = "docs/spec/dependency-rules.dsl"
ARCH_FINDINGS = "docs/findings/ARCH-*.md"
STATE_MACHINES = "docs/spec/state-machines.md"


@pytest.mark.spec("CAO-07-LN-01")
class TestSt0353ArchitectureAgentDefinition:
    """CAO-07-LN-01: outputs, context inputs, and the read check of Step 5."""

    def test_st_0353_declares_dependency_rules_with_its_review(self):
        decl = _declarations(_frontmatter(ARCHITECTURE_AGENT))[DEPENDENCY_RULES]
        assert decl["reviewed_by"] == ["architecture-review-agent"]
        assert decl["required"] is False

    def test_st_0353_declares_arch_findings(self):
        assert ARCH_FINDINGS in _declarations(_frontmatter(ARCHITECTURE_AGENT))

    def test_st_0353_declares_no_state_machines(self):
        assert STATE_MACHINES not in _declarations(_frontmatter(ARCHITECTURE_AGENT))

    def test_st_0353_context_inputs_include_the_domain_structure(self):
        context = _frontmatter(ARCHITECTURE_AGENT)["inputs"]["context"]
        assert {ENTITY_MODEL, STATE_MACHINES} <= set(context)

    def test_st_0353_workflow_runs_the_read_check_instead_of_writing(self):
        workflow = _flat(_section(ARCHITECTURE_AGENT.read_text(encoding="utf-8"), "Workflow"))
        assert "→ state machines per" not in workflow
        assert "the read check of Step 5" in workflow


def _step_5() -> str:
    text = MAINTAIN_ARCHITECTURE.read_text(encoding="utf-8")
    match = re.search(r"^## Step 5 — (.*?)(?=^## |\Z)", text, re.M | re.S)
    assert match, "no Step 5"
    return _flat(match.group(0))


@pytest.mark.spec("CAO-07-LN-01")
class TestSt0353MaintainArchitectureStep5IsAReadCheck:
    """CAO-07-LN-01: Step 5 compares, skips, files ARCH, and writes nothing."""

    def test_st_0353_step_5_is_a_read_check(self):
        assert "Step 5 — Check the components against the state machines" in _step_5()

    def test_st_0353_step_5_skipped_without_state_machines(self):
        assert "When `docs/spec/state-machines.md` does not exist, skip this step." in _step_5()

    def test_st_0353_contradiction_files_arch_finding_for_domain_modeling(self):
        step = _step_5()
        assert "`docs/findings/ARCH-NNNN.md`" in step
        assert "`owner: domain-modeling-agent`" in step

    def test_st_0353_step_5_never_writes_state_machines(self):
        assert "Never write `docs/spec/state-machines.md`." in _step_5()


@pytest.mark.spec("CAO-07-LN-01")
class TestSt0353RunStepDoneRule:
    """CAO-07-LN-01: run-step counts a step as done from its outputs alone."""

    def test_st_0353_changed_input_does_not_restart_a_done_step(self):
        text = _flat(RUN_STEP.read_text(encoding="utf-8"))
        assert "A changed input never restarts a step that is done." in text
        assert "The producer of the changed file starts the next pass in its handoff." in text


CORE_LIST = REPO_ROOT / "packages" / "factory" / "rulebooks" / "core-artifacts.yaml"
STRUCTURE_FILES = [
    "entity-model.md",
    "interface-contracts.md",
    "state-machines.md",
    "validation-rules.md",
]
KEPT_SKILLS = [
    "capture-vision",
    "clarify-requirements",
    "grill-me",
    "grill-with-docs",
    "reverse-map",
    "derive-feature",
]


def _core_outputs(agent: dict) -> set[str]:
    """Return the core list patterns whose sample path a declaration matches."""
    import yaml

    il = load_script("index-lint")
    entries = yaml.safe_load(CORE_LIST.read_text(encoding="utf-8"))["entries"]
    return {
        entry["path_pattern"]
        for entry in entries
        for pattern in _declarations(agent)
        if il.pattern_matches(pattern, entry["sample_path"])
    }


@pytest.mark.spec("CAO-03-LN-01")
class TestSt0349RequirementsAgentKeepsScopeAndBehaviour:
    """CAO-03-LN-01: core outputs, skill list, area spec step, handoff."""

    def test_st_0349_core_outputs_are_scope_map_features_and_areas(self):
        assert _core_outputs(_frontmatter(REQUIREMENTS_AGENT)) == {
            "docs/spec/scope-map.md",
            "docs/spec/features/*.feature",
            "docs/spec/areas/*.md",
        }

    def test_st_0349_area_specs_are_optional_and_reviewed(self):
        decl = _declarations(_frontmatter(REQUIREMENTS_AGENT))[
            "docs/spec/areas/{name}.md"
        ]
        assert decl["required"] is False
        assert decl["reviewed_by"] == ["spec-review-agent"]

    def test_st_0349_skill_list_drops_capture_context(self):
        skills = _frontmatter(REQUIREMENTS_AGENT)["skills"]
        assert "capture-context" not in skills
        assert set(KEPT_SKILLS) <= set(skills)

    def test_st_0349_body_names_no_structure_file(self):
        body = REQUIREMENTS_AGENT.read_text(encoding="utf-8").split("\n---\n", 1)[1]
        assert "Produce supplementary specs" not in body
        assert [f for f in STRUCTURE_FILES if f in body] == []

    def test_st_0349_workflow_writes_an_area_spec_on_request(self):
        workflow = _section(REQUIREMENTS_AGENT.read_text(encoding="utf-8"), "Workflow")
        step = re.search(r"^\s*\w\. \*\*Write area specs\*\*.*$", workflow, re.M)
        assert step, "no area spec step"
        assert "`docs/spec/areas/<area>.md`" in step.group(0)
        assert "the stakeholder says" in step.group(0)

    def test_st_0349_handoff_names_the_domain_modeling_agent(self):
        assert _frontmatter(REQUIREMENTS_AGENT)["handoff-to"] == [
            "domain-modeling-agent"
        ]
        handoff = _section(REQUIREMENTS_AGENT.read_text(encoding="utf-8"), "Handoff")
        assert "domain-modeling-agent" in handoff

    def test_st_0349_spec_review_reads_the_area_specs(self):
        context = _frontmatter(SPEC_REVIEW_AGENT)["inputs"]["context"]
        assert "docs/spec/areas/*.md" in context


ARCHITECTURE_REVIEW_AGENT = AGENTS / "architecture-review-agent.md"
ATAM_REVIEW = SKILLS / "atam-review" / "SKILL.md"


def _rules_check() -> str:
    text = ATAM_REVIEW.read_text(encoding="utf-8")
    match = re.search(
        r"^## Step 1b — Check the dependency rules against the component view\n"
        r"(.*?)(?=^## |\Z)",
        text,
        re.M | re.S,
    )
    assert match, "no Step 1b rules check"
    return _flat(match.group(1))


@pytest.mark.spec("CAO-09-LN-01")
class TestSt0354ArchitectureReviewChecksTheDependencyRules:
    """CAO-09-LN-01: context input, the atam-review rules check, optional rules file."""

    def test_st_0354_rules_file_is_a_context_input(self):
        agent = _frontmatter(ARCHITECTURE_REVIEW_AGENT)
        assert DEPENDENCY_RULES in agent["inputs"]["context"]
        required = {r["path_pattern"] for r in agent["inputs"]["required"]}
        assert DEPENDENCY_RULES not in required

    def test_st_0354_core_list_marks_rules_file_optional(self):
        import yaml

        entries = yaml.safe_load(CORE_LIST.read_text(encoding="utf-8"))["entries"]
        (entry,) = [e for e in entries if e["path_pattern"] == DEPENDENCY_RULES]
        assert entry["optional"] is True

    def test_st_0354_rules_check_reads_the_component_view(self):
        step = _rules_check()
        assert "component view of `docs/spec/architecture.dsl`" in step
        assert "every relationship between them" in step

    def test_st_0354_unknown_component_is_a_mismatch(self):
        assert (
            "A rule that names a module the component view lacks is a mismatch."
            in _rules_check()
        )

    def test_st_0354_forbidden_relationship_is_a_mismatch(self):
        assert (
            "So is a rule that forbids a dependency the component view draws "
            "as a relationship." in _rules_check()
        )

    def test_st_0354_mismatch_files_atam_finding_for_the_architecture_agent(self):
        step = _rules_check()
        assert "`docs/findings/ATAM-NNNN.md`" in step
        assert "`owner: architecture-agent`" in step
        assert "Name the rule and the component view." in step

    def test_st_0354_rules_check_skipped_without_rules_file(self):
        step = _rules_check()
        assert (
            "When `docs/spec/dependency-rules.dsl` does not exist, skip this step"
            in step
        )
        assert "Rules check: skipped" in step

    def test_st_0354_report_carries_the_rules_check(self):
        report = _flat(
            _section(ATAM_REVIEW.read_text(encoding="utf-8"), "Step 4 — Write the review report")
        )
        assert "**Rules check**" in report


TERM_CANDIDATES = "docs/spec/work/term-candidates.md"
WRITE_GLOSSARY = "`--write-glossary`"
CANDIDATE_HEADER = (
    "| Term | Domain area | Source | Proposed definition | Status | Note |"
)
REVERSE_MAP = SKILLS / "reverse-map" / "SKILL.md"
GRILLING = SKILLS / "grilling" / "SKILL.md"
DOMAIN_MODELING = SKILLS / "domain-modeling" / "SKILL.md"
RECONCILE_SPEC = SKILLS / "reconcile-spec" / "SKILL.md"
TERM_WRITERS = [REVERSE_MAP, GRILLING, DOMAIN_MODELING, RECONCILE_SPEC]
WRITE_VERB = re.compile(r"\b(writes?|seeds?|updates?|adds?|creates?)\b", re.I)
NEGATION = re.compile(r"\b(never|neither|not|no|unchanged)\b", re.I)


def _blocks(text: str) -> list[str]:
    """Split a Markdown body into paragraphs and list items, without headings."""
    body = text.split("\n---\n", 1)[1]
    parts = re.split(r"\n\s*\n|\n(?=\s*(?:[-*]|\d+\.) )", body)
    return [_flat(p) for p in parts if p.strip() and not p.lstrip().startswith("#")]


def _glossary_writes(path) -> list[str]:
    """Return the blocks that name a write to the glossary without the argument."""
    return [
        block
        for block in _blocks(path.read_text(encoding="utf-8"))
        if "glossary.md" in block
        and WRITE_VERB.search(block)
        and WRITE_GLOSSARY not in block
        and not NEGATION.search(block)
    ]


@pytest.mark.spec("CAO-06-LN-01")
class TestSt0350TermsBecomeCandidates:
    """CAO-06-LN-01: term candidates or a report row, and one glossary producer."""

    @pytest.mark.parametrize("path", TERM_WRITERS, ids=lambda p: p.parent.name)
    def test_st_0350_skill_writes_no_glossary_without_the_argument(self, path):
        assert _glossary_writes(path) == []

    def test_st_0350_reverse_map_records_found_names_as_candidates(self):
        text = REVERSE_MAP.read_text(encoding="utf-8")
        step = _flat(_section(text, "Record term candidates"))
        assert f"`{TERM_CANDIDATES}`" in step
        assert CANDIDATE_HEADER in text
        assert "status `candidate`" in step
        assert "Source names the code path" in step
        assert "never writes `docs/spec/glossary.md`" in step

    def test_st_0350_reverse_map_writes_only_scope_map_and_candidates(self):
        boundaries = _flat(_section(REVERSE_MAP.read_text(encoding="utf-8"), "Boundaries"))
        assert (
            f"It writes only `docs/spec/scope-map.md` and `{TERM_CANDIDATES}`."
            in boundaries
        )

    def test_st_0350_reverse_map_unattended_mode_records_candidates(self):
        unattended = _flat(
            _section(REVERSE_MAP.read_text(encoding="utf-8"), "Unattended mode")
        )
        assert "Record term candidates as in the attended mode." in unattended
        assert "Seed" not in unattended

    def test_st_0350_domain_modeling_routes_a_settled_term(self):
        route = _flat(
            _section(DOMAIN_MODELING.read_text(encoding="utf-8"), "Where a settled term goes")
        )
        assert f"Only the domain-modeling agent passes {WRITE_GLOSSARY}." in route
        assert f"`{TERM_CANDIDATES}`" in route
        assert "status `confirmed`" in route
        assert "the settled definition" in route
        assert "`docs/spec/glossary.md` stays unchanged" in route

    def test_st_0350_glossary_update_needs_the_argument(self):
        text = DOMAIN_MODELING.read_text(encoding="utf-8")
        update = _flat(_subsection(text, f"Update {GLOSSARY} inline"))
        assert f"Only with {WRITE_GLOSSARY}" in update

    def test_st_0350_grilling_passes_the_argument_on_only_when_received(self):
        mode = _flat(_section(GRILLING.read_text(encoding="utf-8"), "Settled terms"))
        assert f"`{TERM_CANDIDATES}`" in mode
        assert "status `confirmed`" in mode
        assert f"Pass {WRITE_GLOSSARY} on only when this run received it." in mode

    def test_st_0350_reconcile_spec_reports_terminology_drift_as_a_row(self):
        text = _flat(RECONCILE_SPEC.read_text(encoding="utf-8"))
        assert "Artifact `docs/spec/glossary.md`" in text
        assert "Owner `domain-modeling-agent`" in text
        assert "Status `open`" in text
        assert (
            f"It changes neither `docs/spec/glossary.md` nor `{TERM_CANDIDATES}`."
            in text
        )


IMPLEMENTATION_AGENT = AGENTS / "implementation-agent.md"
MUTATION_TESTING = SKILLS / "mutation-testing" / "SKILL.md"
QA_FINDINGS = "docs/findings/QA-*.md"


def _resolve_qa_step() -> str:
    workflow = _section(TEST_STRATEGY_AGENT.read_text(encoding="utf-8"), "Workflow")
    match = re.search(
        r"^\d+\. \*\*Resolve the QA findings\*\*.*?(?=^\d+\. \*\*|^\*\*Pause point|\Z)",
        workflow,
        re.M | re.S,
    )
    assert match, "no step 'Resolve the QA findings'"
    return _flat(match.group(0))


def _post_wave_step() -> str:
    workflow = _section(
        IMPLEMENTATION_AGENT.read_text(encoding="utf-8"), "Workflow — Automated Mode"
    )
    match = re.search(
        r"^\d+\. \*\*Route the QA findings\*\*.*?(?=^\d+\. \*\*|\Z)",
        workflow,
        re.M | re.S,
    )
    assert match, "no step 'Route the QA findings'"
    return _flat(match.group(0))


@pytest.mark.spec("CAO-12-LN-01")
class TestSt0358MutationTestingFilesAQaFinding:
    """CAO-12-LN-01: an unresolved mutant becomes a QA finding with its owner."""

    def test_st_0358_file_qa_finding_names_path_and_owner(self):
        text = _flat(MUTATION_TESTING.read_text(encoding="utf-8"))
        assert "`docs/findings/QA-NNNN.md`" in text
        assert "`owner: test-strategy-agent`" in text
        assert "`status: open`" in text


@pytest.mark.spec("CAO-12-LN-01")
class TestSt0358TestStrategyAgentResolvesQaFindings:
    """CAO-12-LN-01: owned-only rule and the two resolutions."""

    def test_st_0358_declares_qa_findings_as_output_and_context(self):
        agent = _frontmatter(TEST_STRATEGY_AGENT)
        assert QA_FINDINGS in _declarations(agent)
        assert QA_FINDINGS in agent["inputs"]["context"]

    def test_st_0358_works_only_on_open_findings_it_owns(self):
        step = _resolve_qa_step()
        assert "only on open `QA` findings with `owner: test-strategy-agent`" in step
        assert "leaves every other finding unchanged" in step

    def test_st_0358_wrong_layer_changes_the_table_and_resolves(self):
        step = _resolve_qa_step()
        assert "changes the contract-owner table of the QA strategy" in step
        assert "sets `status: resolved`" in step

    def test_st_0358_missing_test_moves_owner_and_stays_open(self):
        step = _resolve_qa_step()
        assert "records in the finding which test is missing" in step
        assert "moves `owner:` to `planning-agent`" in step
        assert "status stays `open`" in step


@pytest.mark.spec("CAO-12-LN-01")
class TestSt0358ImplementationAgentRoutesQaFindings:
    """CAO-12-LN-01: dispatch after the wave, resolution on merge."""

    def test_st_0358_dispatches_test_strategy_agent_for_its_findings(self):
        step = _post_wave_step()
        assert "after `close-wave`" in step
        assert (
            "dispatches the test-strategy agent for each open `QA` finding "
            "with `owner: test-strategy-agent`" in step
        )

    def test_st_0358_no_dispatch_for_planning_agent_findings(self):
        step = _post_wave_step()
        assert (
            "does not dispatch the test-strategy agent for a finding "
            "with `owner: planning-agent`" in step
        )

    def test_st_0358_merge_of_the_story_resolves_the_finding(self):
        step = _post_wave_step()
        assert "a merged story names an open `QA` finding" in step
        assert "sets its `status: resolved`" in step

    def test_st_0358_declares_qa_findings(self):
        assert QA_FINDINGS in _declarations(_frontmatter(IMPLEMENTATION_AGENT))


@pytest.mark.spec("CAO-12-LN-01")
class TestSt0358PlanningAgentReadsQaFindings:
    """CAO-12-LN-01: the planning agent's context input."""

    def test_st_0358_qa_findings_are_a_context_input(self):
        assert QA_FINDINGS in _frontmatter(PLANNING_AGENT)["inputs"]["context"]

    def test_st_0358_adds_the_missing_test_to_a_story_that_names_the_finding(self):
        text = _flat(PLANNING_AGENT.read_text(encoding="utf-8"))
        assert (
            "reads each open `QA` finding with `owner: planning-agent`" in text
        )
        assert "adds the missing test to a story that names the finding" in text


# --- ST-0365: the four gates in automated and manual mode -----------------

DEVELOPER_AGENT = AGENTS / "developer-agent.md"
FOUR_GATES = ["crap-score", "mutation-testing", "test-design-verify", "dependency-check"]
MUTATION_SCRIPT = ".agent-factory/factory/scripts/mutation-testing"


def _gate_check_loop() -> str:
    text = IMPLEMENTATION_AGENT.read_text(encoding="utf-8")
    match = re.search(r"^### Gate-Check Loop\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    assert match, "section '### Gate-Check Loop' missing"
    return _flat(match.group(1))


def _run_the_gates_step() -> str:
    workflow = _section(DEVELOPER_AGENT.read_text(encoding="utf-8"), "Workflow")
    match = re.search(
        r"^\d+\. \*\*Run the gates\*\*.*?(?=^\d+\. \*\*|^\*\*Pause point|\Z)",
        workflow,
        re.M | re.S,
    )
    assert match, "no step 'Run the gates'"
    return _flat(match.group(0))


@pytest.mark.spec("CAO-11-LN-01")
class TestSt0365FourGatesInBothModes:
    """CAO-11-LN-01: the gate section and the manual-mode step name the four gates."""

    @pytest.mark.parametrize("gate", FOUR_GATES)
    def test_st_0365_gate_section_names_the_gate(self, gate):
        assert f"`{gate}`" in _gate_check_loop()

    def test_st_0365_gate_section_runs_the_mutation_script_in_the_background(self):
        section = _gate_check_loop()
        assert MUTATION_SCRIPT in section
        assert "in the background" in section
        assert "`gates.mutation_testing.timeout_minutes`, 30 when unset" in section
        assert "Set no limit of your own" in section
        assert "names the test-strategy agent" in section

    def test_st_0365_gate_section_hands_manual_mode_to_the_developer_agent(self):
        section = _gate_check_loop()
        assert "In manual mode, the developer agent runs the same gates" in section
        assert "replaces the mechanized gate-check loop" not in section

    def test_st_0365_mutation_script_is_a_context_input(self):
        assert MUTATION_SCRIPT in _frontmatter(IMPLEMENTATION_AGENT)["inputs"]["context"]

    @pytest.mark.parametrize("gate", FOUR_GATES)
    def test_st_0365_manual_mode_step_names_the_gate(self, gate):
        assert f"`{gate}`" in _run_the_gates_step()

    def test_st_0365_manual_mode_step_runs_before_the_handback(self):
        step = _run_the_gates_step()
        assert "Manual mode only (`--no-stage --no-commit`)" in step
        assert "Before you hand the story back" in step
        assert "Run `mutation-testing` in the background" in step


# --- ST-0351: the stakeholder confirms term candidates per domain area ----

REQUIREMENTS_AGENT = AGENTS / "requirements-agent.md"
VIRGIL = AGENTS / "virgil.md"
TERM_WORK_FILE_WRITERS = [DOMAIN_MODELING_AGENT, REQUIREMENTS_AGENT, VIRGIL]


def _confirm_section() -> str:
    return _flat(
        _section(DOMAIN_MODELING.read_text(encoding="utf-8"), "Confirm term candidates")
    )


def _workflow_step(path, number: int) -> str:
    workflow = _section(path.read_text(encoding="utf-8"), "Workflow")
    match = re.search(
        rf"^{number}\. \*\*.*?(?=^\d+\. \*\*|^\*\*Pause point|\Z)",
        workflow,
        re.M | re.S,
    )
    assert match, f"{path.name}: no workflow step {number}"
    return _flat(match.group(0))


def _pause_point(path) -> str:
    match = re.search(
        r"^\*\*Pause point:\*\*.*?(?=\n\s*\n|\Z)",
        path.read_text(encoding="utf-8"),
        re.M | re.S,
    )
    assert match, f"{path.name}: no pause point"
    return _flat(match.group(0))


@pytest.mark.spec("CAO-05-LN-01")
class TestSt0351TermsAreConfirmedPerArea:
    """CAO-05-LN-01: pause point, per-area order, move, rejected row, return."""

    def test_st_0351_step_2_passes_the_argument(self):
        step = _workflow_step(DOMAIN_MODELING_AGENT, 2)
        assert f"Invoke `domain-modeling` with {WRITE_GLOSSARY}" in step
        assert "Confirm term candidates" in step

    def test_st_0351_only_step_2_of_the_agent_names_the_argument(self):
        text = DOMAIN_MODELING_AGENT.read_text(encoding="utf-8")
        step = _workflow_step(DOMAIN_MODELING_AGENT, 2)
        assert text.count("--write-glossary") == step.count("--write-glossary") > 0

    def test_st_0351_no_other_agent_names_the_argument(self):
        others = [
            p.name
            for p in AGENTS.glob("*.md")
            if p != DOMAIN_MODELING_AGENT
            and "--write-glossary" in p.read_text(encoding="utf-8")
        ]
        assert others == []

    @pytest.mark.parametrize("path", TERM_WORK_FILE_WRITERS, ids=lambda p: p.stem)
    def test_st_0351_agent_declares_the_work_file_without_review(self, path):
        decl = _declarations(_frontmatter(path))[TERM_CANDIDATES]
        assert decl["required"] is False
        assert "reviewed_by" not in decl

    def test_st_0351_agent_pause_point_asks_one_area_at_a_time(self):
        pause = _pause_point(DOMAIN_MODELING_AGENT)
        assert "one domain area at a time" in pause
        assert "An unattended run skips the pause point" in pause

    def test_st_0351_section_runs_only_with_the_argument(self):
        assert f"only it passes {WRITE_GLOSSARY}" in _confirm_section()

    def test_st_0351_confirmed_rows_move_without_a_question(self):
        section = _confirm_section()
        assert "Move each row with status `confirmed` into the glossary" in section
        assert "without asking the stakeholder again" in section

    def test_st_0351_candidate_gets_a_proposed_definition(self):
        section = _confirm_section()
        assert "Write a proposed definition for each row with status `candidate`" in section
        assert "set its status to `proposed`" in section

    def test_st_0351_rejected_row_returns_to_proposed_with_its_note(self):
        section = _confirm_section()
        assert "You may write a new definition from the note." in section
        assert "The row then returns to `proposed`, and the note stays." in section

    def test_st_0351_pause_point_presents_one_area_at_a_time(self):
        section = _confirm_section()
        assert "Group the `proposed` rows by Domain area." in section
        assert "Present the rows of one domain area together." in section
        assert (
            "Present the next domain area only after the stakeholder has answered "
            "for the current one." in section
        )

    def test_st_0351_steps_run_in_order(self):
        section = _confirm_section()
        marks = [
            "Move the confirmed rows",
            "Propose definitions",
            "Revise rejected rows",
            "Ask per domain area",
            "Record each answer",
        ]
        positions = [section.index(m) for m in marks]
        assert positions == sorted(positions)

    def test_st_0351_confirmed_term_moves_and_leaves_the_work_file(self):
        section = _confirm_section()
        assert "as a Term, Definition, and Avoid row" in section
        assert "Then remove its row from the work file." in section

    def test_st_0351_rejected_row_keeps_the_reason(self):
        section = _confirm_section()
        assert "set the status `rejected` and write the stakeholder's reason into Note" in section
        assert "The term does not enter the glossary." in section

    def test_st_0351_migrated_terms_count_as_confirmed(self):
        section = _confirm_section()
        assert "count as confirmed" in section
        assert "`migrate-spec-layout`" in section
        assert "never asks about them" in section

    def test_st_0351_unattended_run_moves_no_proposal(self):
        unattended = _flat(
            _subsection(DOMAIN_MODELING.read_text(encoding="utf-8"), "Unattended run")
        )
        assert "no stakeholder is present to answer" in unattended
        assert "skips steps 4 and 5" in unattended
        assert "Each `proposed` row keeps its status" in unattended


DEVELOPER_AGENT = AGENTS / "developer-agent.md"
SPEC_FEEDBACK = SKILLS / "spec-feedback" / "SKILL.md"
SPEC_FEEDBACK_REPORTS = "docs/spec/work/spec-feedback-*.md"
SPEC_FEEDBACK_REPORT = "docs/spec/work/spec-feedback-<story-id>.md"
WIDE_SPEC_PATTERN = "docs/spec/**/*.md"
DRIFT_WRITERS = [DEVELOPER_AGENT, IMPLEMENTATION_AGENT]


def _index_agent(name: str) -> dict:
    import yaml

    index = yaml.safe_load(
        (REPO_ROOT / "packages" / "factory" / "INDEX.yaml").read_text(encoding="utf-8")
    )
    (agent,) = [a for a in index["agents"] if a["name"] == name]
    return agent


def _spec_feedback_step_2() -> str:
    return _flat(
        _section(SPEC_FEEDBACK.read_text(encoding="utf-8"), "Step 2 — Write a row")
    )


@pytest.mark.spec("CAO-13-LN-01")
class TestSt0360DriftBecomesAReportRow:
    """CAO-13-LN-01: no specification output, and a row write in Step 2."""

    @pytest.mark.parametrize("path", DRIFT_WRITERS, ids=lambda p: p.stem)
    def test_st_0360_agent_declares_no_specification_output(self, path):
        il = load_script("index-lint")
        patterns = list(_declarations(_frontmatter(path)))
        assert WIDE_SPEC_PATTERN not in patterns
        assert not [
            p for p in patterns if il.pattern_matches(p, "docs/spec/validation-rules.md")
        ]

    @pytest.mark.parametrize("pattern", [SPEC_FEEDBACK_REPORTS, QA_FINDINGS])
    def test_st_0360_developer_agent_declares_the_working_output(self, pattern):
        decl = _declarations(_frontmatter(DEVELOPER_AGENT))[pattern]
        assert decl["required"] is False
        assert "reviewed_by" not in decl

    @pytest.mark.parametrize("pattern", [SPEC_FEEDBACK_REPORTS, QA_FINDINGS])
    def test_st_0360_index_carries_the_working_output(self, pattern):
        agent = _index_agent("developer-agent")
        patterns = [d["path_pattern"] for d in agent["outputs"]["declarations"]]
        assert pattern in patterns
        assert WIDE_SPEC_PATTERN not in patterns

    def test_st_0360_implementation_agent_declares_no_report(self):
        patterns = list(_declarations(_frontmatter(IMPLEMENTATION_AGENT)))
        assert SPEC_FEEDBACK_REPORTS not in patterns

    def test_st_0360_step_2_writes_a_row_into_the_story_report(self):
        step = _spec_feedback_step_2()
        assert f"Write each discrepancy as a row of `{SPEC_FEEDBACK_REPORT}`" in step
        assert "| Artifact | Drift | Evidence | Owner | Status |" in step
        assert "Set the status to `open`." in step

    def test_st_0360_step_2_names_the_producer_as_owner(self):
        step = _spec_feedback_step_2()
        assert "the producer of the artifact" in step
        assert "`domain-modeling-agent`" in step

    def test_st_0360_step_2_changes_no_specification_file(self):
        step = _spec_feedback_step_2()
        assert "Change no specification file." in step
        text = SPEC_FEEDBACK.read_text(encoding="utf-8")
        assert "Update the spec file" not in text
        assert "write-adr" not in text

    def test_st_0360_each_story_has_its_own_report(self):
        step = _spec_feedback_step_2()
        assert "Each story has its own report" in step
        assert "Write only into the report of your own story." in step

    def test_st_0360_harness_mismatch_becomes_a_test_strategy_row(self):
        step = _workflow_step(DEVELOPER_AGENT, 6)
        assert "the Owner is `test-strategy-agent`" in step
        assert "Update the QA strategy" not in step

    def test_st_0360_developer_spec_feedback_step_writes_rows_only(self):
        step = _workflow_step(DEVELOPER_AGENT, 6)
        assert "Update docs if needed" not in step
        assert SPEC_FEEDBACK_REPORT in step


# --- ST-0356: the spec review covers each structure file and the glossary --

INSPECT_SPEC = SKILLS / "inspect-spec" / "SKILL.md"
SPEC_REVIEW_REQUIRED = {
    "docs/spec/features/*.feature",
    "docs/spec/scope-map.md",
    GLOSSARY,
    ENTITY_MODEL,
}
SPEC_REVIEW_CONTEXT = [
    "docs/spec/state-machines.md",
    "docs/spec/validation-rules.md",
    "docs/spec/interface-contracts.md",
    "docs/spec/areas/*.md",
    "docs/spec/schemas/*",
    TERM_CANDIDATES,
]
STRUCTURE_CHECKS = [
    "docs/spec/entity-model.md",
    "docs/spec/state-machines.md",
    "docs/spec/validation-rules.md",
    "docs/spec/interface-contracts.md",
    "docs/spec/schemas/*",
    "docs/spec/areas/*.md",
    GLOSSARY,
]
GLOSSARY_DEFECTS = [
    "Two terms for one concept.",
    "Term not defined.",
    "Avoided term in use.",
]
DOMAIN_OWNER = "`owner: domain-modeling-agent`"


def _inspect_spec_check(heading: str) -> str:
    return _flat(_subsection(INSPECT_SPEC.read_text(encoding="utf-8"), heading))


@pytest.mark.spec("CAO-08-LN-01")
class TestSt0356SpecReviewInputs:
    """CAO-08-LN-01: required and context inputs of the spec-review agent."""

    def test_st_0356_required_inputs_are_the_files_that_always_exist(self):
        required = _frontmatter(SPEC_REVIEW_AGENT)["inputs"]["required"]
        assert {r["path_pattern"] for r in required} == SPEC_REVIEW_REQUIRED

    def test_st_0356_context_inputs_include_the_optional_files(self):
        context = _frontmatter(SPEC_REVIEW_AGENT)["inputs"]["context"]
        assert set(SPEC_REVIEW_CONTEXT) <= set(context)

    def test_st_0356_agent_runs_the_structure_and_glossary_checks(self):
        step = _workflow_step(SPEC_REVIEW_AGENT, 2)
        assert "each structure file that exists" in step
        assert "the glossary" in step
        assert "A missing optional structure file never stops the review." in step

    def test_st_0356_agent_reads_the_scope_map_only(self):
        step = _workflow_step(SPEC_REVIEW_AGENT, 1)
        assert "The scope map is read only" in step
        assert "The stakeholder reviews the scope map." in step


@pytest.mark.spec("CAO-08-LN-01")
class TestSt0356InspectSpecChecksEachStructureFile:
    """CAO-08-LN-01: one check per structure file, one report section each."""

    @pytest.mark.parametrize("path", STRUCTURE_CHECKS)
    def test_st_0356_check_names_the_structure_file(self, path):
        assert f"**`{path}`**" in _inspect_spec_check("Check each structure file")

    def test_st_0356_missing_file_never_stops_the_review(self):
        section = _inspect_spec_check("Check each structure file")
        assert "Skip the check of a file that does not exist." in section
        assert "A missing optional structure file never stops the review." in section

    def test_st_0356_report_has_one_section_per_checked_file(self):
        report = _flat(
            _section(INSPECT_SPEC.read_text(encoding="utf-8"), "Step 3 — Write the review report")
        )
        assert "**Structure checks**" in report
        assert "one section for each file that Step 2 checked" in report


@pytest.mark.spec("CAO-08-LN-01")
class TestSt0356GlossaryCheck:
    """CAO-08-LN-01: the three glossary defects become domain-modeling findings."""

    @pytest.mark.parametrize("defect", GLOSSARY_DEFECTS)
    def test_st_0356_glossary_check_names_the_defect(self, defect):
        assert f"**{defect}**" in _inspect_spec_check("Check the glossary")

    def test_st_0356_glossary_defect_is_a_finding_for_domain_modeling(self):
        section = _inspect_spec_check("Check the glossary")
        # Minor, so the finding reaches its owner without blocking (b63daee5).
        assert f"File each defect as a Minor `SPEC` finding with {DOMAIN_OWNER}." in section
        assert "It does not block" in section

    def test_st_0356_glossary_check_leaves_unused_terms_to_spec_lint(self):
        section = _inspect_spec_check("Check the glossary")
        assert "`GLOSS001`" in section
        assert "Do not report an unused term again." in section


@pytest.mark.spec("CAO-08-LN-01")
class TestSt0356TermCandidateCheck:
    """CAO-08-LN-01: a `proposed` row waits for the stakeholder and is a finding."""

    def test_st_0356_proposed_row_is_a_finding_for_domain_modeling(self):
        section = _inspect_spec_check("Check the term candidates")
        assert f"`{TERM_CANDIDATES}`" in section
        assert (
            f"File one Major `SPEC` finding with {DOMAIN_OWNER} for each row with status `proposed`."
            in section
        )

    def test_st_0356_glossary_terms_count_as_confirmed(self):
        section = _inspect_spec_check("Check the term candidates")
        assert "Terms in the glossary count as confirmed" in section
        assert "`migrate-spec-layout`" in section
        assert "no finding that a glossary term lacks the stakeholder's confirmation" in section

    def test_st_0356_scope_map_gets_no_finding_on_its_content(self):
        section = _inspect_spec_check("Read the scope map only")
        assert "File no finding on the content of the scope map." in section
        assert "The stakeholder reviews the scope map." in section


@pytest.mark.spec("CAO-08-LN-01")
class TestSt0356SpecReviewRunsWithoutOptionalFiles:
    """The spec review runs without schemas/ and without area specs."""

    def test_st_0356_spec_review_is_eligible_without_schemas_or_areas(
        self, tmp_path, monkeypatch
    ):
        import sys

        packages = REPO_ROOT / "packages" / "factory"
        if str(packages) not in sys.path:
            sys.path.insert(0, str(packages))
        from engine.eligibility import evaluate_agent

        for path in [
            "docs/spec/features/payouts.feature",
            "docs/spec/scope-map.md",
            GLOSSARY,
            ENTITY_MODEL,
        ]:
            (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / path).write_text("# fixture\n", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        agent = {"name": "spec-review-agent", **_frontmatter(SPEC_REVIEW_AGENT)}
        result = evaluate_agent(agent)
        assert not (tmp_path / "docs" / "spec" / "schemas").exists()
        assert not (tmp_path / "docs" / "spec" / "areas").exists()
        assert result["eligible"] is True, result


# --- ST-0362: each drift row goes to its owner and then to the reviewer ------

DISPATCH_CONTRACT = RULEBOOKS / "conventions" / "dispatch-contract.md"


def _drift_rows_rule() -> str:
    return _flat(
        _subsection(
            DISPATCH_CONTRACT.read_text(encoding="utf-8"), "Drift Rows After A Merge"
        )
    )


def _manual_mode_rule() -> str:
    return _flat(
        _subsection(DISPATCH_CONTRACT.read_text(encoding="utf-8"), "Manual Mode")
    )


def _automated_step_4() -> str:
    return _workflow_step_in(IMPLEMENTATION_AGENT, "Workflow — Automated Mode", 4)


def _workflow_step_in(path, section: str, number: int) -> str:
    workflow = _section(path.read_text(encoding="utf-8"), section)
    match = re.search(
        rf"^{number}\. \*\*.*?(?=^\d+\. \*\*|^\*\*Prompt template|\Z)",
        workflow,
        re.M | re.S,
    )
    assert match, f"{path.name}: no step {number} in {section}"
    return _flat(match.group(0))


@pytest.mark.spec("CAO-14-LN-01")
class TestSt0362PostMergeDispatchOrder:
    """CAO-14-LN-01: owner first, then the owner's reviewer."""

    def test_st_0362_rule_dispatches_owner_then_reviewer(self):
        rule = _drift_rows_rule()
        owner = rule.index("dispatches the owner of each `open` row")
        reviewer = rule.index("dispatches the owner's reviewer for each `fixed` row")
        assert owner < reviewer
        assert "sets the row to `fixed`" in rule
        assert "sets the row to `confirmed` or `rejected`" in rule

    def test_st_0362_reviewer_is_the_reviewed_by_entry(self):
        rule = _drift_rows_rule()
        assert "`reviewed_by:` entry of the owner's declaration" in rule
        assert "closes at `fixed`" in rule

    def test_st_0362_implementation_agent_runs_the_rule_after_each_merge(self):
        step = _automated_step_4()
        owner = step.index("dispatches the owner of each `open` row")
        reviewer = step.index("dispatches the owner's reviewer for each `fixed` row")
        assert step.index("merge-story") < owner < reviewer
        assert "Drift Rows After A Merge" in step
        assert "before `close-wave`" in step

    def test_st_0362_route_the_qa_findings_stays_step_6(self):
        step = _workflow_step_in(IMPLEMENTATION_AGENT, "Workflow — Automated Mode", 6)
        assert step.startswith("6. **Route the QA findings**")


@pytest.mark.spec("CAO-14-LN-01")
class TestSt0362RejectedRowBecomesABug:
    """CAO-14-LN-01: the rejecting reviewer, or the session agent, files the BUG."""

    def test_st_0362_reviewer_files_a_bug_for_the_developer(self):
        rule = _drift_rows_rule()
        assert (
            "The reviewer that rejects the row files a `BUG` finding, "
            "`docs/findings/BUG-NNNN.md`, with `owner: developer-agent`." in rule
        )

    def test_st_0362_session_agent_records_the_stakeholder_review(self):
        rule = _drift_rows_rule()
        assert (
            "The agent that ran the session sets the row to `confirmed` or "
            "`rejected` for the stakeholder." in rule
        )
        assert (
            "When the stakeholder rejects, the agent that ran the session "
            "files the `BUG` finding." in rule
        )

    def test_st_0362_rejected_row_does_not_block(self):
        assert "A `rejected` row does not block the wave." in _drift_rows_rule()


@pytest.mark.spec("CAO-14-LN-01")
class TestSt0362ManualModeHoldsPerStory:
    """CAO-14-LN-01 and CAO-G31: per-story rule and QA routing at story close."""

    def test_st_0362_manual_mode_keeps_the_story_open(self):
        rule = _manual_mode_rule()
        assert "the drift-row rule holds per story" in rule
        assert (
            "The human does not close a story while its report has an `open` "
            "row, or a `fixed` row about an artifact on the core list." in rule
        )

    def test_st_0362_manual_mode_routes_qa_findings_at_story_close(self):
        rule = _manual_mode_rule()
        assert "At each story's close, the implementation agent routes the open `QA` findings" in rule
        assert "CAO-G31" in rule

    def test_st_0362_manual_workflow_closes_the_story_after_its_rows(self):
        step = _workflow_step_in(IMPLEMENTATION_AGENT, "Workflow — Manual Mode", 8)
        assert "Drift Rows After A Merge" in step
        assert "§ Manual Mode" in step
        assert "route the open `QA` findings" in step

    def test_st_0362_manual_human_sets_done_only_at_close(self):
        step = _workflow_step_in(IMPLEMENTATION_AGENT, "Workflow — Manual Mode", 5)
        assert "step 8 closes the story" in step


@pytest.mark.spec("CAO-13-LN-01")
class TestSt0362DeveloperWritesNoAdr:
    """The developer agent declares no ADR; ADR drift becomes a row."""

    def test_st_0362_developer_agent_declares_no_adr(self):
        assert "docs/adr/*.md" not in _declarations(_frontmatter(DEVELOPER_AGENT))

    def test_st_0362_adr_drift_is_a_row_for_the_architecture_agent(self):
        step = _workflow_step(DEVELOPER_AGENT, 6)
        assert "A stale or missing ADR is drift" in step
        assert "the Owner is `architecture-agent`" in step
        assert "write-adr" not in step


RECONCILIATION_AGENT = AGENTS / "reconciliation-agent.md"
RECONCILE_SPEC = SKILLS / "reconcile-spec" / "SKILL.md"
COMMIT_CONVENTIONS = RULEBOOKS / "conventions" / "commit-conventions.md"
BRANCHING_POLICY = RULEBOOKS / "conventions" / "branching-policy.md"


@pytest.mark.spec("CAO-15-LN-01")
class TestSt0363ReconciliationWritesOnlyItsReport:
    """The reconciliation agent reports drift as rows and changes no other file."""

    def test_st_0363_agent_declares_its_report_and_bug_findings_only(self):
        decls = _declarations(_frontmatter(RECONCILIATION_AGENT))
        assert set(decls) == {
            "docs/reviews/reconciliation-*.md",
            "docs/findings/BUG-*.md",
        }

    def test_st_0363_agent_has_no_capture_context_skill(self):
        skills = _frontmatter(RECONCILIATION_AGENT)["skills"]
        assert "capture-context" not in skills
        assert "reconcile-spec" in skills

    def test_st_0363_skill_names_owner_and_status_columns(self):
        text = RECONCILE_SPEC.read_text(encoding="utf-8")
        assert "Artifact, Drift, Evidence, Owner, and Status" in text
        assert "Status is `open`" in text
        assert "Never edit the artifact" in text

    def test_st_0363_skill_states_suffix_rule_and_sort_order(self):
        text = RECONCILE_SPEC.read_text(encoding="utf-8")
        assert "`reconciliation-YYYY-MM-DD-2.md`" in text
        assert "Never change an earlier report" in text
        assert "sort by date, then by suffix" in text
        assert "The file without a suffix is run 1 of its day" in text

    @pytest.mark.parametrize(
        "path",
        [RECONCILIATION_AGENT, RECONCILE_SPEC, COMMIT_CONVENTIONS, BRANCHING_POLICY],
        ids=lambda p: p.name,
    )
    def test_st_0363_no_recon_tag_remains(self, path):
        assert "RECON" not in path.read_text(encoding="utf-8")


PLAYBOOKS = REPO_ROOT / "packages" / "factory" / "playbooks"
FEATURE_ADDITION = PLAYBOOKS / "feature-addition.md"
GREENFIELD = PLAYBOOKS / "greenfield-development.md"
BROWNFIELD = PLAYBOOKS / "brownfield-onboarding.md"
DOCUMENTATION_UPDATE = PLAYBOOKS / "documentation-update.md"
REVIEW_LOOP_PLAYBOOKS = [FEATURE_ADDITION, GREENFIELD, DOCUMENTATION_UPDATE]


def _step_body(text: str, heading: str) -> str:
    """Return the body of the `### <heading>` step, up to the next `### ` or `## `."""
    match = re.search(
        rf"^### {re.escape(heading)}[^\n]*\n(.*?)(?=^##|\Z)", text, re.M | re.S
    )
    assert match, f"step '### {heading}' missing"
    return match.group(1)


@pytest.mark.spec("CAO-18-LN-01")
class TestSt0364ReviewLoopsSendFindingsToOwners:
    """Review loops read all open findings and send each to its owner."""

    @pytest.mark.parametrize("path", REVIEW_LOOP_PLAYBOOKS, ids=lambda p: p.name)
    def test_st_0364_no_playbook_searches_recon_findings(self, path):
        assert "RECON" not in path.read_text(encoding="utf-8")

    @pytest.mark.parametrize("path", REVIEW_LOOP_PLAYBOOKS, ids=lambda p: p.name)
    def test_st_0364_loop_reads_all_open_findings(self, path):
        assert 'grep -l "status: open" docs/findings/*.md' in path.read_text(
            encoding="utf-8"
        )

    @pytest.mark.parametrize("path", REVIEW_LOOP_PLAYBOOKS, ids=lambda p: p.name)
    def test_st_0364_loop_sends_each_finding_to_its_owner(self, path):
        text = path.read_text(encoding="utf-8")
        assert "owner:" in text
        assert re.search(
            r"[Ss]end each open finding to the agent in its `owner:`", text
        )


@pytest.mark.spec("CAO-18-LN-01")
class TestSt0364StructureAndQaOwnersAreNamed:
    """Each playbook step that produces a moved artifact names its new owner."""

    @pytest.mark.parametrize(
        "path", [FEATURE_ADDITION, GREENFIELD], ids=lambda p: p.name
    )
    def test_st_0364_structure_files_name_the_domain_modeling_agent(self, path):
        text = path.read_text(encoding="utf-8")
        assert re.search(r"Structure files.*`domain-modeling-agent`", text)

    @pytest.mark.parametrize(
        "path", [FEATURE_ADDITION, GREENFIELD], ids=lambda p: p.name
    )
    def test_st_0364_qa_strategy_names_the_test_strategy_agent(self, path):
        text = path.read_text(encoding="utf-8")
        assert re.search(r"QA strategy.*`test-strategy-agent`", text)

    @pytest.mark.parametrize("heading", ["Step 3.2", "Step 3.3", "Step 3.7"])
    def test_st_0364_brownfield_domain_steps_name_the_domain_modeling_agent(
        self, heading
    ):
        body = _step_body(BROWNFIELD.read_text(encoding="utf-8"), heading)
        assert "**Agent**: `domain-modeling-agent`" in body


@pytest.mark.spec("CAO-18-LN-01")
class TestSt0364RunStepStatesOrderAndChoice:
    """run-step: declared inputs set the order; the operator chooses on a tie."""

    def test_st_0364_declared_inputs_set_the_order(self):
        text = RUN_STEP.read_text(encoding="utf-8")
        assert "The declared inputs set the order of the producers" in text

    def test_st_0364_operator_chooses_between_two_eligible_agents(self):
        text = RUN_STEP.read_text(encoding="utf-8")
        assert "When two agents are eligible, the operator chooses" in text


# --- ST-0367: each reconciliation row returns to its owner and reviewer ------

SCRIPTS = REPO_ROOT / "packages" / "factory" / "scripts"


def _backfeed_step() -> str:
    return _flat(_step_body(DOCUMENTATION_UPDATE.read_text(encoding="utf-8"), "Step 1.5"))


def _done_list() -> str:
    return _flat(_section(DOCUMENTATION_UPDATE.read_text(encoding="utf-8"), "DONE"))


def _reconcile_step_4() -> str:
    text = RECONCILE_SPEC.read_text(encoding="utf-8")
    match = re.search(r"^## Step 4 — .*?(?=^## |\Z)", text, re.M | re.S)
    assert match, "reconcile-spec: no Step 4"
    return _flat(match.group(0))


@pytest.mark.spec("CAO-19-LN-01")
class TestSt0367BackfeedStep:
    """CAO-19-LN-01: the backfeed step of documentation-update."""

    def test_st_0367_backfeed_reads_every_report(self):
        step = _backfeed_step()
        assert "Read every `docs/reviews/reconciliation-*.md`, not only the new report." in step
        assert "`rulebooks/core-artifacts.yaml` under the Factory root" in step

    def test_st_0367_owners_of_open_rows_go_before_reviewers(self):
        step = _backfeed_step()
        owner = step.index("dispatch the owner of each `open` row")
        reviewer = step.index("dispatch the reviewer of each `fixed` row on the core list")
        assert owner < reviewer
        assert "one session at a time" in step
        assert "names the row and the report and no skill" in step
        assert "sets the row to `fixed` in the same commit" in step

    def test_st_0367_stakeholder_reviews_after_any_agent_reviewer(self):
        step = _backfeed_step()
        assert "When `reviewed_by:` is `[stakeholder]`, dispatch no reviewer agent." in step
        assert "the stakeholder sees the fix only after the agent set `confirmed`" in step

    def test_st_0367_rejected_row_becomes_a_bug(self):
        step = _backfeed_step()
        assert "A `rejected` row becomes a `BUG` finding with `owner: developer-agent`" in step

    def test_st_0367_row_outside_the_core_list_closes_at_fixed(self):
        step = _backfeed_step()
        assert "A `fixed` row on an artifact outside the core list closes at `fixed`" in step

    def test_st_0367_doc_drift_goes_through_the_backfeed(self):
        text = DOCUMENTATION_UPDATE.read_text(encoding="utf-8")
        assert "**If only doc drift** → Go to Step 1.5" in text

    def test_st_0367_later_run_repeats_no_waiting_row(self):
        step = _reconcile_step_4()
        assert "Read the rows of every earlier report" in step
        assert (
            "Write no row for a drift that has a row in an earlier report, "
            "unless that row is closed: `confirmed`, or `fixed` on an artifact "
            "outside the core list." in step
        )
        assert (
            "For a row still `open`, or `fixed` on an artifact of the core list, "
            "record nothing" in step
        )

    def test_st_0367_reconciliation_agent_hands_rows_to_the_backfeed(self):
        step = _workflow_step(RECONCILIATION_AGENT, 5)
        assert "every earlier report" in step
        handoff = _flat(_section(RECONCILIATION_AGENT.read_text(encoding="utf-8"), "Handoff"))
        assert "backfeed step of `documentation-update`" in handoff


@pytest.mark.spec("CAO-19-LN-02")
class TestSt0367DoneListWaitsForEveryRow:
    """CAO-19-LN-02: the DONE list waits; no script reads a reconciliation report."""

    def test_st_0367_done_list_waits_for_every_row(self):
        done = _done_list()
        assert (
            "No row of any `docs/reviews/reconciliation-*.md` is `open`, "
            "or `fixed` on an artifact of the core list" in done
        )
        assert "names the report, the artifact, and the status of each such row" in done

    @pytest.mark.parametrize(
        "name", ["premerge-check", "dispatch", "dispatch_lib.py"]
    )
    def test_st_0367_no_script_reads_a_reconciliation_report(self, name):
        text = (SCRIPTS / name).read_text(encoding="utf-8")
        assert "docs/reviews/reconciliation-" not in text


@pytest.mark.spec("CAO-19-LN-03")
class TestSt0367OwnerNamesItsOwnSkill:
    """CAO-19-LN-03: the skill comes from the owner's definition, not the core list."""

    def test_st_0367_architecture_agent_lists_both_skills(self):
        skills = _frontmatter(ARCHITECTURE_AGENT)["skills"]
        assert {"maintain-architecture", "model-structurizr-slice"} <= set(skills)

    def test_st_0367_row_step_names_the_skill_per_artifact(self):
        step = _workflow_step(ARCHITECTURE_AGENT, 5)
        assert step.startswith("5. **Fix a drift row**")
        assert "`model-structurizr-slice`" in step
        assert "`maintain-architecture`" in step
        assert "sets the row to `fixed` in the same commit" in step

    def test_st_0367_core_list_entries_have_no_skill_field(self):
        import yaml

        entries = yaml.safe_load(CORE_LIST.read_text(encoding="utf-8"))["entries"]
        for entry in entries:
            assert set(entry) == {"path_pattern", "sample_path", "family", "optional"}
