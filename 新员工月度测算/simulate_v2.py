# -*- coding: utf-8 -*-
"""
新员工月度销售额与毛利测算模型 v2
修正点:
 - 开品后至少3个月才开始销售(FBA入仓滞后): 常规品 launch+3 起售; 节日品 launch+4/+5 窗口(已>=3)
 - 首批采购量 300~500 (取中值400)
 - 每年淘汰10%老品(显式计入, 并附"不计入"对照)
 - FBA净利估算: 毛利(扣产品成本+亚马逊佣金/FBA履约) 再扣 广告/退货/汇率
"""
import csv, statistics

# ============== 参数 ==============
DEVELOPED_PER_MONTH = 10
SUCCESS_RATE        = 0.60
SUCCESSFUL_PER_MONTH= DEVELOPED_PER_MONTH * SUCCESS_RATE     # 6
FESTIVAL_SHARE      = 0.60
REGULAR_SHARE       = 0.40
FESTIVAL_PER_MONTH  = SUCCESSFUL_PER_MONTH * FESTIVAL_SHARE # 3.6
REGULAR_PER_MONTH   = SUCCESSFUL_PER_MONTH * REGULAR_SHARE  # 2.4
UNIT_PRICE          = 10.0
BATCH_Y1            = 400      # 首批采购量 300~500 中值
Y2_FACTOR           = 2.5      # 次年扩大倍数(2~3倍中值)
RETIRE_RATE         = 0.10     # 每年老品淘汰率
REGULAR_LEAD        = 3        # 常规品: 开品后至少3个月起售
FESTIVAL_LEAD       = 4        # 节日品: 提前4~5月开品(取中值4)
MARGIN_LOW, MARGIN_HIGH = 0.25, 0.30
MARGIN_BASE         = (MARGIN_LOW + MARGIN_HIGH) / 2         # 0.275 (贡献毛利)
# FBA 净利扣减项(占销售额比例, 可与用户实际对账调整)
AD_RATE             = 0.15     # 广告 ACOS
RETURN_RATE         = 0.04     # 退货/损毁
FX_RATE             = 0.01     # 汇率波动
DEDUCTIONS          = AD_RATE + RETURN_RATE + FX_RATE        # 0.20
NET_BASE            = MARGIN_BASE - DEDUCTIONS               # 0.075
NET_LOW             = MARGIN_LOW - DEDUCTIONS                # 0.05
NET_HIGH            = MARGIN_HIGH - DEDUCTIONS               # 0.10
HORIZON             = 36

def year_factor(month):
    yr = (month - 1) // 12 + 1
    return 1.0 if yr == 1 else Y2_FACTOR

def build_model(retire):
    skus = []   # {launch, type, count}
    rows = []
    for t in range(1, HORIZON + 1):
        skus.append({'launch': t, 'type': 'fest', 'count': FESTIVAL_PER_MONTH})
        skus.append({'launch': t, 'type': 'reg',  'count': REGULAR_PER_MONTH})
        units = 0.0
        active = 0.0
        for s in skus:
            if t < s['launch'] or s['count'] <= 0:
                continue
            active += s['count']
            f = year_factor(t)
            if s['type'] == 'reg':
                u = (BATCH_Y1 / 12.0) * f if t >= s['launch'] + REGULAR_LEAD else 0.0
            else:
                off = (t - (s['launch'] + FESTIVAL_LEAD)) % 12
                u = (BATCH_Y1 / 2.0) * f if off in (0, 1) else 0.0
            units += s['count'] * u
        sales = units * UNIT_PRICE
        rows.append({
            'month': t, 'active_skus': round(active, 1), 'units': round(units, 1),
            'sales': sales, 'gross_base': sales * MARGIN_BASE,
            'gross_low': sales * MARGIN_LOW, 'gross_high': sales * MARGIN_HIGH,
            'net_base': sales * NET_BASE, 'net_low': sales * NET_LOW, 'net_high': sales * NET_HIGH,
        })
        if t in (12, 24) and retire > 0:
            for s in skus:
                s['count'] *= (1 - retire)
    # 年度汇总
    ys = []
    for y in (1, 2, 3):
        sl = rows[(y-1)*12:y*12]
        ts = sum(r['sales'] for r in sl)
        tg = sum(r['gross_base'] for r in sl)
        tn = sum(r['net_base'] for r in sl)
        ys.append({'year': y, 'sales': ts, 'gross': tg, 'net': tn,
                   'avg_sales': ts/12, 'avg_gross': tg/12, 'avg_net': tn/12})
    launched = SUCCESSFUL_PER_MONTH * HORIZON
    return rows, ys, launched

