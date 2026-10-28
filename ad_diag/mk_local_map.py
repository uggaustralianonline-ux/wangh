import json, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

skus = json.load(open('ad_skus.json', encoding='utf-8'))
# localSku = msku minus the -Nnnnn vendor suffix mapping.
# msku pattern: {localSku}-N{num}  e.g. 326-N4118 -> local 326-4118,  89-12533-N -> 89-12533
def to_local(msku):
    # remove trailing -N<digits>
    m = re.match(r'^(.*)-N(\d+)$', msku)
    if m:
        return m.group(1) + '-' + m.group(2)
    # remove trailing -N
    m = re.match(r'^(.*)-N$', msku)
    if m:
        return m.group(1)
    # case 89-12533-N
    m = re.match(r'^(.*)-N$', msku)
    if m:
        return m.group(1)
    return msku

pairs = {}
for s in skus:
    pairs[s] = to_local(s)
print('total', len(skus))
for s in skus[:20]:
    print(s, '->', pairs[s])
json.dump(pairs, open('msku_local_map.json','w',encoding='utf-8'), ensure_ascii=False)