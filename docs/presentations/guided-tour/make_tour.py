"""Generate slides.txt of the guided tour deck on exact grids.

Run: python3 make_tour.py slides.txt, then remark-deck build <this folder>.
Diagrams are drawn on a character canvas, so boxes and lines join exactly.
"""
import re
import sys

MARK = re.compile(r"\*\*|~~|%%|!!")
COLS, ROWS = 99, 25


def width(s):
    return len(MARK.sub("", s))


def grid(cols, rows, lines):
    assert len(lines) <= rows, (len(lines), rows, lines[:2])
    for line in lines:
        assert width(line) <= cols, (width(line), cols, line)
    return f"```grid {cols}x{rows}\n" + "\n".join(lines) + "\n```"


class Box:
    """A drawn box; the *_out methods give the cell just outside an edge."""

    def __init__(self, r, c, w, h):
        self.r, self.c, self.w, self.h = r, c, w, h

    def top(self, col):
        return (self.r - 1, col)

    def bottom(self, col):
        return (self.r + self.h, col)

    def left(self, row):
        return (row, self.c - 1)

    def right(self, row):
        return (row, self.c + self.w)


HEADS = {(0, 1): "►", (0, -1): "◄", (1, 0): "▼", (-1, 0): "▲"}
CORNERS = {
    ((1, 0), (0, 1)): "└", ((1, 0), (0, -1)): "┘",
    ((-1, 0), (0, 1)): "┌", ((-1, 0), (0, -1)): "┐",
    ((0, 1), (1, 0)): "┐", ((0, 1), (-1, 0)): "┘",
    ((0, -1), (1, 0)): "┌", ((0, -1), (-1, 0)): "└",
}


class Canvas:
    def __init__(self, h, w=95):
        self.c = [[" "] * w for _ in range(h)]
        self.w = w
        self.border = {}

    def grow(self, r):
        while r >= len(self.c):
            self.c.append([" "] * self.w)

    def put(self, r, c, s):
        self.grow(r)
        for i, ch in enumerate(s):
            assert c + i < self.w, (r, c, s)
            self.c[r][c + i] = ch

    def box(self, r, c, lines, w=None):
        w = w or max(len(x) for x in lines) + 4
        h = len(lines) + 2
        self.put(r, c, "┌" + "─" * (w - 2) + "┐")
        for i, line in enumerate(lines):
            assert len(line) <= w - 4, (line, w)
            self.put(r + 1 + i, c, "│ " + line.ljust(w - 4) + " │")
        self.put(r + h - 1, c, "└" + "─" * (w - 2) + "┘")
        for x in range(c + 1, c + w - 1):
            self.border[(r, x)] = "top"
            self.border[(r + h - 1, x)] = "bottom"
        for y in range(r + 1, r + h - 1):
            self.border[(y, c)] = "left"
            self.border[(y, c + w - 1)] = "right"
        return Box(r, c, w, h)

    def route(self, points, head=True):
        """Polyline through points (row, col); corners at the bends,
        an arrow head at the last point."""
        cells = []
        dirs = []
        for (r1, c1), (r2, c2) in zip(points, points[1:]):
            assert r1 == r2 or c1 == c2, (points,)
            d = ((r2 > r1) - (r2 < r1), (c2 > c1) - (c2 < c1))
            n = max(abs(r2 - r1), abs(c2 - c1))
            for i in range(n + (0 if (r2, c2) != points[-1] else 1)):
                cells.append((r1 + d[0] * i, c1 + d[1] * i))
                dirs.append(d)
        # A vertical arrow ends on the box edge it points at, so the head
        # touches the box instead of floating half a row above it.
        last = dirs[-1]
        tip = (cells[-1][0] + last[0], cells[-1][1] + last[1])
        if head and tip in self.border:
            cells.append(tip)
            dirs.append(last)
        for i, (r, c) in enumerate(cells):
            self.grow(r)
            d = dirs[i]
            ch = "│" if d[0] else "─"
            if i > 0 and dirs[i - 1] != d:
                ch = CORNERS[(dirs[i - 1], d)]
            if i == len(cells) - 1 and head:
                ch = HEADS[d]
            old = self.c[r][c]
            if (old, ch) in (("│", "─"), ("─", "│")):
                ch = "┼"
            self.c[r][c] = ch

    def lines(self):
        joins = {"top": ("┴", -1, 0, "│"), "bottom": ("┬", 1, 0, "│"),
                 "left": ("┤", 0, -1, "─"), "right": ("├", 0, 1, "─")}
        for (r, c), side in self.border.items():
            j, dr, dc, line = joins[side]
            rr, cc = r + dr, c + dc
            if self.c[r][c] not in "─│":
                continue  # an arrow head sits on this edge cell
            if 0 <= rr < len(self.c) and 0 <= cc < self.w and self.c[rr][cc] == line:
                self.c[r][c] = j
        return ["".join(row).rstrip() for row in self.c]


