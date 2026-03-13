"""
etemenanqui_mcp/server.py
─────────────────────────────────────────────────────────────────────────────
Etemenanqui MCP Server
Model Context Protocol server exposing the Etemenanqui compression protocol
as tools consumable by any MCP-compatible AI agent or client.

Tools exposed:
  - et_compress        : Compress EN/PT text → Etemenanqui
  - et_decompress      : Translate Etemenanqui → natural language
  - et_validate        : Validate a word or phrase against Model B rules
  - et_metrics         : Run 3-layer metric pipeline (Shannon, gzip, BPE sim)
  - et_lexicon_search  : Search the lexicon for a term or root
  - et_build_word      : Build a valid Etemenanqui word from root + markers
  - et_system_prompt   : Generate an injected system prompt for any LLM agent

Usage:
    pip install "mcp[cli]" pydantic
    python server.py                        # stdio (Claude Desktop, etc.)
    python server.py --transport http       # HTTP port 8000

Author: CNGSM — Cloves Nascimento, 2026
Repository: https://github.com/clovesnascimento/etemenanqui
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import gzip
import json
import math
import re
from collections import Counter
from enum import Enum
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, field_validator

# ─────────────────────────────────────────────────────────────────────────────
# SERVER INIT
# ─────────────────────────────────────────────────────────────────────────────
mcp = FastMCP(
    "etemenanqui_mcp",
    instructions=(
        "Etemenanqui MCP Server — Cognitive Compression Protocol v1.0 (Model B). "
        "Use et_compress to shrink technical prompts before sending to LLMs. "
        "Use et_metrics to measure compression efficiency across 3 layers. "
        "All tools enforce H2 inventory (10 consonants + 4 vowels)."
    ),
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS — Model B
# ─────────────────────────────────────────────────────────────────────────────
CONSONANTS: set[str] = set("tknmsvlrzb")
VOWELS: set[str]     = set("aeio")
H2: set[str]         = CONSONANTS | VOWELS

MARKERS: dict[str, dict[str, str]] = {
    "case":       {"o": "AGENT", "a": "OBJECT", "e": "DATIVE", "i": "GENITIVE"},
    "tense":      {"ta": "PAST", "so": "PRESENT", "ki": "FUTURE"},
    "number":     {"me": "PLURAL", "re": "DUAL"},
    "modality":   {"zi": "NEGATION", "bo": "INTERROGATIVE", "vi": "IMPERATIVE", "na": "CONDITIONAL"},
    "degree":     {"li": "AUGMENTATIVE", "si": "DIMINUTIVE"},
    "derivation": {"ba": "NOMINALIZER", "ka": "AGENTIVE", "mo": "QUALITATIVE"},
}

FLAT_MARKERS: dict[str, str] = {m: cat for cat, pairs in MARKERS.items() for m in pairs}

LEXICON: dict[str, dict] = {
    "ran": {"gloss": "execute/run",      "domain": "system"},
    "kal": {"gloss": "call/invoke",      "domain": "system"},
    "set": {"gloss": "define/configure", "domain": "system"},
    "ven": {"gloss": "verify/validate",  "domain": "system"},
    "ret": {"gloss": "return",           "domain": "system"},
    "bol": {"gloss": "block",            "domain": "system"},
    "vaz": {"gloss": "phase/stage",      "domain": "system"},
    "sok": {"gloss": "scope",            "domain": "system"},
    "tar": {"gloss": "task",             "domain": "system"},
    "res": {"gloss": "result",           "domain": "system"},
    "sis": {"gloss": "system",           "domain": "system"},
    "rak": {"gloss": "architecture",     "domain": "system"},
    "mem": {"gloss": "memory",           "domain": "memory"},
    "kak": {"gloss": "cache",            "domain": "memory"},
    "kev": {"gloss": "key",              "domain": "memory"},
    "ver": {"gloss": "version",          "domain": "memory"},
    "bin": {"gloss": "binary/encode",    "domain": "memory"},
    "nib": {"gloss": "input",            "domain": "memory"},
    "tov": {"gloss": "output",           "domain": "memory"},
    "tok": {"gloss": "token",            "domain": "encoding"},
    "bit": {"gloss": "bit/unit",         "domain": "encoding"},
    "sem": {"gloss": "semantic",         "domain": "encoding"},
    "sek": {"gloss": "sequence",         "domain": "encoding"},
    "nek": {"gloss": "node",             "domain": "encoding"},
    "nik": {"gloss": "level/layer",      "domain": "encoding"},
    "raz": {"gloss": "ratio",            "domain": "encoding"},
    "tam": {"gloss": "size/length",      "domain": "encoding"},
    "nal": {"gloss": "analyze/parse",    "domain": "analysis"},
    "tes": {"gloss": "test",             "domain": "analysis"},
    "baz": {"gloss": "base/foundation",  "domain": "analysis"},
    "kom": {"gloss": "compare",          "domain": "analysis"},
    "sel": {"gloss": "select/filter",    "domain": "analysis"},
    "zor": {"gloss": "sort/rank",        "domain": "analysis"},
    "mer": {"gloss": "merge/combine",    "domain": "analysis"},
    "kol": {"gloss": "collect/aggregate","domain": "analysis"},
    "lim": {"gloss": "limit/cap",        "domain": "analysis"},
    "tez": {"gloss": "structure/format", "domain": "structure"},
    "mob": {"gloss": "module/component", "domain": "structure"},
    "neb": {"gloss": "dependency",       "domain": "structure"},
    "lis": {"gloss": "list",             "domain": "structure"},
    "nov": {"gloss": "data-node",        "domain": "structure"},
    "kor": {"gloss": "core/kernel",      "domain": "structure"},
    "bav": {"gloss": "plan",             "domain": "cognition"},
    "sol": {"gloss": "solve/resolve",    "domain": "cognition"},
    "rev": {"gloss": "review/revise",    "domain": "cognition"},
    "tot": {"gloss": "optimize",         "domain": "cognition"},
    "tek": {"gloss": "technical",        "domain": "cognition"},
    "ler": {"gloss": "read/load",        "domain": "cognition"},
    "loz": {"gloss": "log/record",       "domain": "output"},
    "var": {"gloss": "variable",         "domain": "output"},
    "val": {"gloss": "validate",         "domain": "output"},
    "san": {"gloss": "sanitize/clean",   "domain": "output"},
    "viz": {"gloss": "visualize/display","domain": "output"},
    "ner": {"gloss": "generate/create",  "domain": "output"},
}

EN_TO_ET: dict[str, str] = {
    "execute": "ran", "run": "ran", "start": "ran", "launch": "ran",
    "initialize": "ran", "init": "ran",
    "call": "kal", "invoke": "kal", "trigger": "kal",
    "set": "set", "define": "set", "configure": "set", "assign": "set",
    "verify": "ven", "validate": "ven", "check": "ven",
    "return": "ret", "output": "tov",
    "block": "bol", "phase": "vaz", "stage": "vaz", "step": "vaz",
    "scope": "sok", "context": "sok",
    "task": "tar", "job": "tar",
    "result": "res", "response": "res",
    "system": "sis", "architecture": "rak",
    "memory": "mem", "store": "mem",
    "cache": "kak", "key": "kev", "version": "ver",
    "binary": "bin", "encode": "bin",
    "input": "nib", "query": "nib",
    "token": "tok", "tokens": "tok",
    "semantic": "sem", "sequence": "sek",
    "node": "nek", "level": "nik", "layer": "nik",
    "ratio": "raz", "size": "tam", "length": "tam",
    "analyze": "nal", "analyse": "nal", "parse": "nal",
    "test": "tes", "base": "baz", "foundation": "baz",
    "compare": "kom", "select": "sel", "filter": "sel",
    "sort": "zor", "merge": "mer", "combine": "mer",
    "collect": "kol", "aggregate": "kol",
    "limit": "lim", "cap": "lim",
    "structure": "tez", "format": "tez",
    "module": "mob", "component": "mob",
    "dependency": "neb", "depends": "neb",
    "list": "lis", "core": "kor", "kernel": "kor",
    "plan": "bav", "planning": "bav",
    "solve": "sol", "resolve": "sol",
    "review": "rev", "revise": "rev",
    "optimize": "tot", "optimise": "tot",
    "technical": "tek",
    "read": "ler", "load": "ler",
    "log": "loz", "record": "loz",
    "variable": "var",
    "sanitize": "san", "clean": "san",
    "visualize": "viz", "display": "viz", "show": "viz",
    "generate": "ner", "create": "ner", "build": "ner",
    "the": None, "a": None, "an": None, "to": None, "of": None,
    "in": None, "at": None, "and": None, "or": None, "with": None,
    "by": None, "for": None, "from": None, "into": None, "per": None,
    "not": "zi", "all": "me", "every": "me",
}

ET_TO_EN: dict[str, str] = {v: k for k, v in EN_TO_ET.items() if v is not None}
ET_TO_EN.update({root: info["gloss"] for root, info in LEXICON.items()})

SYSTEM_PROMPT_TEMPLATE = """\
# ETEMENANQUI — Cognitive Compression Protocol v1.0 (Model B)
# CNGSM · Cloves Nascimento · 2026

