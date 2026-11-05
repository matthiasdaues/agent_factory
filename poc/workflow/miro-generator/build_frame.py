"""Build one complete Miro frame from detail.json: groups with their colours, steps,
connectors, artifact boxes with class chips, and proposal notes.

Frame 2 got its colours and chips as later updates on the live board. This script
writes them into the frame itself, so a new frame needs no follow-up calls.
Coordinates are relative to the frame origin and use the same offset as Frame 2,
so the rows of both frames line up.

Writes frame-chunk<N>.svg (one per cluster, under the frame's group) and
frame-cross.txt (connectors between clusters, sent last with widget-id stubs).
"""
import colorsys, json, re
exec(open('layout.py').read().split('out = []')[0])  # pos, groups, layout constants
exec(open('artifacts.py').read().split('AX, AW')[0].split('from xml.sax')[1].split('\n', 1)[1])  # ART

TITLE = 'Process as of 2026-11-05'
OX, OY = 8190, -388                 # Frame 2's origin; relative = absolute - origin
AX, AW, AH = 3277, 400, 96          # artifact column as it stands in Frame 2
NX, NW = AX + AW + 64, 380          # proposal notes column
HUE = {'Initiation': 205, 'Specification': 265, 'Implementation': 145, 'Reconciliation': 28}
CHIP = {  # class: (width, fill, text, stroke)
    'Core': (60, '#dedaff', '#6631d7', None), 'Seam': (60, '#c6dcff', '#305bab', None),
    'Setup': (69, '#e7e7e7', '#313131', None), 'Derived view': (132, '#fff6b6', '#af7e04', None),
    'Decision record': (159, '#f8d3af', '#9b4a08', None), 'Plan': (60, '#adf0c7', '#067429', None),
    'Quality record': (150, '#ffc6c6', '#bd0a0a', None), 'Working': (87, '#ffffff', '#595959', '#595959'),
    'Product': (87, '#313131', '#ffffff', None),
}
LOOP = '<b>review-loop-cap</b> (open)<br>stops after 3 passes, then the human decides'
FIND = '<b>finding-classification</b> (accepted)<br>computed severity, minor findings to a register'
NOTES = {
    'p7': FIND, 'p7d': LOOP, 'b9': FIND, 'b9d': LOOP, 'b11': FIND, 'b11d': LOOP,
    's6': FIND, 's6d': LOOP, 'a6': FIND, 'a6d': LOOP, 'n4': FIND, 'n4d': LOOP,
    'c1': FIND, 'c1d': LOOP, 'r6d': LOOP, 'u2': FIND, 'u3d': LOOP,
    'q4': '<b>counter-ids</b> (accepted)<br>next-id hands out every new ID',
    'm0': '<b>project-agent-flows</b> (draft)<br>Windmill routes, tickets hold the work',
    'w3g': '<b>manual-mode-gates</b> (draft)<br>both modes run the gates through story-gates',
    'n2': '<b>manual-mode-gates</b> (draft)<br>a hook reruns story-gates before done',
    'x2': '<b>gate-evidence</b> (draft)<br>the premerge-check marker can be forged',
    'z2': '<b>gate-evidence</b> (draft)<br>the premerge-check marker can be forged',
}
STY = {'agent': ('#f0f5fd', '#305bab', '#1a1a1a'), 'human': ('#fff5ed', '#9b4a08', '#1a1a1a'),
       'gate': ('#fffbed', '#af7e04', '#1a1a1a'), 'decision': ('#fffbed', '#af7e04', '#1a1a1a'),
       'end': ('#ffffff', '#1a1a1a', '#1a1a1a'), 'fail': ('#fff0f0', '#bd0a0a', '#1a1a1a'),
       'gap': ('#fff0f0', '#bd0a0a', '#bd0a0a')}
KIND = {'down': ('bottom', 'top', 0), 'side': ('right', 'left', 0), 'sidedash': ('right', 'left', 1),
        'loop': ('left', 'left', 1), 'lfwd': ('left', 'left', 0), 'ret': ('top', 'right', 1),
        'down2': ('bottom', 'right', 0), 'rloopL': ('left', 'left', 1), 'fwdlane': ('bottom', 'right', 0)}


def hx(h, l, s):
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360, l, s)
    return '#%02x%02x%02x' % (round(r * 255), round(g * 255), round(b * 255))


def spread(n, w):
    return [0] if n == 1 else [-w + 2 * w * i / (n - 1) for i in range(n)]


def rx(x): return x - OX
def ry(y): return y - OY


