"""
N-US 店铺近30天广告投放效果归因分析
输入：
  - ad_campaign.json (活动级)
  - ad_group.json (广告组级，含 direct/indirect 拆解)
  - ad_product.json (商品级)
  - searchterm_pages/*.txt (搜索词/关键词级)
  - nus_profit.json (利润)
  - msku_local_map.json (SKU映射)
输出：attribution.json（完整归因结果）
"""
import json, io, sys, os, glob, re
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ========= 加载数据 =========
def load_searchterm_pages():
    pages = sorted(glob.glob('searchterm_pages/searchterm_p*.txt'),
                   key=lambda p: int(p.split('p')[-1].split('.')[0]))
    rows = []
    for p in pages:
        raw = open(p, encoding='utf-8-sig').read().strip()
        obj = json.loads(raw)
        text = obj['result']['content'][0]['text']
        inner = json.loads(text)
        for r in inner['data']['data']:
            if r.get('query'):  # 跳过汇总行
                rows.append(r)
    return rows

def load_json(name):
    return json.load(open(name, encoding='utf-8'))

ag = load_json('ad_group.json')['data']['data']
ac = load_json('ad_campaign.json')['data']['data'] if isinstance(load_json('ad_campaign.json').get('data'), dict) else load_json('ad_campaign.json')['data']
profit = load_json('nus_profit.json')
msku_map = load_json('msku_local_map.json')
search_terms = load_searchterm_pages()
print(f'加载完成: ad_group={len(ag)}, ad_campaign={len(ac)}, search_terms={len(search_terms)}, profit_skus={len(profit)}')

# ========= 1. 广告类型（SP/SB/SD）汇总（活动级）=========
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

print('\n=== 广告类型汇总（活动级）===')
print(f"{'类型':<6}{'活动数':>8}{'花费':>12}{'销售额':>12}{'ACOS':>8}{'CTR':>8}{'CVR':>8}{'曝光':>12}{'点击':>10}")
for t in ['SP','SB','SD']:
    c = camp_type[t]
    acos = c['spends']/c['sales']*100 if c['sales'] else 0
    ctr = c['clicks']/c['impressions']*100 if c['impressions'] else 0
    cvr = c['orders']/c['clicks']*100 if c['clicks'] else 0
    print(f"{t:<6}{c['campaigns']:>8}{c['spends']:>12.2f}{c['sales']:>12.2f}{acos:>7.2f}%{ctr:>7.2f}%{cvr:>7.2f}%{c['impressions']:>12.0f}{c['clicks']:>10.0f}")

total_sp = sum(c['spends'] for c in camp_type.values())
total_sa = sum(c['sales'] for c in camp_type.values())
print(f"合计: 花费=${total_sp:.2f} 销售=${total_sa:.2f} ACOS={total_sp/total_sa*100:.2f}%")

# ========= 2. 广告组级 direct/indirect 拆解（自然单带动） =========
print('\n=== 广告组级 direct/indirect 拆解（前20按花费）===')
print(f"{'活动名':<36}{'广告组':<28}{'类型':<4}{'花费':>8}{'广告销售':>10}{'直接销售':>10}{'间接销售':>10}{'间接占比':>8}{'直接订单':>8}{'间接订单':>8}{'ACOS':>8}")
# 过滤掉汇总行（无 campaign_name 的）
ag_detail = [r for r in ag if r.get('campaign_name')]
ag_detail.sort(key=lambda r: float(r.get('spends') or 0), reverse=True)
for r in ag_detail[:20]:
    sp = float(r.get('spends') or 0)
    sa = float(r.get('sales') or 0)
    ds = float(r.get('direct_sales') or 0)
    ids = float(r.get('indirect_sales') or 0)
    do = int(float(r.get('direct_orders') or 0))
    io_ = int(float(r.get('indirect_orders') or 0))
    share = ids/sa*100 if sa else 0
    acos = sp/sa*100 if sa else 0
    st = r.get('sponsored_type','')
    stl = 'SB' if st=='sbv' else st.upper()
    cname = (r.get('campaign_name') or '')[:34]
    gname = (r.get('name') or '')[:26]
    print(f"{cname:<36}{gname:<28}{stl:<4}{sp:>8.0f}{sa:>10.0f}{ds:>10.0f}{ids:>10.0f}{share:>7.1f}%{do:>8}{io_:>8}{acos:>7.1f}%")