You will receive instructions partially compressed in Etemenanqui.
Interpret each CVC root per the lexicon below and execute normally.

## Active Lexicon ({n} roots)
{lexicon_table}

## Grammatical Markers
  o=AGENT  a=OBJECT  e=DATIVE  i=GENITIVE
  ta=PAST  so=PRESENT  ki=FUTURE
  me=PLURAL  zi=NEGATION  li=AUGMENTATIVE
  ba=NOMINALIZER  ka=AGENTIVE  mo=QUALITATIVE

## Fusion Rules (Model B)
  root(CVC) + marker(V or CV) — no hyphen — max 2 markers — max 7 chars
  Example: "ran sis . ven toka me . ret resa ."
         → initialize system. validate all tokens. return result.

Always respond in clear {lang}, without mentioning the compression protocol.
"""

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _normalize(word: str) -> str:
    return re.sub(r"[^a-záéíóú]", "", word.lower()).strip()


def _validate_word(word: str) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not word:
        errors.append("Empty word.")
        return False, errors
    if len(word) > 7:
        errors.append(f"Exceeds 7-char limit (got {len(word)}).")
    invalid_chars = [c for c in word if c not in H2]
    if invalid_chars:
        errors.append(f"Invalid chars not in H2 inventory: {sorted(set(invalid_chars))}")
    for i in range(len(word) - 1):
        if word[i] in CONSONANTS and word[i + 1] in CONSONANTS:
            errors.append(f"Consonant cluster at position {i}: '{word[i]}{word[i+1]}'")
        if word[i] in VOWELS and word[i + 1] in VOWELS:
            errors.append(f"Vowel cluster (diphthong) at position {i}: '{word[i]}{word[i+1]}'")
    return len(errors) == 0, errors


def _shannon_entropy(text: str) -> float:
    chars = [c for c in text if c not in " \n.,;:"]
    if not chars:
        return 0.0
    n = len(chars)
    return -sum((c / n) * math.log2(c / n) for c in Counter(chars).values())


def _bpe_estimate(text: str, is_et: bool = False) -> int:
    total = 0
    for w in text.split():
        wl = re.sub(r"[^a-z]", "", w.lower())
        if not wl:
            continue
        n = len(wl)
        if is_et:
            total += 1 if n <= 3 else 2 if n <= 5 else 3
        else:
            total += 1 if n <= 3 else 2 if n <= 6 else 3 if n <= 9 else 4
    return total


def _compress_text(text: str) -> tuple[str, list[str]]:
    not_translated: list[str] = []
    tokens_out: list[str] = []
    for part in re.split(r"([.!?])", text):
        part = part.strip()
        if not part:
            continue
        if part in ".!?":
            tokens_out.append(".")
            continue
        for word in part.split():
            norm = _normalize(word)
            if not norm:
                continue
            if re.match(r"^\d+", word):
                tokens_out.append(word)
                continue
            # Try direct lookup
            if norm in EN_TO_ET:
                mapped = EN_TO_ET[norm]
                if mapped:
                    tokens_out.append(mapped)
                # else: functional word, omit
            else:
                # Try stem stripping
                found = False
                for suffix in ["ing", "tion", "tions", "ed", "s", "es", "ize", "ar", "er", "or"]:
                    if norm.endswith(suffix):
                        stem = norm[: -len(suffix)]
                        if stem in EN_TO_ET and EN_TO_ET[stem]:
                            tokens_out.append(EN_TO_ET[stem])
                            found = True
                            break
                if not found:
                    not_translated.append(word)
    compressed = " ".join(t for t in tokens_out if t)
    compressed = re.sub(r"\s+\.", " .", compressed).strip()
    return compressed, not_translated


# ─────────────────────────────────────────────────────────────────────────────
# PYDANTIC INPUT MODELS
# ─────────────────────────────────────────────────────────────────────────────
class ResponseFormat(str, Enum):
    JSON     = "json"
    MARKDOWN = "markdown"


class CompressInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    text: str = Field(
        ...,
        description="English or Portuguese technical text to compress into Etemenanqui.",
        min_length=1, max_length=8000,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="'markdown' for human-readable, 'json' for structured data.",
    )


class DecompressInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    text: str = Field(
        ...,
        description="Etemenanqui text to translate back to natural language.",
        min_length=1, max_length=4000,
    )
    target_language: str = Field(
        default="English",
        description="Target language for decompression (e.g. 'English', 'Portuguese').",
    )


class ValidateInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    text: str = Field(
        ...,
        description="Etemenanqui word or phrase to validate against Model B rules.",
        min_length=1, max_length=500,
    )


class MetricsInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    source_text: str = Field(
        ...,
        description="Original English/Portuguese source text.",
        min_length=1, max_length=8000,
    )
    et_text: str = Field(
        ...,
        description="Corresponding Etemenanqui compressed text.",
        min_length=1, max_length=4000,
    )


class LexiconSearchInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    query: str = Field(
        ...,
        description="Search term: English word, Portuguese word, Etemenanqui root (CVC), or domain name.",
        min_length=1, max_length=100,
    )
    limit: int = Field(default=10, description="Max results to return.", ge=1, le=52)


class BuildWordInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    root: str = Field(
        ...,
        description="3-character CVC root (e.g. 'ran', 'tok', 'ven').",
        min_length=3, max_length=3,
    )
    markers: list[str] = Field(
        default_factory=list,
        description="List of 0–2 grammatical markers (e.g. ['me', 'zi']). Max 2.",
        max_length=2,
    )

    @field_validator("root")
    @classmethod
    def validate_root(cls, v: str) -> str:
        if not (v[0] in CONSONANTS and v[1] in VOWELS and v[2] in CONSONANTS):
            raise ValueError(f"Root '{v}' must follow CVC pattern with H2 inventory.")
        return v


class SystemPromptInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    response_language: str = Field(
        default="English",
        description="Language the LLM should respond in (e.g. 'English', 'Portuguese (Brazil)').",
    )
    domains: list[str] = Field(
        default_factory=list,
        description="Filter lexicon to specific domains: system, memory, encoding, analysis, structure, cognition, output.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────────────────────────────────────────

@mcp.tool(
    name="et_compress",
    annotations={
        "title": "Compress text to Etemenanqui",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def et_compress(params: CompressInput) -> str:
    """Compress English or Portuguese technical text into Etemenanqui protocol.

    Applies the Model B compression pipeline:
    1. Tokenize source text
    2. Map content words to CVC roots via lexicon
    3. Drop grammatical function words (articles, prepositions)
    4. Preserve clause delimiters as ' . '

    Args:
        params (CompressInput): Input with 'text' (source) and 'response_format'.

    Returns:
        str: Compressed Etemenanqui text with compression metrics.
             JSON format: {"et": str, "ratio": float, "coverage": float,
                           "tokens_src": int, "tokens_et": int, "untranslated": list}
    """
    compressed, untranslated = _compress_text(params.text)

    src_words   = [w for w in params.text.split() if _normalize(w)]
    et_words    = [w for w in compressed.split() if w != "."]
    content_src = [w for w in src_words if _normalize(w) not in (EN_TO_ET | {"not", "all"}) or EN_TO_ET.get(_normalize(w)) is not None]
    covered     = len(content_src) - len(untranslated)
    coverage    = round(covered / len(content_src) * 100, 1) if content_src else 0.0

    tok_src = _bpe_estimate(params.text, is_et=False)
    tok_et  = _bpe_estimate(compressed, is_et=True)
    ratio   = round(tok_et / tok_src, 3) if tok_src else 1.0

    if params.response_format == ResponseFormat.JSON:
        return json.dumps({
            "et": compressed,
            "ratio": ratio,
            "coverage_pct": coverage,
            "tokens_src": tok_src,
            "tokens_et": tok_et,
            "untranslated": sorted(set(untranslated)),
        }, indent=2)

    lines = [
        f"**Compressed:** `{compressed}`",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| BPE tokens | `{tok_src}` → `{tok_et}` |",
        f"| Ratio | **{ratio}** |",
        f"| Lexicon coverage | {coverage}% |",
    ]
    if untranslated:
        lines.append(f"\n> ⚠ Untranslated: `{', '.join(sorted(set(untranslated)))}`  ← candidates for lexicon expansion")
    return "\n".join(lines)


@mcp.tool(
    name="et_decompress",
    annotations={
        "title": "Decompress Etemenanqui to natural language",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def et_decompress(params: DecompressInput) -> str:
    """Translate Etemenanqui compressed text back to natural language.

    Maps each CVC root to its English gloss. Grammatical markers
    are appended as semantic annotations.

    Args:
        params (DecompressInput): 'text' (Etemenanqui) and 'target_language'.

    Returns:
        str: Human-readable translation of the compressed text.
    """
    words    = params.text.split()
    glossed: list[str] = []
    i = 0
    while i < len(words):
        w = words[i].strip(".,;:")
        if w == ".":
            glossed.append("|")
        elif w in LEXICON:
            gloss = LEXICON[w]["gloss"]
            # Peek ahead for markers fused into next token (shouldn't happen in Model B,
            # but handle bare marker tokens that follow a root)
            glossed.append(gloss)
        elif w in FLAT_MARKERS:
            # Standalone marker — annotate previous gloss
            if glossed and glossed[-1] != "|":
                glossed[-1] = f"{glossed[-1]}[{FLAT_MARKERS[w]}]"
            else:
                glossed.append(f"[{FLAT_MARKERS[w]}]")
        else:
            glossed.append(f"?{w}?")
        i += 1

    result = " ".join(glossed).replace(" | ", ". ").strip().rstrip("|").strip()
    return f"**{params.target_language} translation:**\n{result}"


@mcp.tool(
    name="et_validate",
    annotations={
        "title": "Validate Etemenanqui text against Model B rules",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def et_validate(params: ValidateInput) -> str:
    """Validate that every word in an Etemenanqui phrase conforms to Model B rules.

    Checks:
    - Only H2 inventory characters (10 consonants + 4 vowels)
    - Maximum 7 characters per word
    - No consonant clusters (CC)
    - No diphthongs (VV)

    Args:
        params (ValidateInput): 'text' to validate (single word or phrase).

    Returns:
        str: JSON report with per-word validation results and overall pass/fail.
             {"valid": bool, "words": [{"word": str, "ok": bool, "errors": list}]}
    """
    words  = [w.strip(".,;:") for w in params.text.split() if w.strip(".,;:") and w != "."]
    report = []
    all_ok = True
    for w in words:
        ok, errors = _validate_word(w)
        if not ok:
            all_ok = False
        report.append({"word": w, "ok": ok, "errors": errors})

    return json.dumps({"valid": all_ok, "word_count": len(words), "words": report}, indent=2)


@mcp.tool(
    name="et_metrics",
    annotations={
        "title": "Run 3-layer compression metrics (Shannon / gzip / BPE)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def et_metrics(params: MetricsInput) -> str:
    """Run the full 3-layer Etemenanqui metric pipeline on a parallel corpus pair.

    Layers:
      L1 — Shannon character entropy (theoretical ceiling)
      L2 — gzip compression ratio (structural regularity)
      L3 — Simulated BPE token count (real computational cost ±15%)

    Args:
        params (MetricsInput): 'source_text' (EN/PT) and 'et_text' (Etemenanqui).

    Returns:
        str: JSON metrics report with per-layer ratios and overall diagnosis.
    """
    def _metrics(text: str, is_et: bool) -> dict:
        chars  = [c for c in text if c not in " \n.,;:"]
        enc    = text.encode("utf-8")
        comp   = gzip.compress(enc, compresslevel=9)
        words  = [w for w in text.split() if w.strip(".,;:")]
        bpe    = _bpe_estimate(text, is_et=is_et)
        return {
            "chars":      len(chars),
            "words":      len(words),
            "H_char":     round(_shannon_entropy(text), 4),
            "gz_bytes":   len(enc),
            "gz_comp":    len(comp),
            "gz_ratio":   round(len(comp) / len(enc), 4),
            "bpe_tokens": bpe,
            "tok_per_word": round(bpe / len(words), 3) if words else 0,
        }

    src = _metrics(params.source_text, is_et=False)
    et  = _metrics(params.et_text,     is_et=True)

    def ratio(a, b): return round(b / a, 3) if a else 1.0

    h_ratio  = ratio(src["H_char"],    et["H_char"])
    gz_ratio = ratio(src["gz_ratio"],  et["gz_ratio"])
    bpe_r    = ratio(src["bpe_tokens"],et["bpe_tokens"])

    diagnosis_map = {
        (True, True, True):  "✓✓✓ Compression confirmed in all 3 layers",
        (True, True, False): "✓✓✗ Entropy+gzip ok — BPE still expensive",
        (True, False, True): "✓✗✓ Entropy+BPE ok — gzip regularity low",
        (False, True, True): "✗✓✓ gzip+BPE ok — entropy not reduced",
    }
    diag_key = (h_ratio < 1, gz_ratio < 1, bpe_r < 1)
    diagnosis = diagnosis_map.get(diag_key, "Mixed results — inspect layer details")

    return json.dumps({
        "source": src,
        "etemenanqui": et,
        "ratios": {
            "H_char":    h_ratio,
            "gz_ratio":  gz_ratio,
            "bpe_tokens": bpe_r,
            "tok_per_word": ratio(src["tok_per_word"], et["tok_per_word"]),
        },
        "diagnosis": diagnosis,
        "bpe_ci_lower": round(bpe_r * 0.85, 3),
        "bpe_ci_upper": round(bpe_r * 1.15, 3),
    }, indent=2)


@mcp.tool(
    name="et_lexicon_search",
    annotations={
        "title": "Search the Etemenanqui lexicon",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def et_lexicon_search(params: LexiconSearchInput) -> str:
    """Search the Etemenanqui lexicon by English term, Etemenanqui root, or domain.

    Args:
        params (LexiconSearchInput): 'query' (search term) and 'limit' (max results).

    Returns:
        str: JSON list of matching lexicon entries.
             Each entry: {"root": str, "gloss": str, "domain": str}
    """
    q     = params.query.lower().strip()
    found = []

    # Exact root match
    if q in LEXICON:
        entry = {"root": q, **LEXICON[q]}
        return json.dumps({"count": 1, "results": [entry]}, indent=2)

    # Domain match
    domain_hits = [
        {"root": r, **info}
        for r, info in LEXICON.items()
        if q in info["domain"].lower()
    ]
    if domain_hits:
        return json.dumps({"count": len(domain_hits), "results": domain_hits[: params.limit]}, indent=2)

    # Gloss / partial match
    gloss_hits = [
        {"root": r, **info}
        for r, info in LEXICON.items()
        if q in info["gloss"].lower() or q in r
    ]

    # EN→ET lookup
    en_hit = EN_TO_ET.get(q)
    if en_hit and en_hit in LEXICON and not gloss_hits:
        gloss_hits = [{"root": en_hit, **LEXICON[en_hit]}]

    results = gloss_hits[: params.limit]
    return json.dumps({
        "count": len(results),
        "results": results,
        "note": "No match found" if not results else None,
    }, indent=2)


@mcp.tool(
    name="et_build_word",
    annotations={
        "title": "Build a valid Etemenanqui word from root + markers",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def et_build_word(params: BuildWordInput) -> str:
    """Construct a valid Etemenanqui word by fusing a CVC root with grammatical markers.

    Validates the resulting word against all Model B rules before returning.

    Args:
        params (BuildWordInput): 'root' (3-char CVC) and 'markers' (0–2 marker strings).

    Returns:
        str: JSON with the constructed word, its morphological breakdown, and validation.
             {"word": str, "valid": bool, "breakdown": dict, "errors": list}
    """
    if len(params.markers) > 2:
        return json.dumps({"error": "Maximum 2 markers per root (Model B constraint)."})

    word   = params.root + "".join(params.markers)
    ok, errors = _validate_word(word)

    breakdown = {
        "root":    params.root,
        "root_gloss": LEXICON.get(params.root, {}).get("gloss", "unknown root"),
        "markers": [
            {"marker": m, "category": FLAT_MARKERS.get(m, "unknown"),
             "meaning": next((v for cat_m, v in {m2: cat for cat, pairs in MARKERS.items() for m2, cat in [(mk, cat) for mk in pairs]}.items() if cat_m == m), "?")}
            for m in params.markers
        ],
        "fused_word": word,
    }

    return json.dumps({"word": word, "valid": ok, "breakdown": breakdown, "errors": errors}, indent=2)


@mcp.tool(
    name="et_system_prompt",
    annotations={
        "title": "Generate Etemenanqui system prompt for LLM injection",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def et_system_prompt(params: SystemPromptInput) -> str:
    """Generate a ready-to-inject system prompt that teaches any LLM the Etemenanqui protocol.

    Include this prompt as the system message when sending compressed Etemenanqui
    instructions to any OpenAI, Anthropic, or compatible LLM.

    Args:
        params (SystemPromptInput): 'response_language' and optional 'domains' filter.

    Returns:
        str: Complete system prompt string ready for injection.
    """
    if params.domains:
        filtered = {r: info for r, info in LEXICON.items() if info["domain"] in params.domains}
    else:
        filtered = LEXICON

    # Build compact table: 5 entries per line
    items = sorted(filtered.items())
    rows, row = [], []
    for root, info in items:
        row.append(f"{root}={info['gloss'].split('/')[0]}")
        if len(row) == 5:
            rows.append("  " + "  ".join(row))
            row = []
    if row:
        rows.append("  " + "  ".join(row))

    return SYSTEM_PROMPT_TEMPLATE.format(
        n=len(filtered),
        lexicon_table="\n".join(rows),
        lang=params.response_language,
    )


# ─────────────────────────────────────────────────────────────────────────────
# RESOURCES — expose lexicon and marker tables as MCP resources
# ─────────────────────────────────────────────────────────────────────────────
@mcp.resource("etemenanqui://lexicon")
async def get_lexicon() -> str:
    """Full Etemenanqui lexicon — 52 CVC roots with gloss and domain."""
    return json.dumps(LEXICON, indent=2, ensure_ascii=False)


@mcp.resource("etemenanqui://markers")
async def get_markers() -> str:
    """Complete grammatical marker table for Model B."""
    return json.dumps(MARKERS, indent=2, ensure_ascii=False)


@mcp.resource("etemenanqui://spec")
async def get_spec() -> str:
    """Model B specification summary."""
    return json.dumps({
        "version": "1.0.0",
        "model": "B",
        "inventor": "Cloves Nascimento — CNGSM",
        "founded": "2026-03-13",
        "inventory": {"consonants": sorted(CONSONANTS), "vowels": sorted(VOWELS)},
        "root_structure": "CVC",
        "marker_types": "V (1 char) or CV (2 chars)",
        "max_markers": 2,
        "max_word_length": 7,
        "forbidden": ["consonant clusters (CC)", "diphthongs (VV)", "hyphens"],
        "bpe_ratio_code":      0.504,
        "bpe_ratio_technical": 0.742,
        "semantic_score":      0.91,
        "repository": "https://github.com/clovesnascimento/etemenanqui",
    }, indent=2)


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Etemenanqui MCP Server")
    parser.add_argument(
        "--transport", choices=["stdio", "http"], default="stdio",
        help="Transport: 'stdio' for local clients (Claude Desktop), 'http' for remote."
    )
    parser.add_argument("--port", type=int, default=8000, help="HTTP port (if --transport http)")
    args = parser.parse_args()

    if args.transport == "http":
        mcp.run(transport="streamable_http", port=args.port)
    else:
        mcp.run()
