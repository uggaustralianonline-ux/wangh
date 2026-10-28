import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_mcp(path):
    raw = open(path, encoding='utf-8').read()
    if raw.startswith('\n'):
        raw = raw[1:]
    if raw.endswith('\n'):
        raw = raw[:-1]
    if raw.startswith('The MCP server responded with: '):
        raw = raw[len('The MCP server responded with: '):]
    # raw should be [{"type":"text","text":"{...json...}"}]
    arr = json.loads(raw)
    texts = [x.get('text','') for x in arr if x.get('type')=='text']
    inner = json.loads(texts[0])  # text is itself a JSON string
    return inner

if __name__ == '__main__':
    path = sys.argv[1]
    inner = load_mcp(path)
    print(json.dumps(inner, ensure_ascii=False)[:3000])