def span(g):
    return (min(pos[i]['y'] for i in g['items']) - PADS[g['lvl']],
            max(pos[i]['y'] + pos[i]['h'] for i in g['items']) + PADS[g['lvl']])


# Group tree and colours, in the order of the spec.
owner, cl = {}, None
tree = []
for g in groups:
    if g['lvl'] == 'C':
        cl = g; tree.append((g, []))
    elif g['lvl'] == 'P':
        tree[-1][1].append((g, []))
    else:
        tree[-1][1][-1][1].append(g)
    for i in g['items']:
        if g['lvl'] == 'C': owner[i] = g['name']
colour = {}
for c, phases in tree:
    h = HUE[c['name']]
    colour[id(c)] = (hx(h, .74, .50), hx(h, .38, .45), hx(h, .22, .5))
    for off, (p, subs) in zip(spread(len(phases), 14), phases):
        ph = h + off
        colour[id(p)] = (hx(ph, .84, .55), hx(ph, .42, .45), hx(ph, .24, .5))
        for so, s in zip(spread(len(subs), 6), subs):
            colour[id(s)] = (hx(ph + so, .92, .6), hx(ph + so, .48, .45), hx(ph + so, .26, .5))

chunks = {c['name']: [] for c, _ in tree}
first = tree[0][0]['name']


def add(cluster, line): chunks[cluster].append(line)


# Title and legend go with the first chunk.
ly = 158
add(first, f'<text x="{rx(XC)}" y="{ly - 40}" font-family="noto_sans" font-size="67" font-weight="bold" fill="#1a1a1a">Agent Factory process, cluster to step</text>')
leg = [('agent', 'Agent step'), ('human', 'Human step'), ('gate', 'Gate or decision'),
       ('fail', 'Terminal failure'), ('gap', 'Gap in the definitions')]
for k, (kind, lab) in enumerate(leg):
    f, s, t = STY[kind]; dash = ' stroke-dasharray="5,5"' if kind == 'gap' else ''
    add(first, f'<rect x="{rx(XC) + k * 280}" y="{ly + 10}" width="250" height="60" rx="12" fill="{f}" stroke="{s}" stroke-width="2"{dash} data-content="{lab}" data-text-color="{t}" data-font-family="noto_sans" data-font-size="16" />')
add(first, f'<rect x="{rx(XC) + 5 * 280}" y="{ly + 10}" width="250" height="60" fill="#fff6b6" stroke="#af7e04" stroke-width="2" data-content="Proposal, not implemented" data-text-color="#1a1a1a" data-font-family="noto_sans" data-font-size="16" />')
add(first, f'<textArea x="{rx(XC) + 6 * 280}" y="{ly + 10}" width="1000" font-family="noto_sans" font-size="16" fill="#595959">Solid arrows run forward. Dashed arrows loop back. Decisions branch to the right. Source: the Factory agent definitions, playbooks and scripts on dev as of 2026-11-05. Notes on the right name proposals that would change a step; none of them is implemented yet.</textArea>')
add(first, f'<text x="{AX}" y="{ly + 300}" font-family="noto_sans" font-size="33" font-weight="bold" fill="#1a1a1a">Artifacts</text>')
add(first, f'<text x="{NX}" y="{ly + 300}" font-family="noto_sans" font-size="33" font-weight="bold" fill="#1a1a1a">Proposals</text>')

# Group boxes, outermost first so they sit behind.
for c, phases in tree:
    a, b = span(c); f, s, t = colour[id(c)]
    add(c['name'], f'<rect x="{rx(XC)}" y="{ry(a):.0f}" width="{WC}" height="{b - a:.0f}" rx="24" fill="{f}" stroke="{s}" stroke-width="2" data-content="{esc(c["name"])}" data-text-color="{t}" data-font-family="noto_sans" data-font-size="48" />')
    for p, subs in phases:
        a, b = span(p); f, s, t = colour[id(p)]
        w = W_PH if subs else W_PH + 48 + W_SUB
        add(c['name'], f'<rect x="{rx(X_PH)}" y="{ry(a):.0f}" width="{w}" height="{b - a:.0f}" rx="24" fill="{f}" stroke="{s}" stroke-width="2" data-content="{esc(p["name"])}" data-text-color="{t}" data-font-family="noto_sans" data-font-size="33" />')
        for sg in subs:
            a, b = span(sg); f, s, t = colour[id(sg)]
            add(c['name'], f'<rect x="{rx(X_SUB)}" y="{ry(a):.0f}" width="{W_SUB}" height="{b - a:.0f}" rx="24" fill="{f}" stroke="{s}" stroke-width="2" data-content="{esc(sg["name"])}" data-text-color="{t}" data-font-family="noto_sans" data-font-size="22" />')

