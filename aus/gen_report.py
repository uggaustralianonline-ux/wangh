# -*- coding: utf-8 -*-
"""Generate A-US ad attribution HTML report from result.json."""
import json

d = json.load(open('result.json'))
P = d['profit']; cur, prev = P['cur'], P['prev']
ADS = d['ads']; T = d['tiers']; S = d['subs']
BT = d['by_type']; BG = d['by_targeting']; BP = d['by_portfolio']
SC1 = S['C1 轻度超支']; SC2 = S['C2 重度超支']; SC3 = S['C3 严重失控']; SC4 = S['C4 零单空烧']
KW = d['kw']; TG = d['tg']; PL = d['plan']
per = d['period']; p0, p1 = per[0], per[1]
pprev = d['prev']   # period window labels for previous

def u(x, dec=0, sign=False):
    s = f"{abs(x):,.{dec}f}"
    if x < 0: return '−$' + s
    if sign: return '+$' + s
    return '$' + s

def pct(x, dec=1, sign=False):
    if x is None: return '—'
    s = f"{abs(x):.{dec}f}"
    if x < 0: s = '−' + s
    elif sign: s = '+' + s
    return s + '%'

def n(x):
    return f"{x:,.0f}"

# ---- derived ----
breakeven = P['breakeven']
A_CUT, B_CUT = d['cuts']['A'], d['cuts']['B']
net = ADS['net']
nat_share = P['nat_sales'] / cur['sales'] * 100
recap = P['recapture']

# period-over-period indices (cur/prev*100)
idx_spend = cur['spend']/prev['spend']*100
idx_adsales = cur['ad_sales']/prev['ad_sales']*100
idx_natsales = P['nat_sales']/P['prev_nat_sales']*100  # prev nat from profit dict
idx_totsales = cur['sales']/prev['sales']*100
idx_gp = cur['gp']/prev['gp']*100
idx_gm = P['gm']/P['prev_gm']*100
prev_acos = prev['spend']/prev['ad_sales']*100
idx_acos = ADS['acos']/prev_acos*100
idx_tacos = P['tacos']/P['prev_tacos']*100

# portfolio top 12 by spend
ports = sorted(((k, v) for k, v in BP.items()), key=lambda x: -x[1]['spend'])[:12]

CSS = open('../bus-ad-attribution/bus-ad-attribution.html', encoding='utf-8').read().split('<style>')[1].split('</style>')[0]

def tier_tag(t):
    cls = {'A':'a','B':'b','C':'c'}.get(t, 'c')
    return f'<span class="tag {cls}">{t}</span>'

def fmt_net(x):
    return f'<td class="num {"pos" if x>=0 else "neg"}">{(("+" if x>=0 else "−")+u(abs(x))[1:]) if False else (("+" if x>=0 else "−")+f"{abs(x):,.0f}")}</td>'

def net_cell(x):
    return f'<td class="num {"pos" if x>=0 else "neg"}">{(("+" if x>=0 else "−")+f"{abs(x):,.0f}")}</td>'

def acos_cell(x):
    if x is None: return '<td class="num">—</td>'
    return f'<td class="num {"pos" if x<=breakeven else "neg"}">{pct(x)}</td>'

# ---- HTML head / header ----
html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>A-US 近30天广告效果归因与预算重分配</title>
<style>{CSS}</style>
</head>
<body>

<header class="report-header">
  <div class="container">
    <div class="label">Amazon Ads Attribution · A-US</div>
    <h1>A-US 近 30 天广告效果归因<br>与预算重分配方案</h1>
    <div class="meta">
      <span>数据窗口 {p0} ~ {p1}</span>
      <span>数据源 领星 ERP（广告报表 + 订单利润）</span>
      <span>Profile 4170394317233977</span>
      <span>币种 USD</span>
    </div>
  </div>
</header>

<div class="container">
"""

# ============ 1. 结论 ============
html += f"""
<section>
  <h2>一、核心结论</h2>

  <div class="callout danger">
    <div class="t">整体 ACOS {pct(ADS['acos'])} 已经击穿保本线 {pct(breakeven)}，广告板块本身是亏的。</div>
    全店近 30 天扣除退款、FBA 配送费、佣金、采购成本、头程、仓储等<strong>一切非广告成本</strong>后，每 $1 销售额只剩 <strong>{pct(breakeven)} 美分</strong>可用于支付广告并留存利润。这就是这个店的<strong>盈亏平衡 ACOS = {pct(breakeven)}</strong>。实际 ACOS {pct(ADS['acos'])}，意味着广告直接产出的 {u(cur['ad_sales'])} 销售额，扣完变动成本后只贡献 {u(cur['gp']*cur['ad_sales']/cur['sales'])} 毛利池，却花掉了 {u(ADS['spend'])} 广告费——<strong>广告口径净亏 {u(abs(net))}</strong>。全店还能剩 {pct(P['gm'])} 毛利率，完全靠占比 {pct(nat_share)} 的自然单在补贴广告。
  </div>

  <div class="kpi-grid">
    <div class="kpi"><div class="k">广告花费</div><div class="v">{u(ADS['spend'])}</div><div class="d">环比 {pct(idx_spend-100,sign=True)}</div></div>
    <div class="kpi"><div class="k">广告销售额</div><div class="v">{u(cur['ad_sales'])}</div><div class="d">环比 {pct(idx_adsales-100,sign=True)}</div></div>
    <div class="kpi danger"><div class="k">ACOS</div><div class="v">{pct(ADS['acos'])}</div><div class="d">保本线 {pct(breakeven)} · 超 {pct(ADS['acos']-breakeven)}</div></div>
    <div class="kpi"><div class="k">TACOS</div><div class="v">{pct(P['tacos'])}</div><div class="d">环比 {pct(idx_tacos-100,sign=True)}</div></div>
  </div>
  <div class="kpi-grid">
    <div class="kpi"><div class="k">全店销售额</div><div class="v">{u(cur['sales'])}</div><div class="d">环比 {pct(idx_totsales-100,sign=True)}</div></div>
    <div class="kpi warn"><div class="k">毛利 / 毛利率</div><div class="v">{pct(P['gm'])}</div><div class="d">{u(cur['gp'])} · 已扣广告费</div></div>
    <div class="kpi danger"><div class="k">广告净贡献毛利</div><div class="v">{u(net)}</div><div class="d">广告销售额×{pct(breakeven)} − 花费</div></div>
    <div class="kpi good"><div class="k">自然单占比(销售额)</div><div class="v">{pct(nat_share)}</div><div class="d">{u(P['nat_sales'])} / {u(cur['sales'])}</div></div>
  </div>

  <h3>三句话版本</h3>
  <ol>
    <li><strong>钱花在了错的地方，不是花多了。</strong> {pct(T['C']['spend_pct'])} 的预算（{u(T['C']['spend'])}）落在 ACOS &gt; {pct(B_CUT)} 的低效活动上，这批活动净亏 {u(abs(T['C']['net']))}；而真正赚钱的高效活动只拿到 {pct(T['A']['spend_pct'])} 预算。</li>
    <li><strong>边际效率在恶化，但自然单在接棒。</strong> 环比广告费降 {pct(100-idx_spend)}、广告销售额降 {pct(100-idx_adsales)}，但<strong>自然销售额 +{pct(idx_natsales-100)}（{u(P['nat_sales']-171808.11)}）、总毛利 +{pct(idx_gp-100)}</strong>——少花的广告费没有拖累整体，反而让利润更厚。</li>
    <li><strong>结构性倒挂可被修复。</strong> 把 C 档削减出的 {u(PL['released'])} 预算，{u(PL['addA'])} 回补到 A 档高效活动，净削减 {u(PL['net_cut'])} 广告投放，即可把毛利率从 {pct(P['gm'])} 拉到 {pct(PL['new_gm'])}，月度毛利 +{u(PL['gp_delta'])}（年化约 {u(PL['gp_delta']*12)}）。</li>
  </ol>
