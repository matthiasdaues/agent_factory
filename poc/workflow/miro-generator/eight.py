import math
from xml.sax.saxutils import escape
B='https://miro.com/app/board/uXjVESrJp_A=/?moveToWidget='
P='34587646892'
def node(i,x,y,name,sub,wid,f,s,t,w=360,h=130):
    c=f'<a href="{B}{P}{wid}"><b>{name}</b></a><br>{sub}'
    return f'<rect id="{i}" x="{x-w/2:.0f}" y="{y-h/2:.0f}" width="{w}" height="{h}" rx="24" fill="{f}" stroke="{s}" stroke-width="2" data-content="{escape(c,{chr(34):"&quot;"})}" data-text-color="{t}" data-font-family="noto_sans" data-font-size="18" />'
cx, cy, a = 17500, 1400, 2200
def lem(t):
    d=1+math.sin(t)**2
    return cx + a*math.cos(t)/d, cy - a*math.sin(t)*math.cos(t)/d
right=[('build','Building','waves, TDD, gate-check, merge-story','51326743','#c0eddd','#3b9b7a','#1f5c46'),
       ('cr','Code review','IMPL findings, fixes','51424494','#edcac0','#9b513b','#5c2d1f'),
       ('al','Alignment','reconciliation, truth-map diff','51424495','#edcfc0','#9b5d3b','#5c341f'),
       ('qa','QA','feature run, Fagan, security, bug hunt','51424498','#edd5c0','#9b683b','#5c3b1f'),
       ('cl','Close the feature','DONE checklist, merge into dev','51424499','#eddac0','#9b733b','#5c421f')]
left=[('re','Retrospective','action items','51424500','#eddfc0','#9b7e3b','#5c491f'),
      ('pr','Proposal','draft, grill, review, accept','51119810','#c8c0ed','#4d3b9b','#2a1f5c'),
      ('sp','Specification','feature file, structure files, review','51119813','#d2c0ed','#633b9b','#381f5c'),
      ('ar','Architecture','DSL, ADRs, ATAM','51119816','#ddc0ed','#7a3b9b','#461f5c'),
      ('pl','Planning','EPICs, stories, backlog-lint','51326740','#c0edc8','#3b9b4d','#1f5c2a')]
out=[]
# lobe backdrops
for sx,f,lab,tc in ((-1,'#f4f2fd','Define','#6631d7'),(1,'#eaf9ef','Deliver','#067429')):
    ex=cx+sx*1150
    out.append(f'<ellipse cx="{ex}" cy="{cy}" rx="1350" ry="1000" fill="{f}" stroke="none" />')
for sx,lab,tc in ((-1,'Define','#6631d7'),(1,'Deliver','#067429')):
    out.append(f'<text x="{cx+sx*1150}" y="{cy+24}" text-anchor="middle" font-family="noto_sans" font-size="67" font-weight="bold" fill="{tc}">{lab}</text>')
order=[]
for k,item in enumerate(right):
    x,y=lem(math.pi/2-(k+1)*math.pi/6); out.append(node(item[0],x,y,*item[1:])); order.append(item[0])
for k,item in enumerate(left):
    x,y=lem(3*math.pi/2-(k+1)*math.pi/6); out.append(node(item[0],x,y,*item[1:])); order.append(item[0])
# initiation lead-in row
init=[('su','Setup','init-factory, first session','50965837','#c0e4ed','#3b8a9b','#1f515c'),
      ('fi','Fitting','five steps with Virgil','50965840','#c0dded','#3b7b9b','#1f475c'),
      ('bf','Brownfield onboarding','reverse-map, baseline','50965842','#c0d6ed','#3b6c9b','#1f3e5c'),
      ('gf','Greenfield start','vision, clarify','50965845','#c0cfed','#3b5d9b','#1f345c')]
iy=cy-1650
for k,item in enumerate(init):
    out.append(node(item[0],14700+k*430,iy,*item[1:],w=380))
out.append(f'<text x="14510" y="{iy-110}" font-family="noto_sans" font-size="33" font-weight="bold" fill="#1c3d54">Initiation, once per project</text>')
out.append(f'<text x="14510" y="{iy-260}" font-family="noto_sans" font-size="90" font-weight="bold" fill="#1a1a1a">The Factory lifecycle as a lying 8</text>')
def ln(a,b,lab='',shape='curved',ss=None,es=None,dash=False):
    sd=f' data-start-side="{ss}" data-end-side="{es}"' if ss else ''
    l=f' data-content="{lab}"' if lab else ''
    d=' stroke-dasharray="5,5"' if dash else ''
    return f'<line x1="0" y1="0" x2="1" y2="1" stroke="#313131" stroke-width="3" data-arrow="end" data-shape="{shape}" data-start="{a}" data-end="{b}"{sd}{l}{d} />'
seq=order
for a_,b_ in zip(seq,seq[1:]+seq[:1]):
    if (a_,b_)==('cl','re'): out.append(ln(a_,b_,'next change','straight'))
    elif (a_,b_)==('pl','build'): out.append(ln(a_,b_,'backlog ready','straight'))
    else: out.append(ln(a_,b_))
out.append(ln('su','fi','', 'straight','right','left'))
out.append(ln('fi','bf','', 'straight','right','left'))
out.append(ln('fi','gf','or','elbowed','top','top'))
out.append(ln('bf','pr','first change','elbowed','bottom','top'))
out.append(ln('gf','pr','','elbowed','bottom','top'))
open('eight.svg','w').write('<svg xmlns="http://www.w3.org/2000/svg">\n'+'\n'.join(out)+'\n</svg>')