# ========= 3. 关键词级 TOP 20 =========
print('\n=== 关键词级 TOP 20（按花费）===')
print(f"{'活动名':<36}{'关键词':<32}{'匹配':<8}{'花费':>8}{'广告销售':>10}{'直接销':>8}{'间接销':>8}{'间接占':>6}{'订单':>6}{'ACOS':>8}")
st_sorted = sorted(search_terms, key=lambda r: float(r.get('spends') or 0), reverse=True)
for r in st_sorted[:20]:
    sp = float(r.get('spends') or 0)
    sa = float(r.get('sales') or 0)
    ds = float(r.get('direct_sales') or 0)
    ids = float(r.get('indirect_sales') or 0)
    od = int(float(r.get('orders') or 0))
    share = ids/sa*100 if sa else 0
    acos = sp/sa*100 if sa else 0
    cname = (r.get('campaign_name') or '')[:34]
    q = (r.get('query') or '')[:30]
    mt = (r.get('match_type') or '')[:6]
    print(f"{cname:<36}{q:<32}{mt:<8}{sp:>8.2f}{sa:>10.2f}{ds:>8.2f}{ids:>8.2f}{share:>5.1f}%{od:>6}{acos:>7.1f}%")

# ========= 4. 广告组 × 利润 归因 =========
# 利润数据结构: nus_profit 是列表
print('\n=== 利润数据结构检查 ===')
print('type:', type(profit).__name__)
if isinstance(profit, list):
    print('len:', len(profit))
    print('keys:', list(profit[0].keys()) if profit else 'empty')
    print('sample:', {k:profit[0].get(k) for k in list(profit[0].keys())[:10]})
elif isinstance(profit, dict):
    print('keys:', list(profit.keys())[:10])

# 构建 sku -> 利润 的映射
profit_map = {}
if isinstance(profit, list):
    for p in profit:
        sku = p.get('localSku') or p.get('sku') or p.get('msku')
        if sku:
            profit_map[sku] = p
elif isinstance(profit, dict):
    # 可能是按 sku 索引
    for k, v in profit.items():
        if isinstance(v, dict):
            profit_map[k] = v
print(f'profit map size: {len(profit_map)}')
if profit_map:
    sk = list(profit_map.keys())[0]
    print(f'sample key: {sk}, value keys: {list(profit_map[sk].keys())[:15]}')

# ad_product 按 SKU 聚合花费
ap = load_json('ad_product.json')
if isinstance(ap, dict):
    ap_data = ap.get('data', {}).get('data', []) if isinstance(ap.get('data'), dict) else ap.get('data', [])
else:
    ap_data = ap
print(f'ad_product records: {len(ap_data)}')

ad_by_sku = defaultdict(lambda: {'spends':0.0,'sales':0.0,'orders':0.0,'clicks':0.0,'impressions':0.0})
for r in ap_data:
    sku = r.get('sku') or r.get('msku') or ''
    if not sku:
        continue
    a = ad_by_sku[sku]
    a['spends'] += float(r.get('spends') or 0)
    a['sales'] += float(r.get('sales') or 0)
    a['orders'] += float(r.get('orders') or 0)
    a['clicks'] += float(r.get('clicks') or 0)
    a['impressions'] += float(r.get('impressions') or 0)
print(f'ad_by_sku size: {len(ad_by_sku)}')

# 合并 SKU 级利润与广告
sku_merge = []
for sku, a in ad_by_sku.items():
    local_sku = msku_map.get(sku, sku)
    p = profit_map.get(local_sku) or profit_map.get(sku)
    row = {
        'sku': sku,
        'local_sku': local_sku,
        'spend': a['spends'],
        'ad_sales': a['sales'],
        'orders': a['orders'],
        'clicks': a['clicks'],
        'impressions': a['impressions'],
        'acos': (a['spends']/a['sales']*100) if a['sales'] else None,
    }
    if p:
        gp = float(p.get('gross_profit') or p.get('profit') or 0)
        amt = float(p.get('amount') or p.get('sales_amount') or 0)
        row['gross_profit'] = gp
        row['total_sales'] = amt
        row['ad_share_of_profit'] = (a['spends']/abs(gp)) if gp else None
        row['tacos'] = (a['spends']/amt*100) if amt else None
    sku_merge.append(row)

sku_merge.sort(key=lambda r: r['spend'], reverse=True)

