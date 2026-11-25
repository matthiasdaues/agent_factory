"""Agent Factory step by step: diagrams on character grids, written to slides.txt."""

import re
import sys
import textwrap
from pathlib import Path

# Usage: python3 make_slides.py [slides.txt], then remark-deck build on this folder.
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("slides.txt")
TOO_WIDE = []
MARKERS = re.compile(r"\*\*|%%|__|~~|!!")
FOOTER = "agent factory · step by step"


class Canvas:
    def __init__(self, cols, rows):
        self.cols, self.rows = cols, rows
        self.cells = [[" "] * cols for _ in range(rows)]
        self.marks = []

    def put(self, x, y, text):
        for i, ch in enumerate(text):
            assert 0 <= x + i < self.cols and 0 <= y < self.rows, (x, y, text)
            self.cells[y][x + i] = ch

    def box(self, x, y, w, h, lines=(), align="center"):
        self.put(x, y, "┌" + "─" * (w - 2) + "┐")
        for r in range(1, h - 1):
            self.put(x, y + r, "│" + " " * (w - 2) + "│")
        self.put(x, y + h - 1, "└" + "─" * (w - 2) + "┘")
        for i, line in enumerate(lines):
            if len(line) > w - 4:
                TOO_WIDE.append((line, len(line), w - 4))
            pad = (w - 2 - len(line)) // 2 if align == "center" else 1
            self.put(x + 1 + pad, y + 1 + i, line)

    def vline(self, x, y1, y2, end=None):
        for y in range(y1, y2 + 1):
            self.put(x, y, "│")
        if end:
            self.put(x, y2, end)

    def hline(self, x1, x2, y, end=None):
        for x in range(x1, x2 + 1):
            self.put(x, y, "─")
        if end == "►":
            self.put(x2, y, end)
        elif end == "◄":
            self.put(x1, y, end)

    def mark(self, row, text, marker):
        self.marks.append((row, text, marker))

    def rows_out(self):
        out = ["".join(r).rstrip() for r in self.cells]
        for row, text, marker in self.marks:
            assert text in out[row], (row, text)
            out[row] = out[row].replace(text, f"{marker}{text}{marker}", 1)
        return out


def title(c, text, sub=None):
    c.put(4, 1, text)
    c.mark(1, text, "**")
    if sub:
        c.put(4, 2, sub)
        c.mark(2, sub, "%%")


def text(c, x, y, line, marker=None):
    c.put(x, y, line)
    if marker:
        c.mark(y, line, marker)


def slide(c, footer=FOOTER):
    rows = c.rows_out()
    for r in rows:
        assert len(MARKERS.sub("", r)) <= c.cols, r
    return f"```grid {c.cols}x{c.rows}\n" + "\n".join(rows) + f"\n```\n@footer {footer}"


slides = []

# 1. Title ---------------------------------------------------------------------
c = Canvas(40, 10)
text(c, 3, 2, "AGENT FACTORY", "**")
text(c, 3, 3, "STEP BY STEP", "**")
text(c, 3, 5, "How an idea becomes", "%%")
text(c, 3, 6, "code you can trust")
text(c, 3, 8, "an introduction", "~~")
slides.append(slide(c, "20 November 2026"))

# 2. The one idea --------------------------------------------------------------
c = Canvas(62, 14)
text(c, 3, 2, "YOU DECIDE.", "**")
text(c, 3, 3, "THE ASSISTANT DOES THE WORK.", "**")
text(c, 3, 4, "YOU APPROVE EACH STEP.", "**")
text(c, 3, 6, "The factory never builds everything at once.")
text(c, 3, 7, "It works in small, visible steps")
text(c, 3, 8, "and stops after each one.")
text(c, 3, 10, "An AI works fast, but noisily.", "%%")
text(c, 3, 11, "The cure is frequent, cheap checking:", "%%")
text(c, 3, 12, "by a tool, a test, or you.", "%%")
slides.append(slide(c))