def slide(title, body, caption=(), foot=(), sub=None):
    top = ["", "   **" + title + "**"]
    if sub:
        top.append("   ~~" + sub + "~~")
    top.append("")
    lines = top + [("   " + b) if b else "" for b in body]
    tail = []
    if caption:
        tail += [""] + ["   " + c for c in caption]
    if foot:
        tail += [""] + ["   ~~" + f + "~~" for f in foot]
    while len(lines) + len(tail) < ROWS:
        lines.append("")
    return grid(COLS, ROWS, [x.rstrip() for x in lines + tail])


S = []

# 1 Title
S.append(grid(40, 10, [
    "",
    "",
    "  **A GUIDED TOUR**",
    "",
    "  The run lifecycle and the CRAP gate:",
    "  what the two campaigns built, and",
    "  where it lives in the repository.",
    "",
    "  ~~Agent Factory, 2026-11-22~~",
]))

# 2 How to read
S.append(slide("How to read this tour", [
    "Each slide shows one flow or one structure, with two or three lines below it.",
    "Grey lines name the files where it lives, as paths from the repository root.",
    "",
    "**Part 1**  the run lifecycle, merged 2026-11-19:",
    "          how the Factory starts, drives, checks and ends the work on a feature.",
    "**Part 2**  the CRAP gate, merged 2026-11-22:",
    "          a quality gate that the run lifecycle runs on every story.",
], foot=["Press g to show the character grid, p for the presenter view."]))

# 3 Map
m = Canvas(16)
b1 = m.box(0, 0, ["backlog/ST-*.md", "stories, touches"], 21)
b2 = m.box(0, 30, ["docs/testing.yaml", "gates, measures"], 23)
b3 = m.box(0, 62, ["docs/findings/", "findings and the", "exceptions file"], 21)
d = m.box(6, 0, ["dispatch", "init ... close", "the ledger"], 21)
p = m.box(6, 30, ["premerge-check", "checks at the merge"], 23)
k = m.box(12, 30, ["crap-score", "judges changed code"], 23)
mc = m.box(12, 62, ["measuring command", "(project-owned)"], 21)
m.route([b1.bottom(10), d.top(10)])
m.route([b2.bottom(41), p.top(41)])
m.route([b3.bottom(72), (7, 72), p.right(7)])
m.route([d.right(7), p.left(7)])
m.route([d.bottom(10), (13, 10), k.left(13)])
m.put(12, 12, "runs gate-check")
m.route([p.bottom(41), k.top(41)])
m.put(10, 43, "runs")
m.route([k.right(13), mc.left(13)])
m.route([mc.left(14), k.right(14)])
S.append(slide("The map: what the two campaigns touched", m.lines(), caption=[
    "Campaign 1 built dispatch, the ledger and premerge-check.",
    "Campaign 2 rebuilt crap-score, added its setup and wired it into both."]))

# 4 Terms
S.append(slide("Part 1 · The words", [
    "**run**              everything the Factory does for one feature branch,",
    "                   from dispatch init to dispatch close",
    "**feature branch**   the branch of a run, cut from dev",
    "**story branch**     story/<id>, cut from the feature branch",
    "**unit of work**     a story, or a blocking finding added to the run",
    "**wave**             units of work that start together",
    "**ledger**           the run's inventory: one entry per unit, one record per wave",
    "**gate-check step**  running the gates on a story branch, fixing what they report",
    "**drift row**        code and documents disagree; an owner fixes the document",
], foot=["docs/proposals/run-lifecycle.md § Terms"], sub="the run lifecycle"))

