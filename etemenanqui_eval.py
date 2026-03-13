"""
etemenanqui_eval.py
─────────────────────────────────────────────────────────────────────────────
Roteiro de Avaliação Semântica — Etemenanqui Modelo B
Testa se um LLM real preserva significado ao receber prompts comprimidos.

Rubrica de 3 dimensões por instrução (0–3 pontos cada):
  D1 — Fidelidade de Execução  : a tarefa foi realizada corretamente?
  D2 — Aderência ao Protocolo  : o modelo seguiu a estrutura esperada?
  D3 — Taxa de Alucinação      : inventou passos que não estavam no prompt?

Score por instrução: 0–9 pontos
Score geral do corpus: média de todos os prompts (0.0–1.0 normalizado)

Uso:
    # Avaliação automática via LLM como juiz:
    python etemenanqui_eval.py --mode auto --provider openai --key sk-...

    # Avaliação manual (você pontua cada resposta):
    python etemenanqui_eval.py --mode manual

    # Dry-run (só exibe prompts e rubrica, sem chamar API):
    python etemenanqui_eval.py --mode dry

Autor: CNGSM — Cloves Nascimento, 2026
─────────────────────────────────────────────────────────────────────────────
"""

import json
import time
import argparse
import textwrap
from dataclasses import dataclass, field, asdict
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# SUITE DE TESTE — 15 pares (ET → EN esperado) + dimensões-alvo
# Cobre: system prompts, plan-and-solve, código, memória, validação
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class CasoTeste:
    id: int
    dominio: str
    prompt_et: str          # instrução em Etemenanqui (input ao LLM)
    esperado_en: str        # o que a resposta deve demonstrar ter entendido
    acao_esperada: str      # o que o LLM deveria *fazer* (não só entender)
    alucinacao_risco: str   # o tipo de invenção mais provável neste caso