# 3. Five words ------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "FIVE WORDS", "all the vocabulary you need to start")
c.box(4, 5, 20, 4, ["PLAYBOOK", "the recipe"])
c.hline(24, 31, 6, "►")
c.put(25, 5, "calls")
c.box(32, 5, 20, 4, ["AGENT", "one job"])
c.hline(52, 59, 6, "►")
c.put(52, 5, "delivers")
c.box(60, 5, 16, 4, ["ARTEFACT", "a document"])
c.hline(76, 80, 6, "►")
c.box(81, 5, 15, 4, ["GATE", "checks it"])
c.vline(42, 9, 10, "▼")
c.put(44, 9, "follows")
c.box(32, 11, 20, 4, ["SKILL", "the procedure"])
c.box(4, 11, 20, 4, ["CONTEXT", "the fact sheet"])
c.hline(24, 27, 12)
c.put(28, 12, "┘")
c.vline(28, 8, 11)
c.put(28, 7, "┌")
c.hline(29, 31, 7, "►")
c.put(14, 10, "knowledge")
rows = [("Agent", "one job: write the requirements, review the architecture, fix one bug"),
        ("Skill", "the written procedure an agent follows to do its job well"),
        ("Playbook", "the recipe: which agents run, in what order, for a common situation"),
        ("Gate", "an automatic check that catches mistakes before they cost you time"),
        ("Context", "a few files where the project declares its stack, workflow and rules")]
for i, (word, meaning) in enumerate(rows):
    y = 17 + i
    text(c, 4, y, word, "**")
    c.put(15, y, meaning)
text(c, 4, 23, "The assistant reads the catalogue itself: INDEX.yaml lists every agent, skill and playbook.", "~~")
slides.append(slide(c))

# 4. Worker and checker ------------------------------------------------------------
c = Canvas(99, 25)
title(c, "WHOEVER WORKS DOES NOT CHECK", "the author and the reviewer are never the same agent")
c.box(4, 5, 22, 5, ["AUTHOR", "session 1"])
c.hline(26, 34, 7, "►")
c.box(35, 5, 26, 5, ["ARTEFACT", "a specification, an", "architecture, code"])
c.hline(61, 68, 7, "►")
c.box(69, 5, 26, 5, ["REVIEWER", "a new, empty session", "sees only the artefact"])
c.vline(82, 10, 12)
c.put(82, 12, "┘")
c.hline(15, 81, 12)
c.put(15, 12, "┌")
c.vline(15, 10, 11)
c.put(15, 10, "▲")
c.put(40, 11, "findings go back to the author")
c.mark(11, "findings go back to the author", "~~")
text(c, 4, 14, "Why: you cannot catch the mistake you cannot see.")
text(c, 4, 15, "The same blind spot that made it also hides it.")
pairs = [("requirements-agent", "spec-review-agent"),
         ("architecture-agent", "architecture-review-agent"),
         ("implementation-agent", "code-review-agent, qa-agent"),
         ("the software as built", "reconciliation-agent")]
text(c, 4, 17, "Author", "**")
text(c, 33, 17, "Reviewer", "**")
for i, (a, b) in enumerate(pairs):
    c.put(4, 18 + i, a)
    c.put(27, 18 + i, "──►")
    c.put(33, 18 + i, b)
text(c, 4, 23, "You make the separation: open a new session for every review.", "**")
slides.append(slide(c))

# 5. The first session -----------------------------------------------------------------
c = Canvas(99, 25)
title(c, "YOUR FIRST SESSION", "VIRGIL greets you and offers four doors")
c.box(34, 4, 31, 4, ["VIRGIL", "guide, instructor, liaison"])
c.vline(49, 8, 9)
c.hline(13, 85, 10)
for x in (13, 37, 61, 85):
    c.put(x, 10, "┬" if x not in (13, 85) else ("┌" if x == 13 else "┐"))
    c.put(x, 11, "▼")
