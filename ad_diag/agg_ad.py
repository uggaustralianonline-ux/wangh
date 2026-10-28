import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from collections import defaultdict

d = json.load(open('ad_product.json', encoding='utf-8'))
data = d['data']['data']

agg = defaultdict(lambda: {
    'spends': 0.0, 'sales': 0.0, 'impressions': 0.0,
    'clicks': 0.0, 'orders': 0.0, 'stock': 0.0, 'campaigns': set()
})
for r in data:
    sku = r.get('sku')
    if not sku or r.get('sponsored_type') is None:
        continue
    a = agg[sku]
    a['spends'] += float(r.get('spends') or 0)
    a['sales'] += float(r.get('sales') or 0)
    a['impressions'] += float(r.get('impressions') or 0)
    a['clicks'] += float(r.get('clicks') or 0)
    a['orders'] += float(r.get('orders') or 0)
    a['campaigns'].add(r.get('campaign_name'))
    a['stock'] = float(r.get('afn_fulfillable_quantity') or 0)

print('distinct SKU:', len(agg))
skus = sorted(agg.keys())
json.dump(list(agg.keys()), open('ad_skus.json', 'w', encoding='utf-8'), ensure_ascii=False)
for sku in skus:
    a = agg[sku]
    acos = (a['spends'] / a['sales'] * 100) if a['sales'] else float('inf')
    print(f"{sku}\tspends={a['spends']:.2f}\tsales={a['sales']:.2f}\timp={a['impressions']:.0f}\tclk={a['clicks']:.0f}\tord={a['orders']:.0f}\tacos={acos:.1f}%\tstock={a['stock']:.0f}")