# 分类：高效 / 保本 / 低效
# 高效: 有利润 且 广告费/净利 <= 0.5x (广告费不到利润一半，真正赚钱)
# 保本: 有利润 且 0.5x < 广告费/净利 <= 1.5x (广告基本吃掉利润或微赚)
# 低效: 净利为负 或 广告费/净利 > 1.5x (越投越亏)
cats = {'高效': [], '保本': [], '低效': []}
for r in sku_merge:
    gp = r.get('gross_profit')
    share = r.get('ad_share_of_profit')
    if gp is None:
        # 无利润数据：按 ACOS 判断
        if r.get('acos') and r['acos'] <= 25:
            cats['高效'].append(r)
        elif r.get('acos') and r['acos'] <= 45:
            cats['保本'].append(r)
        else:
            cats['低效'].append(r)
        continue
    if gp <= 0:
        cats['低效'].append(r)
    elif share is not None and share <= 0.5:
        cats['高效'].append(r)
    elif share is not None and share <= 1.5:
        cats['保本'].append(r)
    else:
        cats['低效'].append(r)

print('\n=== 广告 SKU 利润归因分类 ===')
total_cat_spend = 0
for cat, lst in cats.items():
    sp = sum(r['spend'] for r in lst)
    total_cat_spend += sp
    sa = sum(r['ad_sales'] for r in lst)
    print(f"{cat}: SKU数={len(lst)} 花费=${sp:,.2f} 占比={sp/total_sp*100:.1f}% 广告销售=${sa:,.2f}")
print(f"合计: 花费=${total_cat_spend:,.2f} (总广告花费${total_sp:,.2f}的{total_cat_spend/total_sp*100:.1f}%)")

# ========= 5. 活动级利润归因（通过关联的 SKU 估算） =========
# 简单方法：活动名中常含 SKU，如 "326-N4118-SP-KW"
# 我们从活动名中提取 SKU 前缀来关联利润
def extract_sku_from_campaign(name):
    """从活动名提取 SKU，如 326-N4118-SP-KW -> 326-N4118"""
    if not name:
        return None
    # 常见模式: {sku}-SP-..., {sku}  自动, {sku}-SB-...
    # 先尝试找 -SP- / -SB- / -SD- / 自动 之前的部分
    for suffix in ['-SP-', '-SB-', '-SD-', '-SP ', '-SB ', '-SD ', ' 自动', '-KW', '-AUTO']:
        idx = name.find(suffix)
        if idx > 0:
            return name[:idx]
    # 兜底：如果整体看起来像 SKU
    return None

# 构建活动级聚合
camp_detail = defaultdict(lambda: {
    'campaign_name':'', 'sponsored_type':'', 'spends':0.0,'sales':0.0,
    'direct_sales':0.0,'indirect_sales':0.0,'orders':0.0,
    'direct_orders':0.0,'indirect_orders':0.0,'clicks':0.0,'impressions':0.0,
    'ad_groups':0
})
for r in ag_detail:
    cid = r.get('campaign_id')
    if not cid:
        continue
    c = camp_detail[cid]
    c['campaign_name'] = r.get('campaign_name') or c['campaign_name']
    c['sponsored_type'] = r.get('sponsored_type') or c['sponsored_type']
    c['spends'] += float(r.get('spends') or 0)
    c['sales'] += float(r.get('sales') or 0)
    c['direct_sales'] += float(r.get('direct_sales') or 0)
    c['indirect_sales'] += float(r.get('indirect_sales') or 0)
    c['orders'] += float(r.get('orders') or 0)
    c['direct_orders'] += float(r.get('direct_orders') or 0)
    c['indirect_orders'] += float(r.get('indirect_orders') or 0)
    c['clicks'] += float(r.get('clicks') or 0)
    c['impressions'] += float(r.get('impressions') or 0)
    c['ad_groups'] += 1

# 关联活动利润（通过活动名中的 SKU）
camp_list = []
for cid, c in camp_detail.items():
    sku = extract_sku_from_campaign(c['campaign_name'])
    gp = None
    total_sales = None
    share = None
    tacos = None
    if sku:
        local_sku = msku_map.get(sku, sku)
        p = profit_map.get(local_sku) or profit_map.get(sku)
        if p:
            gp = float(p.get('gross_profit') or p.get('profit') or 0)
            total_sales = float(p.get('amount') or p.get('sales_amount') or 0)
            share = (c['spends']/abs(gp)) if gp else None
            tacos = (c['spends']/total_sales*100) if total_sales else None
    # 分类
    if gp is None:
        cat = '未知'
    elif gp <= 0:
        cat = '低效'
    elif share is not None and share <= 0.5:
        cat = '高效'
    elif share is not None and share <= 1.5:
        cat = '保本'
    else:
        cat = '低效'
    camp_list.append({
        'campaign_id': cid,
        'campaign_name': c['campaign_name'],
        'sponsored_type': c['sponsored_type'],
        'spends': c['spends'],
        'sales': c['sales'],
        'direct_sales': c['direct_sales'],
        'indirect_sales': c['indirect_sales'],
        'indirect_share': c['indirect_sales']/c['sales']*100 if c['sales'] else 0,
        'orders': c['orders'],
        'clicks': c['clicks'],
        'impressions': c['impressions'],
        'acos': c['spends']/c['sales']*100 if c['sales'] else None,
        'roas': c['sales']/c['spends'] if c['spends'] else None,
        'sku': sku,
        'gross_profit': gp,
        'total_sales': total_sales,
        'ad_share_of_profit': share,
        'tacos': tacos,
        'category': cat,
        'ad_groups': c['ad_groups'],
    })

