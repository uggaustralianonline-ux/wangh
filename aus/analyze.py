"""A-US 近30天广告效果归因 + 三档分类 + 预算重分配测算。
输出 result.json 供 HTML 报告消费。
"""
import json, csv, glob, math
from collections import defaultdict

# ============ 0. 期间与利润基线 ============
PERIOD = ("2026-07-09", "2026-08-07")
PREV = ("2026-06-09", "2026-07-08")

pf = json.load(open('raw/profit_aus.json', encoding='utf-8'))
pp = json.load(open('raw/profit_aus_prev.json', encoding='utf-8'))
F = lambda d, k: float(d.get(k) or 0)

cur = dict(
    sales=F(pf, 'amount'), volume=F(pf, 'volume'), gp=F(pf, 'gross_profit'),
    spend=abs(F(pf, 'spend')), ad_sales=F(pf, 'ad_sales_amount'),
    purchase=abs(F(pf, 'purchase_costs')), logistics=abs(F(pf, 'logistics_costs')),
    fba=abs(F(pf, 'fulfillment_fee')), commission=abs(F(pf, 'selling_fee')),
    storage=abs(F(pf, 'total_stock_fee')), refund=abs(F(pf, 'refund_amount')),
    promo=abs(F(pf, 'promotion_discount')) + abs(F(pf, 'promotion_fee')),
)
prev = dict(
    sales=F(pp, 'amount'), volume=F(pp, 'volume'), gp=F(pp, 'gross_profit'),
    spend=abs(F(pp, 'spend')), ad_sales=F(pp, 'ad_sales_amount'),
)

# 广告前贡献毛利 = 毛利 + 广告花费  ->  保本 ACOS
pre_ad_gp = cur['gp'] + cur['spend']
BREAKEVEN = pre_ad_gp / cur['sales']
prev_breakeven = (prev['gp'] + prev['spend']) / prev['sales']

# 自然盘（回收率实测）
cur_nat_sales = cur['sales'] - cur['ad_sales']
prev_nat_sales = prev['sales'] - prev['ad_sales']
d_ad_sales = cur['ad_sales'] - prev['ad_sales']
d_nat_sales = cur_nat_sales - prev_nat_sales
RECAPTURE = d_nat_sales / abs(d_ad_sales)   # 削广告后自然单回补比例（实测）

