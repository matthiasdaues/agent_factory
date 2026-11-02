"""Tests for migrate-spec-layout, the move into the core artifact layout.

Covers CAL-01 and CAL-03 of docs/spec/core-artifact-layout-qa-strategy.md.
Every test builds its project at test time with ``make_project``. Later
stories extend ``OLD_LAYOUT_PAYMENTS`` and ``NEW_LAYOUT_PAYMENTS`` or pass
their own file maps.
"""

from __future__ import annotations

import ast
import os
import subprocess
from pathlib import Path

import pytest
from conftest import SOURCE_SCRIPTS_DIR, load_script, requires_docker

SCRIPT = SOURCE_SCRIPTS_DIR / "migrate-spec-layout"
STRUCTURIZR_IMAGE = os.environ.get(
    "STRUCTURIZR_IMAGE", "structurizr/structurizr:2026.05.22-playwright"
)

THEME_JSON = '{\n  "name": "default",\n  "elements": []\n}\n'

ARCHITECTURE_DSL = """workspace "Payments" {
    model {
        user = person "User"
        payments = softwareSystem "Payments"
        user -> payments "Pays"
    }
    views {
        systemContext payments "Context" {
            include *
        }
        theme themes/default/theme.json
    }
}
"""

DEPENDENCY_RULES_DSL = "# dependency rules\n"

# Path table: old path -> new path, one row per row of the Scenario Outline
# "A file of the path table moves with git", plus the theme.
PATH_TABLE_ROWS: dict[str, str] = {
    "docs/spec/payments.feature": "docs/spec/features/payments.feature",
    "docs/spec/supplementary_specs/entity-model.md": "docs/spec/entity-model.md",
    "docs/spec/supplementary_specs/state-machines.md": "docs/spec/state-machines.md",
    "docs/spec/supplementary_specs/validation-rules.md": "docs/spec/validation-rules.md",
    "docs/spec/supplementary_specs/interface-contracts.md": "docs/spec/interface-contracts.md",
    "docs/arc42/architecture.dsl": "docs/spec/architecture.dsl",
    "docs/arc42/dependency-rules.dsl": "docs/spec/dependency-rules.dsl",
    "docs/spec/prd.md": "docs/spec/work/prd.md",
    "docs/spec/payments-gaps.md": "docs/spec/work/payments-gaps.md",
    "docs/spec/payments-qa-strategy.md": "docs/spec/work/payments-qa-strategy.md",
    "docs/spec/SPEC-UPDATE-SUMMARY.md": "docs/spec/work/SPEC-UPDATE-SUMMARY.md",
    "docs/spec/todo.md": "docs/spec/work/todo.md",
    "docs/spec/todos.md": "docs/spec/work/todos.md",
    "docs/spec/supplementary_specs/billing.md": "docs/spec/areas/billing.md",
    "docs/spec/supplementary_specs/billing-qa-strategy.md": "docs/spec/work/billing-qa-strategy.md",
    "docs/arc42/themes/default/theme.json": "docs/assets/themes/default/theme.json",
}

# Files that stay where they are.
STAYING_FILES: dict[str, str] = {
    "docs/spec/scope-map.md": "# Scope map\n",
    "docs/testing.yaml": "suites: []\n",
    "docs/agent-context.md": "# Agent context\n",
    "docs/adr/0001-example.md": "# 1. Example\n",
}


def _content(path: str) -> str:
    if path.endswith("architecture.dsl"):
        return ARCHITECTURE_DSL
    if path.endswith("dependency-rules.dsl"):
        return DEPENDENCY_RULES_DSL
    if path.endswith("theme.json"):
        return THEME_JSON
    return f"# {Path(path).name}\n"


OLD_LAYOUT_PAYMENTS: dict[str, str] = {
    **{old: _content(old) for old in PATH_TABLE_ROWS},
    **STAYING_FILES,
}

NEW_LAYOUT_PAYMENTS: dict[str, str] = {
    **{new: _content(old) for old, new in PATH_TABLE_ROWS.items()},
    **STAYING_FILES,
    "docs/spec/architecture.dsl": ARCHITECTURE_DSL.replace(
        "theme themes/", "theme ../assets/themes/"
    ),
    "docs/arc42/12_glossary.md": (
        "# 12. Glossary\n\n"
        "The terms are in [the glossary](../spec/glossary.md).\n\n"
        "## Referenced from\n\n- [Scope map](../spec/scope-map.md)\n"
    ),
    "docs/spec/glossary.md": "# Glossary\n",
    "docs/arc42/CONTEXT-MAP.md": "# Context map\n\n- payments\n",
}


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout


def make_project(
    root: Path,
    files: dict[str, str] | None = None,
    *,
    uncommitted: dict[str, str] | None = None,
) -> Path:
    """Build a git repository at ``root``.

    ``files`` are written and committed (default: ``OLD_LAYOUT_PAYMENTS``).
    ``uncommitted`` are written after the commit and left untracked or, for
    paths that ``files`` holds, as unstaged changes.
    """
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "test@example.com")
    git(root, "config", "user.name", "Test")
    git(root, "config", "commit.gpgsign", "false")
    for rel, text in (OLD_LAYOUT_PAYMENTS if files is None else files).items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "fixture")
    for rel, text in (uncommitted or {}).items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def run_script(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(SCRIPT), *args, str(root)], capture_output=True, text=True, check=False
    )


def porcelain(root: Path) -> str:
    return git(root, "status", "--porcelain", "--untracked-files=all", "--ignored")


def renames(root: Path) -> dict[str, str]:
    """Map each renamed old path to its new path, from git's staged view."""
    out = git(root, "diff", "--cached", "--name-status", "-M", "HEAD")
    result: dict[str, str] = {}
    for line in out.splitlines():
        status, *paths = line.split("\t")
        if status.startswith("R"):
            result[paths[0]] = paths[1]
    return result


# ── CAL-03-CT-01: the path table ─────────────────────────────────────────


@pytest.fixture(scope="module")
def migrate():
    return load_script("migrate-spec-layout")


@pytest.mark.spec("CAL-03-CT-01")
@pytest.mark.parametrize(("old", "new"), sorted(PATH_TABLE_ROWS.items()))
def test_CAL_03_path_table_maps_old_path_to_new_path(migrate, old, new):
    assert migrate.new_path(old) == new


@pytest.mark.spec("CAL-03-CT-01")
@pytest.mark.parametrize(
    "path",
    [
        "docs/spec/scope-map.md",
        "docs/spec/features/payments.feature",
        "docs/spec/work/payments-gaps.md",
        "docs/spec/areas/billing.md",
        "docs/spec/entity-model.md",
        "docs/testing.yaml",
        "docs/arc42/01_introduction.md",
    ],
)
def test_CAL_03_path_table_maps_new_and_unlisted_paths_to_themselves(migrate, path):
    assert migrate.new_path(path) == path


# ── CAL-03: moves with git ───────────────────────────────────────────────


@pytest.fixture
def migrated(tmp_path: Path) -> tuple[Path, subprocess.CompletedProcess[str]]:
    root = make_project(tmp_path / "old-layout-payments")
    return root, run_script(root)


@pytest.mark.spec("CAL-03")
def test_CAL_03_every_path_table_row_moves_as_a_git_rename(migrated):
    root, result = migrated
    assert result.returncode == 0, result.stderr
    assert renames(root) == PATH_TABLE_ROWS
    for old, new in PATH_TABLE_ROWS.items():
        assert not (root / old).exists()
        assert (root / new).is_file()


@pytest.mark.spec("CAL-03")
def test_CAL_03_status_shows_renamed_and_the_run_lists_each_move(migrated):
    root, result = migrated
    status = git(root, "status")
    assert (
        "renamed:    docs/spec/payments.feature -> docs/spec/features/payments.feature"
        in status
    )
    for old, new in PATH_TABLE_ROWS.items():
        assert f"{old} -> {new}" in result.stdout


