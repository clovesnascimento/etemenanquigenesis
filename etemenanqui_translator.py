"""
etemenanqui_translator.py
─────────────────────────────────────────────────────────────────────────────
Módulo de tradução EN/PT → Etemenanqui para uso em agentes de IA generativa.

Uso básico:
    from etemenanqui_translator import traduzir_para_et, construir_system_prompt

    prompt_comprimido = traduzir_para_et("Initialize system. Validate corpus.")
    system = construir_system_prompt()

Autor: CNGSM — Cloves Nascimento, 2026
Repositório: https://github.com/clovesnascimento/etemenanqui
─────────────────────────────────────────────────────────────────────────────
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# INVENTÁRIO H2
# ─────────────────────────────────────────────────────────────────────────────
C  = set("tknmsvlrzb")
V  = set("aeio")
OK = C | V

# ─────────────────────────────────────────────────────────────────────────────
# DICIONÁRIO DE TRADUÇÃO — EN + PT → raiz ET
# Cada entrada: variantes de superfície → raiz CVC
# ─────────────────────────────────────────────────────────────────────────────
EN_PT_TO_ET: dict[str, str] = {
    # ── executar / run
    "execute": "ran", "run": "ran", "executar": "ran", "rodar": "ran",
    "start": "ran", "launch": "ran", "iniciar": "ran", "inicializar": "ran",
    "initialize": "ran", "init": "ran",

    # ── chamar / call
    "call": "kal", "invoke": "kal", "chamar": "kal", "invocar": "kal",
    "trigger": "kal", "dispatch": "kal",

    # ── definir / set
    "set": "set", "define": "set", "configure": "set",
    "definir": "set", "configurar": "set", "assign": "set", "atribuir": "set",

    # ── verificar / validate
    "verify": "ven", "validate": "ven", "check": "ven",
    "verificar": "ven", "validar": "ven", "confirmar": "ven",

    # ── retornar / return
    "return": "ret", "retornar": "ret", "output": "ret",

    # ── bloco
    "block": "bol", "bloco": "bol",

    # ── fase / phase
    "phase": "vaz", "stage": "vaz", "fase": "vaz", "etapa": "vaz",
    "step": "vaz", "passo": "vaz",

    # ── escopo / scope
    "scope": "sok", "escopo": "sok", "context": "sok", "contexto": "sok",

    # ── tarefa / task
    "task": "tar", "tarefa": "tar", "job": "tar", "trabalho": "tar",

    # ── resultado / result
    "result": "res", "resultado": "res", "output": "res", "saída": "tov",
    "response": "res", "resposta": "res",

    # ── sistema / system
    "system": "sis", "sistema": "sis",

    # ── arquitetura / architecture
    "architecture": "rak", "arquitetura": "rak",

    # ── memória / memory
    "memory": "mem", "memória": "mem", "store": "mem", "armazenar": "mem",

    # ── cache
    "cache": "kak",

    # ── chave / key
    "key": "kev", "chave": "kev",

    # ── versão / version
    "version": "ver", "versão": "ver",

    # ── binário / binary
    "binary": "bin", "binário": "bin", "encode": "bin", "codificar": "bin",

    # ── entrada / input
    "input": "nib", "entrada": "nib", "query": "nib", "consulta": "nib",

    # ── token
    "token": "tok", "tokens": "tok",

    # ── semântico / semantic
    "semantic": "sem", "semântico": "sem", "meaning": "sem", "significado": "sem",

    # ── sequência / sequence
    "sequence": "sek", "sequência": "sek", "order": "sek", "ordem": "sek",

    # ── nó / node
    "node": "nek", "nó": "nek", "vertex": "nek",

    # ── nível / level
    "level": "nik", "nível": "nik", "layer": "nik", "camada": "nik",

    # ── razão / ratio
    "ratio": "raz", "razão": "raz", "rate": "raz",

    # ── tamanho / size
    "size": "tam", "tamanho": "tam", "length": "tam", "comprimento": "tam",

    # ── analisar / analyze
    "analyze": "nal", "analyse": "nal", "analisar": "nal",
    "parse": "nal", "inspect": "nal", "inspecionar": "nal",

    # ── testar / test
    "test": "tes", "testar": "tes",

    # ── base / foundation
    "base": "baz", "foundation": "baz", "baseline": "baz",
    "base": "baz", "fundação": "baz",

    # ── comparar / compare
    "compare": "kom", "comparar": "kom",

    # ── selecionar / select
    "select": "sel", "selecionar": "sel", "filter": "sel", "filtrar": "sel",

    # ── ordenar / sort
    "sort": "zor", "ordenar": "zor", "rank": "zor", "ranquear": "zor",

    # ── mesclar / merge
    "merge": "mer", "mesclar": "mer", "combine": "mer", "combinar": "mer",

    # ── coletar / collect
    "collect": "kol", "coletar": "kol", "aggregate": "kol", "agregar": "kol",
    "gather": "kol",

    # ── limite / limit
    "limit": "lim", "limite": "lim", "cap": "lim", "max": "lim",

    # ── estrutura / structure
    "structure": "tez", "estrutura": "tez", "format": "tez", "formato": "tez",

    # ── módulo / module
    "module": "mob", "módulo": "mob", "component": "mob", "componente": "mob",

    # ── dependência / dependency
    "dependency": "neb", "dependência": "neb", "depends": "neb",

    # ── lista / list
    "list": "lis", "lista": "lis",

    # ── núcleo / core
    "core": "kor", "núcleo": "kor", "kernel": "kor",

    # ── planejar / plan
    "plan": "bav", "planejar": "bav", "planning": "bav",

    # ── resolver / solve
    "solve": "sol", "resolver": "sol", "resolve": "sol",

    # ── revisar / review
    "review": "rev", "revisar": "rev", "revise": "rev",

    # ── otimizar / optimize
    "optimize": "tot", "otimizar": "tot", "optimise": "tot",

    # ── técnico / technical
    "technical": "tek", "técnico": "tek",

    # ── ler / read
    "read": "ler", "ler": "ler", "load": "ler", "carregar": "ler",

    # ── registrar / log
    "log": "loz", "registrar": "loz", "record": "loz", "gravar": "loz",

    # ── variável / variable
    "variable": "var", "variável": "var", "var": "var",

    # ── sanitizar / sanitize
    "sanitize": "san", "sanitizar": "san", "clean": "san", "limpar": "san",

    # ── visualizar / visualize
    "visualize": "viz", "visualizar": "viz", "display": "viz", "exibir": "viz",
    "show": "viz", "mostrar": "viz",

    # ── gerar / generate
    "generate": "ner", "gerar": "ner", "create": "ner", "criar": "ner",
    "build": "ner", "construir": "ner",
}

# Mapeamento de palavras funcionais → marcadores ou omissão
MARKERS_MAP: dict[str, Optional[str]] = {
    # Negação → zi
    "not": "zi", "no": "zi", "don't": "zi", "doesn't": "zi",
    "não": "zi", "sem": "zi",

    # Plural → me
    "all": "me", "todos": "me", "every": "me",

    # Passado → ta (sufixo de verbo)
    "did": "ta", "was": "ta", "were": "ta", "had": "ta",

    # Futuro → ki
    "will": "ki", "shall": "ki",

    # Palavras funcionais → omitir (None)
    "the": None, "a": None, "an": None,
    "to": None, "of": None, "in": None, "at": None,
    "and": None, "or": None, "with": None, "via": None,
    "by": None, "for": None, "from": None, "into": None,
    "before": None, "after": None, "per": None,
    "o": None, "a_art": None, "de": None, "do": None,
    "da": None, "em": None, "no": None, "na": None,
    "e": None, "ou": None, "com": None, "por": None,
    "para": None, "que": None, "um": None, "uma": None,
}

# ─────────────────────────────────────────────────────────────────────────────
# DATACLASS de resultado
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class TraducaoResultado:
    original: str
    etemenanqui: str
    tokens_orig: int
    tokens_et: int
    ratio: float
    nao_traduzidos: list[str]
    cobertura: float          # % de palavras de conteúdo cobertas pelo léxico


# ─────────────────────────────────────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────────────────────────────────────
def _normalizar(palavra: str) -> str:
    """Remove pontuação e converte para minúsculas."""
    return re.sub(r"[^a-záéíóúãõàâêô]", "", palavra.lower()).strip()


def _estimar_bpe(texto: str) -> int:
    """
    Estimador BPE simplificado calibrado para o simulador do projeto.
    EN: palavras técnicas longas custam 2-4 tokens.
    ET: raízes CVC de 3-7 chars custam 1-3 tokens.
    """
    total = 0
    for w in texto.split():
        wl = re.sub(r"[^a-z]", "", w.lower())
        if not wl:
            continue
        n = len(wl)
        # Detecta se é Etemenanqui (só chars H2)
        is_et = all(c in OK for c in wl)
        if is_et:
            if n <= 3:   total += 1
            elif n <= 5: total += 2
            else:        total += 3
        else:
            if n <= 3:   total += 1
            elif n <= 6: total += 2
            elif n <= 9: total += 3
            else:        total += 4
    return total


def _validar_palavra_et(palavra: str) -> bool:
    """Verifica se uma palavra ET está dentro das regras do Modelo B."""
    return (
        len(palavra) <= 7
        and all(c in OK for c in palavra)
    )


# ─────────────────────────────────────────────────────────────────────────────
# NÚCLEO DA TRADUÇÃO
# ─────────────────────────────────────────────────────────────────────────────
def traduzir_palavra(palavra: str) -> tuple[str, bool]:
    """
    Traduz uma palavra para Etemenanqui.
    Retorna (tradução_ou_original, foi_traduzida).
    """
    norm = _normalizar(palavra)
    if not norm:
        return palavra, False

    # 1. Verifica léxico principal
    if norm in EN_PT_TO_ET:
        return EN_PT_TO_ET[norm], True

    # 2. Verifica palavras funcionais
    if norm in MARKERS_MAP:
        marcador = MARKERS_MAP[norm]
        return marcador if marcador else "", True

    # 3. Tenta formas derivadas (remove -ing, -ed, -s, -tion)
    for sufixo, substituto in [
        ("ing", ""), ("tion", ""), ("tions", ""), ("ing", "e"),
        ("ed", ""), ("ed", "e"), ("s", ""), ("es", ""),
        ("ize", ""), ("ise", ""), ("ization", ""), ("ar", ""),
        ("er", ""), ("or", ""),
    ]:
        if norm.endswith(sufixo):
            stem = norm[:-len(sufixo)] + substituto
            if stem in EN_PT_TO_ET:
                return EN_PT_TO_ET[stem], True

    return palavra, False


def traduzir_para_et(
    texto: str,
    modo: str = "prompt",
    retornar_resultado: bool = False,
) -> str | TraducaoResultado:
    """
    Traduz um prompt EN/PT para Etemenanqui.

    Parâmetros:
        texto           — texto de entrada em inglês ou português
        modo            — "prompt" (comprime max) | "legivel" (mantém não-trad.)
        retornar_resultado — se True, retorna TraducaoResultado com métricas

    Retorna:
        str com o prompt comprimido, ou TraducaoResultado se solicitado.

    Exemplo:
        traduzir_para_et("Initialize system. Validate all tokens.")
        → "ran sis . ven toka me ."
    """
    nao_traduzidos = []
    tokens_saida = []
    palavras_conteudo = 0
    palavras_traduzidas = 0

    # Tokeniza preservando pontuação como separador de cláusulas
    sentencas = re.split(r"([.!?])", texto)

    for parte in sentencas:
        parte = parte.strip()
        if not parte:
            continue

        # Pontuação estrutural → mantém como delimitador
        if parte in ".!?":
            tokens_saida.append(".")
            continue

        palavras = parte.split()
        for palavra in palavras:
            norm = _normalizar(palavra)
            if not norm:
                continue

            # Ignora números — mantém literal
            if re.match(r"^\d+", palavra):
                tokens_saida.append(palavra)
                continue

            # Traduz
            traduzida, ok = traduzir_palavra(palavra)

            # Conta cobertura (só para palavras de conteúdo — não funcionais)
            if norm not in MARKERS_MAP:
                palavras_conteudo += 1
                if ok:
                    palavras_traduzidas += 1

            if not ok:
                nao_traduzidos.append(palavra)
                if modo == "legivel":
                    tokens_saida.append(f"[{palavra}]")
                # modo "prompt": omite palavras não traduzidas
            elif traduzida:  # pode ser vazio (palavras funcionais omitidas)
                tokens_saida.append(traduzida)

    # Monta saída — remove espaços duplos
    saida = " ".join(t for t in tokens_saida if t)
    saida = re.sub(r"\s+\.", " .", saida).strip()

    if retornar_resultado:
        tok_orig = _estimar_bpe(texto)
        tok_et   = _estimar_bpe(saida)
        cobertura = (palavras_traduzidas / palavras_conteudo * 100) if palavras_conteudo else 0.0
        return TraducaoResultado(
            original=texto,
            etemenanqui=saida,
            tokens_orig=tok_orig,
            tokens_et=tok_et,
            ratio=round(tok_et / tok_orig, 3) if tok_orig else 1.0,
            nao_traduzidos=sorted(set(nao_traduzidos)),
            cobertura=round(cobertura, 1),
        )

    return saida


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT BUILDER — injeta o léxico ativo no contexto do LLM
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT_TEMPLATE = """\
# ETEMENANQUI — Cognitive Compression Protocol v1.0
# Modelo B | Inventário H2 | CNGSM 2026