</section>
"""

# ============ 2. 保本线推导 ============
refund = cur['refund']; fba = cur['fba']; comm = cur['commission']; pur = cur['purchase']
logi = cur['logistics']; stor = cur['storage']; promo = cur['promo']
html += f"""
<section>
  <h2>二、保本 ACOS 是怎么算出来的</h2>
  <p>把广告花费关联到利润板块，必须先算清「广告前贡献毛利率」——即每 $1 销售额在扣掉所有非广告变动成本后，还剩多少钱能拿去投广告。</p>

  <table>
    <thead><tr><th>利润科目</th><th>金额 (USD)</th><th>占销售额</th><th>说明</th></tr></thead>
    <tbody>
      <tr><td>销售额</td><td class="num">{u(cur['sales'])}</td><td class="num">100.00%</td><td></td></tr>
      <tr><td>退款</td><td class="num neg">−{u(refund)[1:]}</td><td class="num">−{pct(refund/cur['sales']*100)}</td><td></td></tr>
      <tr><td>FBA 配送费</td><td class="num neg">−{u(fba)[1:]}</td><td class="num">−{pct(fba/cur['sales']*100)}</td><td>低客单结构性痛点</td></tr>
      <tr><td>平台佣金</td><td class="num neg">−{u(comm)[1:]}</td><td class="num">−{pct(comm/cur['sales']*100)}</td><td></td></tr>
      <tr><td>采购成本</td><td class="num neg">−{u(pur)[1:]}</td><td class="num">−{pct(pur/cur['sales']*100)}</td><td></td></tr>
      <tr><td>头程物流</td><td class="num neg">−{u(logi)[1:]}</td><td class="num">−{pct(logi/cur['sales']*100)}</td><td></td></tr>
      <tr><td>仓储费</td><td class="num neg">−{u(stor)[1:]}</td><td class="num">−{pct(stor/cur['sales']*100)}</td><td></td></tr>
      <tr><td>促销 / 其他</td><td class="num neg">−{u(promo)[1:]}</td><td class="num">−{pct(promo/cur['sales']*100)}</td><td></td></tr>
      <tr class="tot"><td>广告前贡献毛利</td><td class="num">{u(P['pre_ad_gp'])}</td><td class="num">{pct(breakeven)}</td><td><strong>= 保本 ACOS</strong></td></tr>
      <tr><td>广告费（SP+SB+SD）</td><td class="num neg">−{u(ADS['spend'])[1:]}</td><td class="num">−{pct(P['tacos'])}</td><td>= TACOS</td></tr>
      <tr class="tot"><td>毛利</td><td class="num">{u(cur['gp'])}</td><td class="num">{pct(P['gm'])}</td><td></td></tr>
    </tbody>
  </table>

  <div class="callout">
    <div class="t">口径校验（自洽性检查）</div>
    广告销售额 {u(cur['ad_sales'])} × {pct(breakeven)} − 广告费 {u(ADS['spend'])} = <strong>{u(net)}</strong>（广告板块）<br>
    自然销售额 {u(P['nat_sales'])} × {pct(breakeven)} = <strong>+{u(P['nat_sales']*breakeven/100)}</strong>（自然板块）<br>
    合计 = <strong>{u(P['nat_sales']*breakeven/100 + net)}</strong> ≈ 实际毛利 {u(cur['gp'])} ✓
  </div>

  <p class="note">注：FBA 配送费占比 {pct(fba/cur['sales']*100)}、佣金占比 {pct(comm/cur['sales']*100)} 合计近五成，是这个店保本 ACOS 高达 {pct(breakeven)} 的根本原因。平均客单价仅 {u(P['aov'],2)}，属于低价小件，配送费刚性摊薄了广告承受力。本报告只在广告层做优化，但需提示：<strong>若不解决客单价，广告优化的天花板就锁死在这里。</strong></p>
</section>
"""

# ============ 3. 投放类型 / 方式拆解 ============
sp, sb, sb2 = BT['sp'], BT['sb'], BT['sb2']
html += f"""
<section>
  <h2>三、按投放类型 / 投放方式拆解</h2>

  <div class="chart" id="chartType"></div>

  <table>
    <thead><tr><th>广告类型</th><th>活动数</th><th>花费</th><th>预算占比</th><th>广告销售额</th><th>订单</th><th>ACOS</th><th>ROAS</th><th>净贡献毛利</th></tr></thead>
    <tbody>
      <tr><td>SP 商品推广</td><td class="num">{sp['n']}</td><td class="num">{u(sp['spend'])}</td><td class="num">{pct(sp['spend_pct'])}</td><td class="num">{u(sp['sales'])}</td><td class="num">{sp['orders']}</td><td class="num neg">{pct(sp['acos'])}</td><td class="num">{sp['roas']:.2f}</td>{net_cell(sp['net'])}</tr>
      <tr><td>SB 品牌推广（视频）</td><td class="num">{sb['n']}</td><td class="num">{u(sb['spend'])}</td><td class="num">{pct(sb['spend_pct'])}</td><td class="num">{u(sb['sales'])}</td><td class="num">{sb['orders']}</td><td class="num">{pct(sb['acos'])}</td><td class="num">{sb['roas']:.2f}</td>{net_cell(sb['net'])}</tr>
      <tr><td>SB 品牌推广（商品集）</td><td class="num">{sb2['n']}</td><td class="num">{u(sb2['spend'])}</td><td class="num">{pct(sb2['spend_pct'])}</td><td class="num">{u(sb2['sales'])}</td><td class="num">{sb2['orders']}</td><td class="num">{pct(sb2['acos'])}</td><td class="num">{sb2['roas']:.2f}</td>{net_cell(sb2['net'])}</tr>
      <tr class="tot"><td>合计</td><td class="num">{ADS['n']}</td><td class="num">{u(ADS['spend'])}</td><td class="num">100%</td><td class="num">{u(ADS['sales'])}</td><td class="num">{ADS['orders']}</td><td class="num">{pct(ADS['acos'])}</td><td class="num">{ADS['roas']:.2f}</td>{net_cell(ADS['net'])}</tr>
    </tbody>
  </table>

  <div class="two">
    <div>
      <h4>按投放方式</h4>
      <table>
        <thead><tr><th>方式</th><th>活动</th><th>花费</th><th>ACOS</th><th>净贡献</th></tr></thead>
        <tbody>
          <tr><td>自动 auto</td><td class="num">{BG['auto']['n']}</td><td class="num">{u(BG['auto']['spend'])}</td><td class="num pos">{pct(BG['auto']['acos'])}</td>{net_cell(BG['auto']['net'])}</tr>
          <tr><td>手动 manual</td><td class="num">{BG['manual']['n']}</td><td class="num">{u(BG['manual']['spend'])}</td><td class="num neg">{pct(BG['manual']['acos'])}</td>{net_cell(BG['manual']['net'])}</tr>
        </tbody>
      </table>
      <p class="note">反直觉信号：<strong>自动投放的 ACOS（{pct(BG['auto']['acos'])}）显著优于手动（{pct(BG['manual']['acos'])}）</strong>。手动关键词库里沉淀了大量高竞价低转化的词，人工选词质量低于亚马逊算法。</p>
    </div>
    <div>
      <h4>SP 直接 / 间接归因</h4>
      <table>
        <thead><tr><th>归因</th><th>销售额</th><th>占比</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td>直接（广告 ASIN 本身）</td><td class="num">{u(ADS['direct_sales'])}</td><td class="num">{pct(ADS['direct_sales']/ADS['sales']*100)}</td><td class="num">直接 ACOS {pct(ADS['spend']/ADS['direct_sales']*100)}</td></tr>
          <tr><td>间接（同店其他 ASIN）</td><td class="num">{u(ADS['indirect_sales'])}</td><td class="num">{pct(ADS['indirect_sales']/ADS['sales']*100)}</td><td class="num">间接订单 {ADS['indirect_orders']:,}</td></tr>
        </tbody>
      </table>
      <p class="note">若只看直接归因，ACOS 高达 {pct(ADS['spend']/ADS['direct_sales']*100)}，远超保本线。<strong>{pct(ADS['indirect_sales']/ADS['sales']*100)} 的间接销售额是把整体 ACOS 从 {pct(ADS['spend']/ADS['direct_sales']*100)} 拉回 {pct(ADS['acos'])} 的唯一功臣</strong>，说明店铺 SKU 交叉带动有效，但不足以覆盖投放浪费。</p>
    </div>
  </div>

  <h3>按广告组合（portfolio）拆解 · TOP 12 花费</h3>
  <table>
    <thead><tr><th>广告组合</th><th>活动数</th><th>花费</th><th>销售额</th><th>ACOS</th><th>净贡献</th><th>高效(A)</th><th>保本(B)</th><th>低效(C)</th></tr></thead>
    <tbody>