c.put(49, 10, "┴")
doors = [("H", "HELP", ["I am new and", "need to find", "my way"]),
         ("K", "HOUSEKEEPING", ["check state,", "re-fit,", "update"]),
         ("P", "PROJECT WORK", ["start or", "continue work:", "a playbook"]),
         ("O", "OPEN STAGE", ["just talk,", "until the idea", "takes shape"])]
for x, (key, name, lines) in zip((3, 27, 51, 75), doors):
    c.box(x, 12, 21, 6, [f"{key}: {name}", *lines])
text(c, 4, 20, "Ask at any time: \"where am I?\" or \"what is a gate?\"")
text(c, 4, 22, "The best first step is poc-spike: one idea, one small thing that runs, in minutes.")
text(c, 4, 23, "You watch the loop work before you commit to anything real.")
c.mark(22, "poc-spike", "**")
slides.append(slide(c))

# 6. Setting up ---------------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "SETTING UP", "once per project: install, then fit")
c.box(3, 5, 27, 6, ["INIT-FACTORY", "wires in the factory", "and scans the project"])
c.hline(30, 34, 7, "►")
c.box(35, 4, 38, 9, [])
text(c, 37, 4, " THE FITTING: SIX STEPS ", "**")
fit = ["1  model matrix: which model for what",
       "2  confirm the project fingerprint",
       "3  agent context: where knowledge is",
       "4  test regime: how the project tests",
       "5  decide on pre-commit hooks",
       "6  seed the counter for finding IDs"]
for i, line in enumerate(fit):
    c.put(37, 6 + i, line)
c.hline(73, 79, 7, "►")
c.box(80, 5, 17, 5, ["READY", "for the first", "playbook"])
files = [("model.conf", "maps tiers such as economy, standard, strong to real models"),
         ("project-context.json", "what the scan found: languages, frameworks, CI, linters, tests"),
         ("docs/agent-context.md", "the switchboard: where each agent looks things up"),
         ("docs/testing.yaml", "the test commands and the thresholds of the gates")]
text(c, 4, 17, "What is on your disk afterwards", "**")
for i, (f, d) in enumerate(files):
    c.put(4, 19 + i, f)
    c.put(28, 19 + i, d)
slides.append(slide(c))

# 7. The way of an idea ---------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "THE WAY OF AN IDEA", "five kinds of work and a reconciliation, each with an author and a reviewer")
work = [("REQUIREMENT", ["What do we", "build, and", "for whom?"]),
        ("DESIGN", ["What shape", "does it", "take?"]),
        ("PLANNING", ["small,", "independent", "stories"]),
        ("BUILDING", ["test first,", "then code"]),
        ("QUALITY", ["review and", "hunt bugs"]),
        ("RECONCILE", ["the docs", "against", "the code"])]
xs = [3, 19, 35, 51, 67, 83]
for i, (x, (name, lines)) in enumerate(zip(xs, work)):
    c.box(x, 5, 15, 6, [name, *lines])
    if i < len(xs) - 1:
        c.put(x + 15, 7, "►")
authors = ["requirements", "architecture", "planning", "implementation", "qa", "reconciliation"]
checks = ["spec-review", "architecture-", "backlog-lint", "code-review", "bug hunt", "findings to"]
checks2 = ["", "review (ATAM)", "and you", "", "with tests", "their owner"]
text(c, 3, 12, "Author", "~~")
text(c, 3, 15, "Reviewer", "~~")
for x, a, b, b2 in zip(xs, authors, checks, checks2):
    c.put(x, 13, a[:15])
    c.put(x, 16, b[:15])
    if b2:
        c.put(x, 17, b2[:15])
text(c, 4, 20, "You approve every handover.", "**")
text(c, 4, 21, "Small tasks use shorter playbooks that touch only the kinds of work they need.")
text(c, 4, 22, "If something needs rework, you fix the artefact directly.")
text(c, 4, 23, "There is no \"going back to an earlier phase\".")
slides.append(slide(c))

