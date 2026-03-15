import json
with open('raw_llm_response.txt', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('{')
end = text.rfind('}')
text = text[start:end+1]

try:
    json.loads(text)
    print("Success")
except json.JSONDecodeError as e:
    print(f"Error: {e}")
    if hasattr(e, 'pos'):
        pos = e.pos
        print(repr(text[max(0, pos-40):pos+40]))
