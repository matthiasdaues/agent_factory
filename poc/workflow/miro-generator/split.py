"""Split detail.svg into one self-contained chunk per cluster plus cross-cluster connectors.

Miro's create call takes at most 200,000 characters, and long tool payloads are costly.
Each chunk holds a cluster's shapes and the connectors whose both ends live in it.
Connectors that cross clusters go to cross.txt and are created last with stub elements
(<rect id="x" data-miro-id="..."/>) that point at the already created shapes.
"""
import re, json
lines = open('detail.svg').read().strip().split('\n')[1:-1]
d = json.load(open('detail.json'))
owner = {}; cl = None
for e in d['spec']:
    if isinstance(e, list):
        if e[0] == 'C': cl = e[1]
    else: owner[e['id']] = cl
clusters = json.load(open('clusters.json'))           # name -> (top, bottom), written by layout.py
order = list(clusters)
chunks = {k: [] for k in order}; cross = []
for L in lines:
    m = re.search(r'data-start="([^"]+)" data-end="([^"]+)"', L)
    if m:
        a, b = m.groups()
        (chunks[owner[a]] if owner[a] == owner[b] else cross).append(L); continue
    m = re.search(r' id="([^"]+)"', L)
    if m: chunks[owner[m.group(1)]].append(L); continue
    y = float(re.search(r' y="(-?[\d.]+)"', L).group(1))   # group boxes, title, legend: by y
    for k in order:
        if y < clusters[k][1] + 40: chunks[k].append(L); break
    else: chunks[order[-1]].append(L)
for i, k in enumerate(order):
    open(f'chunk{i+1}.svg', 'w').write('<svg xmlns="http://www.w3.org/2000/svg">\n' + '\n'.join(chunks[k]) + '\n</svg>')
open('cross.txt', 'w').write('\n'.join(cross))
