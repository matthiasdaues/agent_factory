"""next-id and init-factory never print the user info of a remote URL (SEC-0007).

Every remote URL here carries the made-up token `ghp_FAKEtoken0000`. A fake
`ssh` program serves an ssh URL from a local bare repository, so a URL with
user info reaches every success and error path of a claim and a seed. Each
test checks that the token is on neither stream, and that an error message
names the redacted URL.
"""

from __future__ import annotations

import http.server
import os
import socket
import subprocess
import sys
import threading
from contextlib import contextmanager
from pathlib import Path

import pytest
from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR, load_script

ni = load_script("next-id")
initf = load_script("init-factory")

NEXT_ID = SOURCE_SCRIPTS_DIR / "next-id"
INIT_FACTORY = SOURCE_SCRIPTS_DIR / "init-factory"
REF = "refs/ids/counters"
TOKEN = "ghp_FAKEtoken0000"
USER_INFO = f"x-access-token:{TOKEN}@"

# A fake ssh: it runs the remote command, such as `git-upload-pack '/path'`,
# on this machine. The name `ssh` makes git use the OpenSSH options.
FAKE_SSH = """#!/bin/sh
for last; do :; done
exec sh -c "$(printf '%s' "$last" | sed 's/^git-/git /')"
"""

# A fake ssh that fails with a git error text holding the URL and its token.
LEAKING_SSH = f"""#!/bin/sh
echo "fatal: could not read from https://{USER_INFO}factory.invalid/r.git" >&2
exit 128
"""

READ_ONLY_HOOK = """#!/bin/sh
echo read-only >&2
exit 1
"""

STALE_LEASE_HOOK = """#!/bin/sh
unset GIT_QUARANTINE_PATH GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
tree=$(git mktree </dev/null)
sha=$(printf 'start=1000\\ntoken=%s\\n' "$(od -An -N8 -tx8 /dev/urandom | tr -d ' ')" |
  GIT_AUTHOR_NAME=hook GIT_AUTHOR_EMAIL=hook@example.invalid \\
  GIT_COMMITTER_NAME=hook GIT_COMMITTER_EMAIL=hook@example.invalid \\
  git commit-tree "$tree")
git update-ref refs/ids/counters "$sha"
exit 0
"""


# --- fixtures -----------------------------------------------------------------