Você está recebendo instruções parcialmente comprimidas em Etemenanqui.
Interprete cada raiz CVC conforme o léxico abaixo e execute normalmente.

## Léxico ativo ({n_roots} raízes)
{lexico_tabela}

## Marcadores gramaticais
  o=AGENTE  a=OBJETO  e=DATIVO  i=GENITIVO
  ta=PASSADO  so=PRESENTE  ki=FUTURO
  me=PLURAL  zi=NEGAÇÃO  li=AUMENTATIVO
  ba=NOMINALIZADOR  ka=AGENTIVO  mo=QUALITATIVO

## Regras de fusão (Modelo B)
  raiz(CVC) + marcador(V ou CV) — sem hífen, máx 2 marcadores, máx 7 chars
  Ex: rano = executar(AGENTE) | venzi = não-verificar | tokme = tokens(PLURAL)

## Exemplo
  "rano vena teza ." → initialize and validate the structure.
  "bav nalo toka me ." → plan and analyze all tokens.

Responda sempre em português claro, sem mencionar o protocolo de compressão.
"""

def construir_system_prompt(lexico_customizado: Optional[dict] = None) -> str:
    """
    Gera o system prompt com o léxico Etemenanqui injetado.
    Aceita léxico customizado para domínios específicos.
    """
    lexico = lexico_customizado or EN_PT_TO_ET

    # Agrupa por domínio implícito (primeiros 5 por linha para compactar)
    items = [(k, v) for k, v in lexico.items() if len(k) > 2]  # só vars EN longas
    # Deduplica — mantém só primeiro mapeamento por raiz ET
    seen_et = {}
    for src, et in items:
        if et not in seen_et:
            seen_et[et] = src

    linhas = []
    row = []
    for et, src in sorted(seen_et.items()):
        row.append(f"{et}={src}")
        if len(row) == 5:
            linhas.append("  " + "  ".join(row))
            row = []
    if row:
        linhas.append("  " + "  ".join(row))

    return SYSTEM_PROMPT_TEMPLATE.format(
        n_roots=len(seen_et),
        lexico_tabela="\n".join(linhas),
    )


# ─────────────────────────────────────────────────────────────────────────────
# INTEGRAÇÃO COM AGENTE — wrapper drop-in
# ─────────────────────────────────────────────────────────────────────────────
class EtemenanquiAgent:
    """
    Wrapper para integrar compressão Etemenanqui em qualquer agente LLM.

    Uso com OpenAI-compatible API:
        agent = EtemenanquiAgent(llm_client=openai.OpenAI())
        resposta = agent.chat("Initialize context. Validate all tokens.")

    Uso standalone (só compressão, sem LLM):
        agent = EtemenanquiAgent()
        print(agent.comprimir("Initialize system. Load grammar rules."))
    """

    def __init__(self, llm_client=None, model: str = "gpt-4o", verbose: bool = False):
        self.llm    = llm_client
        self.model  = model
        self.verbose = verbose
        self._system = construir_system_prompt()

    def comprimir(self, texto: str) -> TraducaoResultado:
        """Comprime texto e retorna resultado com métricas."""
        return traduzir_para_et(texto, retornar_resultado=True)

    def chat(self, prompt: str, extra_system: str = "") -> str:
        """
        Comprime o prompt e envia ao LLM configurado.
        Requer llm_client compatível com OpenAI SDK.
        """
        if self.llm is None:
            raise RuntimeError("llm_client não configurado. Use EtemenanquiAgent(llm_client=...)")

        resultado = self.comprimir(prompt)

        if self.verbose:
            print(f"[ET] {resultado.tokens_orig}→{resultado.tokens_et} tok "
                  f"(ratio {resultado.ratio}) | cobertura {resultado.cobertura}% "
                  f"| não-trad: {resultado.nao_traduzidos}")

        system = self._system
        if extra_system:
            system += f"\n\n{extra_system}"

        resposta = self.llm.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": resultado.etemenanqui},
            ],
        )
        return resposta.choices[0].message.content


# ─────────────────────────────────────────────────────────────────────────────
# CLI / DEMO
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 68)
    print("  ETEMENANQUI TRANSLATOR — demo")
    print("=" * 68)

    casos = [
        "Initialize context window. Load grammar rules. Set token limit.",
        "Generate master plan. Map dependency graph. Validate sequence order.",
        "Query semantic cache. Compute similarity threshold. Return result.",
        "Analyze prompt structure. Filter redundant tokens. Optimize output.",
        "Log errors to output buffer. Return structured result.",
        # Português
        "Inicializar sistema. Verificar todos os tokens. Gerar resultado.",
        "Planejar fase. Resolver dependências. Retornar estrutura.",
    ]

    for texto in casos:
        r = traduzir_para_et(texto, retornar_resultado=True)
        print(f"\n  IN  : {r.original}")
        print(f"  ET  : {r.etemenanqui}")
        print(f"  BPE : {r.tokens_orig} → {r.tokens_et} tok  "
              f"ratio={r.ratio}  cobertura={r.cobertura}%")
        if r.nao_traduzidos:
            print(f"  ??  : {r.nao_traduzidos}")

    print("\n" + "=" * 68)
    print("  SYSTEM PROMPT (primeiras 20 linhas):")
    print("=" * 68)
    for linha in construir_system_prompt().split("\n")[:20]:
        print(" ", linha)
    print("  ...")
