"""Contract tests for gitignore-style glob matching (Layer 2d).

Covers: *, **, ?, literal matching, and cross-tool agreement between
glob_match used in step-guard and premerge-check.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure dispatch_lib is importable
sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent.parent / "factory" / "scripts")
)

from dispatch_lib import glob_match

# ---------------------------------------------------------------------------
# * — matches within a single segment
# ---------------------------------------------------------------------------


class TestSingleStar:
    def test_matches_filename(self) -> None:
        assert glob_match("UC-*.md", "UC-01.md") is True

    def test_does_not_cross_slash(self) -> None:
        assert glob_match("UC-*.md", "sub/UC-01.md") is False

    def test_matches_empty_segment(self) -> None:
        assert glob_match("UC-*.md", "UC-.md") is True

    def test_matches_multiple_chars(self) -> None:
        assert glob_match("*.py", "dispatch_lib.py") is True

    def test_star_in_middle_of_path(self) -> None:
        assert glob_match("src/*.py", "src/main.py") is True

    def test_star_does_not_match_deeper(self) -> None:
        assert glob_match("src/*.py", "src/sub/main.py") is False

    def test_only_star(self) -> None:
        assert glob_match("*", "anything") is True

    def test_only_star_no_slash(self) -> None:
        assert glob_match("*", "a/b") is False


# ---------------------------------------------------------------------------
# ** — matches across segments
# ---------------------------------------------------------------------------


class TestDoubleStar:
    def test_matches_deeply_nested(self) -> None:
        assert glob_match("src/**/*.py", "src/a/b/c.py") is True

    def test_matches_zero_intermediate_segments(self) -> None:
        assert glob_match("src/**/*.py", "src/main.py") is True

    def test_at_end_matches_everything(self) -> None:
        assert glob_match("docs/**", "docs/spec/use_cases/UC-13.md") is True

    def test_at_start(self) -> None:
        assert glob_match("**/*.md", "a/b/c.md") is True

    def test_at_start_matches_root(self) -> None:
        assert glob_match("**/*.md", "README.md") is True

    def test_double_star_alone(self) -> None:
        assert glob_match("**", "any/path/at/all.txt") is True

    def test_double_star_alone_single_file(self) -> None:
        assert glob_match("**", "file.txt") is True


# ---------------------------------------------------------------------------
# ? — matches one non-separator character
# ---------------------------------------------------------------------------


class TestQuestionMark:
    def test_matches_one_char(self) -> None:
        assert glob_match("file?.py", "file1.py") is True

    def test_does_not_match_two_chars(self) -> None:
        assert glob_match("file?.py", "file12.py") is False

    def test_does_not_match_slash(self) -> None:
        assert glob_match("a?b", "a/b") is False

    def test_matches_any_single_char(self) -> None:
        assert glob_match("?.txt", "x.txt") is True


# ---------------------------------------------------------------------------
# Literal matching
# ---------------------------------------------------------------------------


class TestLiteral:
    def test_exact_path(self) -> None:
        assert glob_match("src/main.py", "src/main.py") is True

    def test_case_sensitive(self) -> None:
        assert glob_match("README.md", "readme.md") is False

    def test_no_match(self) -> None:
        assert glob_match("src/main.py", "src/other.py") is False


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_empty_pattern_matches_empty_path(self) -> None:
        assert glob_match("", "") is True

    def test_empty_pattern_does_not_match_nonempty(self) -> None:
        assert glob_match("", "file.py") is False

    def test_paths_with_special_chars(self) -> None:
        assert glob_match("docs/[notes].md", "docs/[notes].md") is True

    def test_only_wildcards(self) -> None:
        assert glob_match("**/*", "any/path.txt") is True


# ---------------------------------------------------------------------------
# Cross-tool agreement: glob_match used in premerge-check scope checking
# ---------------------------------------------------------------------------


class TestPremergeCheckAgreement:
    """Verify that glob_match produces the same result whether called directly
    (as step-guard would) or through premerge-check's scope-glob logic."""

    def test_allow_in_scope(self) -> None:
        pattern = "docs/spec/use_cases/UC-*.md"
        path = "docs/spec/use_cases/UC-13.md"
        assert glob_match(pattern, path) is True

    def test_deny_out_of_scope(self) -> None:
        pattern = "docs/spec/use_cases/UC-*.md"
        path = "src/main.py"
        assert glob_match(pattern, path) is False

    def test_glob_rejects_what_prefix_would_accept(self) -> None:
        """A path that starts with the pattern's prefix but doesn't match
        the full glob should be rejected."""
        pattern = "docs/spec/use_cases/UC-*.md"
        # This starts with "docs/spec/use_cases/" but isn't UC-*.md
        path = "docs/spec/use_cases/overview.rst"
        assert glob_match(pattern, path) is False