# 5 Two ways
S.append(slide("Two ways to drive a run", [
    "                      **orchestrated**                 **by hand**",
    "who starts a story    the agent, wave by wave      the agent, on the human's go",
    "how stories run       in parallel, if files differ one at a time",
    "where a story runs    its own worktree             the primary checkout",
    "who runs the gates    the implementation agent     the implementation agent",
    "who merges into dev   the human                    the human",
], caption=[
    "Same ledger, steps, checks and end. Only who acts, and when, differs.",
    "The human alone runs return-story and close --drop, which destroy work, and close."],
    foot=["packages/factory/agents/implementation-agent.md § Modes"]))

# 6 Story workflow
w = Canvas(12)
i1 = w.box(0, 0, ["1 implement", "developer agent", "TDD, commits"], 19)
rv = w.box(0, 24, ["2 review", "code-review agent", "files findings"], 21)
q = w.box(0, 50, ["open blocking", "finding?"], 17)
g = w.box(0, 74, ["4 gate check", "fresh agent", "per retry"], 19)
f = w.box(7, 46, ["3 fix: fresh developer", "agent, then re-review"], 26)
mg = w.box(7, 74, ["5 merge-story", "premerge-check,", "status: done"], 19)
w.route([i1.right(2), rv.left(2)])
w.route([rv.right(2), q.left(2)])
w.route([q.right(1), g.left(1)])
w.put(0, 68, "none")
w.route([q.bottom(55), f.top(55)])
w.put(5, 57, "yes")
w.route([f.top(62), q.bottom(62)])
w.route([g.bottom(83), mg.top(83)])
S.append(slide("The story workflow", w.lines(), caption=[
    "Every unit of work takes these steps on its story branch, both ways of driving.",
    "Reviews and gates see commits, never a working copy. Each fix starts a fresh agent."],
    foot=["packages/factory/agents/implementation-agent.md § Story workflow"]))

# 7 Ledger states
L = Canvas(15, w=96)
pe = L.box(2, 0, ["PENDING"], 11)
pr = L.box(2, 19, ["PREPARED"], 12)
dg = L.box(2, 42, ["DISPATCHING"], 15)
dd = L.box(2, 67, ["DISPATCHED"], 14)
dn = L.box(2, 88, ["DONE"], 8)
L.route([pe.right(3), pr.left(3)])
L.put(1, 11, "prepare")
L.route([pr.right(3), dg.left(3)])
L.put(0, 31, "mark-")
L.put(1, 31, "dispatching")
L.route([dg.right(3), dd.left(3)])
L.put(0, 57, "mark-")
L.put(1, 57, "dispatched")
L.route([dd.right(3), dn.left(3)])
L.put(0, 81, "merge-")
L.put(1, 81, "story")
fa = L.box(10, 26, ["FAILED", "re-dispatch -> PREPARED", "return      -> PENDING"], 27)
bl = L.box(10, 60, ["BLOCKED", "re-dispatch -> PREPARED", "return      -> PENDING"], 27)
L.route([dd.bottom(69), (7, 69), (7, 39), fa.top(39)])
L.put(6, 40, "gate fails, no attempt left")
L.route([dd.bottom(73), bl.top(73)])
L.put(8, 51, "conflict, red suite,")
L.put(9, 49, "or gate cannot measure")
L.route([bl.top(79), dd.bottom(79)])
L.put(6, 81, "resume-gates")
L.put(7, 81, "(cannot")
L.put(8, 81, "measure)")
S.append(slide("A ledger entry and its states", L.lines(), caption=[
    "FAILED: the attempts ran out. BLOCKED: no code fix helps. Both wait for the human.",
    "resume-gates is the shortcut back when the code was never judged."],
    foot=["docs/spec/state-machines.md § Ledger Entry Lifecycle"]))

