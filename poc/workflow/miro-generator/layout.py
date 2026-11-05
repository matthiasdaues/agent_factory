import json
from xml.sax.saxutils import escape
def esc(s): return escape(s, {'"': '&quot;'})
d = json.load(open('detail.json')); spec, edges = d['spec'], d['edges']
STY = {'agent': ('#f0f5fd', '#305bab', '#1a1a1a'), 'human': ('#fff5ed', '#9b4a08', '#1a1a1a'),
       'gate': ('#fffbed', '#af7e04', '#1a1a1a'), 'decision': ('#fffbed', '#af7e04', '#1a1a1a'),
       'end': ('#ffffff', '#1a1a1a', '#1a1a1a'), 'fail': ('#fff0f0', '#bd0a0a', '#1a1a1a'),
       'gap': ('#fff0f0', '#bd0a0a', '#bd0a0a')}
SH, DH, SW, DW, LW, RG = 84, 104, 380, 270, 330, 40
CHG = {'S': 104, 'P': 152, 'C': 216}
PADS = {'S': 32, 'P': 52, 'C': 76}
XC, WC = 8240, 469
X_PH, W_PH = XC + WC + 48, 380
X_SUB, W_SUB = X_PH + W_PH + 48, 320
FX = X_SUB + W_SUB + 128
LG = 80
lane_x = lambda l: FX if l == 0 else FX + SW + LG + (l - 1) * (LW + LG)
y = 14 + PADS['C'] + PADS['P'] + PADS['S']
pos, groups, cur = {}, [], {'C': None, 'P': None, 'S': None}
pending = None; started = False
for e in spec:
    if isinstance(e, list):
        lvl, name = e
        if started:
            pending = lvl if pending is None or 'CPS'.index(lvl) < 'CPS'.index(pending) else pending
        for l in 'CPS'['CPS'.index(lvl):]: cur[l] = None
        g = {'lvl': lvl, 'name': name, 'items': [], 'subs': 0}
        if lvl == 'S' and cur['P'] is not None: cur['P']['subs'] += 1
        cur[lvl] = g; groups.append(g); continue
    it = e
    h = DH if it['kind'] == 'decision' else SH
    if it['lane'] == 0:
        if pending: y += CHG[pending] - RG; pending = None
        top = y; y += h + RG; started = True
        w = DW if it['kind'] == 'decision' else SW; x = FX + (SW - w) / 2
    else:
        a = pos[it['at']]; top = a['y'] + a['h'] / 2 - h / 2
        w = DW if it['kind'] == 'decision' else LW; x = lane_x(it['lane'])
    pos[it['id']] = dict(x=x, y=top, w=w, h=h, lane=it['lane'], it=it)
    for l in 'CPS':
        if cur[l] is not None: cur[l]['items'].append(it['id'])
out = []
def span(g):
    return min(pos[i]['y'] for i in g['items']) - PADS[g['lvl']], max(pos[i]['y'] + pos[i]['h'] for i in g['items']) + PADS[g['lvl']]
clusters = {}
for g in groups:
    a, b = span(g)
    if g['lvl'] == 'S':
        out.append(f'<rect x="{X_SUB}" y="{a:.0f}" width="{W_SUB}" height="{b-a:.0f}" rx="24" fill="none" stroke="#1a1a1a" stroke-width="2" data-content="{esc(g["name"])}" data-text-color="#1a1a1a" data-font-family="noto_sans" data-font-size="22" />')
    elif g['lvl'] == 'P':
        w = W_PH if g['subs'] else W_PH + 48 + W_SUB
        out.append(f'<rect x="{X_PH}" y="{a:.0f}" width="{w}" height="{b-a:.0f}" rx="24" fill="none" stroke="#1a1a1a" stroke-width="2" data-content="{esc(g["name"])}" data-text-color="#1a1a1a" data-font-family="noto_sans" data-font-size="33" />')
    else:
        clusters[g['name']] = (a, b)