@pytest.mark.spec("CAL-03")
def test_CAL_03_theme_moves_and_the_dsl_theme_line_follows_it(migrated):
    root, _ = migrated
    dsl = (root / "docs/spec/architecture.dsl").read_text(encoding="utf-8")
    assert "        theme ../assets/themes/default/theme.json\n" in dsl
    assert "theme themes/" not in dsl
    assert (root / "docs/assets/themes/default/theme.json").read_text() == THEME_JSON
    assert not (root / "docs/arc42/themes").exists()


@pytest.mark.spec("CAL-01-IT-01")
def test_CAL_01_migrated_project_keeps_work_in_work_and_other_files_outside_spec(
    migrated,
):
    root, _ = migrated
    work = sorted(p.name for p in (root / "docs/spec/work").iterdir())
    assert work == sorted(
        [
            "prd.md",
            "payments-gaps.md",
            "payments-qa-strategy.md",
            "SPEC-UPDATE-SUMMARY.md",
            "todo.md",
            "todos.md",
            "billing-qa-strategy.md",
        ]
    )
    assert not (root / "docs/spec/schemas").exists()
    assert not (root / "docs/spec/supplementary_specs").exists()
    for rel in STAYING_FILES:
        assert (root / rel).is_file()
    assert (root / "docs/arc42").is_dir()


@pytest.mark.spec("CAL-03-IT-03")
def test_CAL_03_second_run_has_no_work(migrated):
    root, _ = migrated
    before = porcelain(root)
    again = run_script(root)
    assert (again.returncode, again.stdout, again.stderr) == (0, "", "")
    assert porcelain(root) == before


@pytest.mark.spec("CAL-03-IT-03")
def test_CAL_03_project_in_the_new_layout_gives_no_work(tmp_path: Path):
    root = make_project(tmp_path / "new-layout-payments", NEW_LAYOUT_PAYMENTS)
    result = run_script(root)
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")
    assert porcelain(root) == ""


# ── CAL-03-IT-05: files with uncommitted changes, untracked, ignored ─────


@pytest.mark.spec("CAL-03-IT-05")
def test_CAL_03_tracked_file_with_unstaged_change_moves_as_rename_with_change(
    tmp_path: Path,
):
    root = make_project(
        tmp_path / "p", uncommitted={"docs/spec/payments-gaps.md": "# changed\n"}
    )
    result = run_script(root)
    assert result.returncode == 0, result.stderr
    assert (
        renames(root)["docs/spec/payments-gaps.md"] == "docs/spec/work/payments-gaps.md"
    )
    assert (root / "docs/spec/work/payments-gaps.md").read_text() == "# changed\n"


@pytest.mark.spec("CAL-03-IT-05")
def test_CAL_03_tracked_file_with_staged_change_keeps_staged_change(tmp_path: Path):
    root = make_project(
        tmp_path / "p", uncommitted={"docs/spec/payments-gaps.md": "# staged\n"}
    )
    git(root, "add", "docs/spec/payments-gaps.md")
    result = run_script(root)
    assert result.returncode == 0, result.stderr
    assert git(root, "show", ":docs/spec/work/payments-gaps.md") == "# staged\n"


@pytest.mark.spec("CAL-03-IT-05")
@pytest.mark.parametrize("git_state", ["untracked", "ignored"])
def test_CAL_03_file_git_does_not_track_moves_with_plain_move(
    tmp_path: Path, git_state: str
):
    files = dict(OLD_LAYOUT_PAYMENTS)
    del files["docs/spec/payments-gaps.md"]
    if git_state == "ignored":
        files[".gitignore"] = "*-gaps.md\n"
    root = make_project(
        tmp_path / "p", files, uncommitted={"docs/spec/payments-gaps.md": "# local\n"}
    )
    result = run_script(root)
    assert result.returncode == 0, result.stderr
    assert (root / "docs/spec/work/payments-gaps.md").read_text() == "# local\n"
    assert not (root / "docs/spec/payments-gaps.md").exists()


# ── CAL-03: refusals before the first change ─────────────────────────────


def _diverge(root: Path) -> None:
    git(root, "checkout", "-q", "-b", "other")
    (root / "docs/spec/todo.md").write_text("# other\n")
    git(root, "commit", "-q", "-am", "other")
    git(root, "checkout", "-q", "main")
    (root / "docs/spec/todo.md").write_text("# main\n")
    git(root, "commit", "-q", "-am", "main")


def _start_merge(root: Path) -> None:
    _diverge(root)
    subprocess.run(["git", "-C", str(root), "merge", "other"], capture_output=True)


def _start_rebase(root: Path) -> None:
    _diverge(root)
    subprocess.run(["git", "-C", str(root), "rebase", "other"], capture_output=True)


def _lock_index(root: Path) -> None:
    (root / ".git/index.lock").write_text("")


@pytest.mark.spec("CAL-03")
@pytest.mark.parametrize(
    ("start", "named_state"),
    [
        (_start_merge, "merge"),
        (_start_rebase, "rebase"),
        (_lock_index, "index lock"),
    ],
)
def test_CAL_03_busy_repository_refuses_and_changes_no_file(
    tmp_path: Path, start, named_state: str
):
    root = make_project(tmp_path / "p")
    start(root)
    before = porcelain(root)
    files_before = sorted(p for p in root.rglob("*") if ".git" not in p.parts)
    result = run_script(root)
    assert result.returncode == 2
    assert named_state in result.stderr
    assert porcelain(root) == before
    assert sorted(p for p in root.rglob("*") if ".git" not in p.parts) == files_before


@pytest.mark.spec("CAL-03")
def test_CAL_03_existing_destination_refuses_before_the_first_change(tmp_path: Path):
    root = make_project(
        tmp_path / "p", uncommitted={"docs/spec/work/todo.md": "# already here\n"}
    )
    before = porcelain(root)
    result = run_script(root)
    assert result.returncode == 2
    assert "docs/spec/work/todo.md" in result.stderr
    assert porcelain(root) == before


# ── CAL-03-IT-04: a failure partway undoes every move ───────────────────


@pytest.mark.spec("CAL-03-IT-04")
@pytest.mark.skipif(os.geteuid() == 0, reason="root ignores folder permissions")
def test_CAL_03_failure_partway_undoes_every_move(tmp_path: Path):
    root = make_project(
        tmp_path / "p", uncommitted={"docs/spec/notes-gaps.md": "# untracked\n"}
    )
    work = root / "docs/spec/work"
    work.mkdir()
    work.chmod(0o555)
    before = porcelain(root)
    try:
        result = run_script(root)
    finally:
        work.chmod(0o755)
    assert result.returncode == 1
    assert "undone" in result.stderr
    assert porcelain(root) == before
    assert not (root / "docs/spec/features").exists()
    assert not (root / "docs/spec/entity-model.md").exists()
    assert (root / "docs/spec/notes-gaps.md").read_text() == "# untracked\n"
    assert (root / "docs/arc42/architecture.dsl").read_text() == ARCHITECTURE_DSL
    assert (root / "docs/arc42/themes/default/theme.json").read_text() == THEME_JSON


# ── Dry run and project directory argument ──────────────────────────────


@pytest.mark.spec("CAL-03")
def test_CAL_03_dry_run_prints_each_move_and_changes_no_file(tmp_path: Path):
    root = make_project(tmp_path / "p")
    result = run_script(root, "--dry-run")
    assert result.returncode == 0, result.stderr
    for old, new in PATH_TABLE_ROWS.items():
        assert f"{old} -> {new}" in result.stdout
    assert porcelain(root) == ""
    assert not (root / "docs/spec/features").exists()


