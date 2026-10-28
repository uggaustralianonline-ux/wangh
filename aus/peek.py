import json
r = json.load(open('result.json', encoding='utf-8'))
fa = lambda x: (f"{x:.1f}%" if x else "零单")

print('=== 最该加投 TOP12 (A档) ===')
for c in r['top_add'][:12]:
    print(f"{c['name'][:34]:36s} {c['type']:4s} 日预算${c['budget']:>6.2f} 花费${c['spend']:>8.2f} "
          f"销售${c['sales']:>9.2f} ACOS {c['acos']:>6.2f}% ROAS {c['roas']:>5.2f} 净${c['net']:>8.2f}")

print('\n=== 最该削减 TOP15 (C档) ===')
for c in r['top_cut'][:15]:
    print(f"{c['name'][:34]:36s} {c['type']:4s} {c['sub'][:2]:3s} 日预算${c['budget']:>6.2f} "
          f"花费${c['spend']:>8.2f} 销售${c['sales']:>9.2f} ACOS {fa(c['acos']):>8s} 净${c['net']:>8.2f}")

print('\n=== 零单空烧 TOP10 ===')
for c in r['zero'][:10]:
    print(f"{c['name'][:34]:36s} 花费${c['spend']:>7.2f} 点击{c['clicks']:>5d} 曝光{c['impr']:>8d} 状态 {c['state']}")

print('\n=== 广告组合 TOP12 ===')
for k, v in list(r['by_portfolio'].items())[:12]:
    print(f"{k[:16]:18s} 花费${v['spend']:>9,.0f} 占{v['spend_pct']:>5.2f}% ACOS {fa(v['acos']):>7s} "
          f"净${v['net']:>9,.0f} | A${v['tierA']:>7,.0f} B${v['tierB']:>7,.0f} C${v['tierC']:>7,.0f}")

print('\n=== 关键词 最该加投 TOP10 ===')
for k in r['kw_add'][:10]:
    print(f"{(k['text'] or '')[:38]:40s} {k['match']:7s} 花费${k['spend']:>7.2f} 销售${k['sales']:>8.2f} "
          f"ACOS {k['acos']:>6.2f}% 净${k['net']:>7.2f}")

print('\n=== 关键词 最该削减 TOP12 ===')
for k in r['kw_cut'][:12]:
    print(f"{(k['text'] or '')[:38]:40s} {k['match']:7s} 花费${k['spend']:>7.2f} 销售${k['sales']:>8.2f} "
          f"ACOS {fa(k['acos']):>8s} 净${k['net']:>7.2f} bid${k['bid']:.2f}")

print('\n=== 商品/自动定向 最该削减 TOP10 ===')
for t in r['tg_cut'][:10]:
    print(f"{str(t['expr'])[:26]:28s} {t['campaign'][:24]:26s} 花费${t['spend']:>7.2f} "
          f"销售${t['sales']:>8.2f} ACOS {fa(t['acos']):>8s} 净${t['net']:>7.2f}")
