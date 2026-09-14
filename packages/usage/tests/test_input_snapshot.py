"""Tests for usage.input_snapshot — file selection, sorting, and digest."""

from __future__ import annotations

import hashlib
from pathlib import Path

from usage.input_snapshot import snapshot


class TestFileSelection:
    """Top-level JSONL files are selected; subdirectory files excluded."""

    def test_selects_top_level_jsonl(self, snapshot_dir: Path) -> None:
        paths, _ = snapshot(snapshot_dir)
        names = [p.name for p in paths]
        assert "alpha.jsonl" in names
        assert "bravo.jsonl" in names
        assert "charlie.jsonl" in names

    def test_excludes_subdirectory_files(self, snapshot_dir: Path) -> None:
        paths, _ = snapshot(snapshot_dir)
        names = [p.name for p in paths]
        assert "nested.jsonl" not in names

    def test_returns_absolute_paths(self, snapshot_dir: Path) -> None:
        paths, _ = snapshot(snapshot_dir)
        for p in paths:
            assert p.is_absolute()

    def test_exactly_three_files(self, snapshot_dir: Path) -> None:
        paths, _ = snapshot(snapshot_dir)
        assert len(paths) == 3


class TestSortOrder:
    """Sorted by filename encoded to UTF-8 bytes, order-independent."""

    def test_alphabetical_order(self, snapshot_dir: Path) -> None:
        paths, _ = snapshot(snapshot_dir)
        names = [p.name for p in paths]
        assert names == ["alpha.jsonl", "bravo.jsonl", "charlie.jsonl"]

    def test_sort_order_independence(self, tmp_path: Path) -> None:
        """Same files created in different order produce identical results."""
        # Create files in reverse order.
        for name in ["zulu.jsonl", "mike.jsonl", "alpha.jsonl"]:
            (tmp_path / name).write_text("{}\n")

        paths_a, digest_a = snapshot(tmp_path)

        # Create a second directory with different creation order.
        dir_b = tmp_path / "b"
        dir_b.mkdir()
        for name in ["alpha.jsonl", "zulu.jsonl", "mike.jsonl"]:
            (dir_b / name).write_text("{}\n")

        paths_b, digest_b = snapshot(dir_b)

        names_a = [p.name for p in paths_a]
        names_b = [p.name for p in paths_b]
        assert names_a == names_b
        assert digest_a == digest_b


class TestEmptyDirectory:
    """Empty directory returns empty list and a digest."""

    def test_empty_dir_returns_empty_list(self, empty_dir: Path) -> None:
        paths, _ = snapshot(empty_dir)
        assert paths == []

    def test_empty_dir_returns_digest(self, empty_dir: Path) -> None:
        _, digest = snapshot(empty_dir)
        expected = hashlib.sha256(b"").hexdigest()
        assert digest == expected


class TestContentDigest:
    """SHA-256 of sorted filenames, each newline-terminated."""

    def test_known_digest(self, snapshot_dir: Path) -> None:
        _, digest = snapshot(snapshot_dir)
        expected_input = b"alpha.jsonl\nbravo.jsonl\ncharlie.jsonl\n"
        expected = hashlib.sha256(expected_input).hexdigest()
        assert digest == expected

    def test_digest_is_hex_string(self, snapshot_dir: Path) -> None:
        _, digest = snapshot(snapshot_dir)
        assert len(digest) == 64
        int(digest, 16)  # raises if not valid hex


class TestNewListPerInvocation:
    """Each call returns a distinct list object."""

    def test_distinct_list_objects(self, snapshot_dir: Path) -> None:
        paths_a, _ = snapshot(snapshot_dir)
        paths_b, _ = snapshot(snapshot_dir)
        assert paths_a == paths_b
        assert paths_a is not paths_b