@pytest.mark.spec("CAL-03")
def test_CAL_03_target_defaults_to_current_directory(tmp_path: Path):
    root = make_project(tmp_path / "p")
    result = subprocess.run(
        [str(SCRIPT)], cwd=root, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    assert (root / "docs/spec/features/payments.feature").is_file()


# ── CAL-03-IT-02: Structurizr accepts the moved DSL ─────────────────────


@pytest.mark.spec("CAL-03-IT-02")
@requires_docker
@pytest.mark.container
def test_CAL_03_structurizr_validate_accepts_the_migrated_dsl(migrated):
    root, _ = migrated
    docs = root / "docs"
    command = ["docker", "run", "--rm", "--user", f"{os.getuid()}:{os.getgid()}"]
    command += ["-v", f"{docs}:/workspace", STRUCTURIZR_IMAGE]
    command += ["validate", "-workspace", "/workspace/spec/architecture.dsl"]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ERROR" not in result.stdout + result.stderr


# ── CAL-03-IT-01 and CAL-03-IT-06: removals of the actor-goal list and ──
# ── the use-case files, also from the archive (ST-0319) ─────────────────

ARCHIVE_GOAL_LIST = "docs/~archive/spec/actor-goal-list.md"
ARCHIVE_USE_CASE = "docs/~archive/spec/use_cases/UC-04-dispatch-an-agent-via-trigger.md"
ARCHIVE_NOTES = "docs/~archive/spec/old-notes.md"
UC_07 = "docs/spec/use_cases/UC-07.md"
REMOVAL_SET = [ARCHIVE_GOAL_LIST, ARCHIVE_USE_CASE, UC_07]

OLD_LAYOUT_ARCHIVE: dict[str, str] = {
    **OLD_LAYOUT_PAYMENTS,
    ARCHIVE_GOAL_LIST: "# Actor-goal list\n",
    ARCHIVE_USE_CASE: "# UC-04 Dispatch an agent via trigger\n",
    ARCHIVE_NOTES: "# Old notes\n",
    UC_07: "# UC-07\n",
}


def _uc07_untracked(root: Path) -> None:
    git(root, "rm", "-q", "--cached", UC_07)
    git(root, "commit", "-q", "-m", "untrack UC-07")


def _uc07_ignored(root: Path) -> None:
    (root / ".gitignore").write_text("use_cases/UC-07.md\n")
    git(root, "rm", "-q", "--cached", UC_07)
    git(root, "add", ".gitignore")
    git(root, "commit", "-q", "-m", "ignore UC-07")


def _uc07_staged(root: Path) -> None:
    (root / UC_07).write_text("# UC-07 staged\n")
    git(root, "add", UC_07)


def _uc07_unstaged(root: Path) -> None:
    (root / UC_07).write_text("# UC-07 unstaged\n")


class TestRemovals:
    """The removal set: actor-goal-list.md and use_cases/ files under docs/."""

    @pytest.mark.spec("CAL-03-CT-01")
    @pytest.mark.parametrize(
        ("path", "removed"),
        [
            ("docs/spec/actor-goal-list.md", True),
            (ARCHIVE_GOAL_LIST, True),
            (ARCHIVE_USE_CASE, True),
            (UC_07, True),
            ("docs/spec/use_cases/nested/UC-08.md", True),
            (ARCHIVE_NOTES, False),
            ("docs/spec/scope-map.md", False),
            ("use_cases/UC-01.md", False),
            ("actor-goal-list.md", False),
        ],
    )
    def test_CAL_03_removal_set_holds_goal_list_and_use_case_files(
        self, migrate, path: str, removed: bool
    ):
        assert migrate.in_removal_set(path) is removed

    @pytest.mark.spec("CAL-03-IT-01")
    def test_CAL_03_goal_list_and_use_cases_removed_with_git_also_from_archive(
        self, tmp_path: Path
    ):
        root = make_project(tmp_path / "old-layout-archive", OLD_LAYOUT_ARCHIVE)
        result = run_script(root)
        assert result.returncode == 0, result.stderr
        status = git(root, "status")
        for rel in REMOVAL_SET:
            assert f"deleted:    {rel}" in status
            assert not (root / rel).exists()
            assert f"remove: {rel}" in result.stdout
        entries = {line[3:]: line[:2] for line in porcelain(root).splitlines()}
        for rel in REMOVAL_SET:
            assert entries[rel] == "D "
        assert ARCHIVE_NOTES not in porcelain(root)
        assert (root / ARCHIVE_NOTES).read_text() == "# Old notes\n"
        assert renames(root) == PATH_TABLE_ROWS
        assert "delete by hand" not in result.stdout

    @pytest.mark.spec("CAL-03-IT-06")
    @pytest.mark.parametrize(
        "set_state",
        [_uc07_untracked, _uc07_ignored, _uc07_staged, _uc07_unstaged],
        ids=["untracked", "ignored", "staged", "unstaged"],
    )
    def test_CAL_03_removal_file_git_cannot_remove_safely_stays_and_is_listed(
        self, tmp_path: Path, set_state
    ):
        root = make_project(tmp_path / "p", OLD_LAYOUT_ARCHIVE)
        set_state(root)
        content = (root / UC_07).read_text()
        index_before = git(root, "ls-files", "-s", "--", UC_07)
        result = run_script(root)
        assert result.returncode == 0, result.stderr
        assert (root / UC_07).read_text() == content
        assert git(root, "ls-files", "-s", "--", UC_07) == index_before
        assert f"delete by hand: {UC_07}" in result.stdout
        assert f"remove: {UC_07}" not in result.stdout
        assert not (root / ARCHIVE_GOAL_LIST).exists()

    @pytest.mark.spec("CAL-03-IT-06")
    def test_CAL_03_dry_run_lists_removals_and_files_to_delete_by_hand(
        self, tmp_path: Path
    ):
        root = make_project(tmp_path / "p", OLD_LAYOUT_ARCHIVE)
        _uc07_unstaged(root)
        before = porcelain(root)
        result = run_script(root, "--dry-run")
        assert result.returncode == 0, result.stderr
        assert f"remove: {ARCHIVE_GOAL_LIST}\n" in result.stdout
        assert f"remove: {ARCHIVE_USE_CASE}\n" in result.stdout
        assert f"delete by hand: {UC_07}\n" in result.stdout
        assert porcelain(root) == before
        assert (root / ARCHIVE_GOAL_LIST).is_file()

    @pytest.mark.spec("CAL-03-IT-06")
    def test_CAL_03_project_with_only_removals_is_still_work(self, tmp_path: Path):
        files = {
            **NEW_LAYOUT_PAYMENTS,
            ARCHIVE_GOAL_LIST: "# Actor-goal list\n",
            ARCHIVE_NOTES: "# Old notes\n",
        }
        root = make_project(tmp_path / "p", files)
        result = run_script(root)
        assert result.returncode == 0, result.stderr
        # The fold step follows because docs/arc42/CONTEXT-MAP.md remains.
        assert result.stdout.splitlines()[:1] == [f"remove: {ARCHIVE_GOAL_LIST}"]
        assert len(result.stdout.splitlines()) == 2
        assert "capture-context --fold-context-map" in result.stdout.splitlines()[1]
        assert porcelain(root) == f"D  {ARCHIVE_GOAL_LIST}\n"

    @pytest.mark.spec("CAL-03-IT-04")
    @pytest.mark.skipif(os.geteuid() == 0, reason="root ignores folder permissions")
    def test_CAL_03_failure_after_a_removal_restores_the_removed_files(
        self, tmp_path: Path
    ):
        root = make_project(tmp_path / "p", OLD_LAYOUT_ARCHIVE)
        work = root / "docs/spec/work"
        work.mkdir()
        work.chmod(0o555)
        before = porcelain(root)
        try:
            result = run_script(root)
        finally:
            work.chmod(0o755)
        assert result.returncode == 1
        assert "undone" in result.stderr
        assert porcelain(root) == before
        for rel in REMOVAL_SET:
            assert (root / rel).read_text() == OLD_LAYOUT_ARCHIVE[rel]

    @pytest.mark.spec("CAL-03-IT-06")
    def test_CAL_03_script_has_no_forced_or_plain_file_removal(self):
        # The one exception: the undo of Run.create deletes the file the run
        # wrote itself, such as docs/spec/glossary.md (ST-0323).
        source = SCRIPT.read_text(encoding="utf-8")
        helper = next(
            node
            for node in ast.parse(source).body
            if isinstance(node, ast.FunctionDef) and node.name == "_delete_created_file"
        )
        source = source.replace(ast.get_source_segment(source, helper), "")
        assert source.count("_delete_created_file(") == 1
        for forbidden in ('"-f"', "--force", "os.remove", "unlink", "shutil.rmtree"):
            assert forbidden not in source, forbidden


# ── CAL-06-CT-01 and CAL-06-IT-02: chapter 12 becomes the glossary and a ──
# ── link line (ST-0323) ─────────────────────────────────────────────────

CHAPTER12 = "docs/arc42/12_glossary.md"
GLOSSARY = "docs/spec/glossary.md"
LINK_LINE = "The terms are in [the glossary](../spec/glossary.md)."

REFERENCED_FROM = (
    "## Referenced from\n\n"
    "- [Scope map](../spec/scope-map.md)\n"
    "- [ADR 1](../adr/0001-example.md)\n"
)

CHAPTER12_FIRST = (
    "# 12. Glossary\n\n"
    "| Term             | Definition                     |\n"
    "| ---------------- | ------------------------------ |\n"
    "| **Ledger Entry** | One line of the ledger.        |\n"
    "| Invoice          | A bill sent to a customer.     |\n\n"
    "## Usage Analysis Vocabulary\n\n"
    "| Term    | Definition                    |\n"
    "| ------- | ----------------------------- |\n"
    "| Session | One run of an agent.          |\n\n" + REFERENCED_FROM
)

CHAPTER12_SECOND = CHAPTER12_FIRST.replace(
    "| Invoice          | A bill sent to a customer.     |\n",
    "| Invoice          | A bill sent to a customer.     |\n"
    "| Payout           | Money paid to a merchant.      |\n",
)

GLOSSARY_EXPECTED = (
    "# Glossary\n\n"
    "## Terms\n\n"
    "| Term             | Definition                 | Avoid |\n"
    "| ---------------- | -------------------------- | ----- |\n"
    "| **Ledger Entry** | One line of the ledger.    |       |\n"
    "| Invoice          | A bill sent to a customer. |       |\n"
    "| Payout           | Money paid to a merchant.  |       |\n\n"
    "## Usage Analysis Vocabulary\n\n"
    "| Term    | Definition           | Avoid |\n"
    "| ------- | -------------------- | ----- |\n"
    "| Session | One run of an agent. |       |\n"
)

STUB_EXPECTED = "# 12. Glossary\n\n" + LINK_LINE + "\n\n" + REFERENCED_FROM


def make_glossary_project(root: Path) -> Path:
    """Build ``old-layout-glossary``: old-layout-payments plus chapter 12.

    Chapter 12 has two commits; the second adds the row "Payout".
    """
    make_project(root, {**OLD_LAYOUT_PAYMENTS, CHAPTER12: CHAPTER12_FIRST})
    (root / CHAPTER12).write_text(CHAPTER12_SECOND, encoding="utf-8")
    git(root, "commit", "-q", "-am", "add the term Payout")
    return root


def _rows(text: str) -> list[list[str]]:
    """Return the body rows of every table in ``text`` as lists of cells."""
    lines = [line for line in text.splitlines() if line.startswith("|")]
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if set("".join(cells)) <= set("-: ") or cells[0] in ("Term", "Begriff"):
            continue
        rows.append(cells)
    return rows


class TestGlossary:
    """Chapter 12 tables move into docs/spec/glossary.md; a stub stays."""

    @pytest.mark.spec("CAL-06-CT-01")
    def test_CAL_06_headed_section_keeps_its_heading_and_rows(self, migrate):
        chapter = (
            "# 12. Glossary\n\n## Usage Analysis Vocabulary\n\n"
            "| Term        | Definition       |\n| --- | --- |\n"
            "| **Session** | One run.         |\n| Spool | Raw records. |\n"
        )
        result = migrate.convert_chapter12(chapter)
        assert migrate.render_glossary(result.sections) == (
            "# Glossary\n\n## Usage Analysis Vocabulary\n\n"
            "| Term        | Definition   | Avoid |\n"
            "| ----------- | ------------ | ----- |\n"
            "| **Session** | One run.     |       |\n"
            "| Spool       | Raw records. |       |\n"
        )
        assert result.stub == "# 12. Glossary\n\n" + LINK_LINE + "\n"

    @pytest.mark.spec("CAL-06-CT-01")
    def test_CAL_06_table_under_the_title_becomes_section_terms(self, migrate):
        chapter = (
            "[back to index](../README.md)\n\n# 12. Glossary\n\n"
            "Terms in **bold** are canonical.\n\n"
            "| Term | Definition |\n| --- | --- |\n| Invoice | A bill. |\n"
        )
        result = migrate.convert_chapter12(chapter)
        assert [s.heading for s in result.sections] == ["Terms"]
        assert result.sections[0].rows == [("Invoice", "A bill.")]
        assert result.stub == (
            "[back to index](../README.md)\n\n# 12. Glossary\n\n"
            + LINK_LINE
            + "\n\nTerms in **bold** are canonical.\n"
        )

    @pytest.mark.spec("CAL-06-CT-01")
    def test_CAL_06_other_column_names_become_term_definition_and_avoid(self, migrate):
        chapter = (
            "# 12. Glossar\n\n## Fachbegriffe\n\n"
            "| Begriff | Bedeutung |\n| --- | --- |\n"
            "| Rechnung | Eine Forderung. |\n| Buchung | Ein Eintrag. |\n"
        )
        glossary = migrate.render_glossary(migrate.convert_chapter12(chapter).sections)
        table = glossary.split("## Fachbegriffe\n\n")[1]
        header, _separator, *body = table.splitlines()
        assert [c.strip() for c in header.strip("|").split("|")] == [
            "Term",
            "Definition",
            "Avoid",
        ]
        assert _rows(glossary) == [
            ["Rechnung", "Eine Forderung.", ""],
            ["Buchung", "Ein Eintrag.", ""],
        ]
        assert len(body) == 2

    @pytest.mark.spec("CAL-06-CT-01")
    def test_CAL_06_section_without_a_table_stays_below_the_link_line(self, migrate):
        result = migrate.convert_chapter12(CHAPTER12_SECOND)
        assert result.stub == STUB_EXPECTED
        assert migrate.render_glossary(result.sections) == GLOSSARY_EXPECTED

    @pytest.mark.spec("CAL-06-CT-01")
    def test_CAL_06_chapter_without_a_table_gives_no_glossary_work(self, migrate):
        assert migrate.convert_chapter12(STUB_EXPECTED).sections == []

    @pytest.mark.spec("CAL-06-IT-02")
    def test_CAL_06_git_shows_glossary_added_and_chapter_12_modified(
        self, tmp_path: Path
    ):
        root = make_glossary_project(tmp_path / "old-layout-glossary")
        result = run_script(root)
        assert result.returncode == 0, result.stderr
        entries = {line[3:]: line[:2] for line in porcelain(root).splitlines()}
        assert entries[GLOSSARY] == "A "
        assert entries[CHAPTER12] == "M "
        log = git(root, "log", "--format=%s", "--", CHAPTER12).splitlines()
        assert log == ["add the term Payout", "fixture"]
        glossary = (root / GLOSSARY).read_text(encoding="utf-8")
        assert glossary == GLOSSARY_EXPECTED
        assert len(_rows(glossary)) == len(_rows(CHAPTER12_SECOND)) == 4
        assert (root / CHAPTER12).read_text(encoding="utf-8") == STUB_EXPECTED
        assert f"{CHAPTER12} -> {GLOSSARY}" in result.stdout

    @pytest.mark.spec("CAL-06-IT-02")
    def test_CAL_06_dry_run_names_the_glossary_and_changes_no_file(
        self, tmp_path: Path
    ):
        root = make_glossary_project(tmp_path / "p")
        result = run_script(root, "--dry-run")
        assert result.returncode == 0, result.stderr
        assert f"{CHAPTER12} -> {GLOSSARY}" in result.stdout
        assert porcelain(root) == ""
        assert not (root / GLOSSARY).exists()

    @pytest.mark.spec("CAL-06-IT-02")
    def test_CAL_06_existing_glossary_refuses_before_the_first_change(
        self, tmp_path: Path
    ):
        root = make_glossary_project(tmp_path / "p")
        (root / GLOSSARY).write_text("# Glossary\n", encoding="utf-8")
        before = porcelain(root)
        result = run_script(root)
        assert result.returncode == 2
        assert GLOSSARY in result.stderr
        assert porcelain(root) == before
        assert (root / CHAPTER12).read_text(encoding="utf-8") == CHAPTER12_SECOND

    @pytest.mark.spec("CAL-03-IT-04")
    @pytest.mark.skipif(os.geteuid() == 0, reason="root ignores folder permissions")
    def test_CAL_06_failure_after_the_glossary_step_restores_chapter_12(
        self, tmp_path: Path
    ):
        root = make_glossary_project(tmp_path / "p")
        work = root / "docs/spec/work"
        work.mkdir()
        work.chmod(0o555)
        before = porcelain(root)
        try:
            result = run_script(root)
        finally:
            work.chmod(0o755)
        assert result.returncode == 1
        assert "undone" in result.stderr
        assert porcelain(root) == before
        assert not (root / GLOSSARY).exists()
        assert (root / CHAPTER12).read_bytes() == CHAPTER12_SECOND.encode()


# ── CAL-05: old paths the script does not rewrite ────────────────────────

LISTING_HEADING = "Old paths the script did not rewrite:"

DOCS_WORKFLOW = (
    "name: docs\n"
    "on: [push]\n"
    "jobs:\n"
    "  validate:\n"
    "    runs-on: ubuntu-latest\n"
    "    steps:\n"
    "      - uses: actions/checkout@v4\n"
    "      - uses: actions/setup-java@v4\n"
    "        with:\n"
    "          distribution: temurin\n"
    "          java-version: '21'\n"
    "      - run: structurizr validate -workspace docs/arc42/architecture.dsl\n"
)

PRE_COMMIT_CONFIG = (
    "repos:\n"
    "  - repo: local\n"
    "    hooks:\n"
    "      - id: agent_factory_hook-arch-lint\n"
    "        name: arch-lint\n"
    "        entry: arch-lint\n"
    "        language: system\n"
    "        files: ^docs/arc42/architecture.dsl$\n"
    "  - repo: local\n"
    "    hooks:\n"
    "      - id: payments-spec-check\n"
    "        name: payments spec check\n"
    "        entry: scripts/check-spec.sh\n"
    "        language: system\n"
    "        files: ^docs/spec/supplementary_specs/\n"
)

BUILD_DOCS = "#!/bin/sh\nset -e\ncp docs/spec/prd.md site/\n"

AGENT_CONTEXT = (
    "# Agent context\n\n"
    "The PRD is docs/spec/prd.md.\n"
    "Run `structurizr validate docs/arc42/architecture.dsl`.\n"
    "See [the PRD](../docs/spec/prd.md) and [docs/spec/todo.md](spec/todo.md).\n"
    "\n[gaps]: docs/spec/payments-gaps.md\n"
)

OLD_LAYOUT_CI: dict[str, str] = {
    **OLD_LAYOUT_PAYMENTS,
    ".github/workflows/docs.yml": DOCS_WORKFLOW,
    ".pre-commit-config.yaml": PRE_COMMIT_CONFIG,
    "scripts/build-docs.sh": BUILD_DOCS,
    "docs/agent-context.md": AGENT_CONTEXT,
}


def listing(output: str) -> list[str]:
    """Return the lines of the old-path listing at the end of ``output``."""
    lines = output.splitlines()
    assert LISTING_HEADING in lines, output
    start = lines.index(LISTING_HEADING)
    return lines[start + 1 :]


class TestOldPathListing:
    """Every old path outside a Markdown link is listed, and its file stays."""

    @pytest.mark.spec("CAL-05-IT-01")
    @pytest.mark.parametrize(
        ("line", "markdown", "found"),
        [
            ("cp docs/spec/prd.md site/", False, ["docs/spec/prd.md"]),
            (
                "files: ^docs/spec/supplementary_specs/",
                False,
                ["docs/spec/supplementary_specs/"],
            ),
            ("paths: [docs/spec/*.feature]", False, ["docs/spec/*.feature"]),
            (
                "see /srv/p/docs/arc42/themes/x.json.",
                False,
                ["docs/arc42/themes/x.json"],
            ),
            (
                "rm docs/spec/use_cases/UC-01.md",
                False,
                ["docs/spec/use_cases/UC-01.md"],
            ),
            ("cat docs/spec/features/a.feature docs/spec/work/prd.md", False, []),
            ("cat docs/spec/scope-map.md mydocs/spec/prd.md", False, []),
            (
                "`docs/spec/todo.md` and docs/spec/todos.md",
                True,
                [
                    "docs/spec/todo.md",
                    "docs/spec/todos.md",
                ],
            ),
            ("[docs/spec/prd.md](docs/spec/prd.md)", True, []),
            (
                "![d](docs/arc42/themes/d.png) docs/spec/prd.md",
                True,
                ["docs/spec/prd.md"],
            ),
            ("[prd]: docs/spec/prd.md", True, []),
            ("[prd]: docs/spec/prd.md", False, ["docs/spec/prd.md"]),
        ],
    )
    def test_CAL_05_old_paths_in_line_skips_markdown_links_only(
        self, migrate, line: str, markdown: bool, found: list[str]
    ):
        assert migrate.old_paths_in_line(line, markdown) == found

    @pytest.mark.spec("CAL-05-IT-01")
    def test_CAL_05_ci_file_is_listed_with_line_and_stays_byte_equal(
        self, tmp_path: Path
    ):
        root = make_project(tmp_path / "old-layout-ci", OLD_LAYOUT_CI)
        result = run_script(root)
        assert result.returncode == 0, result.stderr
        assert (
            "old path: .github/workflows/docs.yml:12: docs/arc42/architecture.dsl"
            in listing(result.stdout)
        )
        assert (root / ".github/workflows/docs.yml").read_bytes() == (
            DOCS_WORKFLOW.encode()
        )
        assert git(root, "diff", "HEAD", "--", ".github/") == ""

    @pytest.mark.spec("CAL-05-IT-01")
    def test_CAL_05_project_hook_is_listed_and_keeps_its_files_value(
        self, tmp_path: Path
    ):
        root = make_project(tmp_path / "old-layout-ci", OLD_LAYOUT_CI)
        result = run_script(root)
        assert result.returncode == 0, result.stderr
        lines = listing(result.stdout)
        assert (
            "old path: .pre-commit-config.yaml:15: docs/spec/supplementary_specs/"
            in lines
        )
        # The factory hook block belongs to the hook rewrite, not to the listing.
        assert not [line for line in lines if ".pre-commit-config.yaml:8:" in line]
        text = (root / ".pre-commit-config.yaml").read_text(encoding="utf-8")
        assert "      - id: payments-spec-check\n" in text
        assert "        files: ^docs/spec/supplementary_specs/\n" in text

    @pytest.mark.spec("CAL-05-IT-01")
    def test_CAL_05_script_is_listed_and_stays_unchanged(self, tmp_path: Path):
        root = make_project(tmp_path / "old-layout-ci", OLD_LAYOUT_CI)
        result = run_script(root)
        assert result.returncode == 0, result.stderr
        assert "old path: scripts/build-docs.sh:3: docs/spec/prd.md" in listing(
            result.stdout
        )
        assert (root / "scripts/build-docs.sh").read_bytes() == BUILD_DOCS.encode()

    @pytest.mark.spec("CAL-05-IT-01")
    def test_CAL_05_markdown_text_and_code_span_are_listed_links_are_not(
        self, tmp_path: Path
    ):
        root = make_project(tmp_path / "old-layout-ci", OLD_LAYOUT_CI)
        result = run_script(root)
        assert result.returncode == 0, result.stderr
        md = [line for line in listing(result.stdout) if "agent-context.md" in line]
        assert md == [
            "old path: docs/agent-context.md:3: docs/spec/prd.md",
            "old path: docs/agent-context.md:4: docs/arc42/architecture.dsl",
        ]
        # The text stays; only the two links follow their moved targets (ST-0320).
        rewritten = AGENT_CONTEXT.replace(
            "(../docs/spec/prd.md)", "(spec/work/prd.md)"
        ).replace("(spec/todo.md)", "(spec/work/todo.md)")
        assert (root / "docs/agent-context.md").read_bytes() == rewritten.encode()

    @pytest.mark.spec("CAL-05-IT-01")
    def test_CAL_05_no_old_path_outside_links_gives_no_listing(self, tmp_path: Path):
        root = make_project(tmp_path / "old-layout-payments")
        result = run_script(root)
        assert result.returncode == 0, result.stderr
        assert LISTING_HEADING not in result.stdout

    @pytest.mark.spec("CAL-05-IT-01")
    def test_CAL_05_dry_run_prints_the_listing_of_a_real_run(self, tmp_path: Path):
        dry = make_project(tmp_path / "dry", OLD_LAYOUT_CI)
        real = make_project(tmp_path / "real", OLD_LAYOUT_CI)
        before = porcelain(dry)
        dry_result = run_script(dry, "--dry-run")
        real_result = run_script(real)
        assert dry_result.returncode == 0, dry_result.stderr
        assert porcelain(dry) == before
        assert listing(dry_result.stdout) == listing(real_result.stdout)

    @pytest.mark.spec("CAL-05-IT-01")
    def test_CAL_05_listing_names_a_moved_file_at_its_new_path(self, tmp_path: Path):
        files = {
            **OLD_LAYOUT_PAYMENTS,
            "docs/spec/supplementary_specs/billing.md": "# Billing\n\nSee docs/spec/prd.md.\n",
        }
        root = make_project(tmp_path / "p", files)
        result = run_script(root)
        assert listing(result.stdout) == [
            "old path: docs/spec/areas/billing.md:3: docs/spec/prd.md"
        ]

    @pytest.mark.spec("CAL-05-IT-01")
    def test_CAL_05_binary_and_ignored_files_are_not_scanned(self, tmp_path: Path):
        files = {**OLD_LAYOUT_PAYMENTS, ".gitignore": "build/\n"}
        root = make_project(tmp_path / "p", files)
        (root / "logo.bin").write_bytes(b"\x89PNG\0docs/spec/prd.md\n")
        (root / "build").mkdir()
        (root / "build/out.txt").write_text("docs/spec/prd.md\n", encoding="utf-8")
        result = run_script(root)
        assert result.returncode == 0, result.stderr
        assert LISTING_HEADING not in result.stdout

    @pytest.mark.spec("CAL-05-IT-01")
    def test_CAL_05_new_layout_project_with_old_path_in_ci_prints_nothing(
        self, tmp_path: Path
    ):
        files = {**NEW_LAYOUT_PAYMENTS, ".github/workflows/docs.yml": DOCS_WORKFLOW}
        root = make_project(tmp_path / "new-layout-payments", files)
        result = run_script(root)
        assert result.returncode == 0
        assert result.stdout == ""


# ── CAL-04-CT-01, CAL-04-IT-01, CAL-02-IT-01: Markdown links keep ───────
# ── working after the move (ST-0320) ────────────────────────────────────

LINK_CHECK = SOURCE_SCRIPTS_DIR / "link-check"
DECISIONS = "docs/arc42/09_architecture_decisions.md"
RETRO = "docs/reviews/retro.md"

OLD_LAYOUT_LINKS: dict[str, str] = {
    **OLD_LAYOUT_ARCHIVE,
    DECISIONS: (
        "# 9. Decisions\n\n[entity model](../spec/supplementary_specs/entity-model.md)\n"
    ),
    "docs/spec/todo.md": "# todo.md\n\n[retro](../reviews/retro.md)\n",
    RETRO: "# Retro\n",
    "docs/spec/scope-map.md": (
        "# Scope map\n\n"
        "[UC-04](../~archive/spec/use_cases/UC-04-dispatch-an-agent-via-trigger.md)\n"
    ),
    "docs/spec/supplementary_specs/billing.md": (
        "# billing.md\n\n[states](state-machines.md#dispatch)\n"
    ),
    "docs/spec/supplementary_specs/state-machines.md": (
        "# state-machines.md\n\n## Dispatch\n"
    ),
}

LINK_MOVES = {
    "docs/spec/supplementary_specs/entity-model.md": "docs/spec/entity-model.md",
    "docs/spec/supplementary_specs/state-machines.md": "docs/spec/state-machines.md",
    "docs/spec/supplementary_specs/billing.md": "docs/spec/areas/billing.md",
    "docs/spec/todo.md": "docs/spec/work/todo.md",
}
LINK_REMOVED = {ARCHIVE_USE_CASE}


def link_check(root: Path, *files: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(LINK_CHECK), *files], cwd=root, capture_output=True, text=True, check=False
    )


