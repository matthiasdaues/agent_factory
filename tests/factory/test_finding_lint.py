"""Checks of finding-lint (ST-0391).

finding-lint reads every finding file with review_class and every register
file, and rejects recorded values that break a classification rule
(BR-079 to BR-087, BR-090, BR-110). The contract tests call the rule
functions of the script. The integration tests run the script as a
subprocess in a temporary directory.
"""

from __future__ import annotations

import itertools
import json
import os
import shutil
import subprocess
import sys

import pytest
from conftest import load_script

lint = load_script("finding-lint")


def _tree(in_use, harms, fails, cost):
    return {
        "in_use": in_use,
        "harms_downstream": harms,
        "fails_purpose": fails,
        "raises_cost": cost,
    }


def _bar(effect, yes_count=0, confidence="proven", in_use=True):
    flags = [index < yes_count for index in range(4)]
    return {
        "effect": effect,
        "second_breach": flags[0],
        "trusted_access": flags[1],
        "non_default": flags[2],
        "user_action": flags[3],
        "confidence": confidence,
        "in_use": in_use,
    }


def _matrix(importance, exposure, in_use=False):
    return {"importance": importance, "exposure": exposure, "in_use": in_use}


# --- Severity rules -----------------------------------------------------------


@pytest.mark.spec("FC-03-CT-01")
@pytest.mark.parametrize("answers", list(itertools.product([True, False], repeat=4)))
def test_st_0391_the_first_yes_answer_sets_the_tree_severity(answers):
    in_use, harms, fails, cost = answers
    if harms:
        expected = "critical"
    elif fails:
        expected = "major"
    elif cost:
        expected = "minor"
    else:
        expected = "note"
    assert lint.tree_severity(_tree(in_use, harms, fails, cost)) == expected


# The worked examples of FC-03: the answers the feature states, and the severity.
WORKED_EXAMPLES = {
    "bug-0037-on-the-feature-branch": (_tree(False, False, True, False), "major"),
    "bug-0037-in-the-installed-copy": (_tree(True, True, True, False), "critical"),
    "adr-0026-gap": (_tree(False, False, True, False), "major"),
    "qa-triage-step-on-the-feature-branch": (_tree(False, False, True, False), "major"),
    "qa-triage-step-on-dev": (_tree(True, True, True, False), "critical"),
}


@pytest.mark.spec("FC-03-CT-01")
@pytest.mark.parametrize("example", list(WORKED_EXAMPLES))
def test_st_0391_the_worked_examples_compute_as_the_feature_states(example):
    basis, expected = WORKED_EXAMPLES[example]
    assert lint.tree_severity(basis) == expected


@pytest.mark.spec("FC-04-CT-01")
@pytest.mark.parametrize(
    ("effect", "start"),
    [
        ("execution", "Critical"),
        ("secrets", "Critical"),
        ("gate-bypass", "High"),
        ("tampering", "High"),
        ("disclosure", "High"),
        ("limited", "Medium"),
        ("leak", "Low"),
    ],
)
def test_st_0391_the_effect_class_sets_the_starting_level(effect, start):
    assert lint.bug_bar_level(_bar(effect)) == start


@pytest.mark.spec("FC-04-CT-01")
@pytest.mark.parametrize(
    ("effect", "yes_count", "level"),
    [
        ("secrets", 0, "Critical"),
        ("gate-bypass", 1, "Medium"),
        ("limited", 1, "Low"),
        ("leak", 2, "Low"),
        ("secrets", 4, "Low"),
        ("leak", 1, "Low"),
        ("execution", 1, "High"),
        ("execution", 3, "Low"),
    ],
)
def test_st_0391_each_yes_to_a_precondition_lowers_the_level_one_step(
    effect, yes_count, level
):
    assert lint.bug_bar_level(_bar(effect, yes_count)) == level


@pytest.mark.spec("FC-04-CT-01")
@pytest.mark.parametrize(
    "flag", ["second_breach", "trusted_access", "non_default", "user_action"]
)
def test_st_0391_each_precondition_counts_on_its_own(flag):
    basis = _bar("execution")
    basis[flag] = True
    assert lint.bug_bar_level(basis) == "High"


@pytest.mark.spec("FC-04-CT-01")
def test_st_0391_sec_0003_lands_at_high_and_major():
    basis = _bar("execution", yes_count=1, confidence="proven", in_use=True)
    assert lint.bug_bar_level(basis) == "High"
    assert lint.bug_bar_severity(basis) == "major"


@pytest.mark.spec("FC-04-CT-01")
def test_st_0391_a_hardening_finding_has_no_level_and_severity_note():
    basis = _bar("hardening")
    assert lint.bug_bar_level(basis) is None
    assert lint.bug_bar_severity(basis) == "note"


@pytest.mark.spec("FC-04-CT-02")
@pytest.mark.parametrize(
    ("effect", "yes_count", "in_use", "confidence", "severity"),
    [
        ("secrets", 0, True, "proven", "critical"),
        ("secrets", 0, True, "plausible", "major"),
        ("secrets", 0, False, "proven", "major"),
        ("gate-bypass", 0, True, "proven", "major"),
        ("limited", 0, False, "plausible", "major"),
        ("leak", 0, True, "proven", "minor"),
    ],
    ids=[
        "critical",
        "critical-plausible",
        "critical-not-in-use",
        "high",
        "medium",
        "low",
    ],
)
def test_st_0391_the_level_maps_onto_the_shared_scale(
    effect, yes_count, in_use, confidence, severity
):
    basis = _bar(effect, yes_count, confidence=confidence, in_use=in_use)
    assert lint.bug_bar_severity(basis) == severity


@pytest.mark.spec("FC-05-CT-01")
@pytest.mark.parametrize(
    ("importance", "exposure", "severity"),
    [
        ("high", "fails", "major"),
        ("high", "uncertain", "major"),
        ("medium", "fails", "major"),
        ("medium", "uncertain", "minor"),
        ("low", "fails", "minor"),
        ("low", "uncertain", "note"),
    ],
)
def test_st_0391_importance_and_exposure_set_the_matrix_severity(
    importance, exposure, severity
):
    assert lint.matrix_severity(_matrix(importance, exposure), "risk") == severity


