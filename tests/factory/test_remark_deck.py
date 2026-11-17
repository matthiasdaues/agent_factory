"""Tests for `remark-deck`: create, check and build a deck on the monospace grid."""

from __future__ import annotations

import datetime
import subprocess
import sys
from pathlib import Path

from conftest import SOURCE_SCRIPTS_DIR

SCRIPT = SOURCE_SCRIPTS_DIR / "remark-deck"
TODAY = datetime.date.today().isoformat()


def run(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True,
        text=True,
        check=False,
    )


def write_slides(deck: Path, body: str, head: str = "% title: Test\n") -> None:
    deck.mkdir(parents=True, exist_ok=True)
    (deck / "slides.txt").write_text(head + body, encoding="utf-8")


def grid(rows: list[str], size: str = "") -> str:
    return "\n".join(["```grid" + (f" {size}" if size else ""), *rows, "```"]) + "\n"


def test_new_writes_a_dated_page_with_its_assets(tmp_path: Path) -> None:
    deck = tmp_path / "deck"
    result = run("new", deck, "--title", "Agent & Factory", "--lang", "de")
    assert result.returncode == 0, result.stdout + result.stderr
    page = deck / f"{TODAY}_agent-factory.html"
    assert page.is_file()
    assert not (deck / "index.html").exists()
    html = page.read_text(encoding="utf-8")
    assert "<title>Agent &amp; Factory</title>" in html
    assert '<html lang="de">' in html
    assert "%%DECK%%" not in html
    for name in (
        "remark.min.js",
        "fonts/SourceCodePro-ExtraLight.woff2",
        "fonts/SourceCodePro-Medium.woff2",
        "fonts/CormorantGaramond-Light.woff2",
        "media/placeholder.svg",
        "licenses/SourceCodePro-OFL.txt",
        "licenses/CormorantGaramond-OFL.txt",
        "licenses/remark-MIT.txt",
    ):
        assert (deck / name).is_file(), name


def test_new_with_sample_builds_ten_clean_slides(tmp_path: Path) -> None:
    result = run("new", tmp_path / "deck", "--sample", "--topic", "Demo Deck")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "10 slides, 0 problems" in result.stdout
    assert (tmp_path / "deck" / f"{TODAY}_demo-deck.html").is_file()


def test_new_does_not_overwrite_a_deck(tmp_path: Path) -> None:
    deck = tmp_path / "deck"
    write_slides(deck, grid(["mine"]))
    before = (deck / "slides.txt").read_text(encoding="utf-8")
    result = run("new", deck)
    assert result.returncode == 2
    assert (deck / "slides.txt").read_text(encoding="utf-8") == before


def test_header_sets_the_file_name(tmp_path: Path) -> None:
    deck = tmp_path / "deck"
    write_slides(deck, grid(["x"]), head="% title: Ignored\n% topic: Q3 Review\n% date: 2026-01-31\n")
    result = run("build", deck)
    assert result.returncode == 0, result.stdout + result.stderr
    assert (deck / "2026-01-31_q3-review.html").is_file()


def test_invalid_date_header_stops_the_build(tmp_path: Path) -> None:
    deck = tmp_path / "deck"
    write_slides(deck, grid(["x"]), head="% date: 31.01.2026\n")
    assert run("build", deck).returncode == 2


def test_missing_source_is_a_precondition_failure(tmp_path: Path) -> None:
    assert run("check", tmp_path).returncode == 2


def test_markers_take_no_cells(tmp_path: Path) -> None:
    deck = tmp_path / "deck"
    row = "**" + "a" * 20 + "**" + "!!" + "b" * 42 + "!!"
    write_slides(deck, grid([row]))
    result = run("check", deck)
    assert result.returncode == 0, result.stdout


def test_dashes_inside_a_grid_stay_a_row(tmp_path: Path) -> None:
    deck = tmp_path / "deck"
    write_slides(deck, grid(["top", "---", "bottom"]) + "---\n" + grid(["second"]))
    result = run("check", deck)
    assert result.returncode == 0, result.stdout
    assert "2 slides, 0 problems" in result.stdout


def test_check_reports_each_problem_and_build_writes_no_page(tmp_path: Path) -> None:
    deck = tmp_path / "deck"
    rows = ["x" * 63, "**open", "a\tb"] + ["y"] * 12
    body = grid(rows) + "@img media/missing.png 50 0 20 5\n@cross 0 0 1\n@footer\n@wobble 1 2 3 4\n"
    write_slides(deck, body + "---\n```grid 40x10\nunclosed\n")
    result = run("check", deck)
    assert result.returncode == 1
    for expected in (
        "slide 1: 15 rows, the grid has 14",
        "slide 1: row 0 is 63 columns wide, the grid has 62",
        "slide 1: row 1: unpaired **",
        "slide 1: row 2 contains a tab",
        "slide 1: @img: file not found media/missing.png",
        "slide 1: @img leaves the grid: cols 50-69, rows 0-4",
        "slide 1: @cross: needs four whole numbers",
        "slide 1: @footer needs its text",
        "slide 1: unknown directive @wobble",
        "slide 2: grid block is not closed",
    ):
        assert expected in result.stdout, expected
    assert run("build", deck).returncode == 1
    assert not list(deck.glob("*.html"))


def test_grid_size_sets_the_bounds(tmp_path: Path) -> None:
    deck = tmp_path / "deck"
    write_slides(deck, grid(["z" * 99] * 25, size="99x25") + "@blank 0 0 99 25\n")
    assert run("check", deck).returncode == 0
    write_slides(deck, grid(["z" * 100], size="99x25"))
    assert "row 0 is 100 columns wide, the grid has 99" in run("check", deck).stdout