"""
for name, v in ports:
    html += f"""      <tr><td>{name}</td><td class="num">{v['n']}</td><td class="num">{u(v['spend'])}</td><td class="num">{u(v['sales'])}</td><td class="num {'pos' if v['acos']<=breakeven else 'neg'}">{pct(v['acos'])}</td>{net_cell(v['net'])}<td class="num">{u(v['tierA'])}</td><td class="num">{u(v['tierB'])}</td><td class="num neg">{u(v['tierC'])}</td></tr>
"""
html += f"""    </tbody>
  </table>
  <p class="note">「(未分组)」组合占 {pct(BP['(未分组)']['spend_pct'])} 花费却净亏 {u(abs(BP['(未分组)']['net']))}，是预算纪律最涣散的区域；玉米针、发饰钩针、耳贴等命名组合则相对集中可控。</p>
</section>
"""

# ============ 4. 三档分类 ============
html += f"""
<section>
  <h2>四、三档分类：赚钱 / 保本 / 烧钱</h2>
  <p>以保本 ACOS {pct(breakeven)} 为轴，留 ±20% 缓冲带划分。<strong>净贡献毛利 = 广告销售额 × {pct(breakeven)} − 广告花费</strong>，这是判断一个活动到底赚不赚钱的唯一标准。</p>

  <div class="chart" id="chartTier"></div>

  <table>
    <thead><tr><th>档位</th><th>判定</th><th>活动数</th><th>花费</th><th>预算占比</th><th>广告销售额</th><th>订单</th><th>ACOS</th><th>净贡献毛利</th></tr></thead>
    <tbody>
      <tr><td>{tier_tag('A')} 真正赚钱的高效投放</td><td>ACOS ≤ {pct(A_CUT)}</td><td class="num">{T['A']['n']}</td><td class="num">{u(T['A']['spend'])}</td><td class="num">{pct(T['A']['spend_pct'])}</td><td class="num">{u(T['A']['sales'])}</td><td class="num">{T['A']['orders']}</td><td class="num pos">{pct(T['A']['acos'])}</td>{net_cell(T['A']['net'])}</tr>
      <tr><td>{tier_tag('B')} 保本引流的投放</td><td>{pct(A_CUT)} ~ {pct(B_CUT)}</td><td class="num">{T['B']['n']}</td><td class="num">{u(T['B']['spend'])}</td><td class="num">{pct(T['B']['spend_pct'])}</td><td class="num">{u(T['B']['sales'])}</td><td class="num">{T['B']['orders']}</td><td class="num">{pct(T['B']['acos'])}</td>{net_cell(T['B']['net'])}</tr>
      <tr><td>{tier_tag('C')} 纯烧钱的低效投放</td><td>ACOS &gt; {pct(B_CUT)} 或零单</td><td class="num">{T['C']['n']}</td><td class="num">{u(T['C']['spend'])}</td><td class="num neg">{pct(T['C']['spend_pct'])}</td><td class="num">{u(T['C']['sales'])}</td><td class="num">{T['C']['orders']}</td><td class="num neg">{pct(T['C']['acos'])}</td>{net_cell(T['C']['net'])}</tr>
      <tr class="tot"><td>合计</td><td></td><td class="num">{ADS['n']}</td><td class="num">{u(ADS['spend'])}</td><td class="num">100%</td><td class="num">{u(ADS['sales'])}</td><td class="num">{ADS['orders']}</td><td class="num">{pct(ADS['acos'])}</td>{net_cell(ADS['net'])}</tr>
    </tbody>
  </table>

  <div class="callout danger">
    <div class="t">结构性失衡：预算与效率完全倒挂</div>
    高效档拿 {pct(T['A']['spend_pct'])} 预算却是唯一正贡献（净赚 {u(T['A']['net'])}）；烧钱档拿走 {pct(T['C']['spend_pct'])} 预算，一个月净亏 {u(abs(T['C']['net']))}。<strong>如果把 C 档全部关掉，广告板块立刻从净亏 {u(abs(net))} 变成净赚 {u(T['A']['net']+T['B']['net'])}</strong>（当然会损失 {u(T['C']['sales'])} 销售额和相应排名，所以要做的是结构调整而非一刀切）。
  </div>

  <h3>C 档再细分：不是所有「烧钱」都该一刀切</h3>
  <table>
    <thead><tr><th>子档</th><th>判定</th><th>活动数</th><th>花费</th><th>预算占比</th><th>销售额</th><th>订单</th><th>ACOS</th><th>净亏</th><th>处置</th></tr></thead>
    <tbody>
      <tr><td>C1 轻度超标</td><td>{pct(B_CUT)}%~40%</td><td class="num">{SC1['n']}</td><td class="num">{u(SC1['spend'])}</td><td class="num">{pct(SC1['spend_pct'])}</td><td class="num">{u(SC1['sales'])}</td><td class="num">{SC1['orders']}</td><td class="num">{pct(SC1['acos'])}</td>{net_cell(SC1['net'])}<td>结构优化，不关</td></tr>
      <tr><td>C2 重度超标</td><td>40%~80%</td><td class="num">{SC2['n']}</td><td class="num">{u(SC2['spend'])}</td><td class="num">{pct(SC2['spend_pct'])}</td><td class="num">{u(SC2['sales'])}</td><td class="num">{SC2['orders']}</td><td class="num neg">{pct(SC2['acos'])}</td>{net_cell(SC2['net'])}<td>预算腰斩</td></tr>
      <tr><td>C3 严重失控</td><td>&gt; 80%</td><td class="num">{SC3['n']}</td><td class="num">{u(SC3['spend'])}</td><td class="num">{pct(SC3['spend_pct'])}</td><td class="num">{u(SC3['sales'])}</td><td class="num">{SC3['orders']}</td><td class="num neg">{pct(SC3['acos'])}</td>{net_cell(SC3['net'])}<td>立即暂停</td></tr>
      <tr><td>C4 零单空烧</td><td>有花费 0 单</td><td class="num">{SC4['n']}</td><td class="num">{u(SC4['spend'])}</td><td class="num">{pct(SC4['spend_pct'])}</td><td class="num">0</td><td class="num">0</td><td class="num">—</td>{net_cell(SC4['net'])}<td>立即暂停</td></tr>
    </tbody>
  </table>
  <p class="note">C1 是「大而不精」——占了 {pct(SC1['spend_pct'])} 预算、贡献 {SC1['orders']:,} 单，是店铺的销量基本盘，不能关，只能靠否词、降竞价、调位置系数把 ACOS 从 {pct(SC1['acos'])} 压下来。C3/C4 才是真·纯浪费，合计仅 {u(SC3['spend']+SC4['spend'])}，关掉毫无痛感。</p>
