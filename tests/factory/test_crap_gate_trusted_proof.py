"""Integration tests: what gate-setup-proof copies and passes to crap-score (ST-0450).

docs/spec/features/crap-gate-setup.feature, Rule "Test-strategy agent checks
with gate-setup-proof that the measuring command reports true coverage", the
Scenarios that cite DEC-71 and DEC-73. The proof checks values that the User
has not committed, so it calls crap-score with --settings-from-folder, and the
register still comes from the integration branch (BR-138, DEC-71). Each test
builds its own repository in `tmp_path` with the fixture of
test_crap_gate_proof.py and commits the trusted values on `dev` or `main`.
"""

from __future__ import annotations

import pytest
from test_crap_gate_proof import CHECKS, PLANT_FILE, STUB, Repo, check_lines, settings_yaml
from test_crap_gate_trusted_source import commit_on, register

REGISTER = "docs/findings/exceptions.md"
FACTORY_SETTINGS = "docs/factory-settings.yaml"
STUB_LOG_LINE = '        "stub": git("show", "HEAD:scripts/crap-measure-python"),\n'
BACKEND_STUB = "scripts/crap-measure-backend"


def stub(mode: str = "honest", complexity: int = 3) -> str:
    """The folder-aware stub; it also logs the entry of docs/factory-settings.yaml in its commit."""
    text = STUB.format(mode=mode)
    assert text.count(STUB_LOG_LINE) == 1
    text = text.replace(
        STUB_LOG_LINE, STUB_LOG_LINE + f'        "factory_settings": git("ls-tree", "HEAD", "{FACTORY_SETTINGS}"),\n'
    )
    planted = '{"proof_untested": 3, "proof_tested": 3}'
    assert text.count(planted) == 1
    return text.replace(planted, f'{{"proof_untested": {complexity}, "proof_tested": {complexity}}}')


def accepted_untested(score: int) -> str:
    return register((PLANT_FILE, "proof_untested", str(score)))


# --- CG-02-IT-12: docs/factory-settings.yaml in the first commit -----------


@pytest.mark.spec("CG-02-IT-12")
def test_cg_02_the_first_commit_holds_factory_settings_of_the_working_tree_byte_for_byte(tmp_path):
    """Scenario: The first commit of the proof holds docs/factory-settings.yaml of the working tree."""
    repo = Repo(tmp_path)
    repo.stub(stub())
    text = "# uncommitted\nintegration_branch: main\nrelease_tag_patterns: ['v*']\n"
    repo.write(FACTORY_SETTINGS, text)
    blob = repo.git("hash-object", FACTORY_SETTINGS)

    result = repo.proof()

    assert result.returncode == 0, result.stdout + result.stderr
    first = repo.starts()[0]
    mode, kind, oid, path = first["factory_settings"].split()
    assert (kind, oid, path) == ("blob", blob, FACTORY_SETTINGS)


@pytest.mark.spec("CG-02-IT-12")
def test_cg_02_without_factory_settings_in_the_working_tree_the_first_commit_holds_none(tmp_path):
    repo = Repo(tmp_path)
    repo.stub(stub())

    result = repo.proof()

    assert result.returncode == 0, result.stdout + result.stderr
    assert FACTORY_SETTINGS not in repo.starts()[0]["files"]


@pytest.mark.spec("CG-02-IT-12")
@pytest.mark.parametrize(("branch", "code"), [("main", 1), ("dev", 0)])
def test_cg_02_crap_score_in_the_proof_reads_the_register_of_the_named_branch(tmp_path, branch, code):
    """DEC-73: the copy lets crap-score in the proof worktree read refs/heads/main."""
    repo = Repo(tmp_path)
    repo.stub(stub())
    repo.write(FACTORY_SETTINGS, "integration_branch: main\n")
    commit_on(repo, branch, {REGISTER: accepted_untested(12)})

    result = repo.proof()

    assert result.returncode == code, result.stdout + result.stderr
    expected = dict.fromkeys(CHECKS, "PASS")
    if code == 1:
        expected["Catches CRAP"] = "FAIL"
    assert check_lines(result.stdout) == expected


# --- CG-02-IT-13: the proof skips the check for a dropped measure ----------


@pytest.mark.spec("CG-02-IT-13")
def test_cg_02_the_proof_passes_when_dev_also_lists_another_measure(tmp_path):
    """Scenario: The proof skips the check for a measure that the first commit drops (DEC-70, DEC-73)."""
    repo = Repo(tmp_path)
    repo.stub(stub())
    both = settings_yaml() + (
        "      - name: backend\n        files: \"backend/**\"\n"
        f"        command: \"{BACKEND_STUB}\"\n"
    )
    commit_on(repo, "dev", {"docs/testing.yaml": both})
    repo.write("docs/testing.yaml", both)
    backend_log = tmp_path / "backend.log"
    repo.write(BACKEND_STUB, f'#!/bin/sh\necho started >> "{backend_log}"\necho "[]" > "$GATE_OUTPUT"\n')
    (repo.root / BACKEND_STUB).chmod(0o755)

    result = repo.proof()

    assert result.returncode == 0, result.stdout + result.stderr
    assert check_lines(result.stdout) == dict.fromkeys(CHECKS, "PASS")
    assert "name: backend" not in repo.starts()[0]["testing_yaml"]
    assert not backend_log.exists()


# --- CG-02-IT-14: the uncommitted threshold judges -------------------------


@pytest.mark.spec("CG-02-IT-14")
def test_cg_02_the_proof_judges_with_the_uncommitted_threshold(tmp_path):
    """Scenario: The proof after a changed threshold reads the threshold of the working tree.

    Both planted functions have the complexity 9, so proof_tested scores 9 at
    full coverage: it passes the threshold 10 of the working tree and would
    fail the threshold 8 of dev in "Sees the folder".
    """
    repo = Repo(tmp_path)
    repo.stub(stub(complexity=9))
    commit_on(repo, "dev", {"docs/testing.yaml": settings_yaml(8)})
    repo.write("docs/testing.yaml", settings_yaml(10))

    result = repo.proof()

    assert result.returncode == 0, result.stdout + result.stderr
    assert check_lines(result.stdout) == dict.fromkeys(CHECKS, "PASS")


@pytest.mark.spec("CG-02-IT-14")
def test_cg_02_the_proof_still_reads_the_register_from_dev(tmp_path):
    """DEC-71: --settings-from-folder does not change where the register comes from."""
    repo = Repo(tmp_path)
    repo.stub(stub(complexity=9))
    commit_on(repo, "dev", {"docs/testing.yaml": settings_yaml(8), REGISTER: accepted_untested(90)})
    repo.write("docs/testing.yaml", settings_yaml(10))

    result = repo.proof()

    assert result.returncode == 1, result.stdout + result.stderr
    assert check_lines(result.stdout) == {**dict.fromkeys(CHECKS, "PASS"), "Catches CRAP": "FAIL"}
