<div align="center">

<img src="./logo_gold.svg" width="220" alt="Etemenanqui logo"/>

# ETEMENANQUI
### O Protocolo de Compressão Cognitiva

[![License: MIT](https://img.shields.io/badge/license-MIT-EF9F27?style=flat-square&labelColor=0A0C0E)](./LICENSE)
[![Modelo B](https://img.shields.io/badge/modelo-B%20(CVC%2BV%2FCV)-EF9F27?style=flat-square&labelColor=0A0C0E)](./docs/metodologia.md)
[![Inventário H2](https://img.shields.io/badge/inventário-H2%20(10C×4V)-EF9F27?style=flat-square&labelColor=0A0C0E)](./lexicon.json)
[![CI](https://img.shields.io/github/actions/workflow/status/clovesnascimento/etemenanqui/validate.yml?branch=main&label=corpus%20CI&style=flat-square&labelColor=0A0C0E&color=EF9F27)](https://github.com/clovesnascimento/etemenanqui/actions)
[![Semântica](https://img.shields.io/badge/semântica-0.91%20APTO-2ea44f?style=flat-square&labelColor=0A0C0E)](./etemenanqui_eval.py)

**Uma linguagem artificial de protocolo projetada para comunicação eficiente**
**e de baixo custo computacional com ecossistemas de IA.**

*Criador: **Cloves Nascimento** — Arquiteto de Ecossistemas Cognitivos, CNGSM*
*Etemenanqui Lançado: 13 de março de 2026 · Sexta-feira 13*

[Motivação](#i-a-motivação-epistemológica-a-nova-babel) · [Arquitetura](#ii-arquitetura-modelo-b) · [Resultados](#iii-resultados-empíricos) · [Semântica](#iv-validação-semântica) · [Instalação](#instalação) · [Léxico](./lexicon.json)

</div>

---

## I. A Motivação Epistemológica: A Nova Babel

O mito fundador da Torre de Babel (*Gênesis 11:1–9*) narra uma era em que a humanidade possuía uma única linguagem, permitindo construir estruturas formidáveis — até que a fragmentação de línguas interrompeu a obra. Hoje, os tokenizadores modernos de IA recriaram essa exata "confusão": dividem o conhecimento de forma opaca e fragmentada, desperdiçando processamento e janela de contexto.

A linguagem natural humana carrega cerca de **50% de redundância estrutural** (Shannon, 1948). Quando enviamos *system prompts*, lógicas de código ou arquiteturas *Plan-and-Solve* para LLMs usando inglês técnico, pagamos esse custo de redundância integralmente em tokens.

**O Etemenanqui é uma resposta de engenharia matemática para evitar esse desperdício.**

Ao nomear a linguagem *Etemenanqui* — em sumério: *"templo da fundação do céu e da terra"*, o zigurate histórico da Babilônia associado à Torre de Babel — o projeto constrói uma nova torre: um protocolo unificado, matematicamente econômico, que restaura a eficiência de uma comunicação estruturada sem ruídos.

---

## II. Arquitetura — Modelo B

O Etemenanqui não é uma língua natural humana, tampouco uma linguagem de programação. É uma **linguagem de protocolo** — seu habitat exclusivo é a comunicação densa com máquinas.

| Componente | Especificação | Justificativa |
|---|---|---|
| Consoantes | `t k n m s v l r z b` (10) | Inventário H2 — sem ambiguidade de codificação |
| Vogais | `a e i o` (4) | Cobertura mínima suficiente |
| Estrutura de raiz | **CVC** — 3 caracteres | Unidade atômica limpa para o BPE |
| Marcadores | **V** ou **CV** — fusão direta | Elimina o hífen (−26% custo BPE) |
| Teto morfológico | máx. 2 marcadores → ≤ 7 chars | Cega a língua contra fragmentação opaca |
| Fonotática | sem clusters CC, sem ditongos VV | Segmentação perfeita pelo tokenizador |

### Por que o hífen foi eliminado

```
Modelo A (anterior):   tavo-ro   →  4 tokens  [tav][o][-][ro]
Modelo B (definitivo): tavro     →  2 tokens  [tav][ro]
```

### Marcadores gramaticais

| Marcador | Função | Tipo |
|---|---|---|
| `o` `a` `e` `i` | AGENTE · OBJETO · DATIVO · GENITIVO | Caso (V) |
| `ta` `so` `ki` | PASSADO · PRESENTE · FUTURO | Tempo (CV) |
| `me` `re` | PLURAL · DUAL | Número (CV) |
| `zi` `bo` `vi` | NEGAÇÃO · INTERROGATIVO · IMPERATIVO | Modalidade (CV) |
| `li` `si` | AUMENTATIVO · DIMINUTIVO | Grau (CV) |
| `ba` `ka` `mo` | NOMINALIZADOR · AGENTIVO · QUALITATIVO | Derivação (CV) |

---

## III. Resultados Empíricos

### Domínio de Código — o habitat nativo

| Métrica | Inglês (código) | Etemenanqui | Ratio |
|---|---|---|---|
| H_char (Shannon) | 4.373 | 3.674 | **0.840 ▼** |
| gz_ratio | 0.515 | 0.402 | **0.779 ▼** |
| gz_bytes absolutos | 722 B | 330 B | **0.457 ▼** |
| BPE tokens (simulado) | 409 | 206 | **0.504 ▼** |
| Tokens/palavra | 1.99 | 0.92 | **0.462 ▼** |

### Domínio Técnico — Plan-and-Solve

| Métrica | Inglês Técnico | Etemenanqui | Ratio |
|---|---|---|---|
| H_char (Shannon) | 4.388 | 3.523 | **0.803 ▼** |
| gz_ratio | 0.441 | 0.357 | **0.808 ▼** |
| gz_bytes absolutos | 1.050 B | 529 B | **0.504 ▼** |
| BPE tokens (simulado) | 678 | 503 | **0.742 ▼** |
| Tokens/palavra | 1.79 | 1.41 | **0.787 ▼** |

### Lei de escala

| Domínio | tok/pal EN | tok/pal ET | BPE ratio | Diagnóstico |
|---|---|---|---|---|
| Inglês geral | 1.44 | — | — | referência |
| Inglês técnico | 1.79 | 1.41 | **0.742** | ✓✓✓ |
| Inglês código | 1.99 | 0.92 | **0.504** | ✓✓✓ |

> **Lei identificada:** a eficiência cresce proporcionalmente à densidade do domínio. O paradoxo central: o Etemenanqui usa *mais palavras* que o inglês de código (225 vs 206) mas consome *metade dos tokens* (206 vs 409) — otimizado para as engrenagens do tokenizador, não para a leitura humana.

> **Fronteira epistêmica:** o tokenizador `cl100k_base` foi treinado primariamente em inglês. A economia plena se realizaria com um tokenizador co-treinado. No contexto atual, o ganho real fica entre **0.63–0.85** no domínio técnico.

---

## IV. Validação Semântica

Testado em 15 domínios críticos via LLM-as-Judge — princípio *vena sike bava* (preservação de significado):

| Dimensão | Score | Critério |
|---|---|---|
| D1 — Fidelidade de Execução | **2.95 / 3.0** | Executou a tarefa exata na ordem correta |
| D2 — Aderência ao Protocolo | **2.80 / 3.0** | Manteve estrutura, sem prose inútil |
| D3 — Taxa de Alucinação | **3.00 / 3.0** | Zero invenção de escopo |

**Score geral normalizado: 0.91 — ✓✓✓ APTO PARA PRODUÇÃO**

---

## V. Implementação em Agentes

```python
from etemenanqui_translator import EtemenanquiAgent
import openai

agent = EtemenanquiAgent(
    llm_client=openai.OpenAI(api_key="sk-..."),
    verbose=True
)

resposta = agent.chat("Initialize context. Validate all tokens. Generate report.")
```

O ganho prático mais imediato está em **system prompts fixos de agentes** — com ratio 0.742, num agente com 10.000 chamadas/dia: **~1.75 milhões de tokens economizados por dia**.

---

## Instalação

```bash
git clone https://github.com/clovesnascimento/etemenanqui.git
cd etemenanqui
pip install openai

# Pipeline de métricas (L1+L2+L3)
python etemenanqui_pipeline.py

# Tradutor EN/PT → Etemenanqui
python etemenanqui_translator.py

# Avaliação semântica
python etemenanqui_eval.py --mode dry
python etemenanqui_eval.py --mode auto --provider openai --key sk-...
```

---

## Estrutura do repositório

```
etemenanqui/
├── README.md                        ← este manifesto
├── logo_gold.svg                    ← logo oficial (dark + ouro, animado)
├── logo.svg                         ← logo minimalista
├── social_preview.svg               ← banner 1280×640
├── lexicon.json                     ← 52 raízes CVC + marcadores
├── etemenanqui_pipeline.py          ← pipeline L1+L2+L3
├── etemenanqui_translator.py        ← módulo EN/PT → Etemenanqui
├── etemenanqui_eval.py              ← roteiro de avaliação semântica
├── corpus/
│   ├── corpus_tecnico_EN.txt
│   └── corpus_tecnico_ET.txt
└── .github/workflows/validate.yml  ← CI automático
```

---

## VI. Conclusão Filosófica

> *Se uma linguagem atingir compressão perfeita e eliminar toda redundância,*
> *ela preserva espaço para a poesia, a ambiguidade e a emoção humana?*

Os dados respondem com precisão algorítmica: **não**.

A redundância linguística é o canal de segurança e o espaço onde a variação expressiva habita. Ao eliminá-la, o Etemenanqui sacrificou a literatura em nome da mais pura eficiência computacional. É uma linguagem de design, não de cultura.

A nova torre foi erguida. E agora, ela fala perfeitamente na língua das máquinas.

---

## Referências

- Shannon, C.E. (1948). *A Mathematical Theory of Communication*. Bell System Technical Journal.
- Sennrich, R. et al. (2016). *Neural Machine Translation of Rare Words with Subword Units*. ACL.
- Zipf, G.K. (1935). *The Psycho-Biology of Language*.
- *Gênesis 11:1–9* — narrativa da Torre de Babel.
- George, A. (2005). *In Search of the Fabled Tower*. British Museum Press.

---

<div align="center">

**CNGSM — Cognitive Neural & Generative Systems Management**

*Cloves Nascimento — Arquiteto de Ecossistemas Cognitivos · 13 de março de 2026*

</div>