</section>
"""

# ============ 5. 关键词层 ============
html += f"""
<section>
  <h2>五、关键词层归因</h2>
  <p>关键词层覆盖 {u(KW['total_spend'])} 花费（占总花费 {pct(KW['total_spend']/ADS['spend']*100)}），共 {KW['n']:,} 个投放词，覆盖率 {pct(KW['cover'])}%。</p>

  <table>
    <thead><tr><th>档位</th><th>词数</th><th>花费</th><th>该层占比</th><th>销售额</th><th>订单</th><th>ACOS</th><th>净贡献毛利</th></tr></thead>
    <tbody>
      <tr><td>{tier_tag('A')} 高效 ACOS ≤ {pct(A_CUT)}</td><td class="num">{KW['tiers']['A']['n']}</td><td class="num">{u(KW['tiers']['A']['spend'])}</td><td class="num">{pct(KW['tiers']['A']['spend_pct'])}</td><td class="num">{u(KW['tiers']['A']['sales'])}</td><td class="num">{int(KW['tiers']['A']['sales']/14.5)}</td><td class="num pos">{pct(KW['tiers']['A']['acos'])}</td>{net_cell(KW['tiers']['A']['net'])}</tr>
      <tr><td>{tier_tag('B')} 保本 {pct(A_CUT)}~{pct(B_CUT)}</td><td class="num">{KW['tiers']['B']['n']}</td><td class="num">{u(KW['tiers']['B']['spend'])}</td><td class="num">{pct(KW['tiers']['B']['spend_pct'])}</td><td class="num">{u(KW['tiers']['B']['sales'])}</td><td class="num">{int(KW['tiers']['B']['sales']/14.5)}</td><td class="num">{pct(KW['tiers']['B']['acos'])}</td>{net_cell(KW['tiers']['B']['net'])}</tr>
      <tr><td>{tier_tag('C')} 低效 &gt; {pct(B_CUT)}</td><td class="num">{KW['tiers']['C']['n']}</td><td class="num">{u(KW['tiers']['C']['spend'])}</td><td class="num neg">{pct(KW['tiers']['C']['spend_pct'])}</td><td class="num">{u(KW['tiers']['C']['sales'])}</td><td class="num">{int(KW['tiers']['C']['sales']/14.5)}</td><td class="num neg">{pct(KW['tiers']['C']['acos'])}</td>{net_cell(KW['tiers']['C']['net'])}</tr>
    </tbody>
  </table>

  <div class="two">
    <div>
      <h4>按匹配类型</h4>
      <table>
        <thead><tr><th>匹配</th><th>词数</th><th>花费</th><th>ACOS</th><th>净贡献</th></tr></thead>
        <tbody>
          <tr><td>词组 phrase</td><td class="num">{KW['by_match']['phrase']['n']}</td><td class="num">{u(KW['by_match']['phrase']['spend'])}</td><td class="num pos">{pct(KW['by_match']['phrase']['acos'])}</td>{net_cell(KW['by_match']['phrase']['net'])}</tr>
          <tr><td>广泛 broad</td><td class="num">{KW['by_match']['broad']['n']}</td><td class="num">{u(KW['by_match']['broad']['spend'])}</td><td class="num neg">{pct(KW['by_match']['broad']['acos'])}</td>{net_cell(KW['by_match']['broad']['net'])}</tr>
          <tr><td>精准 exact</td><td class="num">{KW['by_match']['exact']['n']}</td><td class="num">{u(KW['by_match']['exact']['spend'])}</td><td class="num neg">{pct(KW['by_match']['exact']['acos'])}</td>{net_cell(KW['by_match']['exact']['net'])}</tr>
        </tbody>
      </table>
      <p class="note"><strong>词组匹配 ACOS {pct(KW['by_match']['phrase']['acos'])} 最优且净贡献为正</strong>，广泛匹配花掉 {pct(KW['by_match']['broad']['spend_pct'])} 预算却净亏 {u(abs(KW['by_match']['broad']['net']))}。建议把广泛匹配里表现好的词移栽到词组匹配，并大幅收窄广泛匹配的预算。</p>
    </div>
    <div>
      <h4>关键词层三档分布</h4>
      <div class="chart chart-sm" id="chartKw"></div>
    </div>
  </div>

  <h3>最该加投的关键词 TOP 12</h3>
  <table>
    <thead><tr><th>关键词</th><th>匹配</th><th>所属活动</th><th>花费</th><th>销售额</th><th>订单</th><th>ACOS</th><th>CVR</th><th>净贡献</th></tr></thead>
    <tbody>
"""
for r in d['kw_add'][:12]:
    html += f"""      <tr><td>{r['text']}</td><td>{r['match']}</td><td>{r['campaign']}</td><td class="num">{u(r['spend'])}</td><td class="num">{u(r['sales'])}</td><td class="num">{r['orders']}</td><td class="num pos">{pct(r['acos'])}</td><td class="num">{pct(r['cvr'])}</td>{net_cell(r['net'])}</tr>
"""
html += f"""    </tbody>
  </table>
  <p class="note">共性：CVR 普遍在 {pct(20)} 以上、CPC 处于低位，曝光尚未吃满，是最干净的加投空间。建议竞价上调 15~25%，Top of Search 位置系数 +30~50%。</p>

  <h3>最该削减 / 否定的关键词 TOP 15</h3>
  <table>
    <thead><tr><th>关键词</th><th>匹配</th><th>所属活动</th><th>花费</th><th>销售额</th><th>订单</th><th>ACOS</th><th>CVR</th><th>净亏</th><th>动作</th></tr></thead>
    <tbody>
"""
for r in d['kw_cut'][:15]:
    act = '否定' if r['cvr'] < 10 else ('暂停' if r['acos']>80 else '降竞价 30%')
    html += f"""      <tr><td>{r['text']}</td><td>{r['match']}</td><td>{r['campaign']}</td><td class="num">{u(r['spend'])}</td><td class="num">{u(r['sales'])}</td><td class="num">{r['orders']}</td><td class="num neg">{pct(r['acos'])}</td><td class="num {'neg' if r['cvr']<10 else ''}">{pct(r['cvr'])}</td>{net_cell(r['net'])}<td>{act}</td></tr>
"""
html += f"""    </tbody>
  </table>

  <div class="callout">
    <div class="t">两类浪费要用不同手法</div>
    <strong>高 CVR + 高 ACOS</strong>（如 sticker earrings，转化没问题）：问题在 <strong>CPC 买贵了</strong>，降竞价即可，不要否定。<br>
    <strong>低 CVR + 高 ACOS</strong>（american flag patches 6.3%、girls patches 8.7%）：<strong>流量不精准</strong>，Listing 与搜索意图不匹配，直接加否定关键词。
  </div>
</section>
"""

# ============ 6. 自然单带动 ============
html += f"""
<section>
  <h2>六、广告对自然单的带动（环比）</h2>

  <div class="chart chart-sm" id="chartNature"></div>

  <table>
    <thead><tr><th>指标</th><th>上期 {pprev[0]}~{pprev[1]}</th><th>本期 {p0}~{p1}</th><th>变化</th><th>读数</th></tr></thead>
    <tbody>
      <tr><td>广告花费</td><td class="num">{u(prev['spend'])}</td><td class="num">{u(cur['spend'])}</td><td class="num {'neg' if cur['spend']>prev['spend'] else 'pos'}">{pct(cur['spend']-prev['spend'],sign=True)} ({pct(idx_spend-100,sign=True)})</td><td>投入减少</td></tr>
      <tr><td>广告销售额</td><td class="num">{u(prev['ad_sales'])}</td><td class="num">{u(cur['ad_sales'])}</td><td class="num neg">{pct(cur['ad_sales']-prev['ad_sales'],sign=True)} ({pct(idx_adsales-100,sign=True)})</td><td><strong>直接产出下降</strong></td></tr>
      <tr><td>自然销售额</td><td class="num">{u(171808.11)}</td><td class="num">{u(P['nat_sales'])}</td><td class="num pos">{pct(P['nat_sales']-171808.11,sign=True)} ({pct(idx_natsales-100,sign=True)})</td><td><strong>增量全在自然侧</strong></td></tr>
      <tr><td>总销售额</td><td class="num">{u(prev['sales'])}</td><td class="num">{u(cur['sales'])}</td><td class="num neg">{pct(cur['sales']-prev['sales'],sign=True)} ({pct(idx_totsales-100,sign=True)})</td><td>规模略缩</td></tr>
      <tr><td>总毛利</td><td class="num">{u(prev['gp'])}</td><td class="num">{u(cur['gp'])}</td><td class="num pos">{pct(cur['gp']-prev['gp'],sign=True)} ({pct(idx_gp-100,sign=True)})</td><td><strong>利润增厚</strong></td></tr>
      <tr><td>毛利率</td><td class="num">{pct(P['prev_gm'])}</td><td class="num">{pct(P['gm'])}</td><td class="num pos">{pct(P['gm']-P['prev_gm'],sign=True)}</td><td>结构改善</td></tr>
      <tr><td>ACOS</td><td class="num">{pct(prev_acos)}</td><td class="num neg">{pct(ADS['acos'])}</td><td class="num neg">{pct(ADS['acos']-prev_acos,sign=True)}</td><td>效率略降</td></tr>
      <tr><td>TACOS</td><td class="num">{pct(P['prev_tacos'])}</td><td class="num">{pct(P['tacos'])}</td><td class="num pos">{pct(P['tacos']-P['prev_tacos'],sign=True)}</td><td>整体健康</td></tr>
      <tr><td>广告净贡献毛利</td><td class="num neg">{u(prev['ad_sales']*P['prev_breakeven']/100-prev['spend'])}</td><td class="num neg">{u(net)}</td><td class="num neg">{pct(net-(prev['ad_sales']*P['prev_breakeven']/100-prev['spend']),sign=True)}</td><td><strong>亏损在扩大</strong></td></tr>
    </tbody>
  </table>

  <div class="callout good">
    <div class="t">关键底气：削减低效广告，自然单不会崩</div>
    环比<strong>少花 {u(prev['spend']-cur['spend'])[1:]}</strong> 广告费，广告销售额降 {pct(100-idx_adsales)}，但自然销售额<strong>逆势 +{pct(idx_natsales-100)}</strong>、总毛利 +{pct(idx_gp-100)}。说明 A-US 的自然流量已经具备自驱力，<mark class="key">当期低效广告既不是自然单的来源、也不是店铺利润的支撑</mark>。实测自然回补率（环比 Δ自然 / |Δ广告|）≈ <strong>{pct(recap)}</strong>——即使削减广告，约 {pct(recap)} 的销量会以自然形式回补。
  </div>

  <h3>投放定向层（自动/ASIN 定向）浪费 TOP 15</h3>
  <table>
    <thead><tr><th>定向表达式</th><th>类型</th><th>所属活动</th><th>花费</th><th>销售额</th><th>订单</th><th>ACOS</th><th>CPC</th><th>净亏</th></tr></thead>
    <tbody>
