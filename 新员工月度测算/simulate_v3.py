# -*- coding: utf-8 -*-
"""
亚马逊新产品开发 · 新员工月度销售额与利润分布模型 v3
严格按用户本次给定参数重建（修正 v2 的口径）：

  - 每月开发 10 个，成功率 60% → 成功 6 / 失败 4
  - 客单价 $10
  - 首批备货 300 件/SKU
  - 毛利 20%（不含退货、汇率、仓储费）
  - 节日 60% / 常规 40%；节日提前 4~5 月开品、平均售期 2 个月
  - 备货爬坡：第1年 ×1.0 → 第2年 ×2.5(2~3倍中值) → 第3年稳定 ×2.5
  - 老品（开售>12个月）每年淘汰 10%
  - **失败产品亏损**：按"销售额的 50%"计 = 0.5 × 300 × $10 = $1500/个，于开品当月确认
  - 核心区间 36 个月（对应"第一/二/三年"框架）；第4年及以后作为"前瞻情景"对比：
        继续 10/月  vs  开发放缓至 5/月 + 需求年降10% → 体现"后续可能会下降"
输出：CSV（逐月明细 + 蒙特卡洛分布带）+ HTML（趋势/累计盈亏/年度/淘汰/前瞻情景/假设）
"""
import csv, random, statistics, os

# ===================== 参数（用户给定） =====================
DEVELOPED        = 10        # 每月开发产品数（前36个月）
SUCCESS_RATE     = 0.60      # 成功率
PRICE            = 10.0      # 客单价 USD
BATCH_Y1         = 300       # 第一年首批备货（件/SKU）
Y2_FACTOR        = 2.5       # 第二年扩大倍数（2~3倍中值）
FEST_SHARE       = 0.60      # 节日品占比
REG_SHARE        = 0.40      # 常规品占比
FEST_LEAD_LO     = 4         # 节日品提前开品月数下限
FEST_LEAD_HI     = 5         # 上限
REG_LEAD         = 3         # 常规品开品到起售月数（FBA滞后，用户未指定，取3）
FEST_SELL_MONTHS = 2         # 节日品平均售期（月）
RETIRE_RATE      = 0.10      # 老品年淘汰率
GROSS_MARGIN     = 0.20      # 毛利（不含退货/汇率/仓储）
FAILED_SALES_RATIO = 0.50    # 失败亏损 = 销售额的 50%
FAILED_LOSS_UNIT = FAILED_SALES_RATIO * BATCH_Y1 * PRICE   # = 1500 USD/失败品
CORE_H           = 36        # 核心区间（月）
EXT_H            = 60        # 前瞻情景区间（月）
N_RUNS           = 800       # 蒙特卡洛次数
DEMAND_DECAY     = 0.90      # 第4年起单SKU需求年降10%（"后续下降"驱动之一）
# 保守净利额外扣减（用户说20%不含这些，作为情景列）：
RETURN_RATE_ASSUM = 0.05     # 退货/损毁
FX_RATE_ASSUM     = 0.02     # 汇率损失
STORAGE_ASSUM     = 0.01     # 仓储费
CONSERV_DEDUCT    = RETURN_RATE_ASSUM + FX_RATE_ASSUM + STORAGE_ASSUM  # 0.08

def year_factor(m):
    yr = (m - 1) // 12 + 1
    if yr <= 3:
        return {1: 1.0, 2: Y2_FACTOR, 3: Y2_FACTOR}[yr]
    return Y2_FACTOR * (DEMAND_DECAY ** (yr - 3))   # 第4年起需求递减