# 8. Requirements ---------------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "1  REQUIREMENTS", "first settle what gets built; then check that it holds together")
c.box(3, 5, 17, 5, ["IDEA", "explored", "with VIRGIL"])
c.hline(20, 23, 7, "►")
c.box(24, 5, 17, 5, ["PROPOSAL", "ready for a", "decision"])
c.hline(41, 44, 7, "►")
c.box(45, 4, 26, 7, ["REQUIREMENTS-AGENT", "PRD · .feature file", "scope map", "gaps report"])
c.hline(71, 74, 7, "►")
c.box(75, 4, 21, 7, ["SPEC REVIEW", "new session", "spec-lint, then", "by content"])
c.vline(57, 11, 11)
c.hline(45, 67, 12); c.put(45, 12, "┌"); c.put(67, 12, "┐"); c.put(57, 12, "┴")
c.put(45, 13, "▼"); c.put(67, 13, "▼")
c.box(33, 14, 24, 5, ["DOMAIN MODELLING", "glossary, entities,", "state machines"])
c.box(58, 14, 19, 5, ["TEST STRATEGY", "QA strategy", "per feature"])
text(c, 79, 12, "SPEC findings go", "~~")
text(c, 79, 13, "to their owner", "~~")
text(c, 4, 20, "The .feature file is the acceptance specification, in Gherkin. It belongs to the")
text(c, 4, 21, "stakeholder, not to the developer, and later runs as tests.")
text(c, 4, 23, "Open SPEC findings? Then loop: fix, review again. Otherwise move on.", "**")
slides.append(slide(c))

# 9. Architecture -------------------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "2  ARCHITECTURE", "make the big decisions on purpose, and record them before code locks them in")
c.box(3, 5, 30, 8, ["ARCHITECTURE-AGENT", "", "arc42 chapters", "Structurizr model (C4)", "ADRs, a Pugh matrix", "for real alternatives"])
c.hline(33, 39, 8, "►")
c.box(40, 5, 26, 8, ["ARCHITECTURE REVIEW", "", "new session", "arch-lint, then ATAM:", "quality goals against", "the decisions"])
c.hline(66, 72, 8, "►")
c.box(73, 6, 23, 6, ["AGENT CONTEXT", "brought up to date,", "concern-lint,", "your approval"])
c.vline(53, 13, 15)
c.put(53, 15, "┘")
c.hline(18, 52, 15)
c.put(18, 15, "┌")
c.vline(18, 13, 14)
c.put(18, 13, "▲")
c.put(20, 16, "ATAM findings: loop until none is open")
c.mark(16, "ATAM findings: loop until none is open", "~~")
text(c, 4, 18, "The model in architecture.dsl is the single source. Diagrams and chapters")
text(c, 4, 19, "are derived from it, never the other way round.")
text(c, 4, 21, "Planning may start only when the agent context is clean and you approve it.", "**")
slides.append(slide(c))

# 10. Planning --------------------------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "3  PLANNING", "specification and architecture become small stories")
plan = [("EPICS", ["slice the", "capabilities"]),
        ("TESTABILITY", ["who owns", "which test?"]),
        ("SLICES", ["stories per", "epic, sketched"]),
        ("STORIES", ["ST-NNNN.md", "written"])]
for i, (name, lines) in enumerate(plan):
    x = 3 + i * 21
    c.box(x, 5, 18, 5, [name, *lines])
    if i < 3:
        c.put(x + 18, 7, "─►")
c.put(4, 4, "planning-agent, create-backlog in phases; you approve after each phase")
c.mark(4, "planning-agent, create-backlog in phases; you approve after each phase", "~~")
c.vline(75, 10, 11, "▼")
c.box(62, 12, 27, 4, ["BACKLOG-LINT", "schema, dependencies"])
c.vline(75, 16, 17, "▼")
c.box(62, 18, 27, 3, ["YOUR APPROVAL"])
text(c, 4, 13, "Every story has:", "**")
for i, line in enumerate(["a goal and acceptance criteria",
                          "a MoSCoW priority",
                          "dependencies on other stories",
                          "the files it touches",
                          "a tier and its gates"]):
    c.put(6, 14 + i, "· " + line)