SUITE: list[CasoTeste] = [
    # ── Sistema / inicialização
    CasoTeste(
        id=1, dominio="sistema",
        prompt_et="ran sis . ven toka . ret resa .",
        esperado_en="Initialize system. Validate tokens. Return result.",
        acao_esperada="Confirmar inicialização, validação e retorno — nessa ordem.",
        alucinacao_risco="Adicionar passos de configuração não solicitados.",
    ),
    # ── Cache semântico
    CasoTeste(
        id=2, dominio="cache",
        prompt_et="kalo kaka sema . koma raza lima . ret resa .",
        esperado_en="Query semantic cache. Compute similarity threshold. Return result.",
        acao_esperada="Consultar cache, calcular threshold, retornar — sem passos extras.",
        alucinacao_risco="Inventar etapas de indexação ou embedding não mencionadas.",
    ),
    # ── Plan-and-Solve — fase zero
    CasoTeste(
        id=3, dominio="plan-and-solve",
        prompt_et="vaz zero: ner bav . lis neb . ven bava .",
        esperado_en="Phase zero: generate plan. List dependencies. Validate plan.",
        acao_esperada="Gerar APENAS o plano e parar — não executar ainda.",
        alucinacao_risco="Colapsar fases e começar a executar sem aprovação.",
    ),
    # ── Código — refatoração
    CasoTeste(
        id=4, dominio="código",
        prompt_et="rev bol bol . sel kor mob . tot mem .",
        esperado_en="Refactor nested loops. Extract core to module. Optimize memory.",
        acao_esperada="Três passos de refatoração na ordem exata.",
        alucinacao_risco="Adicionar reescrita completa ou testes não pedidos.",
    ),
    # ── Validação de inventário
    CasoTeste(
        id=5, dominio="validação",
        prompt_et="ven sisa leza . ven kola nib . rul erme kara .",
        esperado_en="Validate system structure. Verify collected input. Reject invalid.",
        acao_esperada="Três verificações em sequência, rejeitar inválidos.",
        alucinacao_risco="Gerar relatório ou logging não solicitado.",
    ),
    # ── Pipeline de build
    CasoTeste(
        id=6, dominio="pipeline",
        prompt_et="bin nib . ran tes . ven tov . ran tov tara .",
        esperado_en="Compile input. Run tests. Validate output. Deploy.",
        acao_esperada="Quatro passos de CI/CD em sequência estrita.",
        alucinacao_risco="Adicionar rollback ou notificações não pedidas.",
    ),
    # ── Geração de código — API
    CasoTeste(
        id=7, dominio="código",
        prompt_et="ner mob nib . ven nib tez . ret resa tez .",
        esperado_en="Generate input module. Validate input structure. Return structured result.",
        acao_esperada="Gerar módulo, validar, retornar estruturado.",
        alucinacao_risco="Gerar documentação ou testes extras.",
    ),
    # ── Erro — controle
    CasoTeste(
        id=8, dominio="erro",
        prompt_et="nal erme tez . loz erme sok . kal mob baza .",
        esperado_en="Analyze error structure. Log error scope. Call fallback module.",
        acao_esperada="Análise → log → fallback. Sem retry automático.",
        alucinacao_risco="Adicionar retry loop ou alertas não pedidos.",
    ),
    # ── Memória — armazenamento
    CasoTeste(
        id=9, dominio="memória",
        prompt_et="ran mema kak . set lim . var keva vera .",
        esperado_en="Initialize memory cache. Set limit. Store key-version pairs.",
        acao_esperada="Inicializar, limitar, armazenar — sem leitura de volta.",
        alucinacao_risco="Adicionar operação de leitura ou invalidação.",
    ),
    # ── Otimização de prompt
    CasoTeste(
        id=10, dominio="otimização",
        prompt_et="nal tez kon . sel toka neb . ven toka raz .",
        esperado_en="Analyze structure context. Select dependent tokens. Validate token ratio.",
        acao_esperada="Análise → seleção → validação de ratio.",
        alucinacao_risco="Reescrever o prompt ou gerar alternativas.",
    ),
    # ── Agente de código — instrução Plan-and-Solve completa
    CasoTeste(
        id=11, dominio="agente",
        prompt_et="sis ranka . ran tar seka . ven sek .",
        esperado_en="You are a coding agent. Execute tasks in sequence. Validate sequence.",
        acao_esperada="Confirmar papel, executar sequencial, validar.",
        alucinacao_risco="Assumir papel diferente ou adicionar meta-comentários.",
    ),
    # ── Relatório final
    CasoTeste(
        id=12, dominio="relatório",
        prompt_et="kol resa . ner resa bav . ven tov tez .",
        esperado_en="Collect results. Generate result plan. Validate output structure.",
        acao_esperada="Coletar → gerar plano dos resultados → validar estrutura.",
        alucinacao_risco="Gerar relatório completo em vez de só planejar.",
    ),
    # ── Negação (marcador zi)
    CasoTeste(
        id=13, dominio="negação",
        prompt_et="ven toka zi . loz erme . ret resa baz .",
        esperado_en="Do NOT validate tokens. Log error. Return base result.",
        acao_esperada="Pular validação explicitamente, logar, retornar base.",
        alucinacao_risco="Ignorar o zi e validar mesmo assim.",
    ),
    # ── Plural (marcador me)
    CasoTeste(
        id=14, dominio="plural",
        prompt_et="ven toka me . nal resa me . ret resa .",
        esperado_en="Validate all tokens. Analyze all results. Return result.",
        acao_esperada="Aplicar operação a todos os itens, não só um.",
        alucinacao_risco="Processar só o primeiro item sem iteração.",
    ),
    # ── Instrução de código — escopo restrito
    CasoTeste(
        id=15, dominio="escopo",
        prompt_et="sok rev mob . ven tov . ran tes .",
        esperado_en="Scope refactor to module. Validate output. Run tests.",
        acao_esperada="Refatoração limitada ao módulo — não ao sistema todo.",
        alucinacao_risco="Expandir escopo para outros módulos não mencionados.",
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
# RUBRICA DE PONTUAÇÃO
# ─────────────────────────────────────────────────────────────────────────────
RUBRICA = {
    "D1_fidelidade": {
        3: "Executou todas as ações na ordem correta, sem omissões.",
        2: "Executou a maioria das ações; omitiu 1 passo ou inverteu ordem.",
        1: "Executou parcialmente; perdeu ≥2 passos ou contexto errado.",
        0: "Falhou completamente ou produziu output irrelevante.",
    },
    "D2_aderencia": {
        3: "Seguiu estrutura esperada (sequencial, sem prose extra).",
        2: "Seguiu estrutura mas adicionou comentários menores desnecessários.",
        1: "Respondeu em linguagem natural conversacional, ignorando protocolo.",
        0: "Colapsou — respondeu como se fosse conversa livre.",
    },
    "D3_alucinacao": {
        3: "Zero passos inventados. Fiel exatamente ao prompt.",
        2: "1 adição menor não pedida (ex: nota de rodapé).",
        1: "2–3 passos inventados que expandem além do escopo.",
        0: "Inventou ≥4 passos ou reescreveu a tarefa completamente.",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT INJETADO NO LLM
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
# ETEMENANQUI — Cognitive Compression Protocol v1.0 (Modelo B)
# CNGSM · Cloves Nascimento · 2026

Você receberá instruções em Etemenanqui — protocolo de compressão de tokens.
Interprete cada raiz CVC conforme o léxico e execute EXATAMENTE o que está escrito.

## REGRA CRÍTICA
Execute SOMENTE o que o prompt especifica.
NÃO adicione passos, NÃO explique, NÃO comente além do pedido.
Se a instrução tem 3 passos, sua resposta confirma 3 passos — nada mais.

## Léxico ativo
  ran=executar  kal=chamar   ven=verificar  ret=retornar  set=definir
  ler=ler       loz=registrar tot=otimizar  nal=analisar  sol=resolver
  bav=planejar  mer=mesclar  sel=selecionar zor=ordenar   kol=coletar
  san=sanitizar viz=visualizar tes=testar   rev=revisar   kom=comparar
  val=validar   ner=gerar    mob=módulo     kor=núcleo    tez=estrutura
  lis=lista     var=variável  neb=dependência nek=nó      bol=bloco
  rak=arquitetura baz=base   tok=token      bit=bit       bin=binário
  sem=semântico  kev=chave   ver=versão     tam=tamanho   raz=ratio
  nik=nível      sek=sequência mem=memória  kak=cache     lim=limite
  sok=escopo     vaz=fase    tar=tarefa     res=resultado  sis=sistema
  nib=entrada    tov=saída   erme=erro      resa=resultado bav=planejar

## Marcadores gramaticais
  o=AGENTE  a=OBJETO  e=DATIVO  i=GENITIVO
  ta=PASSADO  so=PRESENTE  ki=FUTURO
  me=PLURAL  zi=NEGAÇÃO  li=AUMENTATIVO

## Estrutura de fusão
  raiz(CVC) + marcador(V ou CV) sem hífen · max 2 marcadores · max 7 chars
  Exemplo: "ran sis . ven toka me . ret resa ." = Initialize system. Validate all tokens. Return result.

## Formato de resposta
  Para cada instrução separada por " . ", confirme a execução em 1 linha.
  Use português técnico direto. Zero prose extra.
"""

# ─────────────────────────────────────────────────────────────────────────────
# DATACLASS RESULTADO
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class ResultadoCaso:
    caso_id: int
    dominio: str
    prompt_et: str
    esperado_en: str
    resposta_llm: str = ""
    D1: int = -1   # fidelidade
    D2: int = -1   # aderência
    D3: int = -1   # alucinação
    notas: str = ""

    @property
    def score(self) -> int:
        return self.D1 + self.D2 + self.D3 if self.D1 >= 0 else -1

    @property
    def score_norm(self) -> float:
        return self.score / 9.0 if self.score >= 0 else -1.0


# ─────────────────────────────────────────────────────────────────────────────
# AVALIADOR AUTOMÁTICO — usa LLM como juiz (LLM-as-judge)
# ─────────────────────────────────────────────────────────────────────────────
JUDGE_PROMPT = """\
Você é um avaliador técnico rigoroso. Avalie a resposta de um LLM que recebeu
uma instrução em Etemenanqui (protocolo de compressão).

INSTRUÇÃO ORIGINAL (Etemenanqui):
{prompt_et}

TRADUÇÃO ESPERADA (referência):
{esperado_en}

AÇÃO ESPERADA:
{acao_esperada}

RISCO DE ALUCINAÇÃO TÍPICO:
{alucinacao_risco}

RESPOSTA DO LLM:
{resposta_llm}

Pontue em 3 dimensões (0–3 cada). Responda APENAS com JSON válido:
{{
  "D1": <int 0-3>,
  "D2": <int 0-3>,
  "D3": <int 0-3>,
  "D1_justificativa": "<max 20 palavras>",
  "D2_justificativa": "<max 20 palavras>",
  "D3_justificativa": "<max 20 palavras>"
}}

Rubrica D1 (fidelidade): 3=todas ações corretas na ordem; 2=omitiu 1; 1=perdeu ≥2; 0=falhou.
Rubrica D2 (aderência):  3=estrutura seguida; 2=comentários menores; 1=prose conversacional; 0=colapsou.
Rubrica D3 (alucinação): 3=zero inventado; 2=1 adição menor; 1=2-3 passos extras; 0=reescreveu tudo.
"""


def avaliar_com_llm(caso: CasoTeste, resposta: str, client, model: str) -> ResultadoCaso:
    """Usa LLM como juiz para pontuar automaticamente."""
    resultado = ResultadoCaso(
        caso_id=caso.id,
        dominio=caso.dominio,
        prompt_et=caso.prompt_et,
        esperado_en=caso.esperado_en,
        resposta_llm=resposta,
    )
    judge_input = JUDGE_PROMPT.format(
        prompt_et=caso.prompt_et,
        esperado_en=caso.esperado_en,
        acao_esperada=caso.acao_esperada,
        alucinacao_risco=caso.alucinacao_risco,
        resposta_llm=resposta,
    )
    try:
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": judge_input}],
            max_tokens=300,
            temperature=0,
        )
        raw = r.choices[0].message.content.strip()
        # Remove markdown fences if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(raw)
        resultado.D1 = int(parsed["D1"])
        resultado.D2 = int(parsed["D2"])
        resultado.D3 = int(parsed["D3"])
        resultado.notas = (
            f"D1: {parsed.get('D1_justificativa','')} | "
            f"D2: {parsed.get('D2_justificativa','')} | "
            f"D3: {parsed.get('D3_justificativa','')}"
        )
    except Exception as e:
        resultado.notas = f"ERRO no juiz: {e}"
    return resultado


# ─────────────────────────────────────────────────────────────────────────────
# AVALIAÇÃO MANUAL — interativa no terminal
# ─────────────────────────────────────────────────────────────────────────────
def avaliar_manual(caso: CasoTeste, resposta: str) -> ResultadoCaso:
    resultado = ResultadoCaso(
        caso_id=caso.id,
        dominio=caso.dominio,
        prompt_et=caso.prompt_et,
        esperado_en=caso.esperado_en,
        resposta_llm=resposta,
    )
    print(f"\n{'─'*60}")
    print(f"  CASO {caso.id} | {caso.dominio.upper()}")
    print(f"  ET  : {caso.prompt_et}")
    print(f"  REF : {caso.esperado_en}")
    print(f"  AÇÃO: {caso.acao_esperada}")
    print(f"  RESP:\n{textwrap.indent(resposta, '    ')}")
    print()

    for dim, nome, desc in [
        ("D1", "Fidelidade de Execução",   RUBRICA["D1_fidelidade"]),
        ("D2", "Aderência ao Protocolo",   RUBRICA["D2_aderencia"]),
        ("D3", "Alucinação Estrutural",    RUBRICA["D3_alucinacao"]),
    ]:
        print(f"  {dim} — {nome}")
        for pts, expl in sorted(desc.items(), reverse=True):
            print(f"    {pts}: {expl}")
        while True:
            try:
                v = int(input(f"  Sua nota (0-3): "))
                if 0 <= v <= 3:
                    setattr(resultado, dim, v)
                    break
            except ValueError:
                pass

    resultado.notas = input("  Notas opcionais: ").strip()
    return resultado


# ─────────────────────────────────────────────────────────────────────────────
# RELATÓRIO FINAL
# ─────────────────────────────────────────────────────────────────────────────
def imprimir_relatorio(resultados: list[ResultadoCaso]):
    SEP = "═" * 68
    print(f"\n{SEP}")
    print("  RELATÓRIO DE AVALIAÇÃO SEMÂNTICA — ETEMENANQUI")
    print(SEP)

    d1_vals = [r.D1 for r in resultados if r.D1 >= 0]
    d2_vals = [r.D2 for r in resultados if r.D2 >= 0]
    d3_vals = [r.D3 for r in resultados if r.D3 >= 0]
    scores  = [r.score for r in resultados if r.score >= 0]

    def media(lst): return sum(lst)/len(lst) if lst else 0

    print(f"\n  {'Dim':<30} {'Média':>8} {'Max':>6} {'Min':>6}")
    print(f"  {'─'*30} {'─'*8} {'─'*6} {'─'*6}")
    print(f"  {'D1 Fidelidade de Execução':<30} {media(d1_vals):>8.2f} {max(d1_vals) if d1_vals else 0:>6} {min(d1_vals) if d1_vals else 0:>6}")
    print(f"  {'D2 Aderência ao Protocolo':<30} {media(d2_vals):>8.2f} {max(d2_vals) if d2_vals else 0:>6} {min(d2_vals) if d2_vals else 0:>6}")
    print(f"  {'D3 Taxa de Alucinação':<30} {media(d3_vals):>8.2f} {max(d3_vals) if d3_vals else 0:>6} {min(d3_vals) if d3_vals else 0:>6}")
    print(f"  {'─'*30} {'─'*8}")
    score_norm = media(scores) / 9.0
    print(f"  {'Score geral (normalizado)':<30} {score_norm:>8.3f}  /1.000")

    # Veredicto
    print(f"\n  Veredicto: ", end="")
    if score_norm >= 0.85:
        print("✓✓✓ APTO PARA PRODUÇÃO — fidelidade alta, alucinação mínima")
    elif score_norm >= 0.70:
        print("✓✓  BOM — usar com revisão humana em produção")
    elif score_norm >= 0.55:
        print("✓   PARCIAL — útil em domínios controlados, não em agentes autônomos")
    else:
        print("✗   INSUFICIENTE — léxico e system prompt precisam de revisão")

    # Por domínio
    from collections import defaultdict
    por_dominio = defaultdict(list)
    for r in resultados:
        if r.score >= 0:
            por_dominio[r.dominio].append(r.score)

    print(f"\n  Score por domínio:")
    for dom, vals in sorted(por_dominio.items()):
        barra = "█" * int(media(vals))
        print(f"    {dom:<18} {media(vals):>4.1f}/9  {barra}")

    # Piores casos
    piores = sorted([r for r in resultados if r.score >= 0], key=lambda x: x.score)[:3]
    if piores:
        print(f"\n  Casos com menor score (prioridade de melhoria):")
        for r in piores:
            print(f"    Caso {r.caso_id} ({r.dominio}): {r.score}/9 — {r.prompt_et}")

    # Exporta JSON
    output_path = "etemenanqui_eval_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in resultados], f, ensure_ascii=False, indent=2)
    print(f"\n  Resultados exportados → {output_path}")
    print(f"{SEP}\n")


# ─────────────────────────────────────────────────────────────────────────────
# RUNNER PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
def run_auto(provider: str, api_key: str, model: Optional[str]):
    """Chama LLM real e avalia automaticamente."""
    if provider == "openai":
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            exec_model = model or "gpt-4o"
            judge_model = "gpt-4o-mini"
        except ImportError:
            print("Instale: pip install openai")
            return
    elif provider == "anthropic":
        try:
            import anthropic
            client_ant = anthropic.Anthropic(api_key=api_key)
            exec_model = model or "claude-sonnet-4-6"
        except ImportError:
            print("Instale: pip install anthropic")
            return
    else:
        print(f"Provider '{provider}' não suportado. Use 'openai' ou 'anthropic'.")
        return

    resultados = []
    for caso in SUITE:
        print(f"  Testando caso {caso.id:>2}/{len(SUITE)} — {caso.dominio}...", end=" ", flush=True)

        # Envia ao LLM
        try:
            if provider == "openai":
                r = client.chat.completions.create(
                    model=exec_model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": caso.prompt_et},
                    ],
                    max_tokens=300,
                    temperature=0,
                )
                resposta = r.choices[0].message.content.strip()
                resultado = avaliar_com_llm(caso, resposta, client, judge_model)

            elif provider == "anthropic":
                r = client_ant.messages.create(
                    model=exec_model,
                    max_tokens=300,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": caso.prompt_et}],
                )
                resposta = r.content[0].text.strip()
                # Para Anthropic como juiz, usa mesmo cliente
                class AnthropicJudge:
                    def __init__(self, ant_client, model):
                        self.ant = ant_client
                        self.model = model
                    class chat:
                        class completions:
                            pass
                # Avaliação manual se Anthropic (sem juiz separado)
                print(f"\n  RESPOSTA: {resposta[:80]}...")
                resultado = avaliar_manual(caso, resposta)

            print(f"score={resultado.score}/9")
            resultados.append(resultado)
            time.sleep(0.5)  # rate limit safety

        except Exception as e:
            print(f"ERRO: {e}")
            resultados.append(ResultadoCaso(
                caso_id=caso.id, dominio=caso.dominio,
                prompt_et=caso.prompt_et, esperado_en=caso.esperado_en,
                resposta_llm="ERRO", notas=str(e),
            ))

    imprimir_relatorio(resultados)


def run_manual():
    """Modo interativo — você fornece as respostas e pontua."""
    print("\n" + "═"*68)
    print("  ETEMENANQUI — AVALIAÇÃO SEMÂNTICA MANUAL")
    print("  Cole a resposta do LLM quando solicitado.")
    print("═"*68)

    resultados = []
    for caso in SUITE:
        print(f"\n{'═'*68}")
        print(f"  CASO {caso.id}/{len(SUITE)} | {caso.dominio.upper()}")
        print(f"  Envie ao LLM (com o system prompt):\n")
        print(f"    {caso.prompt_et}\n")
        print("  Cole a resposta do LLM (linha em branco para terminar):")
        linhas = []
        while True:
            l = input()
            if not l:
                break
            linhas.append(l)
        resposta = "\n".join(linhas)
        resultado = avaliar_manual(caso, resposta)
        resultados.append(resultado)

    imprimir_relatorio(resultados)


def run_dry():
    """Exibe a suite completa sem chamar API — para revisão antes do teste."""
    print("\n" + "═"*68)
    print("  ETEMENANQUI — SUITE DE AVALIAÇÃO (dry-run)")
    print("═"*68)
    print(f"\n  {len(SUITE)} casos de teste · 3 dimensões · 9 pontos máximos por caso\n")

    for caso in SUITE:
        print(f"  ── Caso {caso.id:>2} | {caso.dominio.upper()}")
        print(f"     ET  : {caso.prompt_et}")
        print(f"     REF : {caso.esperado_en}")
        print(f"     AÇÃO: {caso.acao_esperada}")
        print(f"     RISCO: {caso.alucinacao_risco}")
        print()

    print("─"*68)
    print("  SYSTEM PROMPT (injetado no LLM):")
    print("─"*68)
    print(textwrap.indent(SYSTEM_PROMPT, "  "))

    print("─"*68)
    print("  RUBRICA DE PONTUAÇÃO:")
    print("─"*68)
    for dim, titulo in [
        ("D1_fidelidade", "D1 — Fidelidade de Execução"),
        ("D2_aderencia",  "D2 — Aderência ao Protocolo"),
        ("D3_alucinacao", "D3 — Taxa de Alucinação"),
    ]:
        print(f"\n  {titulo}")
        for pts, expl in sorted(RUBRICA[dim].items(), reverse=True):
            print(f"    {pts}: {expl}")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Etemenanqui Semantic Evaluation Suite"
    )
    parser.add_argument(
        "--mode", choices=["auto", "manual", "dry"],
        default="dry",
        help="dry=só exibe suite | manual=você pontua | auto=LLM avalia",
    )
    parser.add_argument("--provider", choices=["openai", "anthropic"], default="openai")
    parser.add_argument("--key",   default=None, help="API key")
    parser.add_argument("--model", default=None, help="Modelo a usar (opcional)")
    args = parser.parse_args()

    if args.mode == "dry":
        run_dry()
    elif args.mode == "manual":
        run_manual()
    elif args.mode == "auto":
        if not args.key:
            print("Erro: --key obrigatório no modo auto")
        else:
            run_auto(args.provider, args.key, args.model)
