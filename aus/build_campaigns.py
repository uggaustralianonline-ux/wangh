"""合并 A-US 广告活动分页数据 -> campaigns.csv，并校验覆盖率。"""
import json, csv, glob, os

FIELDS = ['campaign_id','name','sponsored_type','ads_type','targeting_type','state',
          'serving_status','portfolio_name','daily_budget','budget','impressions','clicks',
          'ctr','cpc','spends','orders','ad_units','sales','acos','roas','cvr','cpa',
          'unit_price','direct_orders','direct_sales','direct_acos','indirect_orders',
          'indirect_sales','indirect_roas','top_of_search_impression_share','bidding_type']

rows, summary = {}, None
for p in sorted(glob.glob('raw/camp_p*.json')):
    d = json.load(open(p, encoding='utf-8'))
    for r in d['data']['data']:
        if not r.get('campaign_id'):
            if summary is None:
                summary = r
            continue
        rows[r['campaign_id']] = r

print('去重后活动数:', len(rows))

tot_spend = sum(float(r.get('spends') or 0) for r in rows.values())
tot_sales = sum(float(r.get('sales') or 0) for r in rows.values())
tot_orders = sum(int(r.get('orders') or 0) for r in rows.values())
s_spend = float(summary['spends']); s_sales = float(summary['sales']); s_orders = int(summary['orders'])
print(f'明细花费 {tot_spend:,.2f} / 汇总 {s_spend:,.2f} = 覆盖 {tot_spend/s_spend*100:.2f}%')
print(f'明细销售 {tot_sales:,.2f} / 汇总 {s_sales:,.2f} = 覆盖 {tot_sales/s_sales*100:.2f}%')
print(f'明细订单 {tot_orders:,} / 汇总 {s_orders:,} = 覆盖 {tot_orders/s_orders*100:.2f}%')

with open('campaigns.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction='ignore')
    w.writeheader()
    for r in sorted(rows.values(), key=lambda x: -float(x.get('spends') or 0)):
        w.writerow({k: r.get(k) for k in FIELDS})
json.dump(summary, open('raw/summary.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('写出 campaigns.csv')