# ============ 1. 活动明细 ============
camps = []
with open('campaigns.csv', encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        g = lambda k: float(r.get(k) or 0)
        c = dict(
            id=r['campaign_id'], name=r['name'],
            type=(r['ads_type'] or r['sponsored_type'] or '').lower(),
            targeting=r['targeting_type'] or '-', state=r['state'] or '-',
            serving=r['serving_status'] or '-', portfolio=r['portfolio_name'] or '(未分组)',
            budget=g('daily_budget'), spend=g('spends'), sales=g('sales'),
            orders=int(g('orders')), units=int(g('ad_units')),
            impr=int(g('impressions')), clicks=int(g('clicks')),
            cpc=g('cpc'), cvr=g('cvr'), ctr=g('ctr'),
            d_orders=int(g('direct_orders')), d_sales=g('direct_sales'),
            i_orders=int(g('indirect_orders')), i_sales=g('indirect_sales'),
        )
        c['acos'] = (c['spend'] / c['sales'] * 100) if c['sales'] > 0 else None
        c['roas'] = (c['sales'] / c['spend']) if c['spend'] > 0 else 0
        # 净贡献毛利：广告销售额按广告前贡献毛利率折算，再减广告花费
        c['net'] = c['sales'] * BREAKEVEN - c['spend']
        camps.append(c)

camps = [c for c in camps if c['spend'] > 0 or c['sales'] > 0]
TOT_SPEND = sum(c['spend'] for c in camps)
TOT_SALES = sum(c['sales'] for c in camps)
TOT_ORDERS = sum(c['orders'] for c in camps)

# ============ 2. 三档分类 ============
A_CUT = BREAKEVEN * 0.8 * 100      # 高效上限
B_CUT = BREAKEVEN * 1.2 * 100      # 保本上限


def tier(c):
    if c['sales'] <= 0:
        return 'C', 'C4 零单空烧'
    a = c['acos']
    if a <= A_CUT:
        return 'A', 'A 高效盈利'
    if a <= B_CUT:
        return 'B', 'B 保本引流'
    if a <= 45:
        return 'C', 'C1 轻度超支'
    if a <= 80:
        return 'C', 'C2 重度超支'
    return 'C', 'C3 严重失控'


for c in camps:
    c['tier'], c['sub'] = tier(c)


def agg(rows):
    sp = sum(r['spend'] for r in rows); sa = sum(r['sales'] for r in rows)
    return dict(n=len(rows), spend=sp, sales=sa,
                orders=sum(r['orders'] for r in rows),
                clicks=sum(r['clicks'] for r in rows),
                impr=sum(r['impr'] for r in rows),
                acos=(sp / sa * 100) if sa > 0 else None,
                roas=(sa / sp) if sp > 0 else 0,
                net=sum(r['net'] for r in rows),
                spend_pct=sp / TOT_SPEND * 100, sales_pct=sa / TOT_SALES * 100)


tiers = {k: agg([c for c in camps if c['tier'] == k]) for k in 'ABC'}
subs = {}
for s in ['A 高效盈利', 'B 保本引流', 'C1 轻度超支', 'C2 重度超支', 'C3 严重失控', 'C4 零单空烧']:
    subs[s] = agg([c for c in camps if c['sub'] == s])

# 广告类型 / 投放方式 / 广告组合
by_type = {t: agg([c for c in camps if c['type'] == t])
           for t in sorted({c['type'] for c in camps})}
by_targeting = {t: agg([c for c in camps if c['targeting'] == t])
                for t in sorted({c['targeting'] for c in camps})}
pf_rows = defaultdict(list)
for c in camps:
    pf_rows[c['portfolio']].append(c)
by_portfolio = {k: agg(v) for k, v in pf_rows.items()}
for k, v in by_portfolio.items():
    v['tierA'] = sum(c['spend'] for c in pf_rows[k] if c['tier'] == 'A')
    v['tierB'] = sum(c['spend'] for c in pf_rows[k] if c['tier'] == 'B')
    v['tierC'] = sum(c['spend'] for c in pf_rows[k] if c['tier'] == 'C')

# ============ 3. 关键词层 ============
kw, seen = {}, set()
for p in sorted(glob.glob('raw/kw_p*.json')):
    for r in json.load(open(p, encoding='utf-8'))['data']['data']:
        if not r.get('keyword_id'):
            continue
        k = (r.get('keyword_id'), r.get('campaign_id'), r.get('ad_group_id'))
        if k in seen:
            continue
        seen.add(k)
        g = lambda x: float(r.get(x) or 0)
        sp, sa = g('spends'), g('sales')
        kw[k] = dict(text=r.get('keyword_text'), match=r.get('match_type'),
                     campaign=r.get('campaign_name'), adgroup=r.get('ad_group_name'),
                     type=(r.get('sponsored_type') or '').lower(), state=r.get('state'),
                     bid=g('bid'), cpc=g('cpc'), spend=sp, sales=sa,
                     orders=int(g('orders')), clicks=int(g('clicks')),
                     impr=int(g('impressions')), cvr=g('cvr'),
                     acos=(sp / sa * 100) if sa > 0 else None,
                     net=sa * BREAKEVEN - sp)
kws = list(kw.values())
KW_SPEND = sum(k['spend'] for k in kws)
for k in kws:
    k['tier'], k['sub'] = tier(k)
kw_tiers = {t: dict(n=len([k for k in kws if k['tier'] == t]),
                    spend=sum(k['spend'] for k in kws if k['tier'] == t),
                    sales=sum(k['sales'] for k in kws if k['tier'] == t),
                    net=sum(k['net'] for k in kws if k['tier'] == t)) for t in 'ABC'}
for t in kw_tiers:
    v = kw_tiers[t]
    v['spend_pct'] = v['spend'] / KW_SPEND * 100
    v['acos'] = v['spend'] / v['sales'] * 100 if v['sales'] > 0 else None
by_match = {}
for m in sorted({k['match'] for k in kws if k['match']}):
    rows = [k for k in kws if k['match'] == m]
    sp = sum(r['spend'] for r in rows); sa = sum(r['sales'] for r in rows)
    by_match[m] = dict(n=len(rows), spend=sp, sales=sa,
                       orders=sum(r['orders'] for r in rows),
                       acos=sp / sa * 100 if sa > 0 else None,
                       net=sum(r['net'] for r in rows), spend_pct=sp / KW_SPEND * 100)

# ============ 4. 投放定向层（自动/商品） ============
tg, seen = {}, set()
for p in sorted(glob.glob('raw/tg_p*.json')):
    for r in json.load(open(p, encoding='utf-8'))['data']['data']:
        if not r.get('target_id'):
            continue
        k = (r.get('target_id'), r.get('campaign_id'), r.get('ad_group_id'))
        if k in seen:
            continue
        seen.add(k)
        g = lambda x: float(r.get(x) or 0)
        sp, sa = g('spends'), g('sales')
        tg[k] = dict(expr=r.get('targeting_expression') or r.get('expression_type') or '-',
                     etype=r.get('expression_type') or '-',
                     campaign=r.get('campaign_name'), adgroup=r.get('ad_group_name'),
                     type=(r.get('sponsored_type') or '').lower(),
                     spend=sp, sales=sa, orders=int(g('orders')),
                     clicks=int(g('clicks')), cpc=g('cpc'),
                     acos=(sp / sa * 100) if sa > 0 else None,
                     net=sa * BREAKEVEN - sp)
tgs = list(tg.values())
for t in tgs:
    t['tier'], t['sub'] = tier(t)
TG_SPEND = sum(t['spend'] for t in tgs)

# ============ 5. 预算重分配 ============
# 处置系数（运营启发式，标注为假设）
CUT = {'C4 零单空烧': 1.00, 'C3 严重失控': 1.00, 'C2 重度超支': 0.60, 'C1 轻度超支': 0.30}
ADD_RATE = 0.35            # A 档加投幅度
DECAY = 0.65               # 加投部分边际 ROAS 衰减系数（递减效应）

released, lost_ad_sales = 0.0, 0.0
plan_rows = []
for s, rate in CUT.items():
    v = subs[s]
    cut_spend = v['spend'] * rate
    # 该档 ROAS 下损失的广告销售额，扣除实测自然回补
    lost = cut_spend * (v['roas'] if v['spend'] > 0 else 0) * (1 - RECAPTURE)
    released += cut_spend
    lost_ad_sales += lost
    plan_rows.append(dict(seg=s, action=f'削减 {rate*100:.0f}%', spend=v['spend'],
                          delta_spend=-cut_spend, roas=v['roas'],
                          delta_sales=-lost, n=v['n']))

addA = subs['A 高效盈利']['spend'] * ADD_RATE
gain_ad_sales = addA * subs['A 高效盈利']['roas'] * DECAY
plan_rows.insert(0, dict(seg='A 高效盈利', action=f'加投 {ADD_RATE*100:.0f}%',
                         spend=subs['A 高效盈利']['spend'], delta_spend=addA,
                         roas=subs['A 高效盈利']['roas'] * DECAY,
                         delta_sales=gain_ad_sales, n=subs['A 高效盈利']['n']))
plan_rows.insert(1, dict(seg='B 保本引流', action='维持', spend=subs['B 保本引流']['spend'],
                         delta_spend=0.0, roas=subs['B 保本引流']['roas'],
                         delta_sales=0.0, n=subs['B 保本引流']['n']))

new_spend = TOT_SPEND - released + addA
new_ad_sales = TOT_SALES - lost_ad_sales + gain_ad_sales
new_acos = new_spend / new_ad_sales * 100
# 总销售额：广告销售额变化 + 自然回补
recovered_nat = (lost_ad_sales / (1 - RECAPTURE)) * RECAPTURE if RECAPTURE else 0
new_total_sales = cur['sales'] - lost_ad_sales + gain_ad_sales + recovered_nat
new_gp = new_total_sales * BREAKEVEN - new_spend
new_gm = new_gp / new_total_sales * 100
new_tacos = new_spend / new_total_sales * 100

result = dict(
    period=PERIOD, prev=PREV,
    profit=dict(cur=cur, prev=prev, pre_ad_gp=pre_ad_gp,
                breakeven=BREAKEVEN * 100, prev_breakeven=prev_breakeven * 100,
                gm=cur['gp'] / cur['sales'] * 100, prev_gm=prev['gp'] / prev['sales'] * 100,
                tacos=cur['spend'] / cur['sales'] * 100,
                prev_tacos=prev['spend'] / prev['sales'] * 100,
                nat_sales=cur_nat_sales, prev_nat_sales=prev_nat_sales,
                recapture=RECAPTURE * 100, aov=cur['sales'] / cur['volume']),
    ads=dict(spend=TOT_SPEND, sales=TOT_SALES, orders=TOT_ORDERS,
             units=sum(c['units'] for c in camps),
             impr=sum(c['impr'] for c in camps), clicks=sum(c['clicks'] for c in camps),
             acos=TOT_SPEND / TOT_SALES * 100, roas=TOT_SALES / TOT_SPEND,
             n=len(camps), net=sum(c['net'] for c in camps),
             direct_orders=sum(c['d_orders'] for c in camps),
             indirect_orders=sum(c['i_orders'] for c in camps),
             direct_sales=sum(c['d_sales'] for c in camps),
             indirect_sales=sum(c['i_sales'] for c in camps)),
    cuts=dict(A=A_CUT, B=B_CUT),
    tiers=tiers, subs=subs, by_type=by_type, by_targeting=by_targeting,
    by_portfolio=dict(sorted(by_portfolio.items(), key=lambda x: -x[1]['spend'])),
    kw=dict(total_spend=KW_SPEND, n=len(kws), tiers=kw_tiers, by_match=by_match,
            cover=KW_SPEND / 34179.43 * 100),
    tg=dict(total_spend=TG_SPEND, n=len(tgs), cover=TG_SPEND / 8539.34 * 100),
    plan=dict(rows=plan_rows, released=released, addA=addA,
              net_cut=released - addA, new_spend=new_spend,
              new_ad_sales=new_ad_sales, new_acos=new_acos,
              new_total_sales=new_total_sales, new_gp=new_gp, new_gm=new_gm,
              new_tacos=new_tacos, recovered_nat=recovered_nat,
              gp_delta=new_gp - cur['gp'], assum=dict(
                  cut=CUT, add_rate=ADD_RATE, decay=DECAY, recapture=RECAPTURE)),
    top_add=sorted([c for c in camps if c['tier'] == 'A' and c['spend'] >= 60],
                   key=lambda c: -c['net'])[:20],
    top_cut=sorted([c for c in camps if c['tier'] == 'C'],
                   key=lambda c: c['net'])[:25],
    zero=sorted([c for c in camps if c['sales'] <= 0 and c['spend'] > 0],
                key=lambda c: -c['spend'])[:20],
    kw_add=sorted([k for k in kws if k['tier'] == 'A' and k['spend'] >= 40],
                  key=lambda k: -k['net'])[:20],
    kw_cut=sorted([k for k in kws if k['tier'] == 'C'], key=lambda k: k['net'])[:25],
    tg_cut=sorted([t for t in tgs if t['tier'] == 'C'], key=lambda t: t['net'])[:15],
)
json.dump(result, open('result.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ============ 控制台校验 ============
P = print
P(f"期间 {PERIOD[0]} ~ {PERIOD[1]}")
P(f"总销售额 ${cur['sales']:,.0f} | 毛利 ${cur['gp']:,.0f} ({cur['gp']/cur['sales']*100:.2f}%)")
P(f"广告前贡献毛利 ${pre_ad_gp:,.0f} -> 保本ACOS {BREAKEVEN*100:.2f}%（上期 {prev_breakeven*100:.2f}%）")
P(f"广告 花费${TOT_SPEND:,.0f} 销售${TOT_SALES:,.0f} ACOS {TOT_SPEND/TOT_SALES*100:.2f}% ROAS {TOT_SALES/TOT_SPEND:.2f} TACOS {cur['spend']/cur['sales']*100:.2f}%")
P(f"广告板块净贡献 ${sum(c['net'] for c in camps):,.0f}")
P(f"实测自然回补率 {RECAPTURE*100:.2f}%  (Δ自然${d_nat_sales:,.0f} / Δ广告${abs(d_ad_sales):,.0f})")
P(f"档位阈值: A<= {A_CUT:.2f}%  B<= {B_CUT:.2f}%")
P('-' * 96)
P(f"{'档':22s}{'活动数':>7s}{'花费':>12s}{'预算占比':>10s}{'销售额':>13s}{'ACOS':>9s}{'净贡献':>12s}")
for s, v in subs.items():
    P(f"{s:22s}{v['n']:>7d}{v['spend']:>12,.0f}{v['spend_pct']:>9.2f}%{v['sales']:>13,.0f}"
      f"{(f'{v[chr(97)+chr(99)+chr(111)+chr(115)]:.2f}%' if v['acos'] else '  —'):>9s}{v['net']:>12,.0f}")
P('-' * 96)
for t in 'ABC':
    v = tiers[t]
    P(f"{t}档 活动{v['n']:>5d} 花费${v['spend']:>10,.0f} 占比{v['spend_pct']:>6.2f}% "
      f"ACOS {(f'{v[chr(97)+chr(99)+chr(111)+chr(115)]:.2f}%' if v['acos'] else '—'):>8s} 净贡献${v['net']:>10,.0f}")
P('-' * 96)
P('广告类型:', {k: f"${v['spend']:,.0f}/{v['spend_pct']:.1f}%/ACOS {v['acos']:.1f}%" for k, v in by_type.items()})
P('投放方式:', {k: f"${v['spend']:,.0f}/{v['spend_pct']:.1f}%/ACOS {v['acos']:.1f}%" for k, v in by_targeting.items()})
P('-' * 96)
pl = result['plan']
P(f"释放预算 ${pl['released']:,.0f} | 加投A ${pl['addA']:,.0f} | 净削减 ${pl['net_cut']:,.0f}")
P(f"新广告花费 ${pl['new_spend']:,.0f} | 新广告销售额 ${pl['new_ad_sales']:,.0f} | 新ACOS {pl['new_acos']:.2f}%")
P(f"新总销售额 ${pl['new_total_sales']:,.0f} | 新毛利 ${pl['new_gp']:,.0f} ({pl['new_gm']:.2f}%) | 新TACOS {pl['new_tacos']:.2f}%")
P(f"毛利变化 ${pl['gp_delta']:+,.0f} ({pl['gp_delta']/cur['gp']*100:+.1f}%) | 年化 ${pl['gp_delta']*365/30:+,.0f}")
P('-' * 96)
P(f"关键词覆盖 {result['kw']['cover']:.2f}% ({len(kws)}行)  投放定向覆盖 {result['tg']['cover']:.2f}% ({len(tgs)}行)")
P('关键词三档:', {t: f"${v['spend']:,.0f}/{v['spend_pct']:.1f}%/净${v['net']:,.0f}" for t, v in kw_tiers.items()})
P('匹配方式:', {k: f"${v['spend']:,.0f}/ACOS {v['acos']:.1f}%" for k, v in by_match.items()})