@pytest.mark.spec("FC-05-CT-01")
@pytest.mark.parametrize(
    ("importance", "exposure", "severity"),
    [
        ("high", "fails", "critical"),
        ("high", "uncertain", "critical"),
        ("medium", "fails", "critical"),
        ("medium", "uncertain", "minor"),
        ("low", "fails", "minor"),
        ("low", "uncertain", "note"),
    ],
)
def test_st_0391_in_use_raises_only_major_to_critical(importance, exposure, severity):
    assert (
        lint.matrix_severity(_matrix(importance, exposure, in_use=True), "risk")
        == severity
    )


@pytest.mark.spec("FC-05-CT-01")
@pytest.mark.parametrize(
    "type_name", ["non-risk", "sensitivity-point", "tradeoff-point"]
)
def test_st_0391_non_risks_sensitivity_and_tradeoff_points_are_notes(type_name):
    assert (
        lint.matrix_severity(_matrix("high", "fails", in_use=True), type_name) == "note"
    )


@pytest.mark.spec("FC-02-CT-01")
def test_st_0391_an_architecture_suggestion_is_at_most_minor():
    severity = lint.computed_severity(
        "architecture", "suggestion", "risk", _matrix("high", "fails")
    )
    assert severity == "minor"


@pytest.mark.spec("FC-02-CT-01")
def test_st_0391_a_security_suggestion_is_at_most_minor():
    severity = lint.computed_severity(
        "security", "suggestion", "A06", _bar("execution", 0, "proven", True)
    )
    assert severity == "minor"


@pytest.mark.spec("FC-02-CT-01")
def test_st_0391_the_cap_keeps_a_note_a_note():
    severity = lint.computed_severity(
        "architecture", "suggestion", "risk", _matrix("low", "uncertain")
    )
    assert severity == "note"


@pytest.mark.spec("FC-02-CT-01")
def test_st_0391_the_cap_applies_only_to_suggestions():
    assert (
        lint.computed_severity("architecture", "risk", "risk", _matrix("high", "fails"))
        == "major"
    )
    assert (
        lint.computed_severity("security", "defect", "A06", _bar("execution"))
        == "critical"
    )


# --- Finding files ------------------------------------------------------------

SCHEMAS = lint.load_schemas(lint.FACTORY_ROOT)

DAMAGE = (
    "## Possible damage\n\n"
    "- merges on `dev` from dispatch runs since the installed copy was last updated"
    " — check: compare `git log --merges dev` with the merges the dispatch log records\n"
)
WHY = "**Why this severity:** The lines exist only on the feature branch, and the gate fails its purpose."
BASIS_OF_CLASS = {
    "document": _tree(False, False, True, False),
    "code": _tree(False, False, True, False),
    "runtime": _tree(False, False, True, False),
    "security": _bar("execution", 1, "proven", True),
    "architecture": _matrix("high", "fails"),
}
TYPE_OF_CLASS = {
    "document": "incomplete",
    "code": "function",
    "runtime": "wrong-result",
    "security": "A06",
    "architecture": "risk",
}


def _yaml_value(value) -> str:
    if value is None:
        return ""
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, list):
        return "[" + ", ".join(_yaml_value(item) for item in value) + "]"
    return str(value)


def _finding_fields(review_class: str = "code", **overrides) -> dict:
    fields = {
        "id": "FAGAN-0042",
        "source": "fagan-review",
        "review_class": review_class,
        "category": "risk" if review_class == "architecture" else "defect",
        "type": TYPE_OF_CLASS[review_class],
        "severity": "major",
        "basis": dict(BASIS_OF_CLASS[review_class]),
        "rating": "High" if review_class == "security" else None,
        "override_by": None,
        "override_reason": None,
        "stop_confirmed_by": None,
        "stop_confirmed_reason": None,
        "artifact": "packages/factory/scripts/premerge-check:120",
        "status": "open",
        "owner": "developer-agent",
        "traces": ["ST-0351", "BR-086"],
    }
    fields.update(overrides)
    return fields


def _finding_text(fields: dict, why: str | None = WHY, damage: bool = False) -> str:
    lines = ["---"]
    for key, value in fields.items():
        if isinstance(value, dict):
            lines.append(f"{key}:")
            lines.extend(f"  {sub}: {_yaml_value(item)}" for sub, item in value.items())
        else:
            lines.append(f"{key}: {_yaml_value(value)}".rstrip())
    lines += [
        "---",
        "",
        "# A finding",
        "",
        "**What is wrong:** The gate passes an empty story.",
        "",
    ]
    if why is not None:
        lines += [why, ""]
    lines += ["**Fix:** Refuse an empty story.", ""]
    text = "\n".join(lines)
    if damage:
        text += "\n" + DAMAGE
    return text


def _critical_fields(**overrides) -> dict:
    fields = _finding_fields(
        "code",
        id="BUG-0037",
        severity="critical",
        basis=_tree(True, True, True, False),
        artifact="packages/factory/scripts/dispatch:1383-1390",
    )
    fields.update(overrides)
    return fields


def _check(
    fields: dict, path: str = "docs/findings/FAGAN-0042.md", **text_options
) -> list[str]:
    return lint.check_finding_file(path, _finding_text(fields, **text_options), SCHEMAS)


def _assert_rule(messages: list[str], path: str, rule: str) -> None:
    assert any(
        message.startswith(f"{path}: ") and rule in message for message in messages
    ), messages


@pytest.mark.spec("FC-10-CT-02")
def test_st_0391_a_major_code_finding_from_the_template_passes():
    assert _check(_finding_fields()) == []


@pytest.mark.spec("FC-10-CT-02")
def test_st_0391_a_critical_finding_with_its_possible_damage_passes():
    assert (
        _check(_critical_fields(), path="docs/findings/BUG-0037.md", damage=True) == []
    )


@pytest.mark.spec("FC-06-CT-01")
@pytest.mark.parametrize("review_class", list(BASIS_OF_CLASS))
def test_st_0391_the_basis_has_the_shape_of_the_class(review_class):
    assert _check(_finding_fields(review_class)) == []


@pytest.mark.spec("FC-06-CT-01")
@pytest.mark.parametrize(
    ("review_class", "field"),
    [
        ("code", "fails_purpose"),
        ("document", "raises_cost"),
        ("security", "confidence"),
        ("architecture", "exposure"),
    ],
)
def test_st_0391_a_basis_without_a_field_of_its_class_fails(review_class, field):
    fields = _finding_fields(review_class)
    del fields["basis"][field]
    _assert_rule(_check(fields), "docs/findings/FAGAN-0042.md", "BR-080")