for i, p in pos.items():
    it = p['it']; f, s, t = STY[it['kind']]
    title = it['title'] if it['kind'] == 'decision' else f'<b>{it["title"]}</b>'
    body = title + (f'<br>{it["sub"]}' if it['sub'] else '')
    shape = ' data-shape="rhombus"' if it['kind'] == 'decision' else ' rx="12"'
    dash = ' stroke-dasharray="5,5"' if it['kind'] == 'gap' else ''
    fs = 14 if it['kind'] == 'decision' else 16
    out.append(f'<rect id="{i}"{shape} x="{p["x"]:.0f}" y="{p["y"]:.0f}" width="{p["w"]:.0f}" height="{p["h"]:.0f}" fill="{f}" stroke="{s}" stroke-width="2"{dash} data-content="{esc(body)}" data-text-color="{t}" data-font-family="noto_sans" data-font-size="{fs}" />')
KIND = {'down': ('bottom', 'top', 0), 'side': ('right', 'left', 0), 'sidedash': ('right', 'left', 1),
        'loop': ('left', 'left', 1), 'lfwd': ('left', 'left', 0), 'ret': ('top', 'right', 1),
        'down2': ('bottom', 'right', 0), 'rloopL': ('left', 'left', 1),
        'fwdlane': ('bottom', 'right', 0)}
def pt(P, s):
    return {'bottom': (P['x'] + P['w'] / 2, P['y'] + P['h']), 'top': (P['x'] + P['w'] / 2, P['y']),
            'left': (P['x'], P['y'] + P['h'] / 2), 'right': (P['x'] + P['w'], P['y'] + P['h'] / 2)}[s]
for e in edges:
    a, b = e[0], e[1]; label = e[2] if len(e) > 2 else ''; kind = e[3] if len(e) > 3 else None
    A, B = pos[a], pos[b]
    if kind is None:
        kind = 'side' if B['lane'] > A['lane'] else 'down'
    ss, es, dash = KIND[kind]
    x1, y1 = pt(A, ss); x2, y2 = pt(B, es)
    lab = f' data-content="{esc(label)}"' if label else ''
    dd = ' stroke-dasharray="5,5"' if dash else ''
    out.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#313131" stroke-width="2" data-arrow="end" data-shape="elbowed" data-start="{a}" data-end="{b}" data-start-side="{ss}" data-end-side="{es}"{lab}{dd} />')
# legend above the flow
ly = -230
leg = [('agent', 'Agent step'), ('human', 'Human step'), ('gate', 'Gate or decision'), ('fail', 'Terminal failure'), ('gap', 'Gap in the definitions')]
pre = [f'<text x="{XC}" y="{ly-40}" font-family="noto_sans" font-size="67" font-weight="bold" fill="#1a1a1a">Agent Factory process, cluster to step</text>']
for k, (kind, lab) in enumerate(leg):
    f, s, t = STY[kind]; dash = ' stroke-dasharray="5,5"' if kind == 'gap' else ''
    pre.append(f'<rect x="{XC + k*280}" y="{ly+10}" width="250" height="60" rx="12" fill="{f}" stroke="{s}" stroke-width="2"{dash} data-content="{lab}" data-text-color="{t}" data-font-family="noto_sans" data-font-size="16" />')
pre.append(f'<textArea x="{XC + 5*280}" y="{ly+10}" width="760" font-family="noto_sans" font-size="16" fill="#595959">Solid arrows run forward. Dashed arrows loop back. Decisions branch to the right. Source: the Factory agent definitions, playbooks and scripts as of 2026-11-05.</textArea>')
svg = '<svg xmlns="http://www.w3.org/2000/svg">\n' + '\n'.join(pre + out) + '\n</svg>\n'
open('detail.svg', 'w').write(svg)
json.dump(clusters, open('clusters.json', 'w'))
print(len(svg), clusters, y)
