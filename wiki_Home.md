# Etemenanqui Wiki

> **"The new tower has been built. And now, it speaks perfectly in the language of machines."**

Welcome to the official wiki of **Etemenanqui** — the Cognitive Compression Protocol for AI systems.

---

## What Is Etemenanqui?

Etemenanqui is an **artificial protocol language** engineered to reduce token consumption when communicating with Large Language Models (LLMs). It is not a human language — it is a machine language, designed for the BPE tokenizer, not for the human reader.

| Property | Value |
|---|---|
| Model | **B** (stable) |
| Inventory | H2 — 10 consonants + 4 vowels |
| Root structure | CVC (3 chars) |
| Max word length | 7 chars |
| BPE ratio — code domain | **0.504** |
| BPE ratio — technical domain | **0.742** |
| Semantic score | **0.91 — Production-ready** |
| License | MIT |
| Founded | March 13, 2026 |
| Author | Cloves Nascimento — CNGSM |

---

## Quick Navigation

| Page | Description |
|---|---|
| [[Home]] | This page — overview and status |
| [[Getting-Started]] | Install, configure, first compression in 5 minutes |
| [[Model-B-Specification]] | Full language spec: inventory, roots, markers, syntax |
| [[Lexicon]] | All 52 CVC roots with gloss and domain |
| [[MCP-Server]] | MCP tool reference — 7 tools, 3 resources |
| [[Compression-Pipeline]] | L1 Shannon · L2 gzip · L3 BPE — how to measure |
| [[Agent-Integration]] | 4 patterns for integrating into AI agents |
| [[Semantic-Evaluation]] | How to run the 15-case evaluation suite |
| [[Extending-the-Lexicon]] | Rules for adding new roots |
| [[Benchmarks]] | Empirical results across 3 domains |
| [[Roadmap]] | Current status and next milestones |
| [[FAQ]] | Frequently asked questions |
| [[Philosophy]] | The Babel myth and the conclusion |

---

## Current Status — v1.0.0

| Component | Status |
|---|---|
| Model B specification | ✅ Stable |
| Seed lexicon (52 roots) | ✅ Validated |
| Compression pipeline L1+L2+L3 | ✅ Complete |
| Translator EN/PT → ET | ✅ Shipped |
| MCP Server (7 tools) | ✅ Shipped |
| Semantic evaluation 0.91 | ✅ Passing |
| Engineer manual (English) | ✅ 828 lines |
| CI — GitHub Actions | ✅ Passing |
| tiktoken real benchmark | 🔲 Pending |
| Domain lexicon packs | 🔲 Planned |
| Tokenizer co-training | 🔲 Research |

---

## 60-Second Example

**English (21 tokens):**
```
Initialize system. Validate all tokens. Generate report.
```
**Etemenanqui (6 tokens):**
```
ran sis . ven toka me . ner resa .
```
**Ratio: 0.286 — 71% fewer tokens.**

---

*CNGSM · Cloves Nascimento · 2026 · https://github.com/clovesnascimento/etemenanqui*
