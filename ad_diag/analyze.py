import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from collections import defaultdict

# Load ad data (SKU level, from ad_product)
ad = json.load(open('ad_product.json', encoding='utf-8'))['data']['data']
ad_agg = defaultdict(lambda: {'spends':0.0,'sales':0.0,'impressions':0.0,'clicks':0.0,'orders':0.0,'stock':0.0,'campaigns':set()})
for r in ad:
    sku = r.get('sku')
    if not sku or r.get('sponsored_type') is None:
        continue
    a = ad_agg[sku]
    a['spends'] += float(r.get('spends') or 0)
    a['sales'] += float(r.get('sales') or 0)
    a['impressions'] += float(r.get('impressions') or 0)
    a['clicks'] += float(r.get('clicks') or 0)
    a['orders'] += float(r.get('orders') or 0)
    a['campaigns'].add(r.get('campaign_name'))
    a['stock'] = float(r.get('afn_fulfillable_quantity') or 0)

# Load profit data (N-US)
profit = json.load(open('nus_profit.json', encoding='utf-8'))

# Join on msku
merged = []
for sku, a in ad_agg.items():
    p = profit.get(sku)
    row = {
        'sku': sku,
        'spend': a['spends'],
        'ad_sales': a['sales'],
        'orders': a['orders'],
        'clicks': a['clicks'],
        'impressions': a['impressions'],
        'stock': a['stock'],
        'acos': (a['spends']/a['sales']*100) if a['sales'] else None,
        'ctr': (a['clicks']/a['impressions']*100) if a['impressions'] else None,
        'cvr': (a['orders']/a['clicks']*100) if a['clicks'] else None,
        'gross_profit': p['gross_profit'] if p else None,
        'gp_amount': p['amount'] if p else None,
        'gp_volume': p['volume'] if p else None,
        'total_sales': p['amount'] if p else None,
    }
    if p:
        row['ad_share_of_profit'] = (a['spends']/abs(p['gross_profit'])) if p['gross_profit'] else None
        row['tacos'] = (a['spends']/p['amount']*100) if p['amount'] else None
    merged.append(row)

# sort by spend desc
merged.sort(key=lambda x: -x['spend'])

print(f"{'SKU':<16}{'花费':>9}{'广告销':>9}{'净利':>9}{'广告费/净利':>12}{'TACOS':>8}{'ACOS':>8}{'库存':>7}{'CTR':>6}{'CVR':>6}")
for r in merged:
    asp = f"{r['ad_share_of_profit']:.2f}x" if r.get('ad_share_of_profit') is not None else '-'
    tacos = f"{r['tacos']:.1f}%" if r.get('tacos') is not None else '-'
    acos = f"{r['acos']:.1f}%" if r.get('acos') is not None else '-'
    gp = f"{r['gross_profit']:.0f}" if r.get('gross_profit') is not None else '-'
    ctr = f"{r['ctr']:.1f}" if r.get('ctr') is not None else '-'
    cvr = f"{r['cvr']:.1f}" if r.get('cvr') is not None else '-'
    print(f"{r['sku']:<16}{r['spend']:>9.0f}{r['ad_sales']:>9.0f}{gp:>9}{asp:>12}{tacos:>8}{acos:>8}{r['stock']:>7.0f}{ctr:>6}{cvr:>6}")

json.dump(merged, open('analysis_merged.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)