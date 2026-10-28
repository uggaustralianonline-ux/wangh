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
sid_counter = Counter()
for r in lst:
    pl = r.get('price_list') or []
    for p in pl:
        sid_counter[p.get('sid')] += 1
print('price_list sid dist:', dict(sid_counter.most_common(20)))
# filter sid 4689
def is_nus(r):
    pl = r.get('price_list') or []
    return any(str(p.get('sid'))=='4689' for p in pl)
nus = [r for r in lst if is_nus(r)]
print('N-US items:', len(nus))
for r in nus[:5]:
    pl = r.get('price_list') or []
    sku = pl[0].get('seller_sku') if pl else None
    print(sku, 'gross_profit=', r.get('gross_profit'), 'spend=', r.get('spend'), 'ad_sales_amount=', r.get('ad_sales_amount'), 'amount=', r.get('amount'), 'volume=', r.get('volume'))