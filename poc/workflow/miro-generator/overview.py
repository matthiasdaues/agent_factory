from xml.sax.saxutils import escape
def esc(s): return escape(s, {'"':'&quot;'})
CL = {'Initiation':(14,1356),'Specification':(1510,1356),'Implementation':(2986,1356),'Reconciliation':(4460,1356)}
S=('s',); D=('d',)
# item: (kind, id, title, sub) ; decision: ('d', id, question, loop_target, loop_label)
phases = [
 ('Initiation','Brownfield onboarding',[('s','bf1','Initial scan','init-factory, first-session insight'),('s','bf2','Reverse specification','reverse-map, requirements agent'),('d','bfd','Domain batch confirmed?','bf2','no'),('s','bf3','Architecture baseline','architecture agent')]),
 ('Initiation','Greenfield, from a PoC or an idea',[('s','gf0','Technical PoC','poc-spike, disposable'),('s','gf1','Vision and interview','capture-vision, conversation'),('s','gf2','Foundational proposal','draft-proposal, grilling'),('s','gf3','Spec and architecture','requirements, domain-modeling, architecture')]),
 ('Initiation','Fitting',[('s','fit','Fitting','model matrix, hooks, agent-context.md, testing.yaml'),('d','fitd','All five steps done?','fit','no'),('s','ready','Core and seam in place','project truth confirmed, Factory fitted')]),
 ('Specification','Proposal',[('s','s1','Proposal and grilling','draft-proposal, grilling'),('s','s1r','Proposal review','proposal-review agent, lector'),('d','s1d','Accepted?','s1','no')]),
 ('Specification','Specification',[('s','s2','Specification','requirements, domain-modeling, test-strategy agents'),('s','s2r','Spec review','spec-review agent, stakeholder'),('d','s2d','Findings resolved?','s2','no')]),
 ('Specification','Architecture',[('s','s3','Architecture delta','architecture agent, ADRs'),('s','s3r','ATAM','architecture-review agent'),('d','s3d','Risks accepted?','s3','no')]),
 ('Implementation','Planning',[('s','p1','Backlog creation','planning agent, create-backlog'),('d','p1d','Stories approved?','p1','no'),('s','p2','Wave planning','dependency and file-overlap analysis')]),
 ('Implementation','Building',[('s','b1','Code','developer agent, TDD'),('s','b2','Unit and integration tests','test-design'),('d','g1','Gates pass?','b1','no, fix'),('s','b3','Code review','code-review agent, Fagan, QA agent'),('d','b3d','Review approved?','b1','no, rework'),('s','b4','Merge story','merge-story, post-merge tests')]),
 ('Reconciliation','Alignment',[('s','r1','Align code and specification','reconciliation agent'),('s','r1f','Spec-feedback report','one row per finding, sent to its owner'),('d','r1d','All rows closed?','r1f','no, owner fixes'),('s','r1o','Project truth updated','core artifacts updated by their owners')]),
 ('Reconciliation','Retrospective',[('s','r2','Retrospective','coaching agent, process improvement'),('s','r2o','Practice updated','Factory, agent-context.md, testing.yaml')]),
]
SH,DH,GAP,PAD,PGAP=80,96,28,20,32
SW,DW=380,240
PX,PW=6769,420
FX=PX+PW+64; FC=FX+SW/2
def ch(items): return sum(SH if k[0]=='s' else DH for k in items)+GAP*(len(items)-1)+2*PAD
out=[]; conns=[]; ypos={}
for cl,(cy,chh) in CL.items():
    ps=[p for p in phases if p[0]==cl]
    need=[ch(p[2]) for p in ps]; spare=chh-PGAP*(len(ps)-1)-sum(need)
    assert spare>=0,(cl,spare)
    y=cy
    for p,n in zip(ps,need):
        h=n+spare/len(ps)
        out.append(f'<rect x="{PX}" y="{y:.0f}" width="{PW}" height="{h:.0f}" rx="24" fill="none" stroke="#1a1a1a" stroke-width="2" data-content="{esc(p[1])}" data-text-color="#1a1a1a" data-font-family="noto_sans" data-font-size="33" />')
        iy=y+(h-n)/2+PAD
        for it in p[2]:
            if it[0]=='s':
                c=esc(f'<b>{it[2]}</b><br>{it[3]}')
                out.append(f'<rect id="{it[1]}" x="{FX}" y="{iy:.0f}" width="{SW}" height="{SH}" rx="12" fill="#ffffff" stroke="#1a1a1a" stroke-width="2" data-content="{c}" data-text-color="#1a1a1a" data-font-family="noto_sans" data-font-size="16" />')
                ypos[it[1]]=(iy,SH); iy+=SH+GAP
            else:
                out.append(f'<rect id="{it[1]}" data-shape="rhombus" x="{FC-DW/2:.0f}" y="{iy:.0f}" width="{DW}" height="{DH}" fill="#ffffff" stroke="#1a1a1a" stroke-width="2" data-content="{esc(it[2])}" data-text-color="#1a1a1a" data-font-family="noto_sans" data-font-size="14" />')
                ypos[it[1]]=(iy,DH); iy+=DH+GAP
        y+=h+PGAP
def line(a,b,label='',ss='bottom',es='top',dash=False):
    ya=ypos[a]; yb=ypos[b]
    x1 = FC if ss in('bottom','top') else FX+SW
    x2 = FC if es in('bottom','top') else FX+SW
    y1 = ya[0]+ya[1] if ss=='bottom' else ya[0]+ya[1]/2
    y2 = yb[0] if es=='top' else yb[0]+yb[1]/2
    lab=f' data-content="{esc(label)}"' if label else ''
    d=' stroke-dasharray="5,5"' if dash else ''
    conns.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#313131" stroke-width="2" data-arrow="end" data-shape="elbowed" data-start="{a}" data-end="{b}" data-start-side="{ss}" data-end-side="{es}"{lab}{d} />')
for p in phases:
    its=p[2]
    for a,b in zip(its,its[1:]):
        line(a[1],b[1],'yes' if a[0]=='d' else '')
    for it in its:
        if it[0]=='d': line(it[1],it[3],it[4],'right','right')
line('bf3','fit','','right','right')
line('gf3','fit')
line('ready','s1','first change')
line('s1d','s2','yes')
line('s2d','s3','yes')
line('s3d','p1','accepted design')
line('p2','b1','per wave')
line('b4','r1','after the waves')
line('r1o','r2')
line('r2o','s1','next change','right','right',dash=True)
# fix: within-phase last decision -> next phase first gets 'yes' label; remove duplicates handled above
ymid=(1370+1510)/2
extra=[f'<line data-type="divider" x1="6705" y1="{ymid:.0f}" x2="{FX+SW+160}" y2="{ymid:.0f}" stroke="#b0b0b0" stroke-width="2" data-line-style="dashed" />',
 f'<text x="{FX+SW+160}" y="{ymid-14:.0f}" text-anchor="end" font-family="noto_sans" font-size="16" fill="#595959">once per project</text>',
 f'<text x="{FX+SW+160}" y="{ymid+30:.0f}" text-anchor="end" font-family="noto_sans" font-size="16" fill="#595959">per change</text>']
svg='<svg xmlns="http://www.w3.org/2000/svg">\n'+'\n'.join(out+extra+conns)+'\n</svg>\n'
open('overview.svg','w').write(svg); print(len(svg), len(conns))
