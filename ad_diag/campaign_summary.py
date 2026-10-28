import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from collections import defaultdict

# Campaign-level by type
ac = json.load(open('ad_campaign.json', encoding='utf-8'))['data']['data']
camp_type = defaultdict(lambda: {'spends':0.0,'sales':0.0,'impressions':0.0,'clicks':0.0,'orders':0.0,'campaigns':0})
for r in ac:
    st = r.get('sponsored_type')
    if not st:
        continue
    t = 'SB' if st=='hsa' else ('SD' if st=='sd' else st.upper())
    c = camp_type[t]
    c['spends'] += float(r.get('spends') or 0)
    c['sales'] += float(r.get('sales') or 0)
    c['impressions'] += float(r.get('impressions') or 0)
    c['clicks'] += float(r.get('clicks') or 0)
    c['orders'] += float(r.get('orders') or 0)
    c['campaigns'] += 1

print("=== 广告类型汇总（活动级）===")
print(f"{'类型':<6}{'活动数':>6}{'花费':>10}{'销售额':>10}{'ACOS':>8}{'CTR':>7}{'CVR':>7}{'曝光':>10}{'点击':>8}")
for t, c in camp_type.items():
    acos = c['spends']/c['sales']*100 if c['sales'] else 0
    ctr = c['clicks']/c['impressions']*100 if c['impressions'] else 0
    cvr = c['orders']/c['clicks']*100 if c['clicks'] else 0
    print(f"{t:<6}{c['campaigns']:>6}{c['spends']:>10.2f}{c['sales']:>10.2f}{acos:>7.2f}%{ctr:>6.2f}%{cvr:>6.2f}%{c['impressions']:>10.0f}{c['clicks']:>8.0f}")

# total row from ac[0]
r0 = ac[0]
print(f"\n合计: 花费={r0.get('spends')} 销售={r0.get('sales')} ACOS={r0.get('acos')}% 曝光={r0.get('impressions')} 点击={r0.get('clicks')}")

# Top campaigns by spend
print("\n=== TOP 20 广告活动（按花费）===")
# campaign report rows with campaign via name? campaign field is campaign_name? Let's check
print(f"{'类型':<5}{'花费':>10}{'销售':>10}{'ACOS':>8}{'点击':>7}{'订单':>7}")
for r in ac[1:]:
    st = r.get('sponsored_type')
    if not st: continue
    t = 'SB' if st=='hsa' else ('SD' if st=='sd' else st.upper())
    print(f"{t:<5}{float(r.get('spends') or 0):>10.2f}{float(r.get('sales') or 0):>10.2f}{r.get('acos') or '-':>8}{float(r.get('clicks') or 0):>7.0f}{float(r.get('orders') or 0):>7.0f}")