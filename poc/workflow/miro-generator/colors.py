"""Derive cluster, phase and sub-phase colours and write an update for the shapes in Frame 2.

Parent (cluster): hue H, lightness 0.74, saturation 0.50.
Phase: lighter (0.84), hue spread evenly over H +/- 14 degrees across the cluster's phases.
Sub-phase: lighter again (0.92), hue spread over phase hue +/- 6 degrees.
Border and text: the same hue, darker (border 0.38-0.48, text 0.22-0.26).
The tree holds Miro widget ids (suffixes after '34587646892') from the board as built on 2026-11-03.
"""
import colorsys
P = '34587646892'
FRAME = '3458764689255712008'
tree = [  # (cluster id, hue, [(phase id, [sub-phase ids])])
 ('50965836', 205, [('50965837', ['50965838', '50965839']), ('50965840', ['50965841']),
                    ('50965842', ['50965843', '50965844']), ('50965845', ['50965846', '50965847'])]),
 ('51119809', 265, [('51119810', ['51119811', '51119812']), ('51119813', ['51119814', '51119815']),
                    ('51119816', ['51119817', '51119818'])]),
 ('51326739', 145, [('51326740', ['51326741', '51326742']),
                    ('51326743', ['51326744', '51326745', '51326746', '51326747', '51326748', '51326749', '51326750'])]),
 ('51424493', 28,  [('51424494', []), ('51424495', ['51424496', '51424497']), ('51424498', []),
                    ('51424499', []), ('51424500', [])]),
]
def hx(h, l, s):
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360, l, s)
    return '#%02x%02x%02x' % (round(r * 255), round(g * 255), round(b * 255))
def spread(n, w): return [0] if n == 1 else [-w + 2 * w * i / (n - 1) for i in range(n)]
out = []
for cid, h, phases in tree:
    out.append(f'<rect data-miro-id="{P}{cid}" fill="{hx(h,.74,.50)}" stroke="{hx(h,.38,.45)}" data-text-color="{hx(h,.22,.5)}" />')
    for off, (pid, subs) in zip(spread(len(phases), 14), phases):
        ph = h + off
        out.append(f'<rect data-miro-id="{P}{pid}" fill="{hx(ph,.84,.55)}" stroke="{hx(ph,.42,.45)}" data-text-color="{hx(ph,.24,.5)}" />')
        for so, sid in zip(spread(len(subs), 6), subs):
            sh = ph + so
            out.append(f'<rect data-miro-id="{P}{sid}" fill="{hx(sh,.92,.6)}" stroke="{hx(sh,.48,.45)}" data-text-color="{hx(sh,.26,.5)}" />')
open('colors.svg', 'w').write(
    '<svg xmlns="http://www.w3.org/2000/svg">\n'
    f'<g data-miro-id="{FRAME}" data-frame="Frame 2" transform="translate(8190,-388)">\n'
    '<rect data-type="frame" x="0" y="0" width="5459" height="20072" fill="#ffffff" />\n'
    + '\n'.join(out) + '\n</g>\n</svg>')
