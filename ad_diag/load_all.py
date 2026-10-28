import json, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_mcp(path):
    raw = open(path, encoding='utf-8-sig').read()
    if raw.startswith('\n'):
        raw = raw[1:]
    if raw.endswith('\n'):
        raw = raw[:-1]
    if raw.startswith('The MCP server responded with: '):
        raw = raw[len('The MCP server responded with: '):]
    arr = json.loads(raw)
    texts = [x.get('text','') for x in arr if x.get('type')=='text']
    return json.loads(texts[0])

def describe(name, path):
    if not os.path.exists(path):
        print(f'{name}: MISSING'); return
    inner = load_mcp(path)
    json.dump(inner, open(f'{name}.json','w',encoding='utf-8'), ensure_ascii=False)
    data = inner.get('data')
    # data may be dict or list
    if isinstance(data, dict):
        inner_data = data.get('data')
        total = data.get('total') or (inner_data.get('total') if isinstance(inner_data,dict) else None)
        n = None
        if isinstance(inner_data, dict):
            n = len(inner_data.get('records') or inner_data.get('list') or [])
        elif isinstance(inner_data, list):
            n = len(inner_data)
        print(f'{name}: total={total} n_records_now={n} data_type={type(inner_data).__name__}')
    elif isinstance(data, list):
        print(f'{name}: data is list len={len(data)}')
    else:
        print(f'{name}: data type {type(data)}')

files = {
 'ad_campaign': r'C:\Users\dell\AppData\Local\Temp\trae\toolcall-output\191b3e68-9ae5-4873-b1b0-7913524eff7f.txt',
 'ad_group':    r'C:\Users\dell\AppData\Local\Temp\trae\toolcall-output\a110a87a-73f8-4f58-9ba9-ce2b6854da9b.txt',
 'ad_product':  r'C:\Users\dell\AppData\Local\Temp\trae\toolcall-output\134e5fd9-6069-44fc-b97c-40bd6cf46e7d.txt',
 'profit':      r'C:\Users\dell\AppData\Local\Temp\trae\toolcall-output\d7c53fe7-daee-40d1-8f15-176333acc1fe.txt',
 'stock':       r'C:\Users\dell\AppData\Local\Temp\trae\toolcall-output\349311a7-5f22-4ee7-b15c-363ac64a0e89.txt',
}
for name, path in files.items():
    describe(name, path)