# 8 Merge check
mc = [
    "premerge-check  <target>  <branch>",
    "",
    "   stale base       the branch contains its target",
    "   file count       under the limit",
    "   scope            only the story's files",
    "   code review      a report for this head",
    "   open findings    none blocking",
    "   ready commands   the services are up",
    "   semantic gates   dependency-check, crap-score",
    "   test suite       full suite, in a temporary worktree",
    "        │",
    "        ├──── all pass ──────────────────────► exit 0   merge",
    "        ├──── only a gate cannot measure ────► exit 3   BLOCKED",
    "        └──── anything else ─────────────────► exit 1   no merge",
]
S.append(slide("The check at every merge", mc, caption=[
    "It judges the branch head, not the history, and reruns every gate fresh.",
    "The same script checks the merge of the whole feature into dev."],
    foot=["packages/factory/scripts/premerge-check · docs/adr/0038-*"]))

# 9 Wave close
wc = Canvas(11)
a = wc.box(0, 0, ["last unit of", "the wave merged"], 19)
cw = wc.box(0, 26, ["dispatch close-wave"], 23)
wr = wc.box(0, 60, ["wave record:", "next wave may start"], 23)
o = wc.box(6, 26, ["owner fixes", "the document"], 23)
rv = wc.box(6, 60, ["reviewer confirms", "the fix, then", "close-wave again"], 23)
wc.route([a.right(1), cw.left(1)])
wc.route([cw.right(1), wr.left(1)])
wc.put(0, 51, "passes")
wc.route([cw.bottom(37), o.top(37)])
wc.put(4, 39, "refuses: lists open drift rows")
wc.route([o.right(7), rv.left(7)])
S.append(slide("Closing a wave", wc.lines(), caption=[
    "Drift rows from the wave's spec-feedback reports are settled before the next wave.",
    "The fixes land between waves, so they never race a story merge."],
    foot=["docs/spec/work/spec-feedback-<id>.md · dispatch-contract.md § Drift Rows At The Wave Close"]))

# 10 End and guardrail
left = ["**The end of a run**", "",
        "feature checks: review, QA", "        │", "        ▼",
        "premerge-check dev <feature>", "        │", "        ▼",
        "the human merges into dev", "        │", "        ▼",
        "dispatch close: removes the ledger,", "worktrees and merged branches;",
        "the ledger's frozen copy stays", "as the run's receipt"]
right = ["**The guardrail, before every agent command**", "",
         "refuses:",
         "  push, reset --hard, branch -D",
         "  any hook bypass",
         "  a merge without premerge-check",
         "  a commit in a worktree without",
         "    verify-base",
         "  tests other than the declared ones",
         "    or named files under tests/",
         "  return-story and close --drop",
         "",
         "one script for Claude Code, Codex,",
         "Copilot, pi and OpenCode"]
eg = []
for i in range(max(len(left), len(right))):
    lft = left[i] if i < len(left) else ""
    rgt = right[i] if i < len(right) else ""
    eg.append((lft + " " * (44 - width(lft)) + rgt).rstrip())
S.append(slide("The end of a run, and the guardrail", eg, caption=[
    "A run has an end: merge commits, story status and the receipt are what remain.",
    "The guardrail blocks what cannot be undone. The human watches the rest."],
    foot=["packages/factory/config/hooks/block-dangerous-git.sh · docs/reviews/runs/"]))

# 11 Code map RL
S.append(slide("Part 1 · Where it lives", [
    "**packages/factory/scripts/dispatch**                 the run: init to close",
    "**packages/factory/scripts/dispatch_lib.py**          the ledger and its transitions",
    "**packages/factory/scripts/premerge-check**           the checks at every merge",
    "**packages/factory/config/hooks/block-dangerous-git.sh**   the guardrail",
    "**packages/factory/agents/implementation-agent.md**   how a run is driven",
    "",
    "~~spec          docs/spec/features/run-lifecycle.feature, docs/spec/state-machines.md~~",
    "~~decisions     docs/proposals/run-lifecycle.md, docs/adr/0037-*, docs/adr/0038-*~~",
    "~~how it went   docs/reviews/run-report-run-lifecycle-2026-11-20.md~~",
]))

