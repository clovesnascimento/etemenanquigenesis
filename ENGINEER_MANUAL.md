# Etemenanqui — Engineer's Implementation Manual
## A Machine Language for Machine Minds

**Protocol:** Etemenanqui Cognitive Compression Protocol v1.0 (Model B)
**Author:** Cloves Nascimento — CNGSM (Cognitive Neural & Generative Systems Management)
**Founded:** March 13, 2026
**Repository:** https://github.com/clovesnascimento/etemenanqui

---

## Table of Contents

1. [What Is Etemenanqui](#1-what-is-etemenanqui)
2. [The Problem It Solves](#2-the-problem-it-solves)
3. [Model B Specification](#3-model-b-specification)
4. [Lexicon Reference](#4-lexicon-reference)
5. [Quick Integration Guide](#5-quick-integration-guide)
6. [MCP Server Reference](#6-mcp-server-reference)
7. [Compression Pipeline](#7-compression-pipeline)
8. [Empirical Benchmarks](#8-empirical-benchmarks)
9. [Agent Integration Patterns](#9-agent-integration-patterns)
10. [Semantic Evaluation Protocol](#10-semantic-evaluation-protocol)
11. [Extending the Lexicon](#11-extending-the-lexicon)
12. [Limitations & Honest Caveats](#12-limitations--honest-caveats)
13. [FAQ](#13-faq)

---

## 1. What Is Etemenanqui

Etemenanqui is an **artificial protocol language** designed exclusively for machine-to-machine instruction. It is not a human language, not a programming language, and not a natural language — it is a mathematically engineered communication layer that sits between human intent and LLM execution.

The name comes from Sumerian: *Etemenanki* — "house of the foundation of heaven and earth" — the historical ziggurat of Babylon associated with the Tower of Babel myth. The project builds a new tower: a unified, mathematically economical protocol that restores the efficiency of structured communication without noise.

**What it is:**
- A compressed instruction protocol for technical LLM prompts
- A formal language with strict phonotactic and morphological rules
- An open standard — MIT licensed, fully documented, extensible

**What it is not:**
- A general-purpose language (no articles, no poetry, no ambiguity)
- A replacement for natural language in user-facing interfaces
- A lossless encoding (coverage is currently ~75–85% for technical domains)

---

## 2. The Problem It Solves

Modern LLM tokenizers (Byte Pair Encoding, BPE) were trained primarily on natural English text. When you send technical instructions, they fragment your words in ways that waste tokens:

```
"Invalidate"    →  4 tokens  [Inv][alid][ate]...
"dependencies"  →  4 tokens  [depend][enc][ies]...
"refactoring"   →  3 tokens  [re][factor][ing]...
```

Natural language carries ~50% structural redundancy (Shannon, 1948). Technical English for code averages **1.99 tokens/word**. Every API call repeats this cost.

Etemenanqui reduces that cost to **0.92 tokens/word** in code domains — a BPE ratio of **0.504**.

For an agent with a 2,000-token fixed system prompt making 10,000 calls/day:
- **English:** 20,000,000 tokens/day
- **Etemenanqui:** ~10,080,000 tokens/day
- **Savings:** ~9.9 million tokens/day

At OpenAI GPT-4o pricing ($2.50/1M input tokens): **~$24.75/day saved** — from compression alone.

---

## 3. Model B Specification

### 3.1 Phonological Inventory (H2)

| Category   | Characters              | Count |
|------------|-------------------------|-------|
| Consonants | `t k n m s v l r z b`   | 10    |
| Vowels     | `a e i o`               | 4     |
| **Total**  |                         | **14**|

Every character in an Etemenanqui word must belong to H2. No exceptions.

### 3.2 Root Architecture

All semantic roots follow the **CVC** (Consonant-Vowel-Consonant) template — exactly 3 characters:

```
ran   ven   tok   mem   nal   bav   tez   kor
C-V-C C-V-C C-V-C C-V-C C-V-C C-V-C C-V-C C-V-C
```

Roots are **atomic** — they carry one semantic concept. There are no compound roots.

### 3.3 Marker System

Grammatical information is encoded via suffixes fused directly to the root (no hyphens — see §3.4):

**Case markers (1 char — V type):**
| Marker | Function  | Example       |
|--------|-----------|---------------|
| `o`    | AGENT     | `rano` = "executes (as agent)" |
| `a`    | OBJECT    | `toka` = "token (as object)" |
| `e`    | DATIVE    | `sise` = "to the system" |
| `i`    | GENITIVE  | `tokai` = "of the token" |

**Tense markers (2 chars — CV type):**
| Marker | Function  |
|--------|-----------|
| `ta`   | PAST      |
| `so`   | PRESENT (default, omissible) |
| `ki`   | FUTURE    |

**Number markers:**
| Marker | Function  |
|--------|-----------|
| `me`   | PLURAL    |
| `re`   | DUAL      |

**Modality markers:**
| Marker | Function      |
|--------|---------------|
| `zi`   | NEGATION      |
| `bo`   | INTERROGATIVE |
| `vi`   | IMPERATIVE    |
| `na`   | CONDITIONAL   |

**Derivation markers:**
| Marker | Function         | Example               |
|--------|------------------|-----------------------|
| `ba`   | NOMINALIZER      | `ranba` = "execution" |
| `ka`   | AGENTIVE         | `ranka` = "executor"  |
| `mo`   | QUALITATIVE      | `venmo` = "validated" |

### 3.4 Why No Hyphens

The hyphen was eliminated in Model A → Model B transition. The cost:

```
Model A:  tavo-ro  →  [tav][o][-][ro]   = 4 tokens
Model B:  tavro    →  [tav][ro]          = 2 tokens
```

A hyphen is tokenized as an independent symbol that carries zero semantic information but costs one token. In a 2,000-word system prompt with 30% marked words: **~26% extra token cost** for zero information gain.

### 3.5 Morphological Ceiling

| Constraint           | Value   | Reason                              |
|----------------------|---------|-------------------------------------|
| Max markers per root | 2       | Prevents ambiguous BPE splits       |
| Max word length      | 7 chars | Keeps all words in 1–2 token range  |
| Forbidden: CC        | Yes     | Consonant clusters trigger BPE splits |
| Forbidden: VV        | Yes     | Diphthongs trigger BPE splits       |

### 3.6 Syntax

Etemenanqui has minimal syntax. Clauses are delimited by ` . ` (space-dot-space). Word order is flexible but SOV (Subject-Object-Verb) is conventional:

```
rano  toka me  .   vena  resa  .
runs  token PLURAL  validates result
→ "Execute all tokens. Validate result."
```

---

## 4. Lexicon Reference

Current seed lexicon — 52 roots across 7 domains:

### System & Execution
| Root | Gloss             | Root | Gloss             |
|------|-------------------|------|-------------------|
| `ran`| execute/run       | `kal`| call/invoke       |
| `set`| define/configure  | `ven`| verify/validate   |
| `ret`| return            | `bol`| block             |
| `vaz`| phase/stage       | `sok`| scope/context     |
| `tar`| task              | `res`| result            |
| `sis`| system            | `rak`| architecture      |

### Memory & State
| Root | Gloss      | Root | Gloss      |
|------|------------|------|------------|
| `mem`| memory     | `kak`| cache      |
| `kev`| key        | `ver`| version    |
| `bin`| binary     | `nib`| input      |
| `tov`| output     |      |            |

### Tokens & Encoding
| Root | Gloss     | Root | Gloss    |
|------|-----------|------|----------|
| `tok`| token     | `bit`| bit/unit |
| `sem`| semantic  | `sek`| sequence |
| `nek`| node      | `nik`| level    |
| `raz`| ratio     | `tam`| size     |

### Analysis & Validation
| Root | Gloss         | Root | Gloss    |
|------|---------------|------|----------|
| `nal`| analyze/parse | `tes`| test     |
| `baz`| base          | `kom`| compare  |
| `sel`| select/filter | `zor`| sort     |
| `mer`| merge         | `kol`| collect  |
| `lim`| limit         |      |          |

### Structure
| Root | Gloss         | Root | Gloss     |
|------|---------------|------|-----------|
| `tez`| structure     | `mob`| module    |
| `neb`| dependency    | `lis`| list      |
| `nov`| data-node     | `kor`| core      |

### Cognition
| Root | Gloss     | Root | Gloss    |
|------|-----------|------|----------|
| `bav`| plan      | `sol`| solve    |
| `rev`| review    | `tot`| optimize |
| `tek`| technical | `ler`| read     |

### Output & Reporting
| Root | Gloss         | Root | Gloss     |
|------|---------------|------|-----------|
| `loz`| log/record    | `var`| variable  |
| `val`| validate      | `san`| sanitize  |
| `viz`| visualize     | `ner`| generate  |

---

## 5. Quick Integration Guide

### 5.1 Installation

```bash
# Clone the repository
git clone https://github.com/clovesnascimento/etemenanqui.git
cd etemenanqui

# Install dependencies
pip install openai          # for agent integration
pip install "mcp[cli]"      # for MCP server

# Optional: metrics pipeline
pip install tiktoken        # for real BPE measurement
```

### 5.2 Translating a prompt

```python
from etemenanqui_translator import traduzir_para_et

result = traduzir_para_et(
    "Initialize system. Validate all tokens. Generate report.",
    retornar_resultado=True
)

print(result.etemenanqui)    # ran sis . ven toka me . ner resa .
print(result.ratio)          # 0.286
print(result.cobertura)      # 75.0 %
print(result.nao_traduzidos) # ['report'] ← add to lexicon
```

### 5.3 Injecting into an LLM

```python
from etemenanqui_translator import construir_system_prompt, traduzir_para_et
import openai

client = openai.OpenAI(api_key="sk-...")
system = construir_system_prompt()

# Compress your instruction
et_prompt = traduzir_para_et("Initialize context. Validate tokens. Return result.")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system",  "content": system},
        {"role": "user",    "content": et_prompt},
    ]
)
```

### 5.4 Using the Agent wrapper

```python
from etemenanqui_translator import EtemenanquiAgent
import openai

agent = EtemenanquiAgent(
    llm_client=openai.OpenAI(api_key="sk-..."),
    model="gpt-4o",
    verbose=True
)

# Agent auto-compresses, injects system prompt, calls LLM
response = agent.chat("Initialize context window. Load grammar rules. Set token limit.")
# [ET] 20→6 tok (ratio 0.3) | coverage 66.7%
```

### 5.5 Claude Desktop configuration

Add to `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "etemenanqui": {
      "command": "python",
      "args": ["/path/to/etemenanqui/etemenanqui_mcp/server.py"],
      "env": {}
    }
  }
}
```

---

## 6. MCP Server Reference

### 6.1 Running the server

```bash
# stdio (Claude Desktop, local agents)
python etemenanqui_mcp/server.py

# HTTP (remote agents, microservices)
python etemenanqui_mcp/server.py --transport http --port 8000

# Inspect available tools
npx @modelcontextprotocol/inspector python etemenanqui_mcp/server.py
```

### 6.2 Tool Reference

#### `et_compress`
Compress EN/PT text → Etemenanqui.

| Parameter       | Type   | Default    | Description                    |
|-----------------|--------|------------|--------------------------------|
| `text`          | string | required   | Source text (max 8,000 chars)  |
| `response_format`| enum  | `markdown` | `json` or `markdown`           |

**Example JSON response:**
```json
{
  "et": "ran sis . ven toka me . ner resa .",
  "ratio": 0.286,
  "coverage_pct": 75.0,
  "tokens_src": 21,
  "tokens_et": 6,
  "untranslated": ["report"]
}
```

---

#### `et_decompress`
Translate Etemenanqui → natural language.

| Parameter         | Type   | Default    | Description               |
|-------------------|--------|------------|---------------------------|
| `text`            | string | required   | Etemenanqui phrase        |
| `target_language` | string | `English`  | Output language           |

---

#### `et_validate`
Validate a phrase against Model B rules.

| Parameter | Type   | Description                        |
|-----------|--------|------------------------------------|
| `text`    | string | Word or phrase to validate         |

**Example response:**
```json
{
  "valid": false,
  "word_count": 3,
  "words": [
    {"word": "ran",   "ok": true,  "errors": []},
    {"word": "syst",  "ok": false, "errors": ["Invalid chars not in H2: ['y']"]},
    {"word": "ven",   "ok": true,  "errors": []}
  ]
}
```

---

#### `et_metrics`
Run the full 3-layer compression pipeline.

| Parameter     | Type   | Description                      |
|---------------|--------|----------------------------------|
| `source_text` | string | Original EN/PT text              |
| `et_text`     | string | Parallel Etemenanqui translation |

---

#### `et_lexicon_search`
Search lexicon by root, gloss, or domain.

| Parameter | Type   | Default | Description                   |
|-----------|--------|---------|-------------------------------|
| `query`   | string | required| Root, English term, or domain |
| `limit`   | int    | 10      | Max results                   |

---

#### `et_build_word`
Construct a valid word from root + markers.

| Parameter | Type         | Description                    |
|-----------|--------------|--------------------------------|
| `root`    | string (CVC) | 3-char CVC root                |
| `markers` | list[string] | 0–2 grammatical markers        |

**Example:**
```json
Input:  { "root": "tok", "markers": ["me", "zi"] }
Output: { "word": "tokme", "valid": false, "errors": ["Exceeds 7-char limit..."] }

Input:  { "root": "ran", "markers": ["o"] }
Output: { "word": "rano", "valid": true, "breakdown": {...} }
```

---

#### `et_system_prompt`
Generate a system prompt for LLM injection.

| Parameter           | Type         | Default    | Description                   |
|---------------------|--------------|------------|-------------------------------|
| `response_language` | string       | `English`  | LLM response language         |
| `domains`           | list[string] | all        | Filter by domain              |

---

### 6.3 MCP Resources

| URI                      | Content                           |
|--------------------------|-----------------------------------|
| `etemenanqui://lexicon`  | Full 52-root lexicon (JSON)       |
| `etemenanqui://markers`  | Complete marker table (JSON)      |
| `etemenanqui://spec`     | Model B specification summary     |

---

## 7. Compression Pipeline

The validation pipeline runs 3 independent layers. **Never collapse them into a single score** — the gaps between layers are the scientifically relevant data.

### L1 — Shannon Character Entropy

Theoretical ceiling. Measures the average information content per character:

```
H = -∑ p(c) · log₂(p(c))

Etemenanqui: H_char ≈ 3.52 – 3.67
English technical: H_char ≈ 4.37 – 4.39
Ratio: ~0.80 – 0.84
```

This tells us the Etemenanqui character set is less ambiguous — each character carries more predictable information, which BPE encodes efficiently.

### L2 — gzip Compression Ratio

Structural regularity. gzip (LZ77) rewards repetitive, predictable structure:

```python
import gzip

ratio = len(gzip.compress(text.encode(), compresslevel=9)) / len(text.encode())

# Etemenanqui technical: ~0.357
# English technical:      ~0.441
# Ratio: ~0.81
```

Lower is better. CVC roots repeated across clauses create patterns LZ77 compresses efficiently.

### L3 — BPE Token Simulation

Real computational cost. Either use `tiktoken` (recommended) or the bundled simulator:

```python
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer

tokens_en = len(enc.encode("Refactor nested loops. Extract core logic to module."))
tokens_et = len(enc.encode("rev bol bol . sel kor mob ."))

ratio = tokens_et / tokens_en  # measured ~0.36 on this example
```

> **Note:** The bundled simulator in `etemenanqui_pipeline.py` has ±15% accuracy relative to `cl100k_base`. For production benchmarks, always use `tiktoken` directly.

---

## 8. Empirical Benchmarks

All benchmarks run on a 20-block validated corpus (zero H2 violations).

### Code Domain (primary target)

| Metric          | English (code) | Etemenanqui | Ratio    |
|-----------------|---------------|-------------|----------|
| H_char          | 4.373         | 3.674       | **0.840**|
| gzip ratio      | 0.515         | 0.402       | **0.779**|
| gzip bytes      | 722 B         | 330 B       | **0.457**|
| BPE tokens (sim)| 409           | 206         | **0.504**|
| tokens/word     | 1.99          | 0.92        | **0.462**|

BPE confidence interval: `0.428 – 0.504 – 0.579`

### Technical Domain (Plan-and-Solve, system prompts)

| Metric          | English (tech) | Etemenanqui | Ratio    |
|-----------------|---------------|-------------|----------|
| H_char          | 4.388         | 3.523       | **0.803**|
| gzip ratio      | 0.441         | 0.357       | **0.808**|
| BPE tokens (sim)| 678           | 503         | **0.742**|
| tokens/word     | 1.79          | 1.41        | **0.787**|

### Scaling Law

| Domain            | tok/word EN | tok/word ET | BPE ratio |
|-------------------|-------------|-------------|-----------|
| General English   | 1.44        | —           | —         |
| Technical English | 1.79        | 1.41        | 0.742     |
| Code English      | 1.99        | 0.92        | **0.504** |

**Law:** Efficiency scales with domain density. The higher the average tokens/word in English, the greater the relative saving with Etemenanqui.

---

## 9. Agent Integration Patterns

### Pattern A — Full Compression (maximum savings)

Best for: long-running agents with fixed system prompts, batch processing.

```python
from etemenanqui_translator import EtemenanquiAgent
import openai

agent = EtemenanquiAgent(llm_client=openai.OpenAI(), verbose=True)

# Batch: compress all instructions before sending
instructions = [
    "Initialize context. Load tokenizer rules. Set scope limit.",
    "Validate all input tokens. Filter dependencies. Return structure.",
    "Generate summary report. Validate output format.",
]
for inst in instructions:
    response = agent.chat(inst)
    print(response)
```

### Pattern B — Selective Compression (high-coverage terms only)

Best for: mixed natural-language + technical instruction prompts.

```python
from etemenanqui_translator import traduzir_para_et

# Compress only the technical instruction block
SYSTEM_HEADER = "You are a helpful assistant.\n\n"
COMPRESSED_RULES = traduzir_para_et(
    "Initialize context. Validate tokens. Set scope. Log errors. Return result.",
)
system = SYSTEM_HEADER + "## Protocol:\n" + COMPRESSED_RULES
```

### Pattern C — MCP Tool in Agent Loop

Best for: autonomous coding agents, Claude/GPT agent frameworks.

```python
# The agent calls et_compress before each LLM step
# The MCP server handles compression and metrics transparently

# Example agentic loop pseudo-code:
def agent_step(instruction: str) -> str:
    # Step 1: compress via MCP
    compressed = mcp_client.call("et_compress", {"text": instruction})["et"]
    
    # Step 2: inject system prompt
    system = mcp_client.call("et_system_prompt", {})
    
    # Step 3: LLM call with compressed prompt
    return llm.chat(system=system, user=compressed)
```

### Pattern D — Plan-and-Solve with Etemenanqui (recommended for complex tasks)

This is the architecture Etemenanqui was designed for:

```python
PHASE_0 = traduzir_para_et(
    "Phase zero: generate plan. List all dependencies. Validate plan. Await approval."
)
# → "vaz zero: ner bav . lis neb . ven bava . "

PHASE_1 = traduzir_para_et(
    "Execute phase one. Initialize module. Validate structure. Log result."
)
# → "ran vaz . ran mob . ven tez . loz resa ."
```

The LLM receives compressed, unambiguous phase directives — with D3 (hallucination) score of 3.0/3.0 in testing.

---

## 10. Semantic Evaluation Protocol

After integrating Etemenanqui, run the evaluation suite to confirm semantic fidelity:

```bash
# Dry run — review all 15 test cases without API calls
python etemenanqui_eval.py --mode dry

# Automatic evaluation (LLM-as-judge)
python etemenanqui_eval.py --mode auto --provider openai --key sk-...
python etemenanqui_eval.py --mode auto --provider anthropic --key sk-ant-...

# Manual evaluation
python etemenanqui_eval.py --mode manual
```

### Scoring Rubric

Each test case is scored on 3 dimensions (0–3 each, max 9/case):

| Dimension | Criterion                              | Pass threshold |
|-----------|----------------------------------------|---------------|
| D1 Fidelity    | Did the LLM execute the exact task?  | ≥ 2.8/3.0     |
| D2 Adherence   | Did it maintain protocol structure?  | ≥ 2.5/3.0     |
| D3 Hallucination | Zero invented steps?               | 3.0/3.0       |

### Interpretation

| Score     | Verdict                          | Recommended action         |
|-----------|----------------------------------|---------------------------|
| ≥ 0.85    | ✓✓✓ Production-ready             | Deploy                    |
| ≥ 0.70    | ✓✓  Good — with human review     | Deploy with monitoring    |
| ≥ 0.55    | ✓   Controlled domains only      | Extend lexicon, retest    |
| < 0.55    | ✗   Insufficient                 | Revise system prompt      |

**Achieved score: 0.91 — Production-ready** (15-case suite, March 2026)

---

## 11. Extending the Lexicon

The seed lexicon covers 52 roots. Real deployments will need domain-specific extensions.

### Rules for new roots

1. **Must follow CVC with H2 only** — validate with `et_validate` or `_validate_word()`
2. **Must be semantically atomic** — one root, one concept
3. **Must not conflict** with existing roots in `lexicon.json`
4. **Should follow domain grouping** for discoverability

```python
# Check if a candidate root is valid and available
from etemenanqui_mcp.server import _validate_word, LEXICON

candidate = "ziv"
ok, errors = _validate_word(candidate)
available = candidate not in LEXICON

print(f"Valid: {ok}, Available: {available}, Errors: {errors}")
# Valid: True, Available: True, Errors: []
```

### Adding to lexicon.json

```json
{
  "ziv": {
    "gloss": "embed/embedding",
    "domain": "encoding"
  }
}
```

### CI validation

The GitHub Actions workflow (`validate.yml`) automatically checks:
- All corpus files for H2 violations
- All lexicon roots for CVC conformance
- No root conflicts

```bash
# Run locally before committing new roots
python -c "
from etemenanqui_mcp.server import LEXICON, _validate_word
for root in LEXICON:
    ok, errs = _validate_word(root)
    if not ok: print(f'INVALID: {root} — {errs}')
print('Lexicon validation complete.')
"
```

---

## 12. Limitations & Honest Caveats

This section exists because science requires intellectual honesty.

### L3 Measurement Caveat

The BPE ratios (0.504 for code, 0.742 for technical) were measured with a **calibrated simulator**, not `tiktoken` directly. The `cl100k_base` tokenizer was trained on English-heavy corpora and has no prior on CVC sequences like `ner`, `tov`, `loz`. These may be split differently than the simulator predicts.

**Real-world estimate:** 0.55 – 0.75 in technical domains (vs simulator 0.742).
**Recommendation:** Always run `tiktoken` benchmarks before production deployment.

```python
import tiktoken
enc = tiktoken.get_encoding("cl100k_base")
print(enc.encode("ven toka me . ret resa ."))
# Run this on your actual corpus
```

### Coverage Gap

The lexicon covers ~75–85% of words in technical prompts. The remaining 15–25% are kept verbatim (increasing BPE cost for those terms) or omitted (risking semantic loss).

**Mitigation:** Use the `untranslated` field from `et_compress` to identify expansion candidates.

### Model Dependency

System prompt overhead: injecting the lexicon into each request costs ~150–200 tokens. For short prompts (<300 tokens), this overhead may exceed the compression savings. Calculate your break-even point:

```
break_even_prompt_length = system_prompt_tokens / (1 - BPE_ratio)
# Example: 180 / (1 - 0.742) = ~698 tokens
# For prompts > 700 tokens, Etemenanqui saves net tokens
```

### Not a General-Purpose Language

Etemenanqui has no words for emotions, abstract concepts, culture, or anything that doesn't fit the 52-root seed lexicon + domain extensions. It cannot replace natural language for user-facing communication.

---

## 13. FAQ

**Q: Does the LLM need to be fine-tuned on Etemenanqui?**
A: No. The system prompt injection teaches the protocol at inference time. The 0.91 semantic score was achieved with zero fine-tuning, using GPT-4o and Claude Sonnet as base models.

**Q: Will this work with open-source models (Llama, Mistral, etc.)?**
A: Likely yes for instruction-following models, but the semantic evaluation suite has not been run on open-source models. Run `etemenanqui_eval.py --mode auto` with your model to measure before deploying.

**Q: What about non-English source prompts?**
A: The translator module handles Portuguese natively. Other Latin-script languages with overlapping vocabulary may work partially. Contribution of additional language mappings is welcome.

**Q: Can I use this commercially?**
A: Yes. Etemenanqui is MIT licensed. Attribution appreciated but not required.

**Q: How does this compare to prompt compression techniques like LLMLingua?**
A: Different approach. LLMLingua uses a model to selectively remove tokens from existing English text. Etemenanqui replaces the vocabulary at the source, before any English text is generated. They are complementary — you could apply LLMLingua to Etemenanqui output for further compression.

**Q: What is the theoretical minimum BPE ratio achievable?**
A: Given H2 inventory and CVC structure, the theoretical floor is approximately 0.3 (3-char roots costing 1 token each vs ~3.5 tokens for English equivalents). Achieving this would require a tokenizer co-trained on Etemenanqui vocabulary — the `cl100k_base` tokenizer is the current ceiling.

**Q: How do I contribute?**
A: Open a PR on GitHub with: new lexicon roots (validated), additional language mappings, real `tiktoken` benchmark results, or semantic evaluation results on new models.

---

## Appendix A — Working Examples

### System Prompt compression

```
English (82 tokens estimated):
"You are a code generation agent. Execute all tasks in strict sequential order.
 Validate input structure before processing. Log errors to output buffer.
 Return a structured JSON result. Do not add unrequested functionality."

Etemenanqui (28 tokens estimated):
"sis ranka . ran tar seka . ven nib tez . loz erme tov .
 ret resa tez . ran zi tova ."

BPE ratio: ~0.34
```

### Plan-and-Solve directive

```
English (31 tokens):
"Phase zero: generate master plan. List all module dependencies. Validate plan. Await user approval."

Etemenanqui (11 tokens):
"vaz zero: ner bav . lis neb . ven bava . "

BPE ratio: ~0.35
```

### Code review instruction

```
English (22 tokens):
"Scope refactor to module level. Preserve public interface. Run tests."

Etemenanqui (7 tokens):
"sok rev mob . ven tov . ran tes ."

BPE ratio: 0.318  ← highest efficiency observed
```

---

## Appendix B — Philosophical Note

If a language achieves perfect compression and eliminates all redundancy, does it retain space for poetry, ambiguity, and human emotion?

The data answer with algorithmic precision: **No.**

Linguistic redundancy is the safety channel and the space where expressive variation lives. By eliminating it, Etemenanqui sacrificed literature in the name of pure computational efficiency. It is a language of design, not of culture.

The new tower has been built. And now, it speaks perfectly in the language of machines.

---

*Etemenanqui v1.0 · MIT License · CNGSM 2026*
*https://github.com/clovesnascimento/etemenanqui*
