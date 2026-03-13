# Roadmap

## v1.0.0 — Shipped ✅ (March 13, 2026)

- [x] Model B specification (H2 inventory, CVC roots, direct fusion)
- [x] Seed lexicon — 52 roots across 7 domains
- [x] 3-layer compression pipeline (Shannon, gzip, BPE sim)
- [x] Translator module EN/PT → ET
- [x] MCP Server — 7 tools, 3 resources
- [x] Semantic evaluation suite — 15 cases, 3 dimensions
- [x] Semantic score: **0.91 — Production-ready**
- [x] Engineer manual (English, 828 lines)
- [x] GitHub Actions CI
- [x] README manifesto + badges

---

## v1.1.0 — In Progress 🔲

- [ ] **Real tiktoken benchmark** — replace simulator with `cl100k_base` measurement
- [ ] **Lexicon pack: Medical** — 30+ roots for clinical/pharma prompts
- [ ] **Lexicon pack: Legal** — 30+ roots for contract/compliance prompts
- [ ] **Lexicon pack: Finance** — 30+ roots for trading/risk prompts
- [ ] Portuguese-native translator improvements (better stem matching)
- [ ] VS Code extension — highlight Etemenanqui in `.et` files

---

## v1.2.0 — Planned 📋

- [ ] **Web interface** — paste EN text, get ET + metrics in browser
- [ ] **npm package** — `etemenanqui-js` for TypeScript agents
- [ ] Evaluation results on open-source models (Llama 3, Mistral, Qwen)
- [ ] Comparison study vs LLMLingua compression approach

---

## v2.0.0 — Research 🔬

- [ ] **Tokenizer co-training experiment** — train a BPE tokenizer with Etemenanqui vocabulary included, measure true theoretical ceiling
- [ ] **Etemenanqui-native embedding model** — fine-tuned on compressed corpora
- [ ] Cross-language expansion: Spanish, French, Mandarin source support

---

## Contributing

See [[Extending-the-Lexicon]] for rules on adding new roots.
Open a PR or issue at https://github.com/clovesnascimento/etemenanqui

---

## Scaling Law (empirical)

The core discovery driving the roadmap:

| Domain | BPE ratio | Next target |
|---|---|---|
| General English | baseline | — |
| Technical | 0.742 | 0.65 with expanded lexicon |
| Code | 0.504 | 0.40 with co-trained tokenizer |
| Medical (projected) | ~0.55 | validate in v1.1 |

---

*CNGSM · 2026*