# 12 Formula
f = [
    "              CRAP(f)  =  c² × (1 − cov / 100)³  +  c",
    "",
    "              c    cyclomatic complexity of the function",
    "              cov  share of its lines that the tests run, in %",
    "",
    "                  c = 4    cov = 100 %    →    4.00",
    "                  c = 4    cov =   0 %    →   20.00",
    "                  c = 9    cov =  50 %    →   19.13",
    "",
    "              a changed function fails when CRAP > threshold",
]
S.append(slide("Part 2 · Why a CRAP gate", f, caption=[
    "Complex and untested is the riskiest code; the score grows with exactly that.",
    "Only changed functions count. The project picks the threshold; there is no default."],
    foot=["packages/factory/skills/crap-score/SKILL.md"], sub="the CRAP gate"))

# 13 Who measures
wm = Canvas(14)
y = wm.box(0, 0, ["docs/testing.yaml", "gates.crap-score:", "  threshold, timeout_minutes",
                  "  measures:", "    - name, files, exclude,", "      ready, command"], 33)
k = wm.box(1, 42, ["crap-score", "language-neutral"], 20)
mc = wm.box(0, 71, ["measuring command", "the project's own"], 22)
rb = wm.box(9, 42, ["one JSON row per function:", "file, function, start_line,",
                    "end_line, complexity,", "coverage_pct"], 33)
wm.route([y.right(2), k.left(2)])
wm.route([k.right(2), mc.left(2)])
wm.put(1, 63, "runs")
wm.route([mc.bottom(81), (11, 81), rb.right(11)])
wm.put(6, 83, "writes")
wm.route([rb.top(52), k.bottom(52)])
wm.put(6, 54, "reads")
wm.put(9, 0, "env: GATE_OUTPUT (where to write),")
wm.put(10, 0, "     GATE_FILES, GATE_EXCLUDE")
S.append(slide("Who measures what", wm.lines(), caption=[
    "crap-score knows no language. Each measure names a command the project owns.",
    "For Python the setup ships a template on radon and coverage.py."],
    foot=["packages/factory/skills/setup-crap-score/crap-measure-python · docs/spec/schemas/"]))

# 14 Judging
j = [
    "rows of every measure",
    "   │ wrong shape, or one function twice ─────────────────────► exit 2",
    "   ▼",
    "keep the files of `files`, drop those of `exclude`",
    "   ▼",
    "only the functions the diff touches  (merge base → HEAD)",
    "   ▼",
    "score each, round half up",
    "   ├── at or below the threshold ────────────────────────────► pass",
    "   ├── above, but a row in the exceptions register on dev ───► accepted",
    "   └── above ────────────────────────────────────────────────► fail",
    "",
    "exit 0: all pass or accepted     exit 1: a fail     exit 2: cannot measure",
]
S.append(slide("How crap-score judges", j, caption=[
    "Exit 2 means nobody judged the code. Only a person can accept a function,",
    "in docs/findings/exceptions.md on dev; agents can never write that file."],
    foot=["packages/factory/scripts/crap-score · config/hooks/guard-human-fields"]))

# 15 Where it runs
wr = Canvas(16)
gc = wr.box(0, 0, ["gate-check step", "story worktree"], 20)
pm = wr.box(0, 28, ["premerge-check", "at the merge"], 18)
mg = wr.box(0, 54, ["merged"], 10)
bx = wr.box(10, 10, ["BLOCKED: gate cannot measure"], 32)
hb = wr.box(10, 51, ["human fixes the setup,", "dispatch resume-gates:",
                     "back to the gate check,", "attempts unchanged"], 27)
wr.route([gc.right(1), pm.left(1)])
wr.put(0, 23, "0")
wr.route([pm.right(1), mg.left(1)])
wr.put(0, 49, "0")
wr.route([gc.bottom(4), (6, 4)])
wr.put(7, 0, "1: failed")
wr.put(8, 0, "attempt, fresh")
wr.put(9, 0, "developer")
wr.route([gc.bottom(15), bx.top(15)])
wr.put(6, 16, "2")
wr.route([pm.bottom(37), bx.top(37)])
wr.put(6, 38, "3")
wr.route([bx.right(11), hb.left(11)])
S.append(slide("Where the gate runs, and what exit 2 does", wr.lines(), caption=[
    "A failure costs an attempt; a fresh developer fixes the code.",
    "Cannot measure costs nothing: the story waits as BLOCKED until the setup works."],
    foot=["implementation-agent.md § Gate that cannot measure · crap-gate-setup.md DEC-03, DEC-07"]))