rows, ys, launched = build_model(RETIRE_RATE)
rows_no, ys_no, _  = build_model(0.0)
active_end = rows[-1]['active_skus']
retired_cum = launched - active_end   # 累计淘汰(期望值)

def fmt(x): return f"{x:,.0f}"

# CSV
csv_path = "D:/AI-项目/销售业绩/新员工月度测算/新员工月度测算_v2.csv"
with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['月份','活跃SKU','销量(件)','销售额USD','毛利@27.5%USD',
                '毛利区间25~30%USD','净利估算@7.5%USD','净利区间5~10%USD'])
    for r in rows:
        w.writerow([r['month'], r['active_skus'], fmt(r['units']), fmt(r['sales']),
                    fmt(r['gross_base']), f"{fmt(r['gross_low'])}~{fmt(r['gross_high'])}",
                    fmt(r['net_base']), f"{fmt(r['net_low'])}~{fmt(r['net_high'])}"])

# SVG 图表(销售额 / 毛利 / 净利)
W,H=800,380; PL,PR,PT,PB=66,24,30,46; pw,ph=W-PL-PR,H-PT-PB
maxv=max(r['sales'] for r in rows)
def sx(m): return PL+(m-1)/(HORIZON-1)*pw
def sy(v): return PT+(1-v/maxv)*ph
def line(key,color):
    return f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{" ".join(f"{sx(r["month"]):.1f},{sy(r[key]):.1f}" for r in rows)}"/>'
grid=''
for i in range(5):
    v=maxv*i/4; y=sy(v)
    grid+=f'<line x1="{PL}" y1="{y:.1f}" x2="{W-PR}" y2="{y:.1f}" stroke="#e3e7ee"/>'
    grid+=f'<text x="{PL-8}" y="{y+4:.1f}" text-anchor="end" font-size="10" fill="#6b7280">${v/1000:.1f}k</text>'
vl=''
for m in (12,24,36):
    x=sx(m)
    vl+=f'<line x1="{x:.1f}" y1="{PT}" x2="{x:.1f}" y2="{PT+ph}" stroke="#dfe3ea" stroke-dasharray="4 3"/>'
    vl+=f'<text x="{x:.1f}" y="{H-24}" text-anchor="middle" font-size="10" fill="#6b7280">第{m//12}年末</text>'
