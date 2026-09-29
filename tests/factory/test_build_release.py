"""Contract tests for the build-release script.

Covers: version-branch validation, asset production, SHA256SUMS
verification, deterministic archive (reproducibility), and failure
cleanup.
"""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
import tarfile
from pathlib import Path

import pytest
from conftest import REPO_ROOT


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_repo(tmp_path: Path, branch: str, version: str) -> Path:
    """Create a minimal git repo with a VERSION file on *branch*."""
    repo = tmp_path / "repo"
    repo.mkdir()

    # Minimal factory source tree that build-release needs.
    scripts = repo / "packages" / "factory" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "install-agent-factory").write_text(
        "#!/usr/bin/env python3\nprint('placeholder')\n"
    )
    os.chmod(scripts / "install-agent-factory", 0o755)

    # VERSION file
    version_dir = repo / "packages" / "factory"
    (version_dir / "VERSION").write_text(version)

    # Minimal factory content for the tarball
    agents_dir = repo / "packages" / "factory" / "agents"
    agents_dir.mkdir()
    (agents_dir / "example.md").write_text("# Example agent\n")

    # Git init on the requested branch
    env = {**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@t"}
    subprocess.run(["git", "init", "-b", branch, str(repo)],
                   check=True, capture_output=True, env=env)
    subprocess.run(["git", "-C", str(repo), "add", "."],
                   check=True, capture_output=True, env=env)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "init"],
                   check=True, capture_output=True, env=env)
    return repo