# 16 Running safely
rs = Canvas(15)
rs.put(0, 0, "for each measure, in list order:")
q = rs.box(2, 3, ["has a ready command?"], 24)
lk = rs.box(2, 40, ["take the lock"], 17)
rs.put(3, 59, "file: <git common dir>/")
rs.put(4, 59, "crap-score/<name>.lock")
rd = rs.box(7, 40, ["run ready"], 17)
mc = rs.box(11, 3, ["run the measuring command,", "then release the lock"], 30)
rs.route([q.right(3), lk.left(3)])
rs.put(2, 31, "yes")
rs.route([lk.bottom(48), rd.top(48)])
rs.route([rd.right(8), (8, 66)])
rs.put(7, 59, "fails")
rs.put(8, 68, "exit 2")
rs.route([q.bottom(10), mc.top(10)])
rs.put(7, 12, "no")
rs.route([rd.bottom(48), (12, 48), mc.right(12)])
S.append(slide("Running safely: ready, lock, time limit", rs.lines(), caption=[
    "One clock, timeout_minutes, covers every command and every wait for the lock.",
    "On SIGTERM, SIGINT or SIGHUP the whole process group stops first, then exit 128 + n."],
    foot=["docs/proposals/crap-gate-setup.md DEC-43, DEC-47, DEC-56"]))

# 17 Setup and proof
sp = [
    "**setup-crap-score**  (the test-strategy agent)    **gate-setup-proof**  (temporary worktree)",
    "",
    " 1 find languages and test tools                planted: an untested and a tested",
    " 2 try the tools on a real file                 function of the same complexity",
    " 3 propose exclusions",
    " 4 write the measure, enabled: false            Repeatable     two runs, same rows",
    " 5 run gate-setup-proof ─────────────────────►  Catches CRAP   untested one fails",
    " 6 crap-score --all: threshold, time limit      Sees the folder tested one is 100 %",
    " 7 the person confirms ─► enabled: true         Reports a gap  failing test, exit 2",
]
S.append(slide("Setting the gate up, and proving the setup", sp, caption=[
    "The setup does not trust the measuring command: only one that passes all four checks",
    "is enabled. The person decides every value; the agent proposes, measures and proves."],
    foot=["packages/factory/skills/setup-crap-score/SKILL.md · packages/factory/scripts/gate-setup-proof"]))

# 18 Code map CRAP
S.append(slide("Part 2 · Where it lives", [
    "**packages/factory/scripts/crap-score**                 the gate",
    "**packages/factory/skills/setup-crap-score/**           the setup and the Python template",
    "**packages/factory/scripts/gate-setup-proof**           the four checks",
    "**packages/factory/skills/crap-score/SKILL.md**         the gate, described",
    "**packages/factory/scripts/premerge-check, dispatch**   exit 3, resume-gates",
    "**packages/factory/config/hooks/guard-human-fields**    guards the exceptions file",
    "",
    "~~spec          docs/spec/features/crap-gate-setup.feature, BR-127 to BR-139~~",
    "~~decisions     docs/proposals/crap-gate-setup.md (DEC-01 to DEC-67), docs/adr/0003-*~~",
    "~~how it went   docs/reviews/retro-2026-11-22.md, docs/reviews/runs/~~",
]))

# 19 Next
S.append(slide("What comes next", [
    "**Trusted gate source (DEC-67)**  threshold, exclusions and register from one reader",
    "                                a story cannot change; later a graph store or Jira",
    "**ST-0449**                       set the gate up and enable it in this repository",
    "**Open findings**                 IMPL-0083, IMPL-0093, SEC-0008",
    "**From the retro**                T-0419 to T-0426",
], foot=["docs/spec/work/todo.md · docs/proposals/ledger-run-receipt.md"]))

head = ("% title: Guided tour: run lifecycle and CRAP gate\n"
        "% topic: guided-tour\n% date: 2026-11-22\n% lang: en\n\n")
open(sys.argv[1], "w").write(head + "\n---\n\n".join(S) + "\n")
print(len(S), "slides")