def _write_program(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    path.chmod(0o755)
    return path


@pytest.fixture
def env(tmp_path: Path) -> dict[str, str]:
    home = tmp_path / "home"
    home.mkdir()
    base = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    base.update(
        HOME=str(home),
        GIT_CONFIG_NOSYSTEM="1",
        GIT_TERMINAL_PROMPT="0",
        GIT_CEILING_DIRECTORIES=str(tmp_path),
        GIT_SSH_COMMAND=str(_write_program(tmp_path / "bin" / "ssh", FAKE_SSH)),
    )
    return base


def _git(env: dict[str, str], *args: str) -> str:
    result = subprocess.run(
        ["git", *args], env=env, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


@pytest.fixture
def remote(tmp_path: Path, env: dict[str, str]) -> Path:
    path = tmp_path / "remote.git"
    _git(env, "init", "--quiet", "--bare", str(path))
    return path


def _ssh_url(remote: Path) -> str:
    return f"ssh://{USER_INFO}factory.invalid{remote}"


def _shown(url: str) -> str:
    return url.replace(USER_INFO, "***@")


@pytest.fixture
def url(remote: Path) -> str:
    return _ssh_url(remote)


@pytest.fixture
def clone(tmp_path: Path, env: dict[str, str], url: str) -> Path:
    path = tmp_path / "clone"
    _git(env, "init", "--quiet", str(path))
    _git(env, "-C", str(path), "remote", "add", "origin", url)
    return path


def _set_counter(env: dict[str, str], bare: Path) -> None:
    tree = _git(env, "-C", str(bare), "mktree")
    sha = subprocess.run(
        ["git", "-C", str(bare), "commit-tree", tree],
        input="start=1000\ntoken=fixture0000000000\n",
        env={
            **env,
            "GIT_AUTHOR_NAME": "fixture",
            "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_NAME": "fixture",
            "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
        },
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    _git(env, "-C", str(bare), "update-ref", REF, sha)


def _install_hook(remote: Path, text: str) -> None:
    _write_program(remote / "hooks" / "pre-receive", text)


def _closed_port_url() -> str:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    return f"http://{USER_INFO}127.0.0.1:{port}/remote.git"


@contextmanager
def _http_403():
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(403)
            self.end_headers()

        do_POST = do_GET

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://{USER_INFO}127.0.0.1:{server.server_address[1]}/remote.git"
    finally:
        server.shutdown()
        server.server_close()


def run(env: dict[str, str], cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(NEXT_ID), *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )


def _assert_no_token(result: subprocess.CompletedProcess) -> None:
    assert TOKEN not in result.stdout
    assert TOKEN not in result.stderr
    assert "x-access-token" not in result.stdout + result.stderr


def _assert_failed_and_redacted(result: subprocess.CompletedProcess, url: str) -> None:
    assert result.returncode == 1, result.stderr
    _assert_no_token(result)
    assert _shown(url) in result.stderr, result.stderr


# --- the redaction function ---------------------------------------------------

REDACTIONS = [
    ("https://user:secret@host/r.git", "https://***@host/r.git"),
    ("https://ghp_FAKEtoken0000@host/r.git", "https://***@host/r.git"),
    (
        "https://x-access-token:ghp_FAKEtoken0000@github.com/org/r.git",
        "https://***@github.com/org/r.git",
    ),
    ("http://ci-token:abc@127.0.0.1:8080/r.git", "http://***@127.0.0.1:8080/r.git"),
    ("ssh://git:secret@host:22/r.git", "ssh://***@host:22/r.git"),
    ("git+ssh://git:secret@host/r.git", "git+ssh://***@host/r.git"),
    ("HTTPS://user:secret@host/r.git", "HTTPS://***@host/r.git"),
    (
        "fatal: unable to access 'https://user:p@ss@host/r.git/': 403",
        "fatal: unable to access 'https://***@host/r.git/': 403",
    ),
    ("a https://u:x@h1/a and http://v:y@h2/b", "a https://***@h1/a and http://***@h2/b"),
]

UNCHANGED = [
    "git@github.com:org/repo.git",
    "https://github.com/org/repo.git",
    "https://host/path/with@sign",
    "/tmp/remote.git",
    "no URL here, mail me at a@b.c",
]


@pytest.mark.parametrize("module", [ni, initf], ids=["next-id", "init-factory"])
class TestRedactUserInfo:
    @pytest.mark.parametrize(("text", "shown"), REDACTIONS)
    def test_sec_0007_user_info_becomes_stars(self, module, text, shown):
        assert module.redact_user_info(text) == shown

    @pytest.mark.parametrize("text", UNCHANGED)
    def test_sec_0007_text_without_user_info_stays(self, module, text):
        assert module.redact_user_info(text) == text


@pytest.mark.parametrize("script", [NEXT_ID, INIT_FACTORY], ids=["next-id", "init-factory"])
@pytest.mark.parametrize(
    "ending",
    [
        f"raise RuntimeError('https://{USER_INFO}host/r.git')",
        f"sys.exit('https://{USER_INFO}host/r.git')",
        f"print('https://{USER_INFO}host/r.git')",
    ],
    ids=["exception", "sys-exit", "print"],
)
def test_sec_0007_every_write_of_the_script_passes_the_redaction(script, ending):
    program = (
        "import sys, importlib.util\n"
        "from importlib.machinery import SourceFileLoader\n"
        f"loader = SourceFileLoader('script', {str(script)!r})\n"
        "spec = importlib.util.spec_from_loader('script', loader)\n"
        "mod = importlib.util.module_from_spec(spec)\n"
        "loader.exec_module(mod)\n"
        "mod.redact_output()\n"
        f"{ending}\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", program],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    _assert_no_token(result)
    assert "https://***@host/r.git" in result.stdout + result.stderr


# --- next-id: success paths ---------------------------------------------------


class TestSuccessPathsPrintNoToken:
    def test_sec_0007_seed_and_claim_through_origin(self, env, clone):
        seeded = run(env, clone, "--seed", "1000")
        claimed = run(env, clone, "ST")
        assert (seeded.returncode, claimed.returncode) == (0, 0), seeded.stderr
        assert claimed.stdout == "ST-1001\n"
        _assert_no_token(seeded)
        _assert_no_token(claimed)

    def test_sec_0007_seed_and_claim_through_remote(self, env, tmp_path, url):
        seeded = run(env, tmp_path, "--seed", "1000", "--remote", url)
        claimed = run(env, tmp_path, "ST", "--remote", url)
        assert (seeded.returncode, claimed.returncode) == (0, 0), seeded.stderr
        assert claimed.stdout == "ST-1001\n"
        _assert_no_token(seeded)
        _assert_no_token(claimed)


# --- next-id: error paths -----------------------------------------------------


@pytest.fixture(params=["origin", "remote"])
def call(request, env, tmp_path):
    """Run next-id on a URL, given as the URL of origin or as --remote."""

    def _call(url: str, *args: str) -> subprocess.CompletedProcess:
        if request.param == "remote":
            return run(env, tmp_path, *args, "--remote", url)
        repo = tmp_path / "origin-clone"
        if not repo.exists():
            _git(env, "init", "--quiet", str(repo))
            _git(env, "-C", str(repo), "remote", "add", "origin", url)
        return run(env, repo, *args)

    return _call


class TestErrorPathsShowOnlyTheRedactedUrl:
    def test_sec_0007_missing_counter(self, call, url):
        _assert_failed_and_redacted(call(url, "ST"), url)

    def test_sec_0007_unreachable_remote_on_a_claim(self, call):
        url = _closed_port_url()
        _assert_failed_and_redacted(call(url, "ST"), url)

    @pytest.mark.spec("CIF-07-IT-03")
    def test_st_0376_unreachable_remote_on_a_plan_seed(self, call):
        url = _closed_port_url()
        result = call(url, "--plan-seed")
        _assert_failed_and_redacted(result, url)
        assert result.stdout == ""

    def test_sec_0007_unreachable_remote_on_a_seed(self, call):
        url = _closed_port_url()
        _assert_failed_and_redacted(call(url, "--seed", "1000"), url)

    def test_sec_0007_refused_fetch(self, call):
        with _http_403() as url:
            result = call(url, "ST")
        _assert_failed_and_redacted(result, url)

    def test_sec_0007_refused_push(self, call, env, remote, url):
        _set_counter(env, remote)
        _install_hook(remote, READ_ONLY_HOOK)
        result = call(url, "ST")
        _assert_failed_and_redacted(result, url)
        assert "read-only" in result.stderr

    def test_sec_0007_ten_stale_leases(self, call, env, remote, url):
        _set_counter(env, remote)
        _install_hook(remote, STALE_LEASE_HOOK)
        result = call(url, "ST")
        assert result.returncode == 1
        assert "ten stale leases" in result.stderr
        _assert_no_token(result)

    def test_sec_0007_seed_on_an_existing_counter(self, call, env, remote, url):
        _set_counter(env, remote)
        result = call(url, "--seed", "1000")
        _assert_failed_and_redacted(result, url)
        assert "already exists" in result.stderr

    def test_sec_0007_git_error_text_with_the_token(self, call, env, tmp_path, url):
        env["GIT_SSH_COMMAND"] = str(
            _write_program(tmp_path / "leaking" / "ssh", LEAKING_SSH)
        )
        result = call(url, "ST")
        _assert_failed_and_redacted(result, url)
        assert "https://***@factory.invalid/r.git" in result.stderr


def test_sec_0007_time_limit(monkeypatch, capsys, env, remote, url):
    _set_counter(env, remote)
    for key in ("HOME", "GIT_CONFIG_NOSYSTEM", "GIT_SSH_COMMAND"):
        monkeypatch.setenv(key, env[key])
    real = subprocess.run

    def slow_fetch(cmd, **kwargs):
        if "fetch" in cmd:
            raise subprocess.TimeoutExpired(cmd, kwargs["timeout"])
        return real(cmd, **kwargs)

    monkeypatch.setattr(ni.subprocess, "run", slow_fetch)
    streams = sys.stdout, sys.stderr
    try:
        ni.redact_output()
        assert ni.main(["ST", "--remote", url]) == 1
    finally:
        sys.stdout, sys.stderr = streams
    captured = capsys.readouterr()
    assert TOKEN not in captured.out + captured.err
    assert "30 seconds" in captured.err
    assert _shown(url) in captured.err


# --- init-factory: the counter check ------------------------------------------


def _init_project(tmp_path: Path, env: dict[str, str], url: str) -> Path:
    project = tmp_path / "project"
    _git(env, "init", "--quiet", str(project))
    _git(
        env, "-C", str(project), "-c", "user.name=t", "-c", "user.email=t@example.com",
        "commit", "--quiet", "--allow-empty", "-m", "first",
    )
    _git(env, "-C", str(project), "remote", "add", "origin", url)
    return project


def _init(project: Path, env: dict[str, str]) -> subprocess.CompletedProcess:
    run_env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    run_env["GIT_SSH_COMMAND"] = env["GIT_SSH_COMMAND"]
    return subprocess.run(
        [sys.executable, str(INIT_FACTORY),
         "--source", str(REPO_ROOT), "--target", str(project),
         "--cli", "claude", "--project-name", "demo"],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, env=run_env,
        check=False, timeout=300,
    )


def _assert_user_info_warning(result: subprocess.CompletedProcess, url: str) -> None:
    assert result.returncode == 0, result.stderr
    _assert_no_token(result)
    warning = [
        line for line in result.stdout.splitlines()
        if "credential helper" in line or "user info" in line
    ]
    assert warning, result.stdout
    assert _shown(url) in result.stdout


def test_sec_0007_init_factory_warns_on_user_info_and_checks_the_counter(
    tmp_path, env, url
):
    project = _init_project(tmp_path, env, url)
    result = _init(project, env)
    _assert_user_info_warning(result, url)
    assert "counter: missing on origin" in result.stdout


def test_sec_0007_init_factory_names_an_unreachable_origin_without_the_token(
    tmp_path, env
):
    url = _closed_port_url()
    project = _init_project(tmp_path, env, url)
    result = _init(project, env)
    _assert_user_info_warning(result, url)
    assert "does not answer" in result.stdout