class TestLinkRewrite:
    """Every Markdown link resolves after the move (CAL-04, CAL-02)."""

    @pytest.mark.spec("CAL-04-CT-01")
    @pytest.mark.parametrize(
        ("src", "dst", "text", "expected"),
        [
            pytest.param(
                DECISIONS,
                DECISIONS,
                "[entity model](../spec/supplementary_specs/entity-model.md)",
                "[entity model](../spec/entity-model.md)",
                id="old-target",
            ),
            pytest.param(
                "docs/spec/todo.md",
                "docs/spec/work/todo.md",
                "[retro](../reviews/retro.md)",
                "[retro](../../reviews/retro.md)",
                id="rebased-relative-link",
            ),
            pytest.param(
                "docs/spec/scope-map.md",
                "docs/spec/scope-map.md",
                "See [UC-04](../~archive/spec/use_cases/"
                "UC-04-dispatch-an-agent-via-trigger.md) first.",
                "See `UC-04` first.",
                id="removed-target",
            ),
            pytest.param(
                "docs/arc42/01_introduction.md",
                "docs/arc42/01_introduction.md",
                "[d](../spec/supplementary_specs/state-machines.md#dispatch)",
                "[d](../spec/state-machines.md#dispatch)",
                id="anchor",
            ),
            pytest.param(
                "docs/spec/supplementary_specs/billing.md",
                "docs/spec/areas/billing.md",
                "[states](state-machines.md#dispatch)",
                "[states](../state-machines.md#dispatch)",
                id="both-files-move",
            ),
            pytest.param(
                "docs/spec/todo.md",
                "docs/spec/work/todo.md",
                "[site](https://example.com/docs/spec/todo.md) [top](#todo)",
                "[site](https://example.com/docs/spec/todo.md) [top](#todo)",
                id="external-link",
            ),
            pytest.param(
                DECISIONS,
                DECISIONS,
                "[adr](../adr/0001-example.md) [x](../spec/missing.md)",
                "[adr](../adr/0001-example.md) [x](../spec/missing.md)",
                id="outside-the-path-table",
            ),
            pytest.param(
                DECISIONS,
                DECISIONS,
                "`[e](../spec/supplementary_specs/entity-model.md)`\n"
                "```\n[e](../spec/supplementary_specs/entity-model.md)\n```\n",
                "`[e](../spec/supplementary_specs/entity-model.md)`\n"
                "```\n[e](../spec/supplementary_specs/entity-model.md)\n```\n",
                id="code-is-an-example",
            ),
            pytest.param(
                DECISIONS,
                DECISIONS,
                "[e]: ../spec/supplementary_specs/entity-model.md\n",
                "[e]: ../spec/entity-model.md\n",
                id="reference-definition",
            ),
        ],
    )
    def test_CAL_04_rewrite_links_handles_each_link_class(
        self, migrate, src: str, dst: str, text: str, expected: str
    ):
        rewritten, _ = migrate.rewrite_links(text, src, dst, LINK_MOVES, LINK_REMOVED)
        assert rewritten == expected

    @pytest.mark.spec("CAL-04-CT-01")
    def test_CAL_04_rewrite_links_names_each_old_and_new_target(self, migrate):
        text = (
            "[a](../spec/supplementary_specs/entity-model.md) "
            "[b](../~archive/spec/use_cases/UC-04-dispatch-an-agent-via-trigger.md)"
        )
        _, rewrites = migrate.rewrite_links(
            text, DECISIONS, DECISIONS, LINK_MOVES, LINK_REMOVED
        )
        assert rewrites == [
            ("../spec/supplementary_specs/entity-model.md", "../spec/entity-model.md"),
            (
                "../~archive/spec/use_cases/UC-04-dispatch-an-agent-via-trigger.md",
                "`b`",
            ),
        ]

    @pytest.mark.spec("CAL-04-IT-01")
    def test_CAL_04_link_check_passes_on_every_markdown_file_after_the_run(
        self, tmp_path: Path
    ):
        root = make_project(tmp_path / "old-layout-links", OLD_LAYOUT_LINKS)
        result = run_script(root)
        assert result.returncode == 0, result.stderr
        files = sorted(
            p.relative_to(root).as_posix() for p in (root / "docs").rglob("*.md")
        )
        assert "docs/spec/work/todo.md" in files
        checked = link_check(root, *files)
        assert checked.returncode == 0, checked.stderr
        todo = (root / "docs/spec/work/todo.md").read_text(encoding="utf-8")
        assert "[retro](../../reviews/retro.md)" in todo
        scope_map = (root / "docs/spec/scope-map.md").read_text(encoding="utf-8")
        assert "`UC-04`" in scope_map
        assert "](" not in scope_map
        decisions = (root / DECISIONS).read_text(encoding="utf-8")
        assert "[entity model](../spec/entity-model.md)" in decisions

    @pytest.mark.spec("CAL-02-IT-01")
    def test_CAL_02_dry_run_prints_every_move_and_link_rewrite_and_changes_nothing(
        self, tmp_path: Path
    ):
        root = make_project(tmp_path / "old-layout-links", OLD_LAYOUT_LINKS)
        before = porcelain(root)
        result = run_script(root, "--dry-run")
        assert result.returncode == 0, result.stderr
        assert porcelain(root) == before
        for old, new in PATH_TABLE_ROWS.items():
            assert f"{old} -> {new}\n" in result.stdout
        for line in [
            f"link: {DECISIONS}: ../spec/supplementary_specs/entity-model.md"
            " -> ../spec/entity-model.md",
            "link: docs/spec/work/todo.md: ../reviews/retro.md"
            " -> ../../reviews/retro.md",
            "link: docs/spec/scope-map.md: ../~archive/spec/use_cases/"
            "UC-04-dispatch-an-agent-via-trigger.md -> `UC-04`",
            "link: docs/spec/areas/billing.md: state-machines.md#dispatch"
            " -> ../state-machines.md#dispatch",
        ]:
            assert f"{line}\n" in result.stdout
        real = run_script(make_project(tmp_path / "real", OLD_LAYOUT_LINKS))
        assert result.stdout == real.stdout

    @pytest.mark.spec("CAL-03-IT-04")
    @pytest.mark.skipif(os.geteuid() == 0, reason="root ignores file permissions")
    def test_CAL_04_failure_after_a_link_rewrite_restores_the_rewritten_file(
        self, tmp_path: Path
    ):
        root = make_project(tmp_path / "p", OLD_LAYOUT_LINKS)
        # The rewrite of the decisions chapter comes first; the read-only
        # scope map makes the next rewrite fail.
        scope_map = root / "docs/spec/scope-map.md"
        scope_map.chmod(0o444)
        before = porcelain(root)
        try:
            result = run_script(root)
        finally:
            scope_map.chmod(0o644)
        assert result.returncode == 1
        assert "undone" in result.stderr
        assert porcelain(root) == before
        for rel in (DECISIONS, "docs/spec/todo.md", "docs/spec/scope-map.md"):
            assert (root / rel).read_bytes() == OLD_LAYOUT_LINKS[rel].encode()


