# Getting Started

## Prerequisites

- Python 3.10+
- Git
- An OpenAI or Anthropic API key (for agent integration)

---

## 1. Clone the Repository

```bash
git clone https://github.com/clovesnascimento/etemenanqui.git
cd etemenanqui
```

---

## 2. Install Dependencies

```bash
pip install openai          # agent integration
pip install "mcp[cli]"      # MCP server
pip install pydantic        # MCP validation
```

---

## 3. Your First Compression

```python
from etemenanqui_translator import traduzir_para_et

result = traduzir_para_et(
    "Initialize system. Validate all tokens. Generate report.",
    retornar_resultado=True
)

print(result.etemenanqui)    # ran sis . ven toka me . ner resa .
print(result.ratio)          # 0.286
print(result.cobertura)      # 75.0 %
```

---

## 4. Inject into an LLM

```python
from etemenanqui_translator import construir_system_prompt, traduzir_para_et
import openai

client = openai.OpenAI(api_key="sk-...")
system = construir_system_prompt()
prompt = traduzir_para_et("Initialize context. Validate tokens. Return result.")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system},
        {"role": "user",   "content": prompt},
    ]
)
print(response.choices[0].message.content)
```

---

## 5. Run the MCP Server

```bash
# stdio — for Claude Desktop and local agents
python etemenanqui_mcp_server.py

# HTTP — for remote agents
python etemenanqui_mcp_server.py --transport http --port 8000

# Inspect all tools
npx @modelcontextprotocol/inspector python etemenanqui_mcp_server.py
```

---

## 6. Claude Desktop Integration

Add to `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "etemenanqui": {
      "command": "python",
      "args": ["/path/to/etemenanqui/etemenanqui_mcp_server.py"]
    }
  }
}
```

---

## 7. Run Semantic Evaluation

```bash
# Review the 15-case test suite (no API calls)
python etemenanqui_eval.py --mode dry

# Full automatic evaluation
python etemenanqui_eval.py --mode auto --provider openai --key sk-...
```

Target score: **≥ 0.85** for production deployment.

---

*Next: [[Model-B-Specification]]*
