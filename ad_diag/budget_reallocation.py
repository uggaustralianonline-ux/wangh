"""
预算重分配方案与预期 ROI 改善测算
输入：attribution.json
输出：budget_reallocation.json
"""
import json, io, sys
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

attr = json.load(open('attribution.json', encoding='utf-8'))
camps = attr['campaigns']
total_sp = attr['total_spends']
total_sa = attr['total_sales']

# 筛选有利润数据的活动（排除"未知"类）
known = [c for c in camps if c['category'] in ('高效','保本','低效')]
unknown = [c for c in camps if c['category'] == '未知']

# 1. 可释放预算来源
cut_candidates = [c for c in camps if c['category'] == '低效' and c['spends'] > 50]
cut_candidates.sort(key=lambda r: r['spends'], reverse=True)

# 低效活动按比例削减 60% 预算
cut_ratio = 0.60
released = sum(c['spends'] * cut_ratio for c in cut_candidates)

# 2. 加投目标：高效活动（ROAS 前的），按现有 ROAS 等比加投
grow_candidates = [c for c in camps if c['category'] == '高效' and c['spends'] > 20]
grow_candidates.sort(key=lambda r: r['roas'] or 0, reverse=True)

# 加投额度（高效活动按 roas 加权分配释放预算）
grow_budget = released
total_roas = sum(c['roas'] for c in grow_candidates if c.get('roas'))
grow_alloc = []
for c in grow_candidates[:20]:
    if c.get('roas') and total_roas:
        share = c['roas'] / total_roas
        add = grow_budget * share
    else:
        add = 0
    grow_alloc.append({
        'campaign_name': c['campaign_name'],
        'current_spend': c['spends'],
        'roas': c['roas'],
        'acos': c['acos'],
        'gross_profit': c.get('gross_profit'),
        'add_budget': add,
        'expected_add_sales': add * c['roas'] if c.get('roas') else 0,
    })

# 3. 预期改善测算
cut_spend = released
cut_sales_loss = sum(c['sales'] * cut_ratio for c in cut_candidates)  # 销售额损失
cut_profit_loss = sum(max(0, (c.get('gross_profit') or 0)) * cut_ratio * 0.3 for c in cut_candidates)  # 假设利润损失约为削减带来的净利影响的30%（考虑节省广告费）

grow_add_spend = sum(g['add_budget'] for g in grow_alloc)
grow_add_sales = sum(g['expected_add_sales'] for g in grow_alloc)
# 假设高效活动保持当前利润率，加投带来的利润增量
# 用广告费/净利比反推：高效活动平均 share ~ 0.3x，即利润 = spend / 0.3
avg_share_eff = 0.3
grow_add_profit = grow_add_spend / avg_share_eff * 0.7  # 打7折保守估计

# 整体改善
new_total_spend = total_sp - cut_spend + grow_add_spend
new_total_sales = total_sa - cut_sales_loss + grow_add_sales
new_acos = new_total_spend / new_total_sales * 100 if new_total_sales else 0
current_acos = total_sp / total_sa * 100

# 净利润改善 = 节省的广告费 + 加投带来的利润增量 - 低效活动削减带来的利润损失
net_profit_improve = cut_spend + grow_add_profit - cut_profit_loss

print('=== 预算重分配方案 ===')
print(f'当前总广告花费: ${total_sp:,.2f}')
print(f'当前总广告销售额: ${total_sa:,.2f}')
print(f'当前综合 ACOS: {current_acos:.2f}%')
print()
print(f'--- 削减端（低效活动削减 {cut_ratio*100:.0f}% 预算）---')
print(f'涉及低效活动数: {len(cut_candidates)}')
print(f'释放预算: ${released:,.2f}')
print(f'预计销售额减少: ${cut_sales_loss:,.2f}')
print(f'预计利润损失（保守）: ${cut_profit_loss:,.2f}')
print()
print(f'--- 加投端（高效活动按 ROAS 加权分配）---')
print(f'涉及高效活动数: {min(len(grow_candidates),20)}')
print(f'加投预算: ${grow_add_spend:,.2f}')
print(f'预计新增销售额: ${grow_add_sales:,.2f}')
print(f'预计新增利润（保守）: ${grow_add_profit:,.2f}')
print()
print('--- 整体预期改善 ---')
print(f'新总花费: ${new_total_spend:,.2f} ({new_total_spend/total_sp*100:.1f}% of current)')
print(f'新总销售额: ${new_total_sales:,.2f} ({new_total_sales/total_sa*100:.1f}% of current)')
print(f'新综合 ACOS: {new_acos:.2f}% (改善 {(current_acos-new_acos):.2f}pp)')
print(f'净利改善: ${net_profit_improve:,.2f}')
print(f'净 ROI 改善率: {net_profit_improve/total_sp*100:.1f}% (相对于当前广告花费)')

print()
print('=== TOP 10 重点削减活动 ===')
for c in cut_candidates[:10]:
    cut = c['spends'] * cut_ratio
    gp = c.get('gross_profit')
    print(f"  {c['campaign_name'][:36]:<38} 当前${c['spends']:>7.0f} → 削减${cut:>7.0f}  ACOS={c['acos']:.1f}%  净利={'$'+str(gp) if gp is not None else 'N/A'}")

print()
print('=== TOP 10 重点加投活动 ===')
for g in grow_alloc[:10]:
    print(f"  {g['campaign_name'][:36]:<38} 当前${g['current_spend']:>7.0f} → 加投${g['add_budget']:>7.0f}  ROAS={g['roas']:.2f}  ACOS={g['acos']:.1f}%")

# 保存
result = {
    'current': {
        'total_spend': total_sp,
        'total_sales': total_sa,
        'acos': current_acos,
    },
    'cuts': {
        'count': len(cut_candidates),
        'ratio': cut_ratio,
        'released_budget': released,
        'sales_loss': cut_sales_loss,
        'profit_loss': cut_profit_loss,
        'top_cuts': cut_candidates[:20],
    },
    'grows': {
        'count': len(grow_alloc),
        'add_budget': grow_add_spend,
        'add_sales': grow_add_sales,
        'add_profit': grow_add_profit,
        'top_grows': grow_alloc,
    },
    'projected': {
        'total_spend': new_total_spend,
        'total_sales': new_total_sales,
        'acos': new_acos,
        'net_profit_improve': net_profit_improve,
        'roi_improve_pct': net_profit_improve/total_sp*100,
    }
}
json.dump(result, open('budget_reallocation.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'\n已保存 budget_reallocation.json')