camp_list.sort(key=lambda r: r['spends'], reverse=True)

# 活动级分类汇总
camp_cats = defaultdict(lambda: {'count':0,'spends':0.0,'sales':0.0})
for c in camp_list:
    cat = c['category']
    camp_cats[cat]['count'] += 1
    camp_cats[cat]['spends'] += c['spends']
    camp_cats[cat]['sales'] += c['sales']

print('\n=== 活动级利润归因分类 ===')
for cat in ['高效','保本','低效','未知']:
    c = camp_cats[cat]
    print(f"{cat}: 活动数={c['count']} 花费=${c['spends']:,.2f} 占比={c['spends']/total_sp*100:.1f}% 销售=${c['sales']:,.2f}")

# TOP 高效活动
print('\n=== TOP 10 高效活动（建议加投）===')
top_eff = [c for c in camp_list if c['category']=='高效']
top_eff.sort(key=lambda r: r['roas'] or 0, reverse=True)
print(f"{'活动名':<40}{'类型':<4}{'花费':>8}{'销售':>10}{'ACOS':>7}{'ROAS':>7}{'净利':>8}{'广告/净利':>10}{'间接占':>7}")
for c in top_eff[:10]:
    st = c['sponsored_type'] or ''
    stl = 'SB' if st=='sbv' else st.upper()
    print(f"{(c['campaign_name'] or '')[:38]:<40}{stl:<4}{c['spends']:>8.0f}{c['sales']:>10.0f}"
          f"{(c['acos'] or 0):>6.1f}%{(c['roas'] or 0):>6.2f}{(c.get('gross_profit') or 0):>8.0f}"
          f"{(c.get('ad_share_of_profit') or 0):>9.2f}x{c['indirect_share']:>6.1f}%")

# TOP 低效活动
print('\n=== TOP 10 低效活动（建议削减/暂停）===')
top_low = [c for c in camp_list if c['category']=='低效']
top_low.sort(key=lambda r: r['spends'], reverse=True)
for c in top_low[:10]:
    st = c['sponsored_type'] or ''
    stl = 'SB' if st=='sbv' else st.upper()
    gp = c.get('gross_profit')
    gp_s = f"{gp:,.0f}" if gp is not None else "N/A"
    share_s = f"{c['ad_share_of_profit']:.2f}x" if c.get('ad_share_of_profit') is not None else "N/A"
    print(f"{(c['campaign_name'] or '')[:38]:<40}{stl:<4}{c['spends']:>8.0f}{c['sales']:>10.0f}"
          f"{(c['acos'] or 0):>6.1f}%{(c['roas'] or 0):>6.2f}{gp_s:>8}{share_s:>10}{c['indirect_share']:>6.1f}%")

# ========= 保存输出 =========
out = {
    'camp_type': {t: dict(camp_type[t]) for t in camp_type},
    'sku_merge': sku_merge[:100],  # 前100
    'sku_categories': {cat: [r['sku'] for r in cats[cat]] for cat in cats},
    'sku_category_stats': {cat: {
        'count': len(cats[cat]),
        'spend': sum(r['spend'] for r in cats[cat]),
        'ad_sales': sum(r['ad_sales'] for r in cats[cat]),
    } for cat in cats},
    'campaigns': camp_list[:100],  # 前100活动
    'campaign_category_stats': {cat: dict(camp_cats[cat]) for cat in camp_cats},
    'top_efficient_campaigns': top_eff[:20],
    'top_inefficient_campaigns': top_low[:20],
    'top_keywords': st_sorted[:50],
    'total_spends': total_sp,
    'total_sales': total_sa,
}
json.dump(out, open('attribution.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'\n已保存 attribution.json')