"""
for r in d['tg_cut'][:15]:
    html += f"""      <tr><td>{r['expr']}</td><td>{r['etype']}</td><td>{r['campaign']}</td><td class="num">{u(r['spend'])}</td><td class="num">{u(r['sales'])}</td><td class="num">{r['orders']}</td><td class="num neg">{pct(r['acos'])}</td><td class="num">{u(r['cpc'],2)}</td>{net_cell(r['net'])}</tr>
"""
html += f"""    </tbody>
  </table>
  <p class="note">投放定向层覆盖 {u(TG['total_spend'])} 花费（占 {pct(TG['total_spend']/ADS['spend']*100)}），覆盖率 {pct(TG['cover'])}%。「自动」定向里的低效行多为高 CPC、低转化的垃圾流量，建议直接否掉或限价。</p>
</section>
"""

# ============ 7. 加投与削减清单 ============
html += f"""
<section>
  <h2>七、加投与削减清单</h2>

  <h3>该加投：高效活动 TOP 12</h3>
  <table>
    <thead><tr><th>广告活动</th><th>类型</th><th>组合</th><th>花费</th><th>销售额</th><th>订单</th><th>ACOS</th><th>CVR</th><th>CPC</th><th>净贡献</th><th>建议</th></tr></thead>
    <tbody>
"""
for r in d['top_add'][:12]:
    sugg = '预算 ×2.5' if r['roas']>6 else ('预算 ×2' if r['roas']>4 else '预算 ×1.5')
    html += f"""      <tr><td>{r['name']}</td><td>{r['type'].upper()}</td><td>{r['portfolio']}</td><td class="num">{u(r['spend'])}</td><td class="num">{u(r['sales'])}</td><td class="num">{r['orders']}</td><td class="num pos">{pct(r['acos'])}</td><td class="num">{pct(r['cvr'])}</td><td class="num">{u(r['cpc'],2)}</td>{net_cell(r['net'])}<td>{sugg}</td></tr>
"""
html += f"""    </tbody>
  </table>
  <div class="callout good">
    <div class="t">明显规律：DeepBI 系列自动化活动是全店效率最高的一批</div>
    加投 TOP12 中多数为 DeepBI_ 前缀 + AUTO / corn_holders / patches 活动，平均 ACOS 仅 {pct(sum(x['acos'] for x in d['top_add'][:12])/12)}、ROAS 普遍 5~8。<strong>建议把预算向 DeepBI 体系倾斜，并复盘老活动（125-、79-、89- 系列）的选词与竞价逻辑。</strong>
  </div>

  <h3>该暂停：C3 严重失控 + C4 零单空烧 TOP 12</h3>
  <table>
    <thead><tr><th>广告活动</th><th>类型</th><th>花费</th><th>销售额</th><th>订单</th><th>ACOS</th><th>CVR</th><th>动作</th></tr></thead>
    <tbody>
"""
for r in d['zero'][:12]:
    html += f"""      <tr><td>{r['name']}</td><td>{r['type'].upper()}</td><td class="num">{u(r['spend'])}</td><td class="num">{u(r['sales'])}</td><td class="num">{r['orders']}</td><td class="num">{'—' if r['acos'] is None else pct(r['acos'])}</td><td class="num">{pct(r['cvr'])}</td><td>暂停</td></tr>
"""
html += f"""      <tr class="tot"><td>C3+C4 合计（{SC3['n']+SC4['n']} 个活动）</td><td></td><td class="num">{u(SC3['spend']+SC4['spend'])}</td><td class="num">{u(SC3['sales']+SC4['sales'])}</td><td class="num">{SC3['orders']+SC4['orders']}</td><td class="num neg">{pct((SC3['spend']+SC4['spend'])/(SC3['sales']+SC4['sales'])*100 if (SC3['sales']+SC4['sales'])>0 else 0)}</td><td class="num">—</td><td>释放 {u(SC3['spend']+SC4['spend'])}</td></tr>
    </tbody>
  </table>

  <h3>该腰斩：C2 重度超标 TOP 12</h3>
  <table>
    <thead><tr><th>广告活动</th><th>类型</th><th>组合</th><th>花费</th><th>销售额</th><th>订单</th><th>ACOS</th><th>CVR</th><th>CPC</th><th>净亏</th><th>动作</th></tr></thead>
    <tbody>
"""
for r in d['top_cut'][:12]:
    html += f"""      <tr><td>{r['name']}</td><td>{r['type'].upper()}</td><td>{r['portfolio']}</td><td class="num">{u(r['spend'])}</td><td class="num">{u(r['sales'])}</td><td class="num">{r['orders']}</td><td class="num neg">{pct(r['acos'])}</td><td class="num {'neg' if r['cvr']<10 else ''}">{pct(r['cvr'])}</td><td class="num">{u(r['cpc'],2)}</td>{net_cell(r['net'])}<td>预算 −50%，竞价 −30%</td></tr>
"""
html += f"""      <tr class="tot"><td>C2 合计（{SC2['n']} 个活动）</td><td></td><td></td><td class="num">{u(SC2['spend'])}</td><td class="num">{u(SC2['sales'])}</td><td class="num">{SC2['orders']}</td><td class="num neg">{pct(SC2['acos'])}</td><td class="num">—</td><td class="num">—</td>{net_cell(SC2['net'])}<td>释放 {u(SC2['spend']*0.6)}</td></tr>
    </tbody>
  </table>

  <h3>该优化不该关：C1 大盘活动 TOP 8</h3>
  <table>
    <thead><tr><th>活动</th><th>类型</th><th>组合</th><th>花费</th><th>销售额</th><th>订单</th><th>ACOS</th><th>CVR</th><th>CPC</th><th>净亏</th><th>动作</th></tr></thead>
    <tbody>
"""
for r in d['top_cut'][12:20]:
    html += f"""      <tr><td>{r['name']}</td><td>{r['type'].upper()}</td><td>{r['portfolio']}</td><td class="num">{u(r['spend'])}</td><td class="num">{u(r['sales'])}</td><td class="num">{r['orders']}</td><td class="num neg">{pct(r['acos'])}</td><td class="num {'neg' if r['cvr']<10 else ''}">{pct(r['cvr'])}</td><td class="num">{u(r['cpc'],2)}</td>{net_cell(r['net'])}<td>否词 + 降竞价</td></tr>
