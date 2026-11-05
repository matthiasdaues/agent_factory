import json
exec(open('layout.py').read().split('out = []')[0])  # positions only
from xml.sax.saxutils import escape
def esc(s): return escape(s, {'"': '&quot;'})
ART = {  # (lines, chips); chips name the classes of miro-process-illustration.md
 'i2': (['.agent-factory/', 'config/project-context.json'], ['Setup']),
 'i5': (['spike in a sandbox (optional)'], ['Working']),
 'f0': (['config/model.conf'], ['Setup']),
 'f1': (['project-context.json: fingerprint'], ['Setup']),
 'f2': (['docs/agent-context.md'], ['Seam']),
 'f3': (['docs/testing.yaml'], ['Seam']),
 'f4': (['.pre-commit-config.yaml'], ['Setup']),
 'b1': (['todos.md: missing tests as debt'], ['Plan']),
 'b2': (['docs/spec/scope-map.md', 'work/term-candidates.md'], ['Core', 'Working']),
 'b4': (['docs/spec/architecture.dsl', 'docs/arc42/, docs/adr/'], ['Core', 'Derived view', 'Decision record']),
 'b7': (['features/&lt;project&gt;.feature', 'work/&lt;project&gt;-gaps.md'], ['Core', 'Working']),
 'b6': (['glossary.md', 'entity-model.md'], ['Core']),
 'b8': (['validation-rules.md', 'interface-contracts.md, state-machines.md'], ['Core']),
 'b9': (['docs/reviews/spec-review-&lt;date&gt;.md', 'docs/findings/SPEC-NNNN'], ['Quality record']),
 'b10': (['architecture.dsl: components', 'arc42 chapters 5 to 7, ADRs'], ['Core', 'Derived view', 'Decision record']),
 'b11': (['atam-review.md', 'docs/findings/ATAM-NNNN'], ['Quality record']),
 'b12': (['docs/agent-context.md'], ['Seam']),
 'b13': (['reconciliation report rows', 'docs/findings/BUG-NNNN'], ['Working', 'Quality record']),
 'g0': (['poc/spike/ or docs/spikes/', 'ADR when decided'], ['Working', 'Decision record']),
 'g2': (['docs/agent-context.md'], ['Seam']),
 'p1': (['docs/proposals/&lt;name&gt;.md'], ['Decision record']),
 'p2': (['Decisions table: DEC-NN', 'term-candidates.md: confirmed rows'], ['Decision record', 'Working']),
 'p4': (['Primer section'], ['Decision record']),
 'p3': (['cut plan, edited proposal'], ['Working', 'Decision record']),
 'p7': (['Review findings: PROP-NN', 'Review passes row'], ['Quality record']),
 's1': (['features/&lt;name&gt;.feature', 'work/&lt;name&gt;-gaps.md'], ['Core', 'Working']),
 's2': (['scope-map.md: specified rows'], ['Core']),
 's2a': (['docs/spec/areas/&lt;area&gt;.md'], ['Core']),
 's3': (['glossary.md, entity-model.md', 'states, rules, contracts, schemas/'], ['Core']),
 's4': (['work/&lt;name&gt;-qa-strategy.md'], ['Working']),
 's6': (['docs/reviews/spec-review-&lt;date&gt;.md', 'docs/findings/SPEC-NNNN'], ['Quality record']),
 'a1': (['architecture.dsl, dependency-rules.dsl', 'exported diagrams'], ['Core', 'Derived view']),
 'a2': (['docs/arc42/ chapters'], ['Derived view']),
 'a3p': (['Pugh matrix'], ['Decision record']),
 'a4': (['docs/adr/NNNN-&lt;title&gt;.md', 'chapter 9 index'], ['Decision record']),
 'a6': (['atam-review.md', 'docs/findings/ATAM-NNNN'], ['Quality record']),
 'q2': (['backlog/epics.md'], ['Plan']),
 'q25': (['epics.md: testability and', 'contract ownership tables'], ['Plan']),
 'q3': (['slice table per EPIC'], ['Plan']),
 'q4': (['backlog/ST-NNNN.md'], ['Plan']),
 'q6': (['story: contract decisions,', 'Required API Behavior'], ['Plan']),
 'q7': (['dispatch stories ST-NNNN'], ['Plan']),
 'w1': (['dispatch ledger, wave plan'], ['Plan']),
 'w2': (['worktree and branch per story'], ['Working']),
 'd2': (['tests and code'], ['Product']),
 'd3': (['story commits', 'work/spec-feedback-&lt;story-id&gt;.md'], ['Product', 'Working']),
 'w3g': (['gate reports in .current-work/&lt;gate&gt;/', 'QA-NNNN for unresolved mutants'], ['Quality record']),
 'x5': (['merged story', 'ledger entry, story file'], ['Product', 'Plan']),
 'x6': (['report rows: fixed, confirmed, rejected', 'docs/findings/BUG-NNNN'], ['Working', 'Quality record']),
 'w5': (['ledger: wave branch head'], ['Plan']),
 'w5q': (['QA-NNNN resolved or to planning agent', 'QA strategy owner table'], ['Quality record', 'Working']),
 'n2': (['.current-work/&lt;gate&gt;/&lt;story-id&gt;.json'], ['Quality record']),
 'n3': (['commit with the story ID'], ['Product']),
 'n4': (['docs/findings/IMPL-NNNN'], ['Quality record']),
 'n7': (['report rows: fixed, confirmed, rejected'], ['Working']),
 'c1': (['docs/findings/IMPL-NNNN'], ['Quality record']),
 'r2': (['reviews/reconciliation-&lt;date&gt;.md rows', 'docs/findings/BUG-NNNN'], ['Working', 'Quality record']),
 'r4': (['report rows for the requirements agent'], ['Working']),
 'r6': (['report rows for the planning agent', 'QA-NNNN, owner planning agent'], ['Working', 'Quality record']),
 'r7': (['fixed artifacts, row statuses', 'scope-map.md: implemented rows'], ['Core', 'Working']),
 'u1': (['docs/findings/BUG-NNNN'], ['Quality record']),
 'u2': (['FAGAN-NNNN, SEC-NNNN'], ['Quality record']),
 'u3': (['regression tests, fix commits'], ['Product']),
 'z1': (['handoff with branch tips'], ['Working']),
 'z3': (['merge commit on dev'], ['Product']),
 't1': (['docs/reviews/retro-&lt;date&gt;.md'], ['Quality record']),
 't2': (['action items with tracking location', 'term-candidates.md for vocabulary'], ['Plan', 'Working']),
}
AX, AW = 10503, 400
out = [f'<text x="{AX}" y="60" font-family="noto_sans" font-size="33" font-weight="bold" fill="#1a1a1a">Artifacts</text>']
for k, (lines, chips) in ART.items():
    p = pos[k]
    body = '\x00'.join(lines)
    out.append(f'<rect x="{AX}" y="{p["y"]:.0f}" width="{AW}" height="84" fill="#f7f7f7" stroke="#595959" stroke-width="2" data-content="{esc(body).replace(chr(0),"&lt;br&gt;")}" data-text-color="#1a1a1a" data-font-family="noto_sans" data-font-size="14" />')
# overlap check against side items in lanes >= 2 and lane1 items
for k in ART:
    for i,q in pos.items():
        if q['lane']>=1 and q['x']+q['w']>AX and q['x']<AX+AW and abs(q['y']-pos[k]['y'])<84: print('OVERLAP',k,i)
open('artifacts.svg','w').write('<svg xmlns="http://www.w3.org/2000/svg">\n'+'\n'.join(out)+'\n</svg>')
print(len(ART))