def _run_build(repo: Path, output: Path, extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
    """Run build-release in *repo* with --output *output*."""
    script = REPO_ROOT / "packages" / "factory" / "scripts" / "build-release"
    cmd = [str(script), "--output", str(output)]
    if extra_args:
        cmd.extend(extra_args)
    return subprocess.run(
        cmd,
        cwd=str(repo),
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# Slice 1 — Version-branch validation
# ---------------------------------------------------------------------------

class TestVersionBranchValidation:
    """build-release exits non-zero when VERSION does not match the branch."""

    def test_rc_on_main_rejected(self, tmp_path):
        repo = _make_repo(tmp_path, "main", "1.0.0-rc")
        out = tmp_path / "release"
        result = _run_build(repo, out)
        assert result.returncode != 0
        assert not out.exists() or not list(out.iterdir())

    def test_bare_version_on_dev_rejected(self, tmp_path):
        repo = _make_repo(tmp_path, "dev", "1.0.0")
        out = tmp_path / "release"
        result = _run_build(repo, out)
        assert result.returncode != 0
        assert not out.exists() or not list(out.iterdir())

    def test_valid_version_on_main_accepted(self, tmp_path):
        repo = _make_repo(tmp_path, "main", "1.0.0")
        out = tmp_path / "release"
        result = _run_build(repo, out)
        assert result.returncode == 0

    def test_valid_rc_on_dev_accepted(self, tmp_path):
        repo = _make_repo(tmp_path, "dev", "1.0.0-rc")
        out = tmp_path / "release"
        result = _run_build(repo, out)
        assert result.returncode == 0

    def test_malformed_version_rejected(self, tmp_path):
        repo = _make_repo(tmp_path, "main", "not-a-version")
        out = tmp_path / "release"
        result = _run_build(repo, out)
        assert result.returncode != 0

    def test_bare_version_on_feature_branch_rejected(self, tmp_path):
        repo = _make_repo(tmp_path, "feature/foo", "1.0.0")
        out = tmp_path / "release"
        result = _run_build(repo, out)
        assert result.returncode != 0

    def test_rc_on_feature_branch_accepted(self, tmp_path):
        repo = _make_repo(tmp_path, "feature/foo", "1.0.0-rc")
        out = tmp_path / "release"
        result = _run_build(repo, out)
        assert result.returncode == 0


# ---------------------------------------------------------------------------
# Slice 2 — Asset production
# ---------------------------------------------------------------------------

class TestAssetProduction:
    """build-release produces the required three-file asset set."""

    def test_produces_three_files(self, tmp_path):
        repo = _make_repo(tmp_path, "main", "2.0.0")
        out = tmp_path / "release"
        result = _run_build(repo, out)
        assert result.returncode == 0
        assert (out / "install-agent-factory").exists()
        assert (out / "agent-factory.tar.gz").exists()
        assert (out / "SHA256SUMS").exists()

    def test_install_script_is_verbatim_copy(self, tmp_path):
        repo = _make_repo(tmp_path, "main", "2.0.0")
        out = tmp_path / "release"
        _run_build(repo, out)
        source = repo / "packages" / "factory" / "scripts" / "install-agent-factory"
        assert (out / "install-agent-factory").read_bytes() == source.read_bytes()

    def test_sha256sums_verifies(self, tmp_path):
        repo = _make_repo(tmp_path, "main", "2.0.0")
        out = tmp_path / "release"
        _run_build(repo, out)
        # Parse SHA256SUMS and verify
        sums_text = (out / "SHA256SUMS").read_text()
        for line in sums_text.strip().splitlines():
            digest, fname = line.split()
            computed = hashlib.sha256((out / fname).read_bytes()).hexdigest()
            assert digest == computed, f"digest mismatch for {fname}"

    def test_archive_contains_factory_content(self, tmp_path):
        repo = _make_repo(tmp_path, "main", "2.0.0")
        out = tmp_path / "release"
        _run_build(repo, out)
        with tarfile.open(out / "agent-factory.tar.gz", "r:gz") as tf:
            names = tf.getnames()
        # Should contain the factory tree
        assert any("agents/example.md" in n for n in names)

    def test_default_output_dir(self, tmp_path):
        """When --output is omitted, files go to ./release/."""
        repo = _make_repo(tmp_path, "main", "2.0.0")
        script = REPO_ROOT / "packages" / "factory" / "scripts" / "build-release"
        result = subprocess.run(
            [str(script)],
            cwd=str(repo),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert (repo / "release" / "agent-factory.tar.gz").exists()


# ---------------------------------------------------------------------------
# Slice 3 — Deterministic archive (reproducibility)
# ---------------------------------------------------------------------------

class TestDeterministicArchive:
    """Two builds from the same source produce identical archive digests."""

    def test_reproducible_digest(self, tmp_path):
        repo = _make_repo(tmp_path, "main", "3.0.0")
        out1 = tmp_path / "release1"
        out2 = tmp_path / "release2"
        _run_build(repo, out1)
        _run_build(repo, out2)
        d1 = hashlib.sha256((out1 / "agent-factory.tar.gz").read_bytes()).hexdigest()
        d2 = hashlib.sha256((out2 / "agent-factory.tar.gz").read_bytes()).hexdigest()
        assert d1 == d2

    def test_archive_entries_have_fixed_timestamps(self, tmp_path):
        repo = _make_repo(tmp_path, "main", "3.0.0")
        out = tmp_path / "release"
        _run_build(repo, out)
        with tarfile.open(out / "agent-factory.tar.gz", "r:gz") as tf:
            for member in tf.getmembers():
                assert member.mtime == 0, f"{member.name} has mtime {member.mtime}"

    def test_archive_entries_have_fixed_owner(self, tmp_path):
        repo = _make_repo(tmp_path, "main", "3.0.0")
        out = tmp_path / "release"
        _run_build(repo, out)
        with tarfile.open(out / "agent-factory.tar.gz", "r:gz") as tf:
            for member in tf.getmembers():
                assert member.uname == "root", f"{member.name} uname={member.uname}"
                assert member.gname == "root", f"{member.name} gname={member.gname}"
                assert member.uid == 0
                assert member.gid == 0


# ---------------------------------------------------------------------------
# Slice 4 — Failure cleanup
# ---------------------------------------------------------------------------

class TestFailureCleanup:
    """Failed build leaves no partial output."""

    def test_version_mismatch_no_output(self, tmp_path):
        repo = _make_repo(tmp_path, "main", "1.0.0-rc")
        out = tmp_path / "release"
        result = _run_build(repo, out)
        assert result.returncode != 0
        # Either no dir or empty dir
        if out.exists():
            assert list(out.iterdir()) == []

    def test_missing_install_script_no_output(self, tmp_path):
        repo = _make_repo(tmp_path, "main", "1.0.0")
        # Remove the install-agent-factory so build fails
        (repo / "packages" / "factory" / "scripts" / "install-agent-factory").unlink()
        out = tmp_path / "release"
        result = _run_build(repo, out)
        assert result.returncode != 0
        if out.exists():
            assert list(out.iterdir()) == []