# ── CAL-06-CT-02 and CAL-06-IT-01: the terms of each CONTEXT.md become a ──
# ── glossary section of their own (ST-0324) ─────────────────────────────

CONTEXT = "docs/CONTEXT.md"
ARC42_CONTEXT = "docs/arc42/CONTEXT.md"
LEDGER_CONTEXT = "packages/ledger/CONTEXT.md"
CONTEXT_MAP = "docs/arc42/CONTEXT-MAP.md"
FOLD_STEP = "capture-context --fold-context-map"
CLEANUP_STEP = "remove the duplicate terms"

BILLING_CONTEXT = (
    "# Billing\n\n"
    "Bills customers for delivered orders.\n\n"
    "## Language\n\n"
    "**Invoice**:\n"
    "A request for payment sent to a customer after delivery.\n"
    "_Avoid_: Bill, payment request\n\n"
    "**Customer**:\n"
    "A person or organization that places orders.\n"
    "_Avoid_: Client, buyer, account\n"
)
BILLING_ROUTING = "# Billing\n\nBills customers for delivered orders.\n"
BILLING_SECTION = (
    "## Billing\n\n"
    "| Term     | Definition                                               "
    "| Avoid                  |\n"
    "| -------- | -------------------------------------------------------- "
    "| ---------------------- |\n"
    "| Invoice  | A request for payment sent to a customer after delivery. "
    "| Bill, payment request  |\n"
    "| Customer | A person or organization that places orders.             "
    "| Client, buyer, account |\n"
)
LEDGER_FILE = (
    "# Ledger\n\nKeeps the books.\n\n## Language\n\n"
    "**Ledger Entry**: One booked line.\n"
)
ROUTING_ONLY = "# Architecture\n\nRead the arc42 chapters for the building blocks.\n"
MAP_TEXT = (
    "# Context Map\n\n## Contexts\n\n"
    "- **Ledger** — the books. See `packages/ledger/CONTEXT.md`.\n"
)


