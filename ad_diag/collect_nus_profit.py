import json, sys, io, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_mcp(path):
    raw = open(path, encoding='utf-8-sig').read().strip()
    if raw.startswith('\n'):
        raw = raw[1:]
    if raw.startswith('The MCP server responded with: '):
        raw = raw[len('The MCP server responded with: '):]
    arr = json.loads(raw)
    inner = json.loads(arr[0]['text'])
    return inner

files = {
 'p0':  r'C:\Users\dell\AppData\Local\Temp\trae\toolcall-output\721ca129-0495-4a0d-92da-96f0bf8143b6.txt',
 'p500':r'C:\Users\dell\AppData\Local\Temp\trae\toolcall-output\a8c229b0-8f61-4ba1-bdc6-89d33201a7fb.txt',
 'p1000':r'C:\Users\dell\AppData\Local\Temp\trae\toolcall-output\1c6a6820-26dd-48d5-9dc6-37713f39f043.txt',
 'p1500':r'C:\Users\dell\AppData\Local\Temp\trae\toolcall-output\d15498d7-16d4-4df3-8efe-ec72a0c5173e.txt',
 'p2000':r'C:\Users\dell\AppData\Local\Temp\trae\toolcall-output\aaece5d7-0510-4824-8fda-525f35d2d4f1.txt',
 'p2500':r'C:\Users\dell\AppData\Local\Temp\trae\toolcall-output\72272a18-d84b-4224-acc2-b33cd7c520ca.txt',
}

def is_nus(r):
    pl = r.get('price_list') or []
    return any(str(p.get('sid'))=='4689' for p in pl)

all_nus = {}
for tag, path in files.items():
    inner = load_mcp(path)
    lst = inner.get('data',{}).get('data',{}).get('list',[])
    for r in lst:
        if is_nus(r):
            pl = r.get('price_list') or []
            sku = pl[0].get('seller_sku') if pl else None
            if not sku:
                continue
            all_nus[sku] = {
                'gross_profit': float(r.get('gross_profit') or 0),
                'spend': -float(r.get('spend') or 0),  # negative
                'ad_sales_amount': float(r.get('ad_sales_amount') or 0),
                'amount': float(r.get('amount') or 0),
                'volume': float(r.get('volume') or 0),
                'gross_margin': r.get('gross_margin'),
                'net_gross_margin': r.get('net_gross_margin'),
            }

print('total N-US profit SKUs:', len(all_nus))
json.dump(all_nus, open('nus_profit.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
# sort by spend desc
for sku, v in sorted(all_nus.items(), key=lambda x:-x[1]['spend'])[:30]:
    print(f"{sku}\tspend={v['spend']:.2f}\tad_sales={v['ad_sales_amount']:.2f}\tgp={v['gross_profit']:.2f}\tamount={v['amount']:.2f}\tvol={v['volume']:.0f}")