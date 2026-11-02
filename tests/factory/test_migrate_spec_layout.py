"""Tests for migrate-spec-layout, the move into the core artifact layout.

Covers CAL-01 and CAL-03 of docs/spec/core-artifact-layout-qa-strategy.md.
Every test builds its project at test time with ``make_project``. Later
stories extend ``OLD_LAYOUT_PAYMENTS`` and ``NEW_LAYOUT_PAYMENTS`` or pass
their own file maps.
"""

from __future__ import annotations

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