@pytest.mark.spec("FC-06-CT-01")
def test_st_0391_a_basis_of_another_class_fails():
    fields = _finding_fields("code", basis=_matrix("high", "fails"))
    _assert_rule(_check(fields), "docs/findings/FAGAN-0042.md", "BR-080")


@pytest.mark.spec("FC-06-CT-02")
@pytest.mark.parametrize(
    "artifact",
    [
        "packages/factory/scripts/premerge-check:120",
        "packages/factory/scripts/dispatch:120-134",
        "docs/spec/validation-rules.md#finding-classification-br-079br-095",
    ],
)
def test_st_0391_the_three_artifact_forms_pass(artifact):
    assert lint.artifact_is_valid(artifact)
    assert _check(_finding_fields(artifact=artifact)) == []


@pytest.mark.spec("FC-06-CT-02")
@pytest.mark.parametrize(
    "artifact",
    [
        "packages/factory/scripts/dispatch",
        "packages/factory/scripts/dispatch:134-120",
        "dispatch:",
        "dispatch#",
        "",
    ],
)
def test_st_0391_an_artifact_without_a_line_or_a_heading_fails(artifact):
    assert not lint.artifact_is_valid(artifact)
    _assert_rule(
        _check(_finding_fields(artifact=artifact)),
        "docs/findings/FAGAN-0042.md",
        "BR-086",
    )


@pytest.mark.spec("FC-10-CT-01")
@pytest.mark.parametrize(
    ("review_class", "severity"),
    [
        ("document", "minor"),
        ("code", "critical"),
        ("security", "critical"),
        ("architecture", "minor"),
        ("runtime", "minor"),
    ],
)
def test_st_0391_a_severity_mismatch_fails_in_every_review_class(
    review_class, severity
):
    messages = _check(
        _finding_fields(review_class, severity=severity, status="resolved")
    )
    rule = {"security": "BR-082", "architecture": "BR-083"}.get(review_class, "BR-081")
    _assert_rule(messages, "docs/findings/FAGAN-0042.md", rule)


@pytest.mark.spec("FC-10-CT-01")
def test_st_0391_a_code_finding_of_severity_minor_with_a_yes_to_fails_purpose_fails():
    messages = _check(_finding_fields(severity="minor", status="resolved"))
    _assert_rule(messages, "docs/findings/FAGAN-0042.md", "BR-081")
    assert any("major" in message for message in messages)


@pytest.mark.spec("FC-04-CT-02")
def test_st_0391_a_security_rating_that_differs_from_the_level_fails():
    messages = _check(_finding_fields("security", rating="Critical"))
    _assert_rule(messages, "docs/findings/FAGAN-0042.md", "BR-082")


@pytest.mark.spec("FC-04-CT-02")
def test_st_0391_a_rating_outside_the_security_class_fails():
    messages = _check(_finding_fields("code", rating="High"))
    _assert_rule(messages, "docs/findings/FAGAN-0042.md", "BR-082")


def _set(**values):
    return lambda fields, options: fields.update(values)


def _critical(**values):
    def change(fields, options):
        fields.update(_critical_fields(**values))
        options["damage"] = True

    return change


def _no_damage(fields, options):
    fields.update(_critical_fields())


def _damage(fields, options):
    options["damage"] = True


def _no_why(fields, options):
    options["why"] = None


MINOR_TREE = _tree(False, False, False, True)
NOTE_TREE = _tree(False, False, False, False)

# The rows of the structural Outline of FC-10, except rows 3 and 22, which
# FC-06-CT-01 and FC-06-CT-02 own, and row 17, which needs two files.
STRUCTURAL_ROWS = [
    ("type-outside-vocabulary", _set(type="crash"), "BR-079"),
    ("risk-in-code-class", _set(category="risk"), "BR-079"),
    ("unknown-review-class", _set(review_class="process"), "BR-079"),
    ("suggestion-of-severity-major", _set(category="suggestion"), "BR-084"),
    ("category-question", _set(category="question"), "BR-085"),
    ("no-why-line", _no_why, "BR-086"),
    (
        "waived-empty-override-reason",
        _set(status="waived", override_by="human", override_reason=" "),
        "BR-086",
    ),
    (
        "waived-no-override-by",
        _set(status="waived", override_reason="Accepted."),
        "BR-086",
    ),
    (
        "waived-minor",
        _set(
            status="waived",
            override_by="human",
            override_reason="Accepted.",
            severity="minor",
            basis=MINOR_TREE,
        ),
        "BR-086",
    ),
    (
        "waived-critical-unconfirmed",
        _critical(status="waived", override_by="human", override_reason="Kept."),
        "BR-086",
    ),
    ("resolved-critical-unconfirmed", _critical(status="resolved"), "BR-086"),
    (
        "resolved-critical-empty-reason",
        _critical(
            status="resolved", stop_confirmed_by="human", stop_confirmed_reason=""
        ),
        "BR-086",
    ),
    ("status-fixed", _set(status="fixed"), "BR-086"),
    ("status-open-capitalised", _set(status="Open"), "BR-086"),
    ("status-empty", _set(status=None), "BR-086"),
    ("deferred-with-review-class", _set(status="deferred"), "BR-086"),
    (
        "code-suggestion-fails-purpose",
        _set(category="suggestion", severity="minor"),
        "BR-084",
    ),
    (
        "code-suggestion-harms-downstream",
        _critical(category="suggestion", basis=_tree(True, True, False, False)),
        "BR-084",
    ),
    ("open-minor", _set(severity="minor", basis=MINOR_TREE), "BR-086"),
    ("open-note", _set(severity="note", basis=NOTE_TREE), "BR-086"),
    ("critical-without-possible-damage", _no_damage, "BR-086"),
    ("major-with-possible-damage", _damage, "BR-086"),
    (
        "stop-confirmed-by-without-reason",
        _critical(stop_confirmed_by="human", stop_confirmed_reason=None),
        "BR-086",
    ),
    (
        "stop-confirmed-by-on-major",
        _set(stop_confirmed_by="human", stop_confirmed_reason="Checked."),
        "BR-086",
    ),
    (
        "harms-downstream-not-in-use",
        _critical(basis=_tree(False, True, True, False)),
        "BR-081",
    ),
]