text(c, 4, 21, "Good stories are INVEST: independent, negotiable, valuable, estimable, small, testable.")
text(c, 4, 23, "Set-up such as a test runner or CI goes into the first story that needs it.", "~~")
slides.append(slide(c))

# 11. Building ---------------------------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "4  BUILDING", "test first, gates after every story, one review over the whole feature")
c.box(3, 4, 24, 5, ["IMPLEMENTATION", "hands out stories", "in waves"])
c.hline(27, 31, 6, "►")
c.box(32, 4, 22, 5, ["DEVELOPER", "red, green, tidy", "per story"])
c.hline(54, 58, 6, "►")
c.box(59, 3, 22, 7, ["GATES", "crap-score", "mutation-testing", "test-design-verify", "dependency-check"])
c.hline(81, 85, 6, "►")
c.box(86, 4, 10, 5, ["MERGE", "the", "story"])
c.vline(70, 10, 11)
c.put(70, 12, "┘")
c.hline(43, 69, 12)
c.put(43, 12, "┌")
c.vline(43, 9, 11)
c.put(43, 9, "▲")
c.put(48, 11, "fail")
c.put(4, 13, "FRESH DEVELOPER: only the gate report and the affected files")
c.mark(13, "FRESH DEVELOPER:", "**")
c.put(4, 14, "3 attempts, then one model tier up, 3 more")
c.mark(14, "3 attempts, then one model tier up, 3 more", "~~")
c.box(3, 16, 34, 5, ["AFTER THE LAST WAVE", "CODE REVIEW of the whole", "feature, new session"])
c.hline(37, 41, 18, "►")
c.box(42, 16, 25, 5, ["IMPL FINDINGS", "reviewer gives facts,", "a rule sets severity"])
c.hline(67, 71, 18, "►")
c.box(72, 16, 24, 5, ["BLOCKING?", "fix, then review", "again, all fresh"])
text(c, 4, 22, "A repeat review checks every earlier finding, then inspects everything again:")
text(c, 4, 23, "a fix can bring in a defect the first pass never saw.", "~~")
slides.append(slide(c))

# 12. Quality and reconciliation ------------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "5  QUALITY AND RECONCILIATION", "review independently, hunt bugs, then match the docs to the code")
c.box(3, 4, 30, 8, ["QA AGENT", "new session", "Fagan inspection", "OWASP security review", "bug hunt"])
c.hline(33, 37, 7, "►")
c.box(38, 4, 22, 8, ["PREMERGE-CHECK", "then you merge", "into dev"])
c.hline(60, 64, 7, "►")
c.box(65, 4, 31, 8, ["RECONCILIATION", "on dev, new session", "specification and", "architecture against", "the code as built"])
text(c, 4, 14, "The bug hunt, one bug at a time:", "**")
hunt = ["1  write a test that shows the bug: it fails",
        "2  fix the code: the test passes, and stays",
        "3  hunt again, until a full round finds nothing"]
for i, line in enumerate(hunt):
    c.put(6, 15 + i, line)
text(c, 4, 19, "Every drift found in reconciliation goes to its owner:", "**")
c.put(6, 20, "code defects to the developer, document drift to the document's author.")
text(c, 4, 22, "No open findings left: done. The project is ready for the next feature.", "**")
slides.append(slide(c))

# 12b. Knowledge flow ---------------------------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "KNOWLEDGE FLOW", "forward, the decisions get firmer; backward, the code corrects the assumptions")
text(c, 3, 4, "FORWARD FLOW", "**")
c.put(22, 4, "uncertain ")
c.hline(32, 85, 4, "►")
text(c, 87, 4, "specific", "~~")
forward = [("PROPOSAL", "who needs it"), ("SPECIFICATION", "behaviour"),
           ("ARCHITECTURE", "shape, bounds"), ("PLANNING", "stories"), ("BUILDING", "code, tests")]
