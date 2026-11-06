"""init-factory tells the user how to seed the counter (ST-0375, CID-10)."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from pathlib import Path

from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR, load_script

inf = load_script("init-factory")

COUNTER_REF = "refs/ids/counters"


def _git(cwd: Path, *args: str) -> str:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, env=env, check=True
    )
    return result.stdout


def _project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    _git(project, "init", "-q")
    _git(project, "-c", "user.name=t", "-c", "user.email=t@example.com",
         "commit", "-q", "--allow-empty", "-m", "first")
    return project


def _bare_origin(tmp_path: Path, project: Path) -> Path:
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "-q", "--bare", str(origin))
    _git(project, "remote", "add", "origin", str(origin))
    return origin


def _closed_port_url() -> str:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    return f"http://127.0.0.1:{port}/remote.git"


def _init(target: Path) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(
        [sys.executable, str(SOURCE_SCRIPTS_DIR / "init-factory"),
         "--source", str(REPO_ROOT), "--target", str(target),
         "--cli", "claude", "--project-name", "demo"],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, env=env,
        check=False, timeout=300,
    )


def test_st_0375_missing_counter_names_the_seed_command(tmp_path):
    project = _project(tmp_path)
    origin = _bare_origin(tmp_path, project)

    result = _init(project)

    assert "fitting step 4" in result.stdout
    assert "next-id --plan-seed" in result.stdout
    assert "above your highest ID" not in result.stdout
    assert _git(origin, "for-each-ref", COUNTER_REF) == ""


def test_st_0375_missing_origin_names_the_remote(tmp_path):
    project = _project(tmp_path)

    result = _init(project)

    assert "fitting step 4 keeps the counter in this repository" in result.stdout
    assert "until `origin` exists" in result.stdout
    assert "above your highest ID" not in result.stdout


def test_st_0375_unreachable_origin_warns_and_finishes(tmp_path):
    project = _project(tmp_path)
    url = _closed_port_url()
    _git(project, "remote", "add", "origin", url)

    result = _init(project)

    assert result.returncode == 0, result.stderr
    warning = [ln for ln in result.stdout.splitlines() if "warning" in ln.lower()]
    assert any(url in ln for ln in warning), result.stdout
    record = json.loads((project / ".agent-factory" / "install.json").read_text())
    assert record["cli"] == ["claude"]


def _next_id_seed(project: Path) -> None:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    subprocess.run(
        [sys.executable, str(SOURCE_SCRIPTS_DIR / "next-id"), "--seed", "0"],
        cwd=project, capture_output=True, text=True, env=env, check=True,
    )


def _seeded_local_repo(tmp_path: Path, name: str) -> Path:
    repo = tmp_path / name
    repo.mkdir()
    _git(repo, "init", "-q", "--bare")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    subprocess.run(
        [sys.executable, str(SOURCE_SCRIPTS_DIR / "next-id"), "--seed", "0",
         "--remote", str(repo)],
        capture_output=True, text=True, env=env, check=True,
    )
    return repo


def _seeded_key(project: Path):
    path = project / ".agent-factory" / "config" / "project-context.json"
    return json.loads(path.read_text())["fitting"]["counter_seeded"]


def test_st_0378_counter_seeded_follows_the_remote_the_setting_and_origin(tmp_path):
    """CIF-13-IT-01: five rows of the setting and origin table, then greenfield."""
    results = []

    # no setting, origin holds a counter
    a = tmp_path / "a"
    a.mkdir()
    project = _project(a)
    origin = _bare_origin(a, project)
    _git(project, "update-ref", COUNTER_REF, "HEAD")
    _git(project, "push", "-q", str(origin), COUNTER_REF)
    assert _init(project).returncode == 0
    results.append(_seeded_key(project))

    # no setting, origin holds none
    b = tmp_path / "b"
    b.mkdir()
    project = _project(b)
    _bare_origin(b, project)
    assert _init(project).returncode == 0
    results.append(_seeded_key(project))

    # no setting, no origin
    c = tmp_path / "c"
    c.mkdir()
    project = _project(c)
    assert _init(project).returncode == 0
    results.append(_seeded_key(project))

    # setting names a repository with the counter, origin holds none
    d = tmp_path / "d"
    d.mkdir()
    project = _project(d)
    _bare_origin(d, project)
    _git(project, "config", "agent-factory.counterRemote",
         str(_seeded_local_repo(d, "local.git")))
    assert _init(project).returncode == 0
    results.append(_seeded_key(project))

    # setting names a repository without the counter, no origin
    e = tmp_path / "e"
    e.mkdir()
    project = _project(e)
    empty = e / "empty.git"
    empty.mkdir()
    _git(empty, "init", "-q", "--bare")
    _git(project, "config", "agent-factory.counterRemote", str(empty))
    assert _init(project).returncode == 0
    results.append(_seeded_key(project))

    # greenfield cache, setting names a seeded repository
    f = tmp_path / "f"
    f.mkdir()
    project = _project(f)
    _git(project, "config", "agent-factory.counterRemote", str(project))
    _next_id_seed(project)
    greenfield = {
        "status": "greenfield",
        "model_matrix_configured": False,
        "fingerprint_confirmed": True,
        "agent_context_populated": True,
        "test_regime_detected": True,
        "hooks_decided": True,
        "counter_seeded": False,
    }
    config = project / ".agent-factory" / "config"
    config.mkdir(parents=True)
    (config / "project-context.json").write_text(
        json.dumps({"languages": [], "fitting": greenfield}))
    assert _init(project).returncode == 0
    fitting = json.loads((config / "project-context.json").read_text())["fitting"]
    results.append(fitting["counter_seeded"])
    assert fitting == {**greenfield, "counter_seeded": True}

    assert results == [True, False, False, True, False, True]


def test_st_0378_init_factory_changes_no_ref_of_the_remote(tmp_path):
    """CIF-13-IT-02: the refs of the bare repository stay as they were."""
    project = _project(tmp_path)
    origin = _bare_origin(tmp_path, project)
    _git(project, "push", "-q", str(origin), "HEAD:refs/heads/main")
    before = _git(origin, "for-each-ref")

    assert _init(project).returncode == 0

    assert _git(origin, "for-each-ref") == before
    assert _seeded_key(project) is False


def test_st_0378_unreachable_remote_keeps_a_seeded_key(tmp_path):
    """CIF-13-IT-03: a closed port leaves the key true; exit 0, warning names the remote."""
    project = _project(tmp_path)
    origin = _bare_origin(tmp_path, project)
    _git(project, "update-ref", COUNTER_REF, "HEAD")
    _git(project, "push", "-q", str(origin), COUNTER_REF)
    assert _init(project).returncode == 0
    assert _seeded_key(project) is True

    url = _closed_port_url()
    _git(project, "remote", "set-url", "origin", url)
    result = _init(project)

    assert result.returncode == 0, result.stderr
    assert any(url in ln and "warning" in ln.lower() for ln in result.stdout.splitlines())
    assert _seeded_key(project) is True


def test_st_0378_counter_check_calls_ls_remote_and_no_writing_git_command(
    tmp_path, monkeypatch
):
    """CIF-13-CT-01: every git call is a read; one is ls-remote."""
    project = _project(tmp_path)
    _bare_origin(tmp_path, project)
    calls = []
    real_run = subprocess.run

    def recording_run(cmd, *args, **kwargs):
        calls.append(list(cmd))
        return real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(inf.subprocess, "run", recording_run)

    assert inf.check_counter(project, []) is False

    subcommands = [c[1] for c in calls]
    assert "ls-remote" in subcommands
    assert set(subcommands) <= {"config", "remote", "ls-remote"}
    assert all("--set" not in c and "add" not in c for c in calls)
