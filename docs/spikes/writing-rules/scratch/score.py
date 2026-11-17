import re,json,sys
key=json.load(open(sys.argv[1])); v={}
for l in open(sys.argv[2]):
    m=re.match(r'\|\s*\**(P\d\d)\**\s*\|\s*`?\**(fails|passes)',l)
    if m: v[m.group(1)]=m.group(2)
tp=sum(1 for p,(i,k) in key.items() if k=='objection' and v.get(p)=='fails')
fp=sum(1 for p,(i,k) in key.items() if k=='control' and v.get(p)=='fails')
no=sum(1 for k in key.values() if k[1]=='objection'); nc=len(key)-no
print(f"{sys.argv[2]}: parsed {len(v)}/{len(key)}; objections caught {tp}/{no}; controls flagged {fp}/{nc}")
print(" missed:",sorted(key[p][0] for p,(i,k) in key.items() if k=='objection' and v.get(p)!='fails'))
print(" false alarms:",sorted(key[p][0] for p,(i,k) in key.items() if k=='control' and v.get(p)=='fails'))