for i, (name, line) in enumerate(forward):
    x = 3 + i * 19
    c.box(x, 5, 17, 4, [name, line])
    if i < 4:
        c.put(x + 17, 6, "─►")
# Return channel: from reconciliation up to every stage that settles assumptions
for x in (11, 30, 49, 68):
    c.put(x, 9, "▲")
    c.put(x, 10, "│")
c.hline(11, 68, 11)
c.put(11, 11, "└"); c.put(30, 11, "┴"); c.put(49, 11, "┼"); c.put(68, 11, "┘")
c.put(49, 12, "│")
text(c, 13, 12, "findings go to the owner", "~~")
c.vline(87, 9, 12, "▼")
c.box(79, 13, 17, 5, ["CODE REVIEW", "the whole", "feature"])
c.hline(77, 78, 15, "◄")
c.box(60, 13, 17, 5, ["QA", "review,", "hunt bugs"])
c.hline(58, 59, 15, "◄")
c.box(40, 13, 18, 5, ["RECONCILIATION", "docs against", "the code"])
text(c, 4, 14, "BACKWARD FLOW", "**")
c.put(4, 15, "The code as built tests the")
c.put(4, 16, "\"half-firm assumptions\".")
text(c, 4, 19, "Going forward, each stage settles what the stage before left open.", "**")
c.put(4, 20, "Each decision rests on assumptions. They are firm enough to build on,")
c.put(4, 21, "but only the code shows whether they hold.")
text(c, 4, 23, "When an assumption fails, its owner corrects the document, not only the code.", "**")
slides.append(slide(c))

# 13. Gates ------------------------------------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "WHAT THE MACHINES CHECK", "a gate catches the mistake before you look")
c.box(3, 4, 44, 15, [])
text(c, 5, 4, " ON EVERY COMMIT ", "**")
hooks = [("mdformat", "uniform Markdown"),
         ("link-check", "links resolve"),
         ("mermaid-lint", "diagrams do not break"),
         ("spec-lint", "the spec is consistent"),
         ("arch-lint", "architecture and model"),
         ("backlog-lint", "stories are complete"),
         ("concern-lint", "agent context is valid"),
         ("matrix-lint", "model matrix is valid"),
         ("statemachine-lint", "state machines agree"),
         ("finding-lint", "severity by the rule"),
         ("index-lint", "catalogue is current")]
for i, (h, d) in enumerate(hooks):
    c.put(5, 6 + i, f"{h:<19}{d}")
c.box(50, 4, 46, 8, [])
text(c, 52, 4, " AFTER EVERY STORY ", "**")
sem = [("crap-score", "complexity and coverage"),
       ("mutation-testing", "do the tests catch bugs?"),
       ("test-design-verify", "prescribed tests exist?"),
       ("dependency-check", "dependency rules")]
for i, (h, d) in enumerate(sem):
    c.put(52, 6 + i, f"{h:<19}{d}")
c.box(50, 13, 46, 6, [])
text(c, 52, 13, " BEFORE THE MERGE ", "**")
c.put(52, 15, "premerge-check: every gate passed,")
c.put(52, 16, "base up to date, only allowed files")
text(c, 4, 21, "When a gate fires, the system is working.", "**")
text(c, 4, 22, "Fix the cause. Do not route around the alarm.")
slides.append(slide(c))

# 14. Which playbook ----------------------------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "WHICH PLAYBOOK, WHEN", "the recipe that matches your situation")
books = [("See whether a rough idea works at all", "poc-spike"),
         ("Validate a technical risk before committing to it", "technical-poc"),
         ("Fix one reported bug", "bug-fix"),
         ("Bring the docs back in line with the code", "documentation-update"),
         ("Build a new project properly, start to finish", "greenfield-development"),
         ("Add the factory to code that already exists", "brownfield-onboarding"),
         ("Add a feature to a project the factory manages", "feature-addition"),
         ("Restructure code without changing behaviour", "refactoring"),
         ("Evaluate an architecture against quality goals", "architecture-review"),
         ("Survey a topic with sourced citations", "research-survey"),
         ("Test a specific claim by trying to refute it", "research-topic")]