@pytest.mark.spec("FC-10-CT-02")
@pytest.mark.parametrize(
    ("change", "rule"),
    [row[1:] for row in STRUCTURAL_ROWS],
    ids=[row[0] for row in STRUCTURAL_ROWS],
)
def test_st_0391_a_structural_rule_is_broken(change, rule):
    fields = _finding_fields()
    options: dict = {}
    change(fields, options)
    _assert_rule(_check(fields, **options), "docs/findings/FAGAN-0042.md", rule)


@pytest.mark.spec("FC-10-CT-02")
@pytest.mark.parametrize(
    ("damage", "rule_text"),
    [
        ("## Possible damage\n\n", "item"),
        ("## Possible damage\n\n- merges on `dev` from dispatch runs\n", "check"),
        ("## Possible damage\n\n- — check: run `git log`\n", "check"),
    ],
    ids=["no-item", "item-without-check", "check-without-thing"],
)
def test_st_0391_each_possible_damage_item_needs_a_thing_and_a_check(damage, rule_text):
    text = _finding_text(_critical_fields()) + "\n" + damage
    messages = lint.check_finding_file("docs/findings/BUG-0037.md", text, SCHEMAS)
    _assert_rule(messages, "docs/findings/BUG-0037.md", "BR-086")
    assert any(rule_text in message for message in messages)


@pytest.mark.spec("FC-10-CT-02")
@pytest.mark.parametrize(
    "fields",
    [
        _critical_fields(
            status="waived",
            override_by="human",
            override_reason="Kept.",
            stop_confirmed_by="human",
            stop_confirmed_reason="Checked the merges.",
        ),
        _critical_fields(
            status="resolved",
            stop_confirmed_by="human",
            stop_confirmed_reason="Checked the merges.",
        ),
        _finding_fields(
            status="waived", override_by="human", override_reason="Nobody will fix it."
        ),
        _finding_fields(status="resolved"),
    ],
    ids=[
        "waived-critical-confirmed",
        "resolved-critical-confirmed",
        "waived-major",
        "resolved-major",
    ],
)
def test_st_0391_a_set_aside_or_fixed_finding_with_its_fields_passes(fields):
    damage = fields["severity"] == "critical"
    assert _check(fields, damage=damage) == []


@pytest.mark.spec("FC-04-CT-01")
def test_st_0391_a_security_hardening_finding_is_a_suggestion():
    fields = _finding_fields(
        "security",
        category="defect",
        severity="note",
        basis=_bar("hardening"),
        rating=None,
        status="resolved",
    )
    _assert_rule(_check(fields), "docs/findings/FAGAN-0042.md", "BR-082")
    fields["category"] = "suggestion"
    assert _check(fields) == []


@pytest.mark.spec("FC-10-CT-05")
def test_st_0391_a_file_without_review_class_is_skipped():
    text = "---\nid: OLD-0001\nseverity: Major\nstatus: open\n---\n\n# An old finding\n"
    assert lint.check_finding_file("docs/findings/OLD-0001.md", text, SCHEMAS) == []
    assert not lint.carries_review_class(text)
    assert (
        lint.check_finding_file("docs/findings/README.md", "# Findings\n", SCHEMAS)
        == []
    )


@pytest.mark.spec("FC-10-CT-05")
@pytest.mark.parametrize("status", ["open", "resolved", "waived", "deferred"])
def test_st_0391_every_file_with_review_class_is_checked_whatever_its_status(status):
    fields = _finding_fields(status=status, type="crash")
    _assert_rule(_check(fields), "docs/findings/FAGAN-0042.md", "BR-079")


@pytest.mark.spec("FC-10-CT-02")
def test_st_0391_a_frontmatter_that_cannot_be_read_fails():
    text = "---\nreview_class: code\nbasis:\n  in_use: [unclosed\n---\n"
    messages = lint.check_finding_file("docs/findings/FAGAN-0042.md", text, SCHEMAS)
    _assert_rule(messages, "docs/findings/FAGAN-0042.md", "frontmatter")


@pytest.mark.spec("FC-10-CT-02")
def test_st_0391_the_frontmatter_parser_reads_the_values_of_a_real_finding():
    text = (
        "---\nid: SEC-0007\nreview_class: security   # the class\nbasis:\n  effect: secrets\n"
        "  in_use: false\nrating: Medium\noverride_by:\nartifact: docs/a.md#a-heading\n"
        'traces: [ST-0368, "counter-ids.feature#User sees a failed ID claim, stop"]\n---\nbody\n'
    )
    meta, body = lint.parse_finding(text)
    assert meta == {
        "id": "SEC-0007",
        "review_class": "security",
        "basis": {"effect": "secrets", "in_use": False},
        "rating": "Medium",
        "override_by": None,
        "artifact": "docs/a.md#a-heading",
        "traces": ["ST-0368", "counter-ids.feature#User sees a failed ID claim, stop"],
    }
    assert body == "body\n"


# --- Register files -----------------------------------------------------------

REGISTER_BASIS = {
    "document": _tree(False, False, False, True),
    "code": _tree(True, False, False, True),
    "runtime": _tree(False, False, False, True),
    "security": _bar("leak", 0, "proven", True),
    "architecture": _matrix("medium", "uncertain"),
}
REGISTER_WHY = {
    "document": "A reader can still act on the rule (no to fails_purpose).",
    "code": "The gate still works, so the code serves its purpose (no to fails_purpose).",
    "runtime": "The command still prints the right result (no to fails_purpose).",
    "security": "The effect is a leak, which starts at Low, and no precondition holds.",
    "architecture": "QS-9 has priority 2, so the importance is medium, and the exposure is uncertain.",
}


def _register(review_class: str = "code", **overrides) -> dict:
    data = {
        "id": "FAGAN-0032",
        "source": "fagan-review",
        "review_class": review_class,
        "category": "suggestion" if review_class == "architecture" else "defect",
        "type": TYPE_OF_CLASS[review_class],
        "severity": "minor",
        "artifact": "packages/factory/scripts/dispatch:120",
        "story": "ST-0370",
        "finding": "The function repeats a rule; move it into one helper.",
        "basis": dict(REGISTER_BASIS[review_class]),
        "why_this_severity": REGISTER_WHY[review_class],
        "commit": "d0a78a5c40327c1f7e4c9a204ab5e766a7e0c44b",
        "status": "open",
    }
    data.update(overrides)
    return data


