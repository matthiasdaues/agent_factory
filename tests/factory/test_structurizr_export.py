"""The structurizr wrapper writes SVGs without the render time.

Structurizr puts the time of the export into the footer of every diagram.
Without removing it, an export of an unchanged diagram changes the file, and
each arch-lint run that exports rewrites every image in docs/assets/images.

The tests replace `docker` with a stub on PATH, so they need no Docker.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR

STAMP = re.compile(r"[A-Z][a-z]+day, [A-Z][a-z]+ \d{1,2}, \d{4} at \d{1,2}:\d{2} [AP]M")

SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg"><text id="v-1"><tspan dy="0" >'
    'Containers</tspan></text><text id="v-2"><tspan dy="0" >{stamp}</tspan>'
    "</text></svg>"
)

FAKE_DOCKER = """#!/bin/bash
# Stub for `docker run ... export -output /workspace/assets/images`:
# writes one SVG the way Structurizr names and dates it.
printf '%s' "$FAKE_SVG" > "$FAKE_IMAGES/structurizr-Containers.svg"
"""


def export(tmp_path: Path, stamp: str) -> Path:
    docs = tmp_path / "docs"
    (docs / "spec").mkdir(parents=True, exist_ok=True)
    (docs / "spec" / "architecture.dsl").write_text("workspace {}\n", encoding="utf-8")
    images = docs / "assets" / "images"
    images.mkdir(parents=True, exist_ok=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    docker = bin_dir / "docker"
    docker.write_text(FAKE_DOCKER, encoding="utf-8")
    docker.chmod(0o755)
    env = {k: v for k, v in os.environ.items() if not k.startswith("STRUCTURIZR_")}
    env.update(
        PATH=f"{bin_dir}:{env['PATH']}",
        FAKE_SVG=SVG.format(stamp=stamp),
        FAKE_IMAGES=str(images),
    )
    result = subprocess.run(
        [str(SOURCE_SCRIPTS_DIR / "structurizr"), "export-all"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    return images / "Containers.svg"


def test_export_removes_the_render_time(tmp_path: Path) -> None:
    svg = export(
        tmp_path, "Wednesday, November 18, 2026 at 5:26 PM Coordinated Universal Time"
    )
    text = svg.read_text(encoding="utf-8")
    assert not STAMP.search(text)
    assert '<tspan dy="0" >Containers</tspan>' in text
    assert not (svg.parent / "structurizr-Containers.svg").exists()


def test_two_exports_of_an_unchanged_diagram_are_identical(tmp_path: Path) -> None:
    first = export(
        tmp_path, "Wednesday, November 18, 2026 at 5:26 PM Coordinated Universal Time"
    )
    before = first.read_bytes()
    second = export(
        tmp_path, "Thursday, November 19, 2026 at 9:55 AM Coordinated Universal Time"
    )
    assert second.read_bytes() == before


def test_committed_diagrams_carry_no_render_time() -> None:
    dated = [
        p.name
        for p in sorted((REPO_ROOT / "docs" / "assets" / "images").glob("*.svg"))
        if STAMP.search(p.read_text(encoding="utf-8"))
    ]
    assert dated == []