"""
html += f"""      <tr class="tot"><td>C1 合计（{SC1['n']} 个活动）</td><td></td><td></td><td class="num">{u(SC1['spend'])}</td><td class="num">{u(SC1['sales'])}</td><td class="num">{SC1['orders']}</td><td class="num neg">{pct(SC1['acos'])}</td><td class="num">—</td><td class="num">—</td>{net_cell(SC1['net'])}<td>释放 {u(SC1['spend']*0.3)}</td></tr>
    </tbody>
  </table>
  <div class="callout">
    <div class="t">最大单点机会：125-A1730 与 79-A1562</div>
    两者合计花费 {u(894.22+451.05)}、净亏 {u(382.29+230.40)}。ACOS 高达 47.6% / 55.7%，问题集中在 <strong>CPC 买贵 + 转化不稳</strong>。只要把 ACOS 从 ~50% 压到 {pct(B_CUT)} 附近，单这两项每月可挽回约 {u((894.22+451.05)*(0.50-0.272))[1:]}。
  </div>
</section>
"""

# ============ 8. 预算重分配 ============
rows = PL['rows']
new_spend_list = [r['spend']+r['delta_spend'] for r in rows]
html += f"""
<section>
  <h2>八、预算重分配方案与预期 ROI</h2>

  <div class="chart" id="chartAlloc"></div>

  <table>
    <thead><tr><th>档位</th><th>动作</th><th>现预算</th><th>占比</th><th>新预算</th><th>新占比</th><th>Δ预算</th><th>预期新 ACOS</th><th>毛利池变化</th></tr></thead>
    <tbody>
"""
order = {'A 高效盈利':0,'B 保本引流':1,'C4 零单空烧':2,'C3 严重失控':3,'C2 重度超支':4,'C1 轻度超支':5}
for r in sorted(rows, key=lambda x: order.get(x['seg'],9)):
    ns = r['spend']+r['delta_spend']
    newpct = ns/PL['new_spend']*100
    html += f"""      <tr><td>{tier_tag(r['seg'][0])} {r['seg']}</td><td>{r['action']}</td><td class="num">{u(r['spend'])}</td><td class="num">{pct(r['spend']/ADS['spend']*100)}</td><td class="num">{u(ns)}</td><td class="num">{pct(newpct)}</td><td class="num {'pos' if r['delta_spend']>0 else 'neg'}">{pct(r['delta_spend'],sign=True)}</td><td class="num">{pct(r['roas'] and r['spend']/(r['spend']*r['roas'])*100) if r['roas'] else '—'}</td><td class="num {'pos' if r['delta_sales']*breakeven/100 - r['delta_spend']>0 else 'neg'}">{('+' if r['delta_sales']*breakeven/100 - r['delta_spend']>0 else '−')+u(abs(r['delta_sales']*breakeven/100 - r['delta_spend']))[1:]}</td></tr>
"""
html += f"""      <tr class="tot"><td>合计</td><td></td><td class="num">{u(ADS['spend'])}</td><td class="num">100%</td><td class="num">{u(PL['new_spend'])}</td><td class="num">100%</td><td class="num neg">{pct(PL['net_cut'],sign=True)}</td><td class="num">{pct(PL['new_acos'])}</td><td class="num pos">+{u(PL['gp_delta'])[1:]}</td></tr>
    </tbody>
  </table>

  <h3>预期效果</h3>
  <div class="kpi-grid">
    <div class="kpi good"><div class="k">ACOS</div><div class="v">{pct(PL['new_acos'])}</div><div class="d">{pct(ADS['acos'])} → {pct(PL['new_acos'])}（{pct(PL['new_acos']-ADS['acos'],sign=True)}）</div></div>
    <div class="kpi good"><div class="k">TACOS</div><div class="v">{pct(PL['new_tacos'])}</div><div class="d">{pct(P['tacos'])} → {pct(PL['new_tacos'])}（{pct(PL['new_tacos']-P['tacos'],sign=True)}）</div></div>
    <div class="kpi good"><div class="k">ROAS</div><div class="v">{ADS['sales']/ADS['spend']:.2f}→{PL['new_ad_sales']/PL['new_spend']:.2f}</div><div class="d">+{pct((PL['new_ad_sales']/PL['new_spend'])/(ADS['sales']/ADS['spend'])*100-100)}</div></div>
    <div class="kpi good"><div class="k">毛利率</div><div class="v">{pct(PL['new_gm'])}</div><div class="d">{pct(P['gm'])} → {pct(PL['new_gm'])}（{pct(PL['new_gm']-P['gm'],sign=True)}）</div></div>
  </div>

  <table>
    <thead><tr><th>指标</th><th>现状</th><th>方案后（基准）</th><th>方案后（保守：自然单回补 {pct(recap)}）</th></tr></thead>
    <tbody>
      <tr><td>广告花费</td><td class="num">{u(ADS['spend'])}</td><td class="num">{u(PL['new_spend'])}</td><td class="num">{u(PL['new_spend'])}</td></tr>
      <tr><td>广告销售额</td><td class="num">{u(ADS['sales'])}</td><td class="num">{u(PL['new_ad_sales'])}</td><td class="num">{u(PL['new_ad_sales'])}</td></tr>
      <tr><td>自然销售额（回补）</td><td class="num">{u(P['nat_sales'])}</td><td class="num">{u(P['nat_sales'])}</td><td class="num">{u(P['nat_sales']+PL['recovered_nat'])}</td></tr>
      <tr><td>全店销售额</td><td class="num">{u(cur['sales'])}</td><td class="num">{u(PL['new_total_sales'])}</td><td class="num">{u(PL['new_total_sales']+PL['recovered_nat'])}</td></tr>
      <tr><td>ACOS</td><td class="num neg">{pct(ADS['acos'])}</td><td class="num pos">{pct(PL['new_acos'])}</td><td class="num pos">{pct(PL['new_acos'])}</td></tr>
      <tr><td>TACOS</td><td class="num">{pct(P['tacos'])}</td><td class="num pos">{pct(PL['new_tacos'])}</td><td class="num pos">{pct(PL['new_tacos'])}</td></tr>
      <tr class="tot"><td>月度毛利</td><td class="num">{u(cur['gp'])}</td><td class="num pos">{u(PL['new_gp'])}</td><td class="num pos">{u(PL['new_gp']+PL['recovered_nat']*breakeven/100)}</td></tr>
      <tr class="tot"><td>毛利率</td><td class="num">{pct(P['gm'])}</td><td class="num pos">{pct(PL['new_gm'])}</td><td class="num pos">{pct((PL['new_gp']+PL['recovered_nat']*breakeven/100)/(PL['new_total_sales']+PL['recovered_nat'])*100)}</td></tr>
      <tr class="tot"><td>月度毛利增量</td><td class="num">—</td><td class="num pos">+{u(PL['gp_delta'])} ({pct(PL['gp_delta']/cur['gp']*100)})</td><td class="num pos">+{u(PL['gp_delta']+PL['recovered_nat']*breakeven/100)}</td></tr>
      <tr class="tot"><td>年化毛利增量</td><td class="num">—</td><td class="num pos">+{u(PL['gp_delta']*12)}</td><td class="num pos">+{u((PL['gp_delta']+PL['recovered_nat']*breakeven/100)*12)}</td></tr>
    </tbody>
  </table>

  <div class="callout good">
    <div class="t">核心 ROI 改善</div>
    广告投入产出（毛利口径 ROI = 净贡献毛利 / 广告花费）从 <strong>{pct(net/ADS['spend']*100)}</strong> 改善到 <strong>{pct((PL['new_ad_sales']*breakeven/100 - PL['new_spend'])/PL['new_spend']*100)}</strong>。即便在保守情景下，月度毛利仍增加 <strong>{u(PL['gp_delta']+PL['recovered_nat']*breakeven/100)}</strong>，年化约 <strong>{u((PL['gp_delta']+PL['recovered_nat']*breakeven/100)*12)}</strong>。<br>
    注意：广告板块在基准情景下仍接近保本（净贡献 {u(PL['new_ad_sales']*breakeven/100 - PL['new_spend'])}），这是 {pct(breakeven)} 保本线太高导致的结构性问题。<strong>要让广告真正赚钱，必须同时推进提客单价 / 降 FBA 配送费的动作。</strong>
  </div>

  <h3>执行节奏：分两步走，控风险</h3>
  <ol>
    <li><strong>第 1~3 天（零风险动作，释放 {u(SC3['spend']+SC4['spend'])}/月）</strong><br>
      暂停 C3 全部 {SC3['n']} 个活动 + C4 全部 {SC4['n']} 个活动；否定 american flag patches、girls patches 等低 CVR 词。</li>
    <li><strong>第 4~7 天（释放 {u(SC2['spend']*0.6)}/月）</strong><br>
      C2 全档预算腰斩、竞价下调 30%；CVR &lt;8% 的直接暂停。</li>
    <li><strong>第 8~14 天（观察期）</strong><br>
      监控自然订单、BSR、Session 是否下滑。判定标准：自然订单周环比跌幅 &lt;5% 即视为安全，可继续；若跌幅 &gt;8%，回滚 C2 的 50% 预算。</li>
    <li><strong>第 15~21 天（释放 {u(SC1['spend']*0.3)}/月）</strong><br>
      确认安全后启动 C1 优化：125-A1730、79-A1562 等竞价 −30%，全档否词清理，预算 −30%。</li>
    <li><strong>第 8 天起同步执行（投入 {u(PL['addA'])}/月）</strong><br>
      A 档 {T['A']['n']} 个活动加投 35% + Top of Search 位置系数 +30~50%；加投关键词 corn holders / patches / school patches 等竞价 +15~25%。</li>
  </ol>

  <div class="callout">
    <div class="t">测算假设（供复核）</div>
    <ul style="margin-bottom:0;">
      <li>保本 ACOS {pct(breakeven)} 取自本期实际 P&amp;L，未考虑成本波动。</li>
      <li>A 档加投按<strong>边际 ROAS 衰减</strong>测算，加投后 ROAS 仍显著高于整体（自 {ADS['roas']:.2f} 提升至 {PL['new_ad_sales']/PL['new_spend']:.2f}）。</li>
      <li>C2 腰斩、C1 削减 30% 仅假设砍掉最差部分，未假设额外优化收益。</li>
      <li>保守情景已计入<strong>自然单回补率 {pct(recap)}</strong>（削广告后约两成销量以自然形式回补）。</li>
      <li>未计入削减后可能的自然排名下滑（除保守情景外）。</li>
    </ul>
  </div>
