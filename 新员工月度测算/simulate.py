# -*- coding: utf-8 -*-
"""
新员工月度销售额与毛利测算模型
假设均显式写入报告；所有数字为期望值(允许SKU为小数计数)。
"""
import csv, json, statistics

# ============== 参数 ==============
DEVELOPED_PER_MONTH = 10      # 每月开发新品数
SUCCESS_RATE        = 0.60     # 成功率
SUCCESSFUL_PER_MONTH= DEVELOPED_PER_MONTH * SUCCESS_RATE   # 6
FESTIVAL_SHARE      = 0.60     # 节日产品占比
REGULAR_SHARE       = 0.40     # 常规产品占比
FESTIVAL_PER_MONTH  = SUCCESSFUL_PER_MONTH * FESTIVAL_SHARE   # 3.6
REGULAR_PER_MONTH   = SUCCESSFUL_PER_MONTH * REGULAR_SHARE    # 2.4
UNIT_PRICE          = 10.0     # 客单价 USD
BATCH_Y1            = 300      # 首年首批备货
Y2_FACTOR           = 2.5      # 次年扩大倍数(2~3倍取中值)
RETIRE_RATE         = 0.10     # 每年老产品淘汰率
MARGIN_LOW          = 0.25
MARGIN_HIGH         = 0.30
MARGIN_BASE         = (MARGIN_LOW + MARGIN_HIGH) / 2   # 0.275
HORIZON             = 36       # 3年
LEAD                = 4        # 节日提前开品月数(4~5取中值)

def year_factor(month):
    yr = (month - 1) // 12 + 1
    return 1.0 if yr == 1 else Y2_FACTOR   # 第3年稳定(仍按2.5)

# SKU 以小数计数表示期望值
skus = []   # {launch, type, count}
rows = []

for t in range(1, HORIZON + 1):
    # 本月新增成功SKU
    skus.append({'launch': t, 'type': 'fest', 'count': FESTIVAL_PER_MONTH})
    skus.append({'launch': t, 'type': 'reg',  'count': REGULAR_PER_MONTH})

    units = 0.0
    active = 0.0
    for s in skus:
        if t < s['launch']:
            continue
        c = s['count']
        if c <= 0:
            continue
        active += c
        f = year_factor(t)
        if s['type'] == 'reg':
            u = (BATCH_Y1 / 12.0) * f          # 常规: 全年均匀
        else:
            off = (t - (s['launch'] + LEAD)) % 12
            u = (BATCH_Y1 / 2.0) * f if off in (0, 1) else 0.0  # 节日: 2个月窗口, 每年重现
        units += c * u

    sales = units * UNIT_PRICE
    profit_base = sales * MARGIN_BASE
    profit_low  = sales * MARGIN_LOW
    profit_high = sales * MARGIN_HIGH
    rows.append({
        'month': t,
        'active_skus': round(active, 1),
        'units': round(units, 1),
        'sales': round(sales, 1),
        'profit_base': round(profit_base, 1),
        'profit_low': round(profit_low, 1),
        'profit_high': round(profit_high, 1),
    })

    # 年末淘汰10%
    if t in (12, 24):
        for s in skus:
            s['count'] *= (1 - RETIRE_RATE)

# ============== 年度汇总 ==============
def year_slice(y):
    a, b = (y-1)*12 + 1, y*12
    return rows[a-1:b]

year_summary = []
for y in (1, 2, 3):
    sl = year_slice(y)
    tot_sales = sum(r['sales'] for r in sl)
    tot_profit = sum(r['profit_base'] for r in sl)
    avg_sales = tot_sales / 12
    avg_profit = tot_profit / 12
    year_summary.append({
        'year': y,
        'total_sales': round(tot_sales, 1),
        'total_profit': round(tot_profit, 1),
        'avg_monthly_sales': round(avg_sales, 1),
        'avg_monthly_profit': round(avg_profit, 1),
        'margin': MARGIN_BASE,
    })

# ============== 分布统计 ==============
sales_vals = [r['sales'] for r in rows]
profit_vals = [r['profit_base'] for r in rows]
dist = {
    'sales_min': min(sales_vals), 'sales_max': max(sales_vals),
    'sales_avg': statistics.mean(sales_vals), 'sales_median': statistics.median(sales_vals),
    'profit_min': min(profit_vals), 'profit_max': max(profit_vals),
    'profit_avg': statistics.mean(profit_vals), 'profit_median': statistics.median(profit_vals),
}

