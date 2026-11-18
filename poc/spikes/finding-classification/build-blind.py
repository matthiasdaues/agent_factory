"""Build blind copies of review findings from their filing commits.

Usage: python3 -I build-blind.py <repo> <run-dir> <key-dir> [ID ...]

For each finding, the script finds the commit that added the file, reads the
file as filed, and removes the rating. It writes:

- <run-dir>/blind/<ID>.md: the finding without the rating.
- <run-dir>/filing.tsv: ID, filing SHA, filing date.
- <key-dir>/<run>-strip-log.md: every line the script removed, per finding.
  It names the filed rating, so it stays out of the raters' run folder.
- <key-dir>/answer-key.tsv: ID, source, category, severity as filed. The
  script adds rows to an existing key and keeps the rows of other IDs.

Without IDs, the script takes every docs/findings/*.md at HEAD.
Read the strip log before you dispatch raters. It must list only rating
fields, resolution text, and lines that name the severity.
"""

import re
import subprocess
import sys
from pathlib import Path

RATING_FIELDS = re.compile(r"^(severity|category|status|blocking|priority|rating):")
# The only resolution label in the filed gigacron findings. Body labels such
# as "**Decision case:**" are part of the finding and stay.
RESOLUTION = re.compile(r"\n\*\*Resolution\b")
NAMES_SEVERITY = re.compile(r"severity|\b(critical|major|minor)\b", re.IGNORECASE)


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", repo, *args], check=True, capture_output=True, text=True
    ).stdout


def field(frontmatter, name):
    m = re.search(rf"^{name}:\s*(\S+)", frontmatter, re.MULTILINE)
    return m.group(1) if m else ""


def strip(text):
    _, fm, body = text.split("---\n", 2)
    removed = [line for line in fm.splitlines() if RATING_FIELDS.match(line)]
    fm = "\n".join(l for l in fm.splitlines() if not RATING_FIELDS.match(l)) + "\n"
    parts = RESOLUTION.split(body, maxsplit=1)
    if len(parts) == 2:
        removed += ["**Resolution" + parts[1].rstrip()]
    kept = []
    for line in parts[0].rstrip().splitlines():
        (removed if NAMES_SEVERITY.search(line) else kept).append(line)
    return "---\n" + fm + "---\n" + "\n".join(kept) + "\n", removed


def main():
    repo, run_dir, key_dir, *ids = sys.argv[1:]
    run, key = Path(run_dir), Path(key_dir)
    (run / "blind").mkdir(parents=True, exist_ok=True)
    key.mkdir(parents=True, exist_ok=True)
    if not ids:
        ids = sorted(p.stem for p in Path(repo, "docs/findings").glob("*-[0-9]*.md"))
    filing, answers, log = [], [], ["# Strip log", ""]
    for fid in ids:
        path = f"docs/findings/{fid}.md"
        added = git(repo, "log", "--diff-filter=A", "--format=%H %cs", "--", path)
        sha, date = added.strip().splitlines()[-1].split()
        filed = git(repo, "show", f"{sha}:{path}")
        fm = filed.split("---\n", 2)[1]
        answers.append(
            "\t".join(
                [fid, field(fm, "source"), field(fm, "category"), field(fm, "severity")]
            )
        )
        filing.append(f"{fid}\t{sha} {date}")
        blind, removed = strip(filed)
        (run / "blind" / f"{fid}.md").write_text(blind)
        log += [f"## {fid}", "", "```"] + removed + ["```", ""]
    (run / "filing.tsv").write_text("\n".join(filing) + "\n")
    log_file = key / f"{run.name}-strip-log.md"
    log_file.write_text("\n".join(log))
    # Merge, so a new run keeps the filed ratings of earlier runs.
    key_file = key / "answer-key.tsv"
    rows = {}
    if key_file.exists():
        rows = {l.split("\t", 1)[0]: l for l in key_file.read_text().splitlines() if l}
    rows.update({a.split("\t", 1)[0]: a for a in answers})
    key_file.write_text("\n".join(rows[i] for i in sorted(rows)) + "\n")
    print(f"{len(ids)} findings; read {log_file} before dispatch")


if __name__ == "__main__":
    main()
