"""
分页拉取 N-US 店铺近30天搜索词报告（关键词级）
每页 200 条，拉满全部记录，保存为 search_term_all.json
用法：python fetch_searchterm.py
"""
import json, time, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 复用 parse_mcp 的解析逻辑
def load_mcp_text(path):
    raw = open(path, encoding='utf-8-sig').read()
    if raw.startswith('\n'):
        raw = raw[1:]
    if raw.startswith('The MCP server responded with: '):
        raw = raw[len('The MCP server responded with: '):]
    raw = raw.strip()
    arr = json.loads(raw)
    texts = [x.get('text','') for x in arr if x.get('type')=='text']
    return json.loads(texts[0])

# 因为 MCP 工具需要通过 run_mcp 调用，这里我们在 shell 中调用
# 本脚本负责把各页合并并保存
# 实际拉取通过 shell 中的 for 循环 + curl 做不到，改用 python 直接通过 subprocess 多次调用 mcp
# 更简单：把数据已经在 MCP 输出文件中，这里只负责合并
if __name__ == '__main__':
    pass