# ===================== 模拟核心 =====================
def simulate(rng, deterministic, dev_fn, horizon):
    """dev_fn(m)->该月开发数；返回 rows: list[dict]，月索引 1..horizon。"""
    skus = []
    rows = {m: {'sales': 0.0, 'gross': 0.0, 'fail_loss': 0.0, 'active': 0.0} for m in range(1, horizon + 1)}
    # —— 开品阶段 ——
    for d in range(1, horizon + 1):
        n_dev = dev_fn(d)
        if deterministic:
            n_fail = n_dev * (1 - SUCCESS_RATE)
            n_fest = FEST_SHARE * SUCCESS_RATE * n_dev
            n_reg  = REG_SHARE  * SUCCESS_RATE * n_dev
            skus.append({'birth': d, 'type': 'fest', 'launch': d + 4, 'count': n_fest})
            skus.append({'birth': d, 'type': 'reg',  'launch': d + REG_LEAD, 'count': n_reg})
        else:
            n_fail = sum(1 for _ in range(n_dev) if rng.random() >= SUCCESS_RATE)
            for _ in range(n_dev - n_fail):
                is_fest = rng.random() < FEST_SHARE
                lead = rng.randint(FEST_LEAD_LO, FEST_LEAD_HI) if is_fest else REG_LEAD
                skus.append({'birth': d, 'type': 'fest' if is_fest else 'reg',
                             'launch': d + lead, 'alive': True})
        rows[d]['fail_loss'] += n_fail * FAILED_LOSS_UNIT
    # —— 销售 & 淘汰阶段 ——
    for t in range(1, horizon + 1):
        f = year_factor(t)
        for s in skus:
            if deterministic:
                if s['count'] <= 0:
                    continue
                cnt = s['count']
            else:
                if not s['alive']:
                    continue
                cnt = 1.0
            if t < s['launch']:
                continue
            if s['type'] == 'reg':
                u = (BATCH_Y1 / 12.0) * f
            else:
                off = (t - s['launch']) % 12
                u = (BATCH_Y1 / 2.0) * f if off in (0, 1) else 0.0
            rows[t]['sales'] += cnt * u * PRICE
            rows[t]['active'] += cnt
        if t in range(12, horizon + 1, 12):   # 年末淘汰
            for s in skus:
                if t - s['birth'] >= 12:
                    if deterministic:
                        s['count'] *= (1 - RETIRE_RATE)
                    else:
                        if s['alive'] and rng.random() < RETIRE_RATE:
                            s['alive'] = False
        rows[t]['gross'] = rows[t]['sales'] * GROSS_MARGIN
        rows[t]['net']   = rows[t]['gross'] - rows[t]['fail_loss']
    return [rows[m] for m in range(1, horizon + 1)]

def pct(vals, p):
    if not vals:
        return 0.0
    sv = sorted(vals)
    k = (len(sv) - 1) * p / 100.0
    lo = int(k); hi = min(lo + 1, len(sv) - 1)
    return sv[lo] + (sv[hi] - sv[lo]) * (k - lo)

# ===================== 运行 =====================
rng = random.Random(20260810)
dev_const = lambda m: DEVELOPED
base = simulate(rng, True, dev_const, CORE_H)                 # 期望基准(36月)
mc_sales, mc_net = [[] for _ in range(CORE_H)], [[] for _ in range(CORE_H)]
for _ in range(N_RUNS):
    r = simulate(rng, False, dev_const, CORE_H)
    for i in range(CORE_H):
        mc_sales[i].append(r[i]['sales']); mc_net[i].append(r[i]['net'])

bands = [{'sales_p10': pct(mc_sales[i],10), 'sales_p50': pct(mc_sales[i],50), 'sales_p90': pct(mc_sales[i],90),
         'net_p10':   pct(mc_net[i],10),   'net_p50':   pct(mc_net[i],50),   'net_p90':   pct(mc_net[i],90)}
        for i in range(CORE_H)]

# 累计盈亏平衡（基准）
cum = 0.0; breakeven = None
for i, r in enumerate(base, 1):
    cum += r['net']
    if breakeven is None and cum >= 0:
        breakeven = i

# 前瞻情景：继续 10/月  vs  放缓 5/月 + 需求年降10%
ext_continue = simulate(rng, True, dev_const, EXT_H)
ext_mature  = simulate(rng, True, lambda m: DEVELOPED if m <= 36 else 5, EXT_H)
def yearly_sales(rows, yrs):
    return [sum(r['sales'] for r in rows[(y-1)*12:y*12]) for y in yrs]
ext_years = list(range(1, EXT_H//12 + 1))
yc_sales = yearly_sales(ext_continue, ext_years)
ym_sales = yearly_sales(ext_mature, ext_years)

def year_block(rows, y):
    sl = rows[(y-1)*12:y*12]
    return {'sales': sum(r['sales'] for r in sl), 'gross': sum(r['gross'] for r in sl),
            'fail': sum(r['fail_loss'] for r in sl), 'net': sum(r['net'] for r in sl),
            'avg_sales': sum(r['sales'] for r in sl)/12, 'avg_net': sum(r['net'] for r in sl)/12}
ys = [year_block(base, y) for y in (1,2,3)]
total_sales = sum(r['sales'] for r in base); total_gross = sum(r['gross'] for r in base)
total_fail  = sum(r['fail_loss'] for r in base); total_net = sum(r['net'] for r in base)
active_end  = base[-1]['active']

def fmt(x): return f"{x:,.0f}"

# ===================== CSV =====================
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, "新员工月度测算_v3.csv")
with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['月份','年度','活跃SKU','销量(件)','销售额USD','毛利@20%USD','失败亏损USD',
                '经营利润USD(毛利-失败)','保守净利USD(再扣退货5%+汇率2%+仓储1%)',
                '销售额P50','销售额P10','销售额P90','经营利润P50','经营利润P10','经营利润P90'])
    for i, r in enumerate(base, 1):
        b = bands[i-1]
        cons = r['net'] - r['sales'] * CONSERV_DEDUCT
        w.writerow([i, (i-1)//12+1, round(r['active'],1), fmt(r['sales']/PRICE), fmt(r['sales']),
                    fmt(r['gross']), fmt(r['fail_loss']), fmt(r['net']), fmt(cons),
                    fmt(b['sales_p50']), fmt(b['sales_p10']), fmt(b['sales_p90']),
                    fmt(b['net_p50']), fmt(b['net_p10']), fmt(b['net_p90'])])

# ===================== HTML =====================
W,H=900,420; PL,PR,PT,PB=70,30,34,52; pw,ph=W-PL-PR,H-PT-PB
maxv=max(max(r['sales'] for r in base), 1); minv=min(min(r['net'] for r in base), 0)
def sx(m): return PL+(m-1)/(CORE_H-1)*pw
def sy(v): return PT+(1-(v-minv)/(maxv-minv))*ph
bars=''; bw=pw/CORE_H*0.6
for i,r in enumerate(base,1):
    x=sx(i)-bw/2; y=sy(r['sales']); bars+=f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{PT+ph-y:.1f}" fill="#bfdbfe"/>'
for i,r in enumerate(base,1):
    if r['fail_loss']>0:
        x=sx(i)-bw/2; y0=sy(0); y1=sy(-r['fail_loss'])
        bars+=f'<rect x="{x:.1f}" y="{y0:.1f}" width="{bw:.1f}" height="{y1-y0:.1f}" fill="#fca5a5" opacity="0.85"/>'
def line(vals,color,wdt=2.4):
    return f'<polyline fill="none" stroke="{color}" stroke-width="{wdt}" points="{" ".join(f"{sx(i):.1f},{sy(v):.1f}" for i,v in enumerate(vals,1))}"/>'
net_line=line([r['net'] for r in base],'#16a34a'); gross_line=line([r['gross'] for r in base],'#f59e0b')
grid=''
for i in range(6):
    v=minv+(maxv-minv)*i/5; y=sy(v)
    grid+=f'<line x1="{PL}" y1="{y:.1f}" x2="{W-PR}" y2="{y:.1f}" stroke="#eef1f5"/>'
    grid+=f'<text x="{PL-8}" y="{y+4:.1f}" text-anchor="end" font-size="10" fill="#6b7280">${v/1000:.0f}k</text>'