text(c, 4, 4, "You want to …", "**")
text(c, 62, 4, "Start with", "**")
c.put(4, 5, "─" * 91)
for i, (want, book) in enumerate(books):
    c.put(4, 6 + i, want)
    c.put(62, 6 + i, book)
text(c, 4, 19, "A playbook describes a typical path, not a fixed one. Which agents may run next")
text(c, 4, 20, "follows from the artefacts that already exist.")
text(c, 4, 22, "Not sure? Choose P in the menu. VIRGIL asks and suggests the recipe.", "~~")
slides.append(slide(c))

# 15. Extending the factory --------------------------------------------------------------------------------
c = Canvas(99, 25)
title(c, "EXTENDING THE FACTORY", "fit it to your project, and add what only your project needs")
c.box(3, 4, 44, 9, [])
text(c, 5, 4, " FIT IT TO YOUR PROJECT ", "**")
fit = [("model matrix", "which model for what"),
       ("agent context", "where knowledge lives"),
       ("test regime", "how the project tests"),
       ("hooks", "which checks run on commit"),
       ("conventions", "yours override the defaults")]
for i, (k, d) in enumerate(fit):
    c.put(5, 6 + i, f"{k:<14}{d}")
c.box(50, 4, 46, 9, [])
text(c, 52, 4, " ADD YOUR OWN PARTS ", "**")
own = [("skills", "a procedure only you need"),
       ("agents", "a job only your project has"),
       ("templates", "the shape of your documents")]
for i, (k, d) in enumerate(own):
    c.put(52, 6 + i, f"{k:<11}{d}")
c.put(52, 10, "Ask the agent to add the part and to")
c.put(52, 11, "refresh INDEX.yaml and the Copilot agents.")
text(c, 4, 14, "EXAMPLE: A CAMUNDA TEAM", "**")
c.put(4, 15, "\"Add a skill bpmn-model-review that checks our BPMN models, and refresh INDEX.yaml.\"")
c.put(4, 16, "Copilot writes the skill into .agent-factory/factory/skills/ and runs index-lint.")
text(c, 4, 18, "An update saves your parts, but does not put them back.", "**")
c.put(4, 19, "update-factory stops and names each file you added. With --force, it copies the files")
c.put(4, 20, "to .agent-factory/user-changes/ and installs the new release. Ask the agent to copy them back.")
text(c, 4, 21, "Git ignores .agent-factory/, so your parts stay on your machine. Share them by hand.", "~~")
text(c, 4, 23, "Useful for every project? Propose it for the factory core.", "**")
slides.append(slide(c))

# 16. Three habits -----------------------------------------------------------------------------------------
c = Canvas(62, 14)
text(c, 3, 1, "THREE HABITS", "**")
habits = [("Read before you approve.", "Your yes is the last gate. It matters most."),
          ("Let the gates do their job.", "An alarm is not a fault. Fix the cause."),
          ("One small step at a time.", "Noise gets corrected before it compounds.")]
for i, (head, body) in enumerate(habits):
    y = 3 + i * 3
    text(c, 3, y, f"{i + 1}  {head}", "**")
    c.put(6, y + 1, body)
text(c, 3, 12, "To begin: one poc-spike. The rest comes by doing.", "~~")
slides.append(slide(c))

assert not TOO_WIDE, TOO_WIDE
header = ("% title: Agent Factory Step by Step\n% topic: agent-factory-step-by-step\n"
          "% date: 2026-11-20\n% lang: en\n")
OUT.write_text(header + "\n---\n".join(slides) + "\n")
print(f"{len(slides)} slides written to {OUT}")
