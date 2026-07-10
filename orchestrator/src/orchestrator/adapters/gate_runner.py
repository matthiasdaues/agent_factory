"""Working-tree cleanliness gate adapter."""

import subprocess
from pathlib import Path
from typing import List

from orchestrator.entities import GateResult


class WorkingTreeGate:
    """Working-tree cleanliness gate (ADR-0013).

    Agents commit their own work; pre-commit hooks fire inside the agent
    subprocess. The orchestrator's gate is a working-tree cleanliness
    check after the agent exits.
    """

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def verify(self, cwd: Path, exit_code: int) -> GateResult:
        """Check working-tree state after agent exit.

        Four-cell matrix:
        - exit 0 + clean → passed
        - exit 0 + dirty → confabulation (trust violation, VR-025)
        - non-zero + dirty → failed (clean tree before retry)
        - non-zero + clean → failed
        """
        try:
            dirty_files = self._dirty_files(cwd)
        except RuntimeError as exc:
            return GateResult(
                passed=False,
                errored=True,
                hook="git-error",
                error_count=0,
                output=str(exc),
            )

        if exit_code == 0:
            if not dirty_files:
                return GateResult(
                    passed=True,
                    errored=False,
                    hook="working-tree",
                    error_count=0,
                )
            return GateResult(
                passed=False,
                errored=True,
                hook="confabulation",
                error_count=len(dirty_files),
                output="exit 0 but uncommitted changes: " + ", ".join(dirty_files),
            )

        return GateResult(
            passed=False,
            errored=False,
            hook="working-tree",
            error_count=len(dirty_files),
            output=", ".join(dirty_files) if dirty_files else "",
        )

    def clean_tree(self, cwd: Path) -> None:
        """Reset working tree before retry (ADR-0013, VR-026)."""
        subprocess.run(
            ["git", "checkout", "."],
            cwd=cwd,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "clean", "-fd"],
            cwd=cwd,
            capture_output=True,
            check=True,
        )

    def artifacts_changed(self, artifact_paths: List[str]) -> bool:
        """Return True if any declared artifact has uncommitted changes (VR-012)."""
        for pattern in artifact_paths:
            matches = list(self.repo_root.glob(pattern))
            if not matches:
                continue
            resolved = [str(match.relative_to(self.repo_root)) for match in matches]
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD", "--"] + resolved,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
            )
            if result.stdout.strip():
                return True
            result_untracked = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard", "--"] + resolved,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
            )
            if result_untracked.stdout.strip():
                return True
        return False

    def _dirty_files(self, cwd: Path) -> list[str]:
        """Return list of dirty file paths from git status.

        Raises RuntimeError if git status fails, so verify() can surface
        the failure as an errored GateResult rather than hiding it.
        """
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"git status failed (rc={result.returncode}): {result.stderr.strip()}"
            )
        files = []
        for line in result.stdout.splitlines():
            if line.strip():
                files.append(line[3:].strip().strip('"'))
        return files