# Steps, artifacts with chips, notes.
for i, p in pos.items():
    it = p['it']; f, s, t = STY[it['kind']]; c = owner[i]
    title = it['title'] if it['kind'] == 'decision' else f'<b>{it["title"]}</b>'
    body = title + (f'<br>{it["sub"]}' if it['sub'] else '')
    shape = ' data-shape="rhombus"' if it['kind'] == 'decision' else ' rx="12"'
    dash = ' stroke-dasharray="5,5"' if it['kind'] == 'gap' else ''
    fs = 14 if it['kind'] == 'decision' else 16
    add(c, f'<rect id="{i}"{shape} x="{rx(p["x"]):.0f}" y="{ry(p["y"]):.0f}" width="{p["w"]:.0f}" height="{p["h"]:.0f}" fill="{f}" stroke="{s}" stroke-width="2"{dash} data-content="{esc(body)}" data-text-color="{t}" data-font-family="noto_sans" data-font-size="{fs}" />')
for k, (lines, chips) in ART.items():
    p = pos[k]; c = owner[k]; y = ry(p['y']) + (p['h'] - AH) / 2
    body = '&lt;br&gt;'.join(esc(l) for l in lines)
    add(c, f'<rect x="{AX}" y="{y:.0f}" width="{AW}" height="{AH}" fill="#f7f7f7" stroke="#595959" stroke-width="2" data-content="{body}" data-text-color="#1a1a1a" data-font-family="noto_sans" data-font-size="14" />')
    cx = AX + 10
    for ch in chips:
        w, fill, txt, stroke = CHIP[ch]
        st = f' stroke="{stroke}" stroke-width="2" stroke-dasharray="5,5"' if stroke else ' stroke="none"'
        add(c, f'<rect x="{cx}" y="{y + 10:.0f}" width="{w}" height="26" rx="13" fill="{fill}"{st} data-content="{ch}" data-text-color="{txt}" data-font-family="noto_sans" data-font-size="12" data-font-weight="bold" />')
        cx += w + 8
for k, text in NOTES.items():
    p = pos[k]; c = owner[k]; y = ry(p['y']) + (p['h'] - 84) / 2
    add(c, f'<rect x="{NX}" y="{y:.0f}" width="{NW}" height="84" fill="#fff6b6" stroke="#af7e04" stroke-width="2" data-content="{esc(text)}" data-text-color="#1a1a1a" data-font-family="noto_sans" data-font-size="14" />')


def pt(P, s):
    x, y = rx(P['x']), ry(P['y'])
    return {'bottom': (x + P['w'] / 2, y + P['h']), 'top': (x + P['w'] / 2, y),
            'left': (x, y + P['h'] / 2), 'right': (x + P['w'], y + P['h'] / 2)}[s]


cross = []
for e in edges:
    a, b = e[0], e[1]; label = e[2] if len(e) > 2 else ''; kind = e[3] if len(e) > 3 else None
    A, B = pos[a], pos[b]
    if kind is None:
        kind = 'side' if B['lane'] > A['lane'] else 'down'
    ss, es, dash = KIND[kind]
    x1, y1 = pt(A, ss); x2, y2 = pt(B, es)
    lab = f' data-content="{esc(label)}"' if label else ''
    dd = ' stroke-dasharray="5,5"' if dash else ''
    line = f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#313131" stroke-width="2" data-arrow="end" data-shape="elbowed" data-start="{a}" data-end="{b}" data-start-side="{ss}" data-end-side="{es}"{lab}{dd} />'
    (chunks[owner[a]] if owner[a] == owner[b] else cross).append(line)

bottom = max(ry(p['y'] + p['h']) for p in pos.values()) + 200
W, H = NX + NW + 64, int(bottom)
for n, (name, lines) in enumerate(chunks.items(), 1):
    open(f'frame-chunk{n}.svg', 'w').write(
        '<svg xmlns="http://www.w3.org/2000/svg">\n'
        f'<g id="frame" transform="translate(20600,-388)" data-frame="{TITLE}">\n'
        f'<rect data-type="frame" x="0" y="0" width="{W}" height="{H}" fill="#ffffff" data-title="{TITLE}" />\n'
        + '\n'.join(lines) + '\n</g>\n</svg>\n')
    print(n, name, len(lines), 'items', len(open(f'frame-chunk{n}.svg').read()), 'chars')
open('frame-cross.txt', 'w').write('\n'.join(cross))
print('cross', len(cross), 'frame', W, 'x', H)