xl=''.join(f'<text x="{sx(m):.1f}" y="{H-9}" text-anchor="middle" font-size="10" fill="#6b7280">M{m}</text>' for m in (1,6,12,18,24,30,36))
chart=f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial,sans-serif">
<rect width="{W}" height="{H}" fill="#fff"/>{grid}{vl}
{line('sales','#2563eb')}{line('gross_base','#16a34a')}{line('net_base','#f59e0b')}{xl}
<rect x="{PL}" y="6" width="13" height="10" fill="#2563eb"/><text x="{PL+18}" y="15" font-size="11" fill="#374151">月销售额</text>
<rect x="{PL+110}" y="6" width="13" height="10" fill="#16a34a"/><text x="{PL+128}" y="15" font-size="11" fill="#374151">月毛利@27.5%</text>
<rect x="{PL+250}" y="6" width="13" height="10" fill="#f59e0b"/><text x="{PL+268}" y="15" font-size="11" fill="#374151">月净利估算@7.5%</text>
</svg>'''

# 表格
tr=''.join(f"<tr><td>{r['month']}</td><td>{r['active_skus']}</td><td>{fmt(r['units'])}</td><td>${fmt(r['sales'])}</td><td>${fmt(r['gross_base'])}</td><td>${fmt(r['gross_low'])}~${fmt(r['gross_high'])}</td><td>${fmt(r['net_base'])}</td><td>${fmt(r['net_low'])}~${fmt(r['net_high'])}</td></tr>" for r in rows)
yr=''.join(f"<tr><td>第{y['year']}年</td><td>${fmt(y['sales'])}</td><td>${fmt(y['gross'])}</td><td>${fmt(y['net'])}</td><td>${fmt(y['avg_sales'])}</td><td>${fmt(y['avg_gross'])}</td><td>${fmt(y['avg_net'])}</td></tr>" for y in ys)
# 淘汰对照
cmp=''.join(f"<tr><td>第{i+1}年</td><td>${fmt(ys[i]['sales'])}</td><td>${fmt(ys_no[i]['sales'])}</td><td>${fmt(ys_no[i]['sales']-ys[i]['sales'])}</td></tr>" for i in range(3))

html=f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>新员工月度销售额与利润测算 v2 (FBA)</title>
<style>body{{font-family:Segoe UI,'Microsoft YaHei',Arial,sans-serif;color:#1f2937;background:#f7f8fa;margin:0;padding:24px}}
.card{{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:20px 24px;margin-bottom:18px;box-shadow:0 1px 3px rgba(0,0,0,.04)}}
h1{{font-size:22px;margin:0 0 4px}} h2{{font-size:16px;margin:18px 0 8px;color:#374151}}
.sub{{color:#6b7280;font-size:13px}} table{{border-collapse:collapse;width:100%;font-size:13px}}
th,td{{border:1px solid #e5e7eb;padding:6px 8px;text-align:right}} th{{background:#f3f4f6;color:#374151}}
td:first-child,th:first-child{{text-align:center}} .scroll{{max-height:440px;overflow:auto}}
.kv{{display:flex;flex-wrap:wrap;gap:10px}} .stat{{flex:1;min-width:150px;background:#f9fafb;border:1px solid #eef0f3;border-radius:8px;padding:10px 12px}}
.stat b{{display:block;font-size:18px;color:#111827}} .stat span{{font-size:12px;color:#6b7280}}
.ass{{font-size:12.5px;color:#4b5563;line-height:1.7}} .ass li{{margin:2px 0}}
.warn{{background:#fff7ed;border:1px solid #fed7aa;color:#9a3412;padding:10px 14px;border-radius:8px;font-size:13px;margin-bottom:14px}}</style>
</head><body>
<h1>亚马逊 FBA 新员工 · 月度销售额与利润测算 v2</h1>
<div class="sub">开发节奏：每月 10 个 → 60% 成功率 → 每月成功 6 个（节日 3.6 / 常规 2.4）｜区间：入职 36 个月｜已修正：3个月销售滞后 / 首批300~500(中值400) / 每年淘汰10% / FBA净利估算</div>

<div class="warn">⚠️ 前 3 个月为 FBA 入仓滞后期，<b>零销售额</b>；首批采购按中值 400 件计（300~500 区间对应 ±25% 波动）；10% 年度淘汰已计入；净利为估算（见假设口径）。</div>

<div class="card"><h2>逐月趋势</h2>{chart}</div>

<div class="card"><h2>分布统计（36 个月）</h2><div class="kv">
<div class="stat"><span>月销售额 中位数</span><b>${fmt(statistics.median(r['sales'] for r in rows))}</b></div>
<div class="stat"><span>月销售额 平均</span><b>${fmt(statistics.mean(r['sales'] for r in rows))}</b></div>
<div class="stat"><span>月销售额 峰值</span><b>${fmt(max(r['sales'] for r in rows))}</b></div>
<div class="stat"><span>月毛利@27.5% 平均</span><b>${fmt(statistics.mean(r['gross_base'] for r in rows))}</b></div>
<div class="stat"><span>月净利@7.5% 平均</span><b>${fmt(statistics.mean(r['net_base'] for r in rows))}</b></div>
<div class="stat"><span>第3年末在售SKU</span><b>{active_end}</b></div>
</div></div>

<div class="card"><h2>年度汇总</h2>
<table><thead><tr><th>年度</th><th>年销售额</th><th>年毛利@27.5%</th><th>年净利@7.5%</th><th>月均销售额</th><th>月均毛利</th><th>月均净利</th></tr></thead><tbody>{yr}</tbody></table></div>

<div class="card"><h2>10% 年度淘汰的影响（计入 vs 不计入）</h2>
<table><thead><tr><th>年度</th><th>计入淘汰 年销售额</th><th>不计入淘汰 年销售额</th><th>差额(淘汰造成的减少)</th></tr></thead><tbody>{cmp}</tbody></table>
<div class="sub" style="margin-top:8px">36个月累计成功上架约 {fmt(launched)} 个 SKU（期望值），因每年淘汰10%，第3年末在售约 {active_end} 个，累计淘汰约 {fmt(retired_cum)} 个。第3年销售额因此比"不淘汰"低约 {fmt(ys_no[2]['sales']-ys[2]['sales'])}。</div></div>

<div class="card"><h2>逐月明细（36 个月）</h2>
<div class="scroll"><table><thead><tr><th>月份</th><th>活跃SKU</th><th>销量(件)</th><th>销售额</th><th>毛利@27.5%</th><th>毛利区间25~30%</th><th>净利@7.5%</th><th>净利区间5~10%</th></tr></thead><tbody>{tr}</tbody></table></div></div>

<div class="card"><h2>模型假设与口径（v2）</h2>
<ul class="ass">
<li><b>节奏</b>：每月开发 10 → 60% 成功 → 每月成功上架 6（节日 3.6 / 常规 2.4）。</li>
<li><b>销售滞后</b>：FBA 入仓，开品后至少 3 个月才起售。常规品自 launch+3 起全年均匀售；节日品在 launch+4/+5 的 2 个月窗口售（每年同期重现）。前 3 个月零销售。</li>
<li><b>首批采购</b>：300~500 件，取中值 <b>400</b> 件/SKU（±25% 对应 300/500）。</li>
<li><b>备货爬坡</b>：第1年 ×1.0（400）→ 第2年 ×2.5（1000）→ 第3年维持 2.5（稳定，之后逐年下降）。</li>
<li><b>结构</b>：节日 60% / 常规 40%。节日年售 2 个月（200 件/月窗口），常规年售 12 个月（约 33 件/月）。</li>
<li><b>淘汰</b>：每年年末淘汰 <b>10%</b> 在售老品（已计入，并附对照）。</li>
<li><b>毛利口径</b>：25~30% 为<b>贡献毛利</b>＝销售额 − 产品成本 − 亚马逊佣金(15%) − FBA 履约/仓储费。</li>
<li><b>净利估算</b>：再扣 广告 ACOS 15% + 退货 4% + 汇率 1% ＝ 约 5~10%（中值 7.5%）。<b>此为估算，扣减比例可按实际对账调整。</b></li>
<li>SKU 以小数计数表示期望值；实际落地有波动，建议按 ±15~25% 做敏感性预留。</li>
</ul></div>
</body></html>'''

html_path="D:/AI-项目/销售业绩/新员工月度测算/新员工月度测算_v2.html"
open(html_path,'w',encoding='utf-8').write(html)
print("DONE")
print("CSV :",csv_path); print("HTML:",html_path)
for y in ys: print(f"第{y['year']}年  销售额${fmt(y['sales'])}  毛利${fmt(y['gross'])}  净利${fmt(y['net'])}  月均销售${fmt(y['avg_sales'])}")
print("淘汰对照(不计入-计入) 年差额:", [fmt(ys_no[i]['sales']-ys[i]['sales']) for i in range(3)])
print(f"累计上架{launched:.0f}  第3年末在售{active_end}  累计淘汰{retired_cum:.1f}")
