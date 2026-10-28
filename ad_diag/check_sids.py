import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from collections import Counter

raw = open(r'C:\Users\dell\AppData\Local\Temp\trae\toolcall-output\721ca129-0495-4a0d-92da-96f0bf8143b6.txt', encoding='utf-8-sig').read().strip()
if raw.startswith('The MCP server responded with: '):
    raw = raw[len('The MCP server responded with: '):]
arr = json.loads(raw)
inner = json.loads(arr[0]['text'])
data = inner['data']['data']
lst = data.get('list', [])
print('list len', len(lst))
# check sids field
def sidsof(r):
    return r.get('sids') or []
all_sids = Counter()
for r in lst:
    for s in sidsof(r):
        all_sids[s] += 1
print('sids dist (first 20):', dict(list(all_sids.most_common(20))))
# find items with sid 4689 (N-US)
nus = [r for r in lst if 4689 in sidsof(r)]
print('items with sid 4689:', len(nus))
if nus:
    r = nus[0]
    print('sample:', {k: r.get(k) for k in ['gross_profit','spend','ad_sales_amount','amount','volume','net_gross_margin','gross_margin','seller_store_countries']})
    print('price_list:', r.get('price_list'))