def make_vocabulary_project(root: Path) -> Path:
    """Build ``old-layout-vocabulary``: old-layout-glossary plus vocabulary files."""
    make_glossary_project(root)
    for rel, text in {
        CONTEXT: BILLING_CONTEXT,
        CONTEXT_MAP: MAP_TEXT,
        LEDGER_CONTEXT: LEDGER_FILE,
        ARC42_CONTEXT: ROUTING_ONLY,
    }.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "vocabulary files")
    return root


def _headings(text: str) -> list[str]:
    return [line[3:] for line in text.splitlines() if line.startswith("## ")]


class TestVocabulary:
    """The terms of each CONTEXT.md move into the glossary; routing stays."""

    @pytest.mark.spec("CAL-06-CT-02")
    def test_CAL_06_list_form_becomes_rows_and_language_section_goes(self, migrate):
        text = (
            BILLING_CONTEXT.replace("## Language", "## Language\n")
            + "\n## Relationships\n\nBilling reads the ledger.\n"
        )
        section, rest = migrate.convert_context(text, CONTEXT)
        assert section.heading == "Billing"
        assert section.rows == [
            (
                "Invoice",
                "A request for payment sent to a customer after delivery.",
                "Bill, payment request",
            ),
            (
                "Customer",
                "A person or organization that places orders.",
                "Client, buyer, account",
            ),
        ]
        assert migrate.render_sections([section]) + "\n" == BILLING_SECTION
        assert (
            rest
            == BILLING_ROUTING + "\n## Relationships\n\nBilling reads the ledger.\n"
        )

    @pytest.mark.spec("CAL-06-CT-02")
    def test_CAL_06_definition_on_the_term_line_and_a_bar_in_a_cell(self, migrate):
        section, rest = migrate.convert_context(
            "## Language\n\n**A|B**: Either a or\nb.\n", "x/CONTEXT.md"
        )
        assert section.heading == "x/CONTEXT.md"
        assert section.rows == [("A\\|B", "Either a or b.", "")]
        assert rest == "\n"

    @pytest.mark.spec("CAL-06-CT-02")
    def test_CAL_06_context_without_language_gives_no_terms(self, migrate):
        assert migrate.convert_context(ROUTING_ONLY, ARC42_CONTEXT) is None

    @pytest.mark.spec("CAL-06-CT-02")
    @pytest.mark.parametrize(
        "body",
        [
            "Some prose first.\n",
            "- **Invoice**: A bill.\n",
            "**Invoice**:\n### Group\n",
        ],
    )
    def test_CAL_06_language_section_outside_the_list_form_is_an_error(
        self, migrate, body
    ):
        with pytest.raises(migrate.ListFormError):
            migrate.convert_context("# Billing\n\n## Language\n\n" + body, CONTEXT)

    @pytest.mark.spec("CAL-06-CT-02")
    def test_CAL_06_duplicate_terms_compare_without_markup_and_case(self, migrate):
        glossary = migrate.render_glossary(
            [
                migrate.GlossarySection("Terms", rows=[("**Invoice**", "x")]),
                migrate.GlossarySection("Billing", rows=[("invoice", "y", "")]),
                migrate.GlossarySection("Ledger", rows=[("Entry", "z", "")]),
            ]
        )
        assert migrate.duplicate_terms(glossary) == [("Invoice", ["Terms", "Billing"])]

    @pytest.mark.spec("CAL-06-IT-01")
    def test_CAL_06_two_vocabularies_never_stop_the_script(self, tmp_path: Path):
        root = make_vocabulary_project(tmp_path / "old-layout-vocabulary")
        result = run_script(root)
        assert result.returncode == 0, result.stderr
        glossary = (root / GLOSSARY).read_text(encoding="utf-8")
        assert _headings(glossary) == [
            "Terms",
            "Usage Analysis Vocabulary",
            "Billing",
            "Ledger",
        ]
        assert glossary.startswith(GLOSSARY_EXPECTED)
        assert BILLING_SECTION in glossary
        assert ["Ledger Entry", "One booked line.", ""] in _rows(glossary)
        lines = result.stdout.splitlines()
        assert "duplicate term: Invoice in Terms, Billing" in lines
        assert any(FOLD_STEP in line for line in lines)
        assert CLEANUP_STEP in lines[-1] and "domain-modeling" in lines[-1]
        assert (root / CONTEXT).read_text(encoding="utf-8") == BILLING_ROUTING
        assert (root / ARC42_CONTEXT).read_bytes() == ROUTING_ONLY.encode()
        assert (root / CONTEXT_MAP).read_text(encoding="utf-8") == MAP_TEXT
        for path in root.rglob("CONTEXT.md"):
            assert "## Language" not in path.read_text(encoding="utf-8"), path

    @pytest.mark.spec("CAL-06-IT-01")
    @pytest.mark.parametrize(
        ("source", "files"),
        [
            (CONTEXT, {CONTEXT: BILLING_CONTEXT}),
            (ARC42_CONTEXT, {ARC42_CONTEXT: BILLING_CONTEXT}),
            (
                LEDGER_CONTEXT,
                {CONTEXT_MAP: MAP_TEXT, LEDGER_CONTEXT: LEDGER_FILE},
            ),
        ],
    )
    def test_CAL_06_each_vocabulary_source_without_chapter_12_creates_the_glossary(
        self, tmp_path: Path, source, files
    ):
        root = make_project(tmp_path / "p", {**NEW_LAYOUT_PAYMENTS, **files})
        (root / GLOSSARY).unlink()
        git(root, "commit", "-q", "-am", "no glossary")
        result = run_script(root)
        assert result.returncode == 0, result.stderr
        glossary = (root / GLOSSARY).read_text(encoding="utf-8")
        heading = "Ledger" if source == LEDGER_CONTEXT else "Billing"
        assert _headings(glossary) == [heading]
        entries = {line[3:]: line[:2] for line in porcelain(root).splitlines()}
        assert entries[GLOSSARY] == "A "
        assert "## Language" not in (root / source).read_text(encoding="utf-8")
        assert f"{source} -> {GLOSSARY}" in result.stdout
        assert FOLD_STEP in result.stdout
        assert "duplicate term" not in result.stdout
        assert CLEANUP_STEP not in result.stdout

    @pytest.mark.spec("CAL-06-IT-01")
    def test_CAL_06_existing_glossary_gets_the_context_terms_appended(
        self, tmp_path: Path
    ):
        existing = (
            "# Glossary\n\n## Terms\n\n"
            "| Term    | Definition | Avoid |\n| ------- | ---------- | ----- |\n"
            "| Invoice | A bill.    |       |\n"
        )
        root = make_project(
            tmp_path / "p",
            {**NEW_LAYOUT_PAYMENTS, GLOSSARY: existing, CONTEXT: BILLING_CONTEXT},
        )
        result = run_script(root)
        assert result.returncode == 0, result.stderr
        assert (root / GLOSSARY).read_text(encoding="utf-8") == (
            existing + "\n" + BILLING_SECTION
        )
        assert "duplicate term: Invoice in Terms, Billing" in result.stdout
        assert CLEANUP_STEP in result.stdout
        assert (root / CONTEXT).read_text(encoding="utf-8") == BILLING_ROUTING

    @pytest.mark.spec("CAL-06-IT-01")
    def test_CAL_06_routing_only_context_in_the_new_layout_gives_no_work(
        self, tmp_path: Path
    ):
        root = make_project(
            tmp_path / "p", {**NEW_LAYOUT_PAYMENTS, CONTEXT: ROUTING_ONLY}
        )
        result = run_script(root)
        assert result.returncode == 0, result.stderr
        assert result.stdout == ""
        assert porcelain(root) == ""

    @pytest.mark.spec("CAL-06-IT-01")
    def test_CAL_06_language_section_outside_the_list_form_refuses(
        self, tmp_path: Path
    ):
        text = "# Billing\n\n## Language\n\nInvoices are bills.\n"
        root = make_project(tmp_path / "p", {**NEW_LAYOUT_PAYMENTS, CONTEXT: text})
        result = run_script(root)
        assert result.returncode == 2
        assert CONTEXT in result.stderr
        assert porcelain(root) == ""

    @pytest.mark.spec("CAL-03-IT-04")
    @pytest.mark.skipif(os.geteuid() == 0, reason="root ignores folder permissions")
    def test_CAL_06_failure_after_a_language_removal_restores_every_file(
        self, tmp_path: Path
    ):
        root = make_vocabulary_project(tmp_path / "p")
        work = root / "docs/spec/work"
        work.mkdir()
        work.chmod(0o555)
        before = porcelain(root)
        try:
            result = run_script(root)
        finally:
            work.chmod(0o755)
        assert result.returncode == 1
        assert "undone" in result.stderr
        assert porcelain(root) == before
        assert not (root / GLOSSARY).exists()
        assert (root / CONTEXT).read_text(encoding="utf-8") == BILLING_CONTEXT
        assert (root / LEDGER_CONTEXT).read_text(encoding="utf-8") == LEDGER_FILE

    @pytest.mark.spec("CAL-06-IT-01")
    def test_CAL_06_existing_glossary_with_chapter_12_and_context_terms_exits_0(
        self, tmp_path: Path
    ):
        existing = "# Glossary\n\n## Acronyms\n\n| Term | Definition | Avoid |\n| --- | --- | --- |\n| SLA | Service level agreement. | |\n"
        root = make_vocabulary_project(tmp_path / "p")
        (root / GLOSSARY).write_text(existing, encoding="utf-8")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "glossary")
        result = run_script(root)
        assert result.returncode == 0, result.stderr
        glossary = (root / GLOSSARY).read_text(encoding="utf-8")
        assert glossary.startswith(existing)
        assert _headings(glossary) == [
            "Acronyms",
            "Terms",
            "Usage Analysis Vocabulary",
            "Billing",
            "Ledger",
        ]
        assert "duplicate term: Invoice in Terms, Billing" in result.stdout
        assert (root / CHAPTER12).read_text(encoding="utf-8") == STUB_EXPECTED
        entries = {line[3:]: line[:2] for line in porcelain(root).splitlines()}
        assert entries[GLOSSARY] == "M "