def _register_path(review_class: str = "code", name: str = "FAGAN-0032") -> str:
    return f"docs/findings/register/{review_class}/{name}.json"


@pytest.mark.spec("FC-10-CT-08")
@pytest.mark.parametrize("review_class", list(REGISTER_BASIS))
def test_st_0391_a_register_file_of_each_class_passes(review_class):
    assert (
        lint.check_register_file(
            _register_path(review_class), _register(review_class), SCHEMAS
        )
        == []
    )


@pytest.mark.spec("FC-10-CT-03")
@pytest.mark.parametrize("review_class", ["document", "code", "runtime"])
@pytest.mark.parametrize(
    "why", ["The gate still works.", "The gate still works (No to fails_purpose)."]
)
def test_st_0391_a_minor_tree_register_file_needs_its_fails_purpose_marker(
    review_class, why
):
    path = _register_path(review_class)
    messages = lint.check_register_file(
        path, _register(review_class, why_this_severity=why), SCHEMAS
    )
    _assert_rule(messages, path, "BR-087")


@pytest.mark.spec("FC-10-CT-03")
@pytest.mark.parametrize("review_class", ["security", "architecture"])
def test_st_0391_a_minor_security_or_architecture_register_file_needs_no_marker(
    review_class,
):
    data = _register(review_class)
    assert lint.MARKER not in data["why_this_severity"]
    assert lint.check_register_file(_register_path(review_class), data, SCHEMAS) == []


@pytest.mark.spec("FC-10-CT-04")
def test_st_0391_a_register_file_whose_severity_does_not_match_its_basis_fails():
    path = _register_path("document", "SPEC-0061")
    data = _register("document", id="SPEC-0061", basis=_tree(False, False, True, False))
    _assert_rule(lint.check_register_file(path, data, SCHEMAS), path, "BR-081")


@pytest.mark.spec("FC-10-CT-04")
@pytest.mark.parametrize(
    ("review_class", "change", "rule"),
    [
        ("security", {"basis": _bar("gate-bypass", 0)}, "BR-082"),
        (
            "architecture",
            {"category": "risk", "basis": _matrix("high", "fails")},
            "BR-083",
        ),
        ("code", {"basis": _tree(False, False, False, False)}, "BR-081"),
    ],
    ids=["security-major", "architecture-major", "code-note"],
)
def test_st_0391_a_register_severity_mismatch_fails_in_other_classes(
    review_class, change, rule
):
    path = _register_path(review_class)
    _assert_rule(
        lint.check_register_file(path, _register(review_class, **change), SCHEMAS),
        path,
        rule,
    )


@pytest.mark.spec("FC-10-CT-08")
@pytest.mark.parametrize(
    ("change", "rule"),
    [
        ({"status": "waived", "override_reason": "Accepted as is."}, "BR-110"),
        (
            {"status": "waived", "override_by": "human", "override_reason": "  "},
            "BR-110",
        ),
        (
            {
                "status": "waived",
                "override_by": "",
                "override_reason": "Accepted as is.",
            },
            "BR-110",
        ),
        ({"review_class": "document", "type": "incomplete"}, "BR-090"),
        ({"id": "FAGAN-0033"}, "BR-090"),
    ],
    ids=[
        "waived-no-override-by",
        "waived-blank-override-reason",
        "waived-empty-override-by",
        "class-of-another-folder",
        "id-not-file-name",
    ],
)
def test_st_0391_a_register_file_breaks_a_rule_of_the_register(change, rule):
    path = _register_path()
    _assert_rule(
        lint.check_register_file(path, _register(**change), SCHEMAS), path, rule
    )


@pytest.mark.spec("FC-10-CT-08")
def test_st_0391_the_stakeholder_waives_a_register_file_that_nobody_will_fix():
    data = _register(
        status="waived", override_by="human", override_reason="Accepted as is."
    )
    assert lint.check_register_file(_register_path(), data, SCHEMAS) == []


@pytest.mark.spec("FC-10-CT-08")
@pytest.mark.parametrize(
    "path",
    [
        "docs/findings/register/FAGAN-0032.json",
        "docs/findings/register/process/FAGAN-0032.json",
        "docs/findings/register/code/old/FAGAN-0032.json",
    ],
    ids=["no-class-folder", "unknown-class-folder", "nested-folder"],
)
def test_st_0391_a_register_file_outside_a_class_folder_fails(path):
    _assert_rule(lint.check_register_file(path, _register(), SCHEMAS), path, "BR-090")


@pytest.mark.spec("FC-10-CT-08")
@pytest.mark.parametrize(
    ("change", "rule"),
    [
        ({"category": "risk"}, "BR-079"),
        ({"type": "crash"}, "BR-079"),
        ({"artifact": "packages/factory/scripts/dispatch"}, "BR-086"),
        ({"basis": _tree(False, True, False, True)}, "BR-081"),
    ],
    ids=["risk-in-code", "type-outside-vocabulary", "bare-path", "harms-not-in-use"],
)
def test_st_0391_a_register_file_shares_the_rules_of_a_finding(change, rule):
    path = _register_path()
    _assert_rule(
        lint.check_register_file(path, _register(**change), SCHEMAS), path, rule
    )


@pytest.mark.spec("FC-10-CT-08")
def test_st_0391_a_register_file_that_is_no_object_fails():
    path = _register_path()
    _assert_rule(
        lint.check_register_file(path, ["not", "an", "object"], SCHEMAS), path, "BR-090"
    )


# --- The whole set of findings ------------------------------------------------

LINT = lint.FACTORY_ROOT / "scripts" / "finding-lint"


def _write(root, relative: str, content) -> None:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if not isinstance(content, str):
        content = json.dumps(content, indent=2)
    target.write_text(content, encoding="utf-8")


def _clean_set(root) -> None:
    """Write the Demo Data of ST-0391 under *root*."""
    _write(root, "docs/findings/FAGAN-0042.md", _finding_text(_finding_fields()))
    _write(
        root,
        "docs/findings/BUG-0037.md",
        _finding_text(_critical_fields(), damage=True),
    )
    _write(root, "docs/findings/register/code/FAGAN-0032.json", _register())
    _write(root, "docs/findings/register/architecture.jsonl", '{"id": "ATAM-0001"}\n')