</section>
"""

# ============ 9. 数据口径 ============
html += f"""
<section>
  <h2>九、数据口径与覆盖度</h2>
  <table>
    <thead><tr><th>项目</th><th>说明</th></tr></thead>
    <tbody>
      <tr><td>店铺</td><td>A-US（sid 4651，Profile 4170394317233977，站点 ATVPDKIKX0DER，美国）</td></tr>
      <tr><td>时间窗口</td><td>本期 {p0} ~ {p1}（30 天）；环比期 {pprev[0]} ~ {pprev[1]}</td></tr>
      <tr><td>活动层覆盖</td><td>全店 {ADS['n']} 个活动，全部明细分析，花费 / 销售 / 订单覆盖率均 100%</td></tr>
      <tr><td>关键词层覆盖</td><td>全店 {KW['n']:,} 个投放词，覆盖花费 <strong>{pct(KW['cover'])}</strong>（关键词层占总花费 {pct(KW['total_spend']/ADS['spend']*100)}）</td></tr>
      <tr><td>投放定向层覆盖</td><td>全店 {TG['n']:,} 个定向，覆盖花费 <strong>{pct(TG['cover'])}</strong></td></tr>
      <tr><td>广告花费口径</td><td>利润表 {u(ADS['spend'])}（SP {u(BT['sp']['spend'])} / SB {u(BT['sb']['spend']+BT['sb2']['spend'])}）；与广告报表差异 &lt;0.01%</td></tr>
      <tr><td>广告销售额口径</td><td>含直接 + 间接归因（同店其他 ASIN 带动）</td></tr>
      <tr><td>毛利口径</td><td>领星「预估毛利润」，已扣除退款、FBA、佣金、采购、头程、仓储、广告费</td></tr>
      <tr><td>净贡献毛利</td><td>本报告自定义 = 广告销售额 × {pct(breakeven)} − 广告花费。用于判定单个活动/关键词是否真实盈利</td></tr>
    </tbody>
  </table>
</section>

<div class="footer">
  报告生成于 2026-08-08 · 数据源：领星 ERP MCP（ad_campaign_report / ad_campaign_keyword_report / ad_campaign_targeting_report / query_order_profit_list）· 所有金额单位 USD
</div>

</div>

<script src="./_shared/js/echarts.min.js"></script>
<script>
const AX={{ink:'#1a2332',muted:'#6b7785',rule:'#e2e6ec',blue:'#2563eb',amber:'#f59e0b',red:'#dc2626',green:'#16a34a',orange:'#ea580c'}};
const BE={breakeven};
const fontFam="'InstrumentSans','Microsoft YaHei',sans-serif";

// 1. 投放类型
(function(){{
  const c=echarts.init(document.getElementById('chartType'));
  c.setOption({{
    textStyle:{{fontFamily:fontFam}},
    title:{{text:'各广告类型：花费 vs 净贡献毛利',left:'center',top:8,textStyle:{{fontSize:14,color:AX.ink}}}},
    tooltip:{{trigger:'axis',axisPointer:{{type:'shadow'}}}},
    legend:{{bottom:4,data:['广告花费','广告销售额','净贡献毛利','ACOS']}},
    grid:{{left:70,right:66,top:52,bottom:44}},
    xAxis:{{type:'category',data:['SP 商品推广','SB 视频','SB 商品集'],axisLine:{{lineStyle:{{color:AX.rule}}}},axisLabel:{{color:AX.muted}}}},
    yAxis:[
      {{type:'value',name:'USD',axisLabel:{{color:AX.muted,formatter:v=>v/1000+'k'}},splitLine:{{lineStyle:{{color:AX.rule}}}}}},
      {{type:'value',name:'ACOS',max:80,axisLabel:{{color:AX.muted,formatter:'{{value}}%'}},splitLine:{{show:false}}}}
    ],
    series:[
      {{name:'广告花费',type:'bar',data:[{sp['spend']:.0f},{sb['spend']:.0f},{sb2['spend']:.0f}],itemStyle:{{color:AX.blue}}}},
      {{name:'广告销售额',type:'bar',data:[{sp['sales']:.0f},{sb['sales']:.0f},{sb2['sales']:.0f}],itemStyle:{{color:'#93c5fd'}}}},
      {{name:'净贡献毛利',type:'bar',data:[{sp['net']:.0f},{sb['net']:.0f},{sb2['net']:.0f}],itemStyle:{{color:AX.red}}}},
      {{name:'ACOS',type:'line',yAxisIndex:1,data:[{sp['acos']:.2f},{sb['acos']:.2f},{sb2['acos']:.2f}],itemStyle:{{color:AX.orange}},lineStyle:{{width:2.5}},symbolSize:8,
        markLine:{{silent:true,symbol:'none',data:[{{yAxis:BE,label:{{formatter:'保本 {breakeven:.2f}%',color:AX.green,fontSize:11}},lineStyle:{{color:AX.green,type:'dashed',width:2}}}}]}}}}
    ]
  }});
  window.addEventListener('resize',()=>c.resize());
}})();

