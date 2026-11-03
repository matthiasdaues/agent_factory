import json
exec(open('layout.py').read().split('out = []')[0])  # positions only
from xml.sax.saxutils import escape
def esc(s): return escape(s, {'"': '&quot;'})
ART = {
 'i2': ['.agent-factory/', 'config/project-context.json'],
 'i5': ['spike in a sandbox (optional)'],
 'f0': ['config/model.conf'],
 'f1': ['project-context.json: fingerprint'],
 'f2': ['docs/agent-context.md'],
 'f3': ['docs/testing.yaml'],
 'f4': ['.pre-commit-config.yaml'],
 'b1': ['todos.md: missing tests as debt'],
 'b2': ['docs/spec/scope-map.md', 'docs/spec/glossary.md (seeded)'],
 'b4': ['docs/spec/architecture.dsl', 'docs/arc42/, docs/adr/'],
 'b6': ['glossary.md', 'entity-model.md'],
 'b7': ['features/&lt;project&gt;.feature', 'work/&lt;project&gt;-gaps.md'],
 'b8': ['validation-rules.md', 'interface-contracts.md, state-machines.md'],
 'b9': ['docs/reviews/spec-review-&lt;date&gt;.md', 'docs/findings/SPEC-NNNN'],
 'b10': ['architecture.dsl: components', 'arc42 chapters 5 to 7, ADRs'],
 'b11': ['atam-review.md', 'docs/findings/ATAM-NNNN'],
 'b12': ['docs/agent-context.md'],
 'b13': ['reconciliation report', 'docs/findings/RECON-NNNN'],
 'g0': ['poc/spike/ or docs/spikes/', 'ADR when decided'],
 'g2': ['docs/agent-context.md'],
 'p1': ['docs/proposals/&lt;name&gt;.md', 'status: draft'],
 'p2': ['Decisions table: DEC-NN'],
 'p3': ['cut plan, edited proposal'],
 'p4': ['Primer section'],
 'p6': ['status: open, commit'],
 'p7': ['Review findings: PROP-NN', 'Review passes row'],
 'p9': ['status: accepted', 'baseline SHA'],
 's1': ['features/&lt;name&gt;.feature', 'work/&lt;name&gt;-gaps.md'],
 's2': ['scope-map.md: specified rows'],
 's3': ['entity-model.md, state-machines.md', 'interface-contracts.md, validation-rules.md'],
 's4': ['work/&lt;name&gt;-qa-strategy.md'],
 's6': ['docs/reviews/spec-review-&lt;date&gt;.md', 'docs/findings/SPEC-NNNN'],
 's7': ['impact.architecture_change'],
 'a1': ['docs/spec/architecture.dsl', 'exported diagrams'],
 'a2': ['docs/arc42/ chapters'],
 'a3p': ['Pugh matrix'],
 'a4': ['docs/adr/NNNN-&lt;title&gt;.md', 'chapter 9 index'],
 'a6': ['atam-review.md', 'docs/findings/ATAM-NNNN'],
 'q1': ['EPIC slicing approach'],
 'q2': ['backlog/epics.md'],
 'q25': ['epics.md: testability and', 'contract ownership tables'],
 'q3': ['slice table per EPIC'],
 'q4': ['backlog/ST-NNNN.md'],
 'q6': ['story: contract decisions,', 'Required API Behavior'],
 'q7': ['dispatch stories ST-NNNN'],
 'w1': ['dispatch ledger, wave plan'],
 'w2': ['worktree and branch per story'],
 'd2': ['tests and code'],
 'd3': ['story commits', 'spec edits via spec-feedback'],
 'w3': ['gate reports: crap-score, mutation,', 'test-design-verify, dependency-check'],
 'x5': ['merged story, ledger entry', 'story status: done'],
 'w5': ['ledger: wave branch head'],
 'n3': ['commit with the story ID'],
 'n4': ['docs/findings/IMPL-NNNN'],
 'c1': ['docs/findings/IMPL-NNNN'],
 'r2': ['updated spec and architecture', 'docs/findings/RECON-NNNN'],
 'r4': ['scope-map.md: implemented rows'],
 'r6': ['RECON-TEST-PATH, RECON-TEST-COVERAGE'],
 'u1': ['docs/findings/BUG-NNNN'],
 'u2': ['FAGAN-NNNN, SEC-NNNN'],
 'u3': ['regression tests, fix commits'],
 'z1': ['handoff with branch tips'],
 'z3': ['merge commit on dev', 'proposal status: implemented'],
 't1': ['docs/reviews/retro-&lt;date&gt;.md'],
 't2': ['action items with tracking location'],
}
AX, AW = 10503, 400
out = [f'<text x="{AX}" y="60" font-family="noto_sans" font-size="33" font-weight="bold" fill="#1a1a1a">Artifacts</text>']
for k, lines in ART.items():
    p = pos[k]
    body = '\x00'.join(lines)
    out.append(f'<rect x="{AX}" y="{p["y"]:.0f}" width="{AW}" height="84" fill="#f7f7f7" stroke="#595959" stroke-width="2" data-content="{esc(body).replace(chr(0),"&lt;br&gt;")}" data-text-color="#1a1a1a" data-font-family="noto_sans" data-font-size="14" />')
# overlap check against side items in lanes >= 2 and lane1 items
for k in ART:
    for i,q in pos.items():
        if q['lane']>=1 and q['x']+q['w']>AX and q['x']<AX+AW and abs(q['y']-pos[k]['y'])<84: print('OVERLAP',k,i)
open('artifacts.svg','w').write('<svg xmlns="http://www.w3.org/2000/svg">\n'+'\n'.join(out)+'\n</svg>')
print(len(ART))