def _run(root, *args):
    return subprocess.run(
        [sys.executable, str(LINT), *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.spec("FC-10-CT-02")
def test_st_0391_an_id_that_is_a_finding_file_and_a_register_file_fails(tmp_path):
    _write(
        tmp_path,
        "docs/findings/BUG-0067.md",
        _finding_text(_finding_fields(id="BUG-0067")),
    )
    _write(
        tmp_path, "docs/findings/register/code/BUG-0067.json", _register(id="BUG-0067")
    )
    _assert_rule(
        lint.lint_tree(tmp_path, SCHEMAS), "docs/findings/BUG-0067.md", "BR-090"
    )


@pytest.mark.spec("FC-10-CT-02")
def test_st_0391_an_id_that_names_two_register_files_fails(tmp_path):
    _write(tmp_path, "docs/findings/register/code/FAGAN-0032.json", _register())
    _write(
        tmp_path,
        "docs/findings/register/document/FAGAN-0032.json",
        _register("document"),
    )
    messages = lint.lint_tree(tmp_path, SCHEMAS)
    _assert_rule(messages, "docs/findings/register/code/FAGAN-0032.json", "BR-090")
    assert any(
        "docs/findings/register/document/FAGAN-0032.json" in message
        for message in messages
    )


@pytest.mark.spec("FC-10-CT-05")
def test_st_0391_an_old_finding_with_the_id_of_a_register_file_is_skipped(tmp_path):
    _write(
        tmp_path,
        "docs/findings/BUG-0067.md",
        "---\nid: BUG-0067\nseverity: Major\nstatus: resolved\n---\n",
    )
    _write(
        tmp_path, "docs/findings/register/code/BUG-0067.json", _register(id="BUG-0067")
    )
    assert lint.lint_tree(tmp_path, SCHEMAS) == []


@pytest.mark.spec("FC-10-CT-08")
def test_st_0391_a_register_file_that_is_no_json_fails(tmp_path):
    _write(tmp_path, "docs/findings/register/code/FAGAN-0032.json", "{not json")
    _assert_rule(
        lint.lint_tree(tmp_path, SCHEMAS),
        "docs/findings/register/code/FAGAN-0032.json",
        "BR-090",
    )


@pytest.mark.spec("FC-10-IT-01")
def test_st_0391_a_clean_set_of_findings_passes(tmp_path):
    _clean_set(tmp_path)
    _write(
        tmp_path,
        "docs/findings/OLD-0001.md",
        "---\nid: OLD-0001\nseverity: Major\nstatus: open\n---\n",
    )
    result = _run(tmp_path)
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


@pytest.mark.spec("FC-10-IT-01")
def test_st_0391_a_project_without_findings_passes(tmp_path):
    assert _run(tmp_path).returncode == 0


@pytest.mark.spec("FC-10-IT-01")
def test_st_0391_one_broken_file_gives_exit_1_and_one_line(tmp_path):
    _clean_set(tmp_path)
    _write(tmp_path, "docs/findings/BUG-0037.md", _finding_text(_critical_fields()))
    result = _run(tmp_path)
    assert result.returncode == 1
    lines = result.stdout.splitlines()
    assert len(lines) == 1, lines
    assert lines[0].startswith("docs/findings/BUG-0037.md: BR-086 possible damage: ")


@pytest.mark.spec("FC-10-IT-01")
@pytest.mark.parametrize("args", [["--bogus"], ["docs/findings/FAGAN-0042.md"]])
def test_st_0391_an_unknown_argument_is_a_usage_error(tmp_path, args):
    result = _run(tmp_path, *args)
    assert result.returncode == 2
    assert "usage: finding-lint" in result.stderr


@pytest.mark.spec("FC-10-IT-01")
def test_st_0391_the_demo_scenario_of_the_story(tmp_path):
    _clean_set(tmp_path)
    assert _run(tmp_path).returncode == 0

    fagan = tmp_path / "docs/findings/FAGAN-0042.md"
    fagan.write_text(
        fagan.read_text(encoding="utf-8").replace("severity: major", "severity: minor"),
        encoding="utf-8",
    )
    result = _run(tmp_path)
    assert result.returncode == 1
    assert "docs/findings/FAGAN-0042.md: BR-081 severity" in result.stdout
    _write(tmp_path, "docs/findings/FAGAN-0042.md", _finding_text(_finding_fields()))

    _write(tmp_path, "docs/findings/BUG-0037.md", _finding_text(_critical_fields()))
    result = _run(tmp_path)
    assert result.returncode == 1
    assert "docs/findings/BUG-0037.md: BR-086 possible damage" in result.stdout
    _write(
        tmp_path,
        "docs/findings/BUG-0037.md",
        _finding_text(_critical_fields(), damage=True),
    )

    _write(
        tmp_path,
        "docs/findings/register/code/FAGAN-0032.json",
        _register(why_this_severity="The gate works."),
    )
    result = _run(tmp_path)
    assert result.returncode == 1
    assert "docs/findings/register/code/FAGAN-0032.json: BR-087" in result.stdout
    _write(tmp_path, "docs/findings/register/code/FAGAN-0032.json", _register())

    _write(
        tmp_path,
        "docs/findings/OLD-0001.md",
        "---\nid: OLD-0001\nseverity: Major\nstatus: open\n---\n",
    )
    assert _run(tmp_path).returncode == 0


def _copy_factory(root):
    """Copy the lint, schema-validate, and the register schemas into a Factory root."""
    factory = root / "factory"
    (factory / "scripts").mkdir(parents=True)
    for name in ("finding-lint", "schema-validate"):
        shutil.copy(lint.FACTORY_ROOT / "scripts" / name, factory / "scripts" / name)
    shutil.copytree(
        lint.FACTORY_ROOT / "rulebooks" / "schemas", factory / "rulebooks" / "schemas"
    )
    return factory


@pytest.mark.spec("FC-07-IT-01")
def test_st_0391_the_lint_reads_the_schemas_under_the_factory_root_it_runs_from(
    tmp_path,
):
    factory = _copy_factory(tmp_path)
    project = tmp_path / "project"
    _clean_set(project)
    schema = factory / "rulebooks" / "schemas" / "finding-register-code.schema.json"
    data = json.loads(schema.read_text(encoding="utf-8"))
    data["properties"]["finding"]["type"] = "integer"
    schema.write_text(json.dumps(data), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(factory / "scripts" / "finding-lint")],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert (
        "docs/findings/register/code/FAGAN-0032.json: BR-090 schema-validate"
        in result.stdout
    )


@pytest.mark.spec("FC-07-IT-01")
@pytest.mark.parametrize(
    "missing",
    [
        "scripts/schema-validate",
        "rulebooks/schemas/finding-register-runtime.schema.json",
    ],
)
def test_st_0391_a_missing_schema_or_validator_exits_2(tmp_path, missing):
    factory = _copy_factory(tmp_path)
    (factory / missing).unlink()
    result = subprocess.run(
        [sys.executable, str(factory / "scripts" / "finding-lint")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert missing.rsplit("/", 1)[1] in result.stderr


# --- Lowering and removal against HEAD (ST-0392) ------------------------------

FAGAN_PATH = "docs/findings/FAGAN-0042.md"
BUG_PATH = "docs/findings/BUG-0037.md"
REGISTER_PATH = "docs/findings/register/code/FAGAN-0032.json"
OVERRIDE = {"override_by": "human", "override_reason": "The gate still works."}
CONFIRMED = {
    "stop_confirmed_by": "human",
    "stop_confirmed_reason": "No dispatch run merged since the copy was updated.",
}


def _major_bug(**overrides) -> dict:
    """BUG-0037 lowered to major: harms_downstream false, no confirmation fields."""
    fields = _critical_fields(basis=_tree(True, False, True, False), severity="major")
    fields.update(overrides)
    return fields


def _compare(files: dict, head: dict) -> list[str]:
    return lint.compare_with_head(
        {path: _as_text(content) for path, content in files.items()},
        {path: _as_text(content) for path, content in head.items()},
    )


def _as_text(content) -> str:
    if isinstance(content, str):
        return content
    return json.dumps(content, indent=2)


@pytest.mark.spec("FC-10-CT-06")
def test_st_0392_a_lowering_without_the_override_fields_fails():
    head = {FAGAN_PATH: _finding_text(_finding_fields())}
    files = {FAGAN_PATH: _finding_text(_finding_fields(severity="minor"))}
    messages = _compare(files, head)
    _assert_rule(messages, FAGAN_PATH, "BR-109 lowering")
    assert "FAGAN-0042" in messages[0].split(": ", 2)[2]


@pytest.mark.spec("FC-10-CT-06")
@pytest.mark.parametrize(
    "override",
    [
        {"override_by": "human"},
        {"override_reason": "Accepted."},
        {"override_by": "human", "override_reason": "  "},
    ],
    ids=["no-reason", "no-by", "blank-reason"],
)
def test_st_0392_a_lowering_with_one_override_field_fails(override):
    head = {BUG_PATH: _finding_text(_critical_fields(**CONFIRMED), damage=True)}
    files = {BUG_PATH: _finding_text(_major_bug(**override))}
    _assert_rule(_compare(files, head), BUG_PATH, "BR-109 lowering")


@pytest.mark.spec("FC-10-CT-06")
def test_st_0392_a_raise_needs_no_override_fields():
    head = {FAGAN_PATH: _finding_text(_finding_fields())}
    raised = _finding_fields(severity="critical", basis=_tree(True, True, True, False))
    files = {FAGAN_PATH: _finding_text(raised, damage=True)}
    assert _compare(files, head) == []


@pytest.mark.spec("FC-10-CT-06")
def test_st_0392_an_unchanged_severity_needs_no_override_fields():
    text = _finding_text(_finding_fields())
    assert _compare({FAGAN_PATH: text}, {FAGAN_PATH: text}) == []


@pytest.mark.spec("FC-10-CT-06")
def test_st_0392_the_stakeholder_lowers_a_confirmed_critical_finding():
    head = {BUG_PATH: _finding_text(_critical_fields(**CONFIRMED), damage=True)}
    files = {BUG_PATH: _finding_text(_major_bug(**OVERRIDE))}
    assert _compare(files, head) == []


@pytest.mark.spec("FC-10-CT-06")
@pytest.mark.parametrize(
    "head_fields",
    [{}, {"stop_confirmed_by": "human"}],
    ids=["unconfirmed", "no-reason"],
)
def test_st_0392_a_critical_finding_is_lowered_only_after_its_stop_is_confirmed_at_head(
    head_fields,
):
    head = {BUG_PATH: _finding_text(_critical_fields(**head_fields), damage=True)}
    files = {BUG_PATH: _finding_text(_major_bug(**OVERRIDE))}
    messages = _compare(files, head)
    _assert_rule(messages, BUG_PATH, "BR-109 lowering")
    assert any("BUG-0037" in message for message in messages)


@pytest.mark.spec("FC-10-CT-06")
def test_st_0392_a_lowering_cannot_confirm_the_stop_in_the_same_commit():
    head = {BUG_PATH: _finding_text(_critical_fields(), damage=True)}
    files = {BUG_PATH: _finding_text(_major_bug(**OVERRIDE, **CONFIRMED))}
    _assert_rule(_compare(files, head), BUG_PATH, "BR-109 lowering")


@pytest.mark.spec("FC-10-CT-06")
def test_st_0392_a_finding_lowered_to_major_drops_its_confirmation_fields():
    head = {BUG_PATH: _finding_text(_critical_fields(**CONFIRMED), damage=True)}
    files = {BUG_PATH: _finding_text(_major_bug(**OVERRIDE))}
    assert lint.lint_files(files, head, SCHEMAS) == []
    kept = {BUG_PATH: _finding_text(_major_bug(**OVERRIDE, **CONFIRMED))}
    _assert_rule(lint.lint_files(kept, head, SCHEMAS), BUG_PATH, "BR-086 confirmation")


@pytest.mark.spec("FC-10-CT-07")
def test_st_0392_a_removed_finding_file_without_a_register_file_fails():
    head = {FAGAN_PATH: _finding_text(_finding_fields(status="resolved"))}
    messages = _compare({}, head)
    _assert_rule(messages, FAGAN_PATH, "BR-109 removal")
    assert "FAGAN-0042" in messages[0].split(": ", 2)[2]


@pytest.mark.spec("FC-10-CT-07")
def test_st_0392_the_stakeholder_moves_a_filed_finding_into_the_register():
    head = {FAGAN_PATH: _finding_text(_finding_fields())}
    files = {_register_path(name="FAGAN-0042"): _register(id="FAGAN-0042", **OVERRIDE)}
    assert _compare(files, head) == []


@pytest.mark.spec("FC-10-CT-07")
@pytest.mark.parametrize(
    "change",
    [
        {},
        {"override_by": "human"},
        {"override_by": "human", "override_reason": ""},
        {**OVERRIDE, "status": "resolved"},
    ],
    ids=["no-keys", "no-reason", "empty-reason", "resolved"],
)
def test_st_0392_an_agent_cannot_move_a_filed_finding_into_the_register(change):
    head = {FAGAN_PATH: _finding_text(_finding_fields())}
    files = {_register_path(name="FAGAN-0042"): _register(id="FAGAN-0042", **change)}
    _assert_rule(_compare(files, head), FAGAN_PATH, "BR-109 removal")


@pytest.mark.spec("FC-10-CT-07")
def test_st_0392_a_move_of_an_unconfirmed_critical_finding_fails():
    head = {BUG_PATH: _finding_text(_critical_fields(), damage=True)}
    files = {_register_path(name="BUG-0037"): _register(id="BUG-0037", **OVERRIDE)}
    _assert_rule(_compare(files, head), BUG_PATH, "BR-109 lowering")


@pytest.mark.spec("FC-10-CT-07")
@pytest.mark.parametrize(
    "line", ["", "review_class: document\n"], ids=["deleted", "changed"]
)
def test_st_0392_a_version_keeps_the_review_class_of_its_head_version(line):
    head = {BUG_PATH: _finding_text(_critical_fields(), damage=True)}
    changed = _finding_text(_critical_fields(status="resolved"), damage=True)
    files = {BUG_PATH: changed.replace("review_class: code\n", line)}
    messages = _compare(files, head)
    _assert_rule(messages, BUG_PATH, "BR-109 review class")
    assert any("BUG-0037" in message for message in messages)


@pytest.mark.spec("FC-10-CT-07")
def test_st_0392_a_file_that_drops_review_class_is_still_checked():
    head = {BUG_PATH: _finding_text(_critical_fields(), damage=True)}
    changed = _finding_text(_critical_fields(status="resolved"), damage=True)
    files = {BUG_PATH: changed.replace("review_class: code\n", "")}
    messages = lint.lint_files(files, head, SCHEMAS)
    _assert_rule(messages, BUG_PATH, "BR-109 review class")
    _assert_rule(messages, BUG_PATH, "BR-086 confirmation")


@pytest.mark.spec("FC-10-CT-07")
def test_st_0392_the_migration_moves_a_file_without_review_class_into_the_register():
    head = {
        "docs/findings/BUG-0067.md": "---\nid: BUG-0067\nseverity: Minor\nstatus: open\n---\n"
    }
    files = {_register_path(name="BUG-0067"): _register(id="BUG-0067")}
    assert _compare(files, head) == []


@pytest.mark.spec("FC-10-CT-09")
def test_st_0392_a_removed_register_file_without_a_finding_file_fails():
    messages = _compare({}, {REGISTER_PATH: _register()})
    _assert_rule(messages, REGISTER_PATH, "BR-110 removal")
    assert "FAGAN-0032" in messages[0].split(": ", 2)[2]


@pytest.mark.spec("FC-10-CT-09")
def test_st_0392_a_register_file_raised_to_a_finding_file_passes():
    raised = _finding_fields(id="FAGAN-0032")
    files = {"docs/findings/FAGAN-0032.md": _finding_text(raised)}
    assert _compare(files, {REGISTER_PATH: _register()}) == []


@pytest.mark.spec("FC-10-CT-09")
def test_st_0392_a_finding_file_without_review_class_replaces_no_register_file():
    files = {"docs/findings/FAGAN-0032.md": "---\nid: FAGAN-0032\nstatus: open\n---\n"}
    _assert_rule(
        _compare(files, {REGISTER_PATH: _register()}), REGISTER_PATH, "BR-110 removal"
    )


@pytest.mark.spec("FC-10-CT-09")
def test_st_0392_a_register_file_that_stays_resolved_passes():
    head = {REGISTER_PATH: _register()}
    assert _compare({REGISTER_PATH: _register(status="resolved")}, head) == []


@pytest.mark.spec("FC-10-CT-09")
def test_st_0392_the_removal_of_an_old_jsonl_register_is_no_removal():
    head = {"docs/findings/register/code.jsonl": '{"id": "FAGAN-0032"}\n'}
    assert _compare({}, head) == []


def _git_env(tmp_path) -> dict:
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    env.update(HOME=str(home), GIT_CONFIG_NOSYSTEM="1")
    return env


def _git(root, env, *args) -> None:
    subprocess.run(["git", *args], cwd=root, env=env, check=True, capture_output=True)


def _repo(tmp_path):
    """Return a git repository in tmp_path with the test setup of the QA strategy."""
    root = tmp_path / "repo"
    root.mkdir()
    env = _git_env(tmp_path)
    _git(root, env, "init", "-b", "main")
    _git(root, env, "config", "user.name", "Test")
    _git(root, env, "config", "user.email", "test@example.com")
    _git(root, env, "config", "commit.gpgsign", "false")
    return root, env


def _commit(root, env, message: str = "commit") -> None:
    _git(root, env, "add", "-A")
    _git(root, env, "commit", "-m", message)


def _run_in(root, env, *args):
    return subprocess.run(
        [sys.executable, str(LINT), *args],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.spec("FC-15-IT-01")
def test_st_0392_the_stakeholder_raises_fagan_0032_to_a_finding_file(tmp_path):
    root, env = _repo(tmp_path)
    _clean_set(root)
    _commit(root, env)
    _write(
        root,
        "docs/findings/FAGAN-0032.md",
        _finding_text(_finding_fields(id="FAGAN-0032")),
    )
    result = _run_in(root, env)
    assert result.returncode == 1
    assert "BR-090 one ID" in result.stdout
    (root / REGISTER_PATH).unlink()
    result = _run_in(root, env)
    assert (result.returncode, result.stdout) == (0, "")
