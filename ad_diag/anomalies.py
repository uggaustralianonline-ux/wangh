import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

merged = json.load(open('analysis_merged.json', encoding='utf-8'))

print("=== 断货风险 SKU（库存低但仍在大力投广告）===")
print(f"{'SKU':<16}{'花费':>8}{'广告销':>8}{'库存':>7}{'ACOS':>8}{'CVR':>7}")
for r in merged:
    if r['stock'] <= 40 and r['spend'] >= 30:
        acos = f"{r['acos']:.1f}%" if r.get('acos') is not None else '-'
        cvr = f"{r['cvr']:.1f}%" if r.get('cvr') is not None else '-'
        print(f"{r['sku']:<16}{r['spend']:>8.0f}{r['ad_sales']:>8.0f}{r['stock']:>7.0f}{acos:>8}{cvr:>7}")

print()
print("=== 零库存仍在投广告 ===")
for r in merged:
    if r['stock'] == 0 and r['spend'] > 0:
        print(f"{r['sku']:<16} 花费={r['spend']:.0f} 库存={r['stock']:.0f}")

print()
print("=== 滞销烧钱（ACOS过高且无/低转化）===")
print(f"{'SKU':<16}{'花费':>8}{'广告销':>8}{'库存':>7}{'ACOS':>8}{'订单':>6}{'CVR':>7}")
for r in merged:
    if r['acos'] is not None and r['acos'] > 80 and r['spend'] >= 15:
        cvr = f"{r['cvr']:.1f}%" if r.get('cvr') is not None else '-'
        print(f"{r['sku']:<16}{r['spend']:>8.0f}{r['ad_sales']:>8.0f}{r['stock']:>7.0f}{r['acos']:>7.1f}%{r['orders']:>6.0f}{cvr:>7}")

print()
print("=== 假赚钱 SKU（广告费 >= 2x 净利）===")
print(f"{'SKU':<16}{'花费':>8}{'净利':>8}{'广告费/净利':>12}{'ACOS':>8}{'TACOS':>8}")
for r in merged:
    if r.get('ad_share_of_profit') is not None and r['ad_share_of_profit'] >= 2.0 and r['gross_profit'] > 0:
        print(f"{r['sku']:<16}{r['spend']:>8.0f}{r['gross_profit']:>8.0f}{r['ad_share_of_profit']:>11.2f}x{r['acos']:>7.1f}%{r['tacos']:>7.1f}%")

print()
print("=== 亏损 SKU（净利为负）===")
for r in merged:
    if r.get('gross_profit') is not None and r['gross_profit'] < 0:
        print(f"{r['sku']:<16} 花费={r['spend']:.0f} 净利={r['gross_profit']:.0f} ACOS={r['acos']:.1f}% 库存={r['stock']:.0f}")