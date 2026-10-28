import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

raw = open(r'C:\Users\dell\AppData\Local\Temp\trae\toolcall-output\721ca129-0495-4a0d-92da-96f0bf8143b6.txt', encoding='utf-8-sig').read().strip()
if raw.startswith('The MCP server responded with: '):
    raw = raw[len('The MCP server responded with: '):]
arr = json.loads(raw)
inner = json.loads(arr[0]['text'])
data = inner['data']['data']
lst = data.get('list', [])
r = lst[0]
for k, v in r.items():
    if any(x in k for x in ['spend', 'ad_sales', 'gross_profit', 'net', 'amount', 'volume', 'sku', 'sid', 'store', 'gross_margin', 'total']):
        print(k, '=', '[list]' if isinstance(v, list) else v)