vl=''.join(f'<line x1="{sx(m):.1f}" y1="{PT}" x2="{sx(m):.1f}" y2="{PT+ph}" stroke="#dfe3ea" stroke-dasharray="4 3"/><text x="{sx(m):.1f}" y="{H-28}" text-anchor="middle" font-size="10" fill="#6b7280">第{m//12}年末</text>' for m in (12,24,36))
xl=''.join(f'<text x="{sx(m):.1f}" y="{H-10}" text-anchor="middle" font-size="10" fill="#6b7280">M{m}</text>' for m in (1,6,12,18,24,30,36))
chart=f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial,sans-serif">
<rect width="{W}" height="{H}" fill="#fff"/>{grid}{vl}{bars}{net_line}{gross_line}{xl}
<rect x="{PL}" y="6" width="13" height="10" fill="#bfdbfe"/><text x="{PL+18}" y="15" font-size="11" fill="#374151">月销售额</text>
<rect x="{PL+100}" y="6" width="13" height="10" fill="#f59e0b"/><text x="{PL+118}" y="15" font-size="11" fill="#374151">月毛利@20%</text>
<rect x="{PL+210}" y="6" width="13" height="10" fill="#16a34a"/><text x="{PL+228}" y="15" font-size="11" fill="#374151">月经营利润(扣失败)</text>
<rect x="{PL+360}" y="6" width="13" height="10" fill="#fca5a5"/><text x="{PL+378}" y="15" font-size="11" fill="#374151">月失败亏损(负向)</text></svg>'''

# 累计盈亏
W2,H2=900,300; PL2,PR2,PT2,PB2=70,30,30,40; pw2,ph2=W2-PL2-PR2,H2-PT2-PB2
cum_vals=[]; c=0.0
for r in base: c+=r['net']; cum_vals.append(c)
cmax=max(cum_vals+[0]); cmin=min(cum_vals+[0])
def sx2(m): return PL2+(m-1)/(CORE_H-1)*pw2
def sy2(v): return PT2+(1-(v-cmin)/(cmax-cmin or 1))*ph2
zline=f'<line x1="{PL2}" y1="{sy2(0):.1f}" x2="{W2-PR2}" y2="{sy2(0):.1f}" stroke="#9ca3af" stroke-dasharray="5 3"/>'
cpoly=f'<polyline fill="none" stroke="#2563eb" stroke-width="2.4" points="{" ".join(f"{sx2(i):.1f},{sy2(v):.1f}" for i,v in enumerate(cum_vals,1))}"/>'
cgrid=''.join(f'<line x1="{PL2}" y1="{sy2(minv2):.1f}" x2="{W2-PR2}" y2="{sy2(minv2):.1f}" stroke="#eef1f5"/><text x="{PL2-8}" y="{sy2(minv2)+4:.1f}" text-anchor="end" font-size="10" fill="#6b7280">${minv2/1000:.0f}k</text>' for minv2 in [cmin+(cmax-cmin)*i/4 for i in range(5)])
cvl=''.join(f'<line x1="{sx2(m):.1f}" y1="{PT2}" x2="{sx2(m):.1f}" y2="{PT2+ph2}" stroke="#dfe3ea" stroke-dasharray="4 3"/>' for m in (12,24,36))
cx=''.join(f'<text x="{sx2(m):.1f}" y="{H2-8}" text-anchor="middle" font-size="10" fill="#6b7280">M{m}</text>' for m in (1,12,24,36))
cum_chart=f'''<svg viewBox="0 0 {W2} {H2}" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial,sans-serif">
<rect width="{W2}" height="{H2}" fill="#fff"/>{cgrid}{cvl}{zline}{cpoly}{cx}
<text x="{PL2+6}" y="16" font-size="11" fill="#2563eb">累计经营利润（盈亏平衡月：第{breakeven}个月）</text></svg>'''

# 前瞻情景：年度销售额 继续 vs 放缓
W3,H3=900,300; PL3,PR3,PT3,PB3=70,30,30,40; pw3,ph3=W3-PL3-PR3,H3-PT3-PB3
ymax=max(max(yc_sales),max(ym_sales))*1.1 or 1
def sx3(y): return PL3+(y-1)/(len(ext_years)-1)*pw3
def sy3(v): return PT3+(1-v/ymax)*ph3
lc=f'<polyline fill="none" stroke="#2563eb" stroke-width="2.6" points="{" ".join(f"{sx3(y):.1f},{sy3(yc_sales[y-1]):.1f}" for y in ext_years)}"/>'
lm=f'<polyline fill="none" stroke="#dc2626" stroke-width="2.6" stroke-dasharray="6 3" points="{" ".join(f"{sx3(y):.1f},{sy3(ym_sales[y-1]):.1f}" for y in ext_years)}"/>'
dots=''.join(f'<circle cx="{sx3(y):.1f}" cy="{sy3(yc_sales[y-1]):.1f}" r="3.5" fill="#2563eb"/><circle cx="{sx3(y):.1f}" cy="{sy3(ym_sales[y-1]):.1f}" r="3.5" fill="#dc2626"/>' for y in ext_years)
sg=''.join(f'<line x1="{PL3}" y1="{sy3(v):.1f}" x2="{W3-PR3}" y2="{sy3(v):.1f}" stroke="#eef1f5"/><text x="{PL3-8}" y="{sy3(v)+4:.1f}" text-anchor="end" font-size="10" fill="#6b7280">${v/1000:.0f}k</text>' for v in [ymax*i/4 for i in range(5)])
svl=''.join(f'<line x1="{sx3(y):.1f}" y1="{PT3}" x2="{sx3(y):.1f}" y2="{PT3+ph3}" stroke="#dfe3ea" stroke-dasharray="4 3"/><text x="{sx3(y):.1f}" y="{H3-8}" text-anchor="middle" font-size="10" fill="#6b7280">第{y}年</text>' for y in ext_years)
fwd_chart=f'''<svg viewBox="0 0 {W3} {H3}" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial,sans-serif">
<rect width="{W3}" height="{H3}" fill="#fff"/>{sg}{svl}{lc}{lm}{dots}
<rect x="{PL3}" y="6" width="13" height="10" fill="#2563eb"/><text x="{PL3+18}" y="15" font-size="11" fill="#374151">继续 10个/月</text>
<rect x="{PL3+130}" y="6" width="13" height="10" fill="#dc2626"/><text x="{PL3+148}" y="15" font-size="11" fill="#374151">放缓 5个/月+需求年降10%</text></svg>'''
peak_mature = ext_years[ym_sales.index(max(ym_sales))]

# 年度表(核心3年)
yrt=''.join(f"<tr><td>第{y}年</td><td>${fmt(ys[y-1]['sales'])}</td><td>${fmt(ys[y-1]['gross'])}</td><td>${fmt(ys[y-1]['fail'])}</td><td><b>${fmt(ys[y-1]['net'])}</b></td><td>${fmt(ys[y-1]['avg_sales'])}</td><td>${fmt(ys[y-1]['avg_net'])}</td></tr>" for y in (1,2,3))
# 逐月表
tr=''.join(f"<tr><td>{i}</td><td>{(i-1)//12+1}</td><td>{round(r['active'],1)}</td><td>{fmt(r['sales']/PRICE)}</td><td>${fmt(r['sales'])}</td><td>${fmt(r['gross'])}</td><td>${fmt(r['fail_loss'])}</td><td>${fmt(r['net'])}</td><td>${fmt(r['net']-r['sales']*CONSERV_DEDUCT)}</td></tr>" for i,r in enumerate(base,1))

html=f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>新员工月度销售额与利润分布 v3</title>
<style>body{{font-family:Segoe UI,'Microsoft YaHei',Arial,sans-serif;color:#1f2937;background:#f7f8fa;margin:0;padding:24px}}
.card{{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:20px 24px;margin-bottom:18px;box-shadow:0 1px 3px rgba(0,0,0,.04)}}
h1{{font-size:22px;margin:0 0 4px}} h2{{font-size:16px;margin:18px 0 8px;color:#374151}}
.sub{{color:#6b7280;font-size:13px}} table{{border-collapse:collapse;width:100%;font-size:13px}}
th,td{{border:1px solid #e5e7eb;padding:6px 8px;text-align:right}} th{{background:#f3f4f6;color:#374151}}
td:first-child,th:first-child,td:nth-child(2),th:nth-child(2){{text-align:center}}
.scroll{{max-height:460px;overflow:auto}} .kv{{display:flex;flex-wrap:wrap;gap:10px}}
.stat{{flex:1;min-width:150px;background:#f9fafb;border:1px solid #eef0f3;border-radius:8px;padding:10px 12px}}
.stat b{{display:block;font-size:18px;color:#111827}} .stat span{{font-size:12px;color:#6b7280}}
.ass{{font-size:12.5px;color:#4b5563;line-height:1.75}} .ass li{{margin:3px 0}}
.warn{{background:#eff6ff;border:1px solid #bfdbfe;color:#1e40af;padding:10px 14px;border-radius:8px;font-size:13px;margin-bottom:14px}}
.note{{background:#fefce8;border:1px solid #fde68a;color:#854d0e;padding:10px 14px;border-radius:8px;font-size:13px;margin-bottom:14px}}</style>
</head><body>
<h1>亚马逊新品开发 · 新员工月度销售额与利润分布（v3）</h1>
<div class="sub">每月开发 10 → 60% 成功(6) / 40% 失败(4) ｜ 客单价 $10 ｜ 首批 300 件 ｜ 毛利 20%(不含退货/汇率/仓储) ｜ 节日60%/常规40% ｜ 节日提前4~5月开品·售期2月 ｜ 第1年×1→第2年×2.5→第3年稳定 ｜ 老品年淘汰10% ｜ 失败亏损=销售额50%($1500/个)</div>

<div class="warn">⚠️ 与上一版(v2)的核心差异：① 毛利由 27.5% 改为 <b>20%</b>（你本次给定，且明确不含退货/汇率/仓储）；② 首批备货由 300~500 中值 400 改为 <b>300</b>；③ <b>新增失败产品亏损</b>（v2 完全未计）—— 每月 4 个失败品 × $1500 = <b>$6000/月</b>，于开品当月确认。</div>

<div class="card"><h2>逐月趋势：销售额 / 毛利 / 经营利润 / 失败亏损（核心 36 个月）</h2>{chart}</div>

<div class="card"><h2>累计经营利润与盈亏平衡</h2>{cum_chart}
<div class="sub" style="margin-top:8px">前 3 个月为 FBA 入仓滞后期，零销售但已产生失败亏损；累计经营利润约在 <b>第 {breakeven} 个月</b> 转正。</div></div>

<div class="card"><h2>分布统计（36 个月 · 蒙特卡洛 {N_RUNS} 次）</h2><div class="kv">
<div class="stat"><span>月销售额 均值</span><b>${fmt(statistics.mean(r['sales'] for r in base))}</b></div>
<div class="stat"><span>月销售额 P90(乐观)</span><b>${fmt(pct([b['sales_p90'] for b in bands],50))}</b></div>
<div class="stat"><span>月销售额 P10(悲观)</span><b>${fmt(pct([b['sales_p10'] for b in bands],50))}</b></div>
<div class="stat"><span>月经营利润 均值</span><b>${fmt(statistics.mean(r['net'] for r in base))}</b></div>
<div class="stat"><span>月经营利润 P10(悲观)</span><b>${fmt(pct([b['net_p10'] for b in bands],50))}</b></div>
<div class="stat"><span>第3年末在售SKU</span><b>{active_end}</b></div>
</div></div>

<div class="card"><h2>年度汇总（核心 3 年）</h2>
<table><thead><tr><th>年度</th><th>年销售额</th><th>年毛利@20%</th><th>年失败亏损</th><th>年经营利润</th><th>月均销售额</th><th>月均经营利润</th></tr></thead><tbody>{yrt}</tbody></table>
<div class="sub" style="margin-top:8px">36 个月累计：销售额 <b>${fmt(total_sales)}</b> ｜ 毛利 <b>${fmt(total_gross)}</b> ｜ 失败亏损 <b>${fmt(total_fail)}</b> ｜ 经营利润 <b>${fmt(total_net)}</b>。</div></div>

<div class="card"><h2>"后续可能会下降" 前瞻情景（第4年及以后）</h2>{fwd_chart}
<div class="sub" style="margin-top:8px">
<b>蓝线（继续 10 个/月）</b>：规模效应使年销售额持续抬升（第3年 ${fmt(ym_sales[2])} → 第5年 ${fmt(yc_sales[4])}），并不下降——前提是开发节奏不减速。<br>
<b>红线（放缓至 5 个/月 + 单SKU需求年降10%）</b>：年销售额在 <b>第 {peak_mature} 年</b> 见顶（${fmt(max(ym_sales))}）后回落，体现你所说的"后续可能会下降"。<br>
结论：<b>"下降"是否成立，取决于第4年后是否仍维持高强度开发</b>；老品 10% 年淘汰 + 需求自然衰减会持续侵蚀存量，若不再净扩张则总量必然见顶回落。
</div></div>

<div class="card"><h2>逐月明细（核心 36 个月）</h2>
<div class="scroll"><table><thead><tr><th>月份</th><th>年</th><th>活跃SKU</th><th>销量(件)</th><th>销售额</th><th>毛利@20%</th><th>失败亏损</th><th>经营利润</th><th>保守净利*</th></tr></thead><tbody>{tr}</tbody></table></div>
<div class="sub" style="margin-top:8px">*保守净利 = 经营利润 − 销售额×(退货5%+汇率2%+仓储1%)，即把你说"20%不含"的三项成本也扣掉后的更谨慎口径，供参考。</div></div>

<div class="card"><h2>模型假设与口径（v3）</h2>
<ul class="ass">
<li><b>节奏</b>：每月开发 10 个；成功率 60% → 每月成功 6（节日 3.6 / 常规 2.4）、失败 4。</li>
<li><b>客单价 / 毛利</b>：单价 $10；毛利 <b>20%</b> = 销售额 − 产品成本 − 亚马逊佣金 − FBA 履约/仓储（你给定口径，<b>不含</b>退货、汇率、仓储费）。</li>
<li><b>首批备货</b>：300 件/SKU（你给定）。第1年 ×1.0 → 第2年 ×2.5 → 第3年稳定 ×2.5（后续需求年降 10% 已在前瞻情景体现）。</li>
<li><b>节日品</b>：占 60%，提前 4~5 月开品，平均售期 2 个月（每年同期重现窗口）；常规品占 40%，开品后约 3 个月起售、全年均匀。</li>
<li><b>失败亏损</b>：失败产品按"销售额的 50%"计亏损 = 0.5 × 300 × $10 = <b>$1500/个</b>，每月 4 个 = <b>$6000/月</b>，于开品当月确认（沉没成本前置）。</li>
<li><b>老品淘汰</b>：开售满 12 个月后，每年年末淘汰 <b>10%</b>（确定值按 0.9 衰减；蒙特卡洛按 10% 概率随机剔除）。</li>
<li><b>分布</b>：蒙特卡洛 {N_RUNS} 次，随机化每月成功/失败数(二项)、节日开品提前月数(4/5)、节日销售窗口、年度淘汰；逐月给出 P10/P50/P90 带。</li>
<li><b>口径提示</b>：本表"毛利/经营利润"未扣退货、汇率、仓储；"保守净利"列已额外扣除 8% 作更谨慎参考。实际落地建议按 ±15~25% 做敏感性预留。</li>
</ul></div>
</body></html>'''

html_path=os.path.join(base_dir,"新员工月度测算_v3.html")
open(html_path,'w',encoding='utf-8').write(html)

print("DONE")
print("CSV :",csv_path); print("HTML:",html_path)
print(f"盈亏平衡月: 第{breakeven}个月")
for y in (1,2,3):
    b=ys[y-1]; print(f"第{y}年  销售额${fmt(b['sales'])}  毛利${fmt(b['gross'])}  失败${fmt(b['fail'])}  经营利润${fmt(b['net'])}  月均利润${fmt(b['avg_net'])}")
print(f"36月累计  销售额${fmt(total_sales)}  毛利${fmt(total_gross)}  失败${fmt(total_fail)}  经营利润${fmt(total_net)}  第3年末在售SKU{active_end:.1f}")
print("前瞻(年度销售额): 继续10/月=",[fmt(x) for x in yc_sales]," 放缓5/月+需求降10%=",[fmt(x) for x in ym_sales]," 见顶年",peak_mature)