# ============== 写 CSV ==============
csv_path = "D:/AI-项目/销售业绩/新员工月度测算/新员工月度测算.csv"
with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['月份', '活跃SKU数', '销量(件)', '销售额(USD)',
                '毛利@27.5%(USD)', '毛利下限@25%(USD)', '毛利上限@30%(USD)'])
    for r in rows:
        w.writerow([r['month'], r['active_skus'], r['units'], r['sales'],
                    r['profit_base'], r['profit_low'], r['profit_high']])

# ============== 画 SVG 折线图 ==============
W, H = 780, 360
PL, PR, PT, PB = 64, 24, 28, 44
pw, ph = W - PL - PR, H - PT - PB
maxv = max(sales_vals)
def sx(m): return PL + (m - 1) / (HORIZON - 1) * pw
def sy(v): return PT + (1 - v / maxv) * ph

def line(key, color):
    pts = ' '.join(f"{sx(r['month']):.1f},{sy(r[key]):.1f}" for r in rows)
    return f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{pts}"/>'

grid = ''
for i in range(5):
    v = maxv * i / 4
    y = sy(v)
    grid += f'<line x1="{PL}" y1="{y:.1f}" x2="{W-PR}" y2="{y:.1f}" stroke="#e3e7ee"/>'
    grid += f'<text x="{PL-8}" y="{y+4:.1f}" text-anchor="end" font-size="10" fill="#6b7280">${v/1000:.1f}k</text>'
vlines = ''
for m in (12, 24, 36):
    x = sx(m)
    vlines += f'<line x1="{x:.1f}" y1="{PT}" x2="{x:.1f}" y2="{PT+ph}" stroke="#dfe3ea" stroke-dasharray="4 3"/>'
    vlines += f'<text x="{x:.1f}" y="{H-22}" text-anchor="middle" font-size="10" fill="#6b7280">第{m//12}年末</text>'
xlabels = ''
for m in (1, 6, 12, 18, 24, 30, 36):
    xlabels += f'<text x="{sx(m):.1f}" y="{H-8}" text-anchor="middle" font-size="10" fill="#6b7280">M{m}</text>'

chart_svg = f'''
<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, Arial, sans-serif">
  <rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>
  {grid}{vlines}
  {line('sales', '#2563eb')}
  {line('profit_base', '#16a34a')}
  {xlabels}
  <rect x="{PL}" y="6" width="14" height="10" fill="#2563eb"/>
  <text x="{PL+20}" y="15" font-size="11" fill="#374151">月销售额 (USD)</text>
  <rect x="{PL+150}" y="6" width="14" height="10" fill="#16a34a"/>
  <text x="{PL+170}" y="15" font-size="11" fill="#374151">月毛利@27.5% (USD)</text>
</svg>'''

# ============== 生成 HTML 报告 ==============
def fmt(x): return f"{x:,.0f}"

table_rows = ''
for r in rows:
    table_rows += (f"<tr><td>{r['month']}</td><td>{r['active_skus']}</td><td>{fmt(r['units'])}</td>"
                   f"<td>${fmt(r['sales'])}</td><td>${fmt(r['profit_base'])}</td>"
                   f"<td>${fmt(r['profit_low'])}~${fmt(r['profit_high'])}</td></tr>")

year_rows = ''
for y in year_summary:
    year_rows += (f"<tr><td>第{y['year']}年</td><td>${fmt(y['total_sales'])}</td>"
                  f"<td>${fmt(y['total_profit'])}</td><td>${fmt(y['avg_monthly_sales'])}</td>"
                  f"<td>${fmt(y['avg_monthly_profit'])}</td></tr>")

html = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>新员工月度销售额与毛利测算</title>
<style>
 body{{font-family:Segoe UI,'Microsoft YaHei',Arial,sans-serif;color:#1f2937;background:#f7f8fa;margin:0;padding:24px}}
 .card{{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:20px 24px;margin-bottom:18px;box-shadow:0 1px 3px rgba(0,0,0,.04)}}
 h1{{font-size:22px;margin:0 0 4px}} h2{{font-size:16px;margin:18px 0 8px;color:#374151}}
 .sub{{color:#6b7280;font-size:13px}}
 table{{border-collapse:collapse;width:100%;font-size:13px}}
 th,td{{border:1px solid #e5e7eb;padding:6px 8px;text-align:right}}
 th{{background:#f3f4f6;color:#374151;position:sticky;top:0}}
 td:first-child,th:first-child{{text-align:center}}
 .scroll{{max-height:420px;overflow:auto}}
 .kv{{display:flex;flex-wrap:wrap;gap:10px}}
 .stat{{flex:1;min-width:150px;background:#f9fafb;border:1px solid #eef0f3;border-radius:8px;padding:10px 12px}}
 .stat b{{display:block;font-size:18px;color:#111827}} .stat span{{font-size:12px;color:#6b7280}}
 .assump{{font-size:12.5px;color:#4b5563;line-height:1.7}}
 .assump li{{margin:2px 0}}
 .pos{{color:#16a34a}} .neg{{color:#dc2626}}
</style></head><body>
<h1>亚马逊新员工 · 月度销售额与毛利测算</h1>
<div class="sub">开发节奏：每月开发 10 个 → 成功率 60% → 每月成功上架 6 个 SKU（节日 3.6 / 常规 2.4）｜测算区间：入职后 36 个月</div>

<div class="card">
  <h2>逐月趋势（销售额 vs 毛利）</h2>
  {chart_svg}
</div>

<div class="card">
  <h2>分布统计（36 个月）</h2>
  <div class="kv">
    <div class="stat"><span>月销售额 最低</span><b>${fmt(dist['sales_min'])}</b></div>
    <div class="stat"><span>月销售额 中位数</span><b>${fmt(dist['sales_median'])}</b></div>
    <div class="stat"><span>月销售额 平均</span><b>${fmt(dist['sales_avg'])}</b></div>
    <div class="stat"><span>月销售额 最高</span><b>${fmt(dist['sales_max'])}</b></div>
    <div class="stat"><span>月毛利@27.5% 平均</span><b>${fmt(dist['profit_avg'])}</b></div>
    <div class="stat"><span>月毛利@27.5% 最高</span><b>${fmt(dist['profit_max'])}</b></div>
  </div>
</div>

<div class="card">
  <h2>年度汇总</h2>
  <table><thead><tr><th>年度</th><th>年销售额</th><th>年毛利@27.5%</th><th>月均销售额</th><th>月均毛利</th></tr></thead>
  <tbody>{year_rows}</tbody></table>
  <div class="sub" style="margin-top:8px">说明：第 2 年备货量提升 2.5×（2~3 倍中值），第 3 年维持稳定；每年年末淘汰 10% 老产品。</div>
</div>

<div class="card">
  <h2>逐月明细（36 个月）</h2>
  <div class="scroll"><table><thead><tr><th>月份</th><th>活跃SKU</th><th>销量(件)</th><th>销售额</th><th>毛利@27.5%</th><th>毛利区间(25%~30%)</th></tr></thead>
  <tbody>{table_rows}</tbody></table></div>
</div>

<div class="card">
  <h2>模型假设与口径</h2>
  <ul class="assump">
    <li>开发节奏：每月开发 <b>10</b> 个新品，成功率 <b>60%</b> → 每月成功上架 <b>6</b> 个（节日 3.6 / 常规 2.4）。</li>
    <li>客单价 <b>$10</b>；首年首批备货 <b>300</b> 件/ SKU。</li>
    <li>备货爬坡：第 1 年 ×1.0（300 件），第 2 年 ×<b>2.5</b>（750 件，2~3 倍取中值），第 3 年维持 <b>2.5</b>（稳定，之后逐年下降）。</li>
    <li>结构：节日 60% / 常规 40%。节日产品销售期 <b>2 个月</b>/年（每月 150 件），每年同期重现；常规产品全年均匀（每月 25 件）。</li>
    <li>节日提前 <b>4~5 个月</b>开品（取中值 4）：SKU 在上市后第 5~6 个月进入销售窗口，之后每年同期重现。</li>
    <li>淘汰：每年年末淘汰 <b>10%</b> 老产品（活跃计数 ×0.9）。</li>
    <li>毛利：按毛利率 <b>25%~30%</b> 计（取中值 27.5% 作主线，区间列于表末列）。此为<b>毛利</b>，未扣除广告/仓储/头程/退货/汇率等费用。</li>
    <li>SKU 以小数计数表示期望值；实际落地会有波动，建议按 ±15% 做敏感性预留。</li>
  </ul>
</div>
</body></html>'''

html_path = "D:/AI-项目/销售业绩/新员工月度测算/新员工月度测算.html"
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("DONE")
print("CSV :", csv_path)
print("HTML:", html_path)
print("年度汇总:")
for y in year_summary:
    print(f"  第{y['year']}年  销售额${fmt(y['total_sales'])}  毛利${fmt(y['total_profit'])}  月均销售${fmt(y['avg_monthly_sales'])}")
print("分布: 月销售额 min/median/avg/max =",
      fmt(dist['sales_min']), fmt(dist['sales_median']), fmt(dist['sales_avg']), fmt(dist['sales_max']))
print("      月毛利avg/max =", fmt(dist['profit_avg']), fmt(dist['profit_max']))