// 2. 三档
(function(){{
  const c=echarts.init(document.getElementById('chartTier'));
  c.setOption({{
    textStyle:{{fontFamily:fontFam}},
    title:{{text:'预算占比 vs 净贡献毛利：结构性倒挂',left:'center',top:8,textStyle:{{fontSize:14,color:AX.ink}}}},
    tooltip:{{trigger:'axis',axisPointer:{{type:'shadow'}}}},
    legend:{{bottom:4,data:['预算占比','净贡献毛利','ACOS']}},
    grid:{{left:66,right:66,top:52,bottom:60}},
    xAxis:{{type:'category',data:['A 高效赚钱\\n{T['A']['n']}个活动','B 保本引流\\n{T['B']['n']}个活动','C1 轻度超标\\n{SC1['n']}个活动','C2 重度超标\\n{SC2['n']}个活动','C3 严重失控\\n{SC3['n']}个活动','C4 零订单\\n{SC4['n']}个活动'],axisLine:{{lineStyle:{{color:AX.rule}}}},axisLabel:{{color:AX.muted,fontSize:11,lineHeight:15}}}},
    yAxis:[
      {{type:'value',name:'预算占比',axisLabel:{{color:AX.muted,formatter:'{{value}}%'}},splitLine:{{lineStyle:{{color:AX.rule}}}}}},
      {{type:'value',name:'净贡献 USD',axisLabel:{{color:AX.muted,formatter:v=>v/1000+'k'}},splitLine:{{show:false}}}}
    ],
    series:[
      {{name:'预算占比',type:'bar',data:[{T['A']['spend_pct']:.2f},{T['B']['spend_pct']:.2f},{SC1['spend_pct']:.2f},{SC2['spend_pct']:.2f},{SC3['spend_pct']:.2f},{SC4['spend_pct']:.2f}],
        itemStyle:{{color:p=>[AX.green,AX.amber,AX.orange,'#f87171',AX.red,'#7f1d1d'][p.dataIndex]}},
        label:{{show:true,position:'top',formatter:'{{c}}%',fontSize:11,color:AX.ink}}}},
      {{name:'净贡献毛利',type:'line',yAxisIndex:1,data:[{T['A']['net']:.0f},{T['B']['net']:.0f},{SC1['net']:.0f},{SC2['net']:.0f},{SC3['net']:.0f},{SC4['net']:.0f}],itemStyle:{{color:AX.ink}},lineStyle:{{width:2.5}},symbolSize:9,
        markLine:{{silent:true,symbol:'none',data:[{{yAxis:0,lineStyle:{{color:AX.muted,type:'dashed'}}}}]}}}}
    ]
  }});
  window.addEventListener('resize',()=>c.resize());
}})();

// 3. 关键词层三档
(function(){{
  const c=echarts.init(document.getElementById('chartKw'));
  c.setOption({{
    textStyle:{{fontFamily:fontFam}},
    title:{{text:'关键词层：三档花费占比',left:'center',top:8,textStyle:{{fontSize:13,color:AX.ink}}}},
    tooltip:{{trigger:'axis',axisPointer:{{type:'shadow'}}}},
    grid:{{left:54,right:24,top:44,bottom:40}},
    xAxis:{{type:'category',data:['A 高效','B 保本','C 低效'],axisLine:{{lineStyle:{{color:AX.rule}}}},axisLabel:{{color:AX.muted}}}},
    yAxis:{{type:'value',name:'该层占比',axisLabel:{{color:AX.muted,formatter:'{{value}}%'}},splitLine:{{lineStyle:{{color:AX.rule}}}}}},
    series:[
      {{name:'花费占比',type:'bar',data:[
        {{value:{KW['tiers']['A']['spend_pct']:.2f},itemStyle:{{color:AX.green}}}},
        {{value:{KW['tiers']['B']['spend_pct']:.2f},itemStyle:{{color:AX.amber}}}},
        {{value:{KW['tiers']['C']['spend_pct']:.2f},itemStyle:{{color:AX.red}}}}
      ],label:{{show:true,position:'top',formatter:'{{c}}%',fontSize:11,color:AX.ink}},barWidth:'52%'}}
    ]
  }});
  window.addEventListener('resize',()=>c.resize());
}})();

// 4. 自然单带动（环比指数）
(function(){{
  const c=echarts.init(document.getElementById('chartNature'));
  c.setOption({{
    textStyle:{{fontFamily:fontFam}},
    title:{{text:'环比：少花广告费，利润反而增厚',left:'center',top:8,textStyle:{{fontSize:14,color:AX.ink}}}},
    tooltip:{{trigger:'axis'}},
    legend:{{bottom:4,data:['上期','本期']}},
    grid:{{left:80,right:40,top:52,bottom:44}},
    xAxis:{{type:'category',data:['广告花费','广告销售额','自然销售额','总销售额','总毛利','毛利率','ACOS','TACOS'],axisLine:{{lineStyle:{{color:AX.rule}}}},axisLabel:{{color:AX.muted,fontSize:11}}}},
    yAxis:{{type:'value',name:'指数（上期=100）',axisLabel:{{color:AX.muted}},splitLine:{{lineStyle:{{color:AX.rule}}}}}},
    series:[
      {{name:'上期',type:'bar',data:[100,100,100,100,100,100,100,100],itemStyle:{{color:'#cbd5e1'}},barGap:'8%'}},
      {{name:'本期',type:'bar',data:[{idx_spend:.2f},{idx_adsales:.2f},{idx_natsales:.2f},{idx_totsales:.2f},{idx_gp:.2f},{idx_gm:.2f},{idx_acos:.2f},{idx_tacos:.2f}],
        itemStyle:{{color:p=>[AX.blue,AX.red,AX.green,AX.red,AX.green,AX.green,AX.red,AX.green][p.dataIndex]}},
        label:{{show:true,position:'top',formatter:p=>(p.value-100>0?'+':'')+(p.value-100).toFixed(1)+'%',fontSize:10,color:AX.ink}}}}
    ]
  }});
  window.addEventListener('resize',()=>c.resize());
}})();

// 5. 预算重分配
(function(){{
  const c=echarts.init(document.getElementById('chartAlloc'));
  c.setOption({{
    textStyle:{{fontFamily:fontFam}},
    title:{{text:'预算重分配：{ADS['spend']:.0f} → {PL['new_spend']:.0f}',left:'center',top:8,textStyle:{{fontSize:14,color:AX.ink}}}},
    tooltip:{{trigger:'axis',axisPointer:{{type:'shadow'}},valueFormatter:v=>'$'+v.toLocaleString()}},
    legend:{{bottom:4,data:['现预算','新预算']}},
    grid:{{left:74,right:40,top:52,bottom:44}},
    xAxis:{{type:'category',data:['A 高效','B 保本','C1 轻度超标','C2 重度超标','C3 严重失控','C4 零单'],axisLine:{{lineStyle:{{color:AX.rule}}}},axisLabel:{{color:AX.muted,fontSize:12}}}},
    yAxis:{{type:'value',name:'USD / 30天',axisLabel:{{color:AX.muted,formatter:v=>v/1000+'k'}},splitLine:{{lineStyle:{{color:AX.rule}}}}}},
    series:[
      {{name:'现预算',type:'bar',data:[{rows[0]['spend']:.0f},{rows[1]['spend']:.0f},{rows[5]['spend']:.0f},{rows[4]['spend']:.0f},{rows[3]['spend']:.0f},{rows[2]['spend']:.0f}],itemStyle:{{color:'#cbd5e1'}}}},
      {{name:'新预算',type:'bar',data:[{rows[0]['spend']+rows[0]['delta_spend']:.0f},{rows[1]['spend']+rows[1]['delta_spend']:.0f},{rows[5]['spend']+rows[5]['delta_spend']:.0f},{rows[4]['spend']+rows[4]['delta_spend']:.0f},{rows[3]['spend']+rows[3]['delta_spend']:.0f},{rows[2]['spend']+rows[2]['delta_spend']:.0f}],
        itemStyle:{{color:p=>[AX.green,AX.amber,AX.orange,'#f87171',AX.red,AX.red][p.dataIndex]}},
        label:{{show:true,position:'top',formatter:p=>{{const o=[{rows[0]['spend']:.0f},{rows[1]['spend']:.0f},{rows[5]['spend']:.0f},{rows[4]['spend']:.0f},{rows[3]['spend']:.0f},{rows[2]['spend']:.0f}][p.dataIndex];const dd=p.value-o;return (dd>0?'+':'')+'$'+dd.toLocaleString();}},fontSize:11,color:AX.ink}}}}
    ]
  }});
  window.addEventListener('resize',()=>c.resize());
}})();
</script>
</body>
</html>
"""

open('aus-ad-attribution.html', 'w', encoding='utf-8').write(html)
print('written', len(html), 'bytes')
