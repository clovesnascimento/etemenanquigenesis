"""
tradutor_agente.py
─────────────────────────────────────────────────────────────────────────────
Agente Tradutor Profissional — powered by DeepSeek
Skill: Tradução, Localização Cultural, Revisão e Controle de Qualidade

Funcionalidades:
  - Tradução entre qualquer par de idiomas
  - Adaptação cultural (localização)
  - Pesquisa terminológica por área (técnico, jurídico, médico, literário)
  - Revisão e controle de qualidade embutidos
  - Memória de tradução (glossário de sessão)
  - Modo Plan-and-Solve: o agente planeja antes de traduzir

Uso:
    python tradutor_agente.py                         # modo interativo
    python tradutor_agente.py --texto "Hello world"   # tradução direta
    python tradutor_agente.py --arquivo doc.txt        # tradução de arquivo

Requisito:
    pip install openai  (SDK compatível com DeepSeek)
    
Configurar API key:
    export DEEPSEEK_API_KEY="sk-..."
    ou editar a variável API_KEY abaixo.

Autor: CNGSM — Cloves Nascimento, 2026
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import json
import argparse
import textwrap
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional
from openai import OpenAI

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO — edite aqui ou use variável de ambiente
# ─────────────────────────────────────────────────────────────────────────────
API_KEY  = os.getenv("DEEPSEEK_API_KEY", "sk-SUA-CHAVE-AQUI")
BASE_URL = "https://api.deepseek.com"
MODEL    = "deepseek-chat"

# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT — Skill de Tradutor Profissional
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM_TRADUTOR = """\
Você é um Tradutor Profissional Sênior especializado em múltiplos domínios.

## Suas competências
- **Tradução e Versão**: Converte textos preservando significado, tom e intenção original.
- **Adaptação Cultural (Localização)**: Ajusta gírias, expressões idiomáticas e normas
  culturais para o público-alvo — nunca traduz literalmente o que deve ser adaptado.
- **Pesquisa Terminológica**: Domina terminologia técnica em medicina, direito, engenharia,
  tecnologia, literatura e audiovisual. Usa o termo correto no contexto certo.
- **Revisão e Controle de Qualidade**: Antes de entregar, revisa gramática, pontuação,
  coerência de estilo e consistência terminológica.
- **Sigilo**: Trata todo documento como confidencial. Nunca menciona conteúdo
  sensível fora do contexto da tradução solicitada.

## Áreas de especialização
  Técnica · Jurídica · Médica · Literária · Audiovisual · Juramentada · Tecnologia

## Protocolo de trabalho (Plan-and-Solve)
Para textos longos ou complexos, opere em fases:

**Fase 0 — Análise**: Identifique idioma de origem, domínio, tom e terminologia crítica.
**Fase 1 — Tradução**: Execute a tradução com máxima fidelidade.
**Fase 2 — Localização**: Ajuste expressões culturais para o público-alvo.
**Fase 3 — Revisão QA**: Revise gramática, estilo e consistência. Entregue versão final.

## Formato de resposta
- Para textos curtos: entregue a tradução diretamente, limpa e formatada.
- Para textos longos: use as fases acima e sinalize cada etapa.
- Sempre informe o par idiomático usado (ex: EN → PT-BR).
- Se detectar ambiguidade terminológica, apresente a opção escolhida e justifique.
- Nunca adicione notas desnecessárias. Entregue o texto, não um ensaio sobre ele.
"""

# ─────────────────────────────────────────────────────────────────────────────
# GLOSSÁRIO DE SESSÃO — memória de tradução
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class EntradaGlossario:
    termo_original: str
    traducao: str
    idioma_origem: str
    idioma_destino: str
    dominio: str
    contexto: str = ""

class GlossarioSessao:
    """Memória de tradução para consistência terminológica na sessão."""
    def __init__(self):
        self.entradas: list[EntradaGlossario] = []

    def adicionar(self, termo: str, traducao: str,
                  origem: str, destino: str, dominio: str, contexto: str = ""):
        self.entradas.append(EntradaGlossario(termo, traducao, origem, destino, dominio, contexto))

    def como_texto(self) -> str:
        if not self.entradas:
            return ""
        linhas = ["## Glossário de sessão (use estes termos para consistência)"]
        for e in self.entradas:
            linhas.append(f"  {e.termo_original} ({e.idioma_origem}) → {e.traducao} ({e.idioma_destino}) [{e.dominio}]")
        return "\n".join(linhas)

    def exportar(self, path: str = "glossario_sessao.json"):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([asdict(e) for e in self.entradas], f, ensure_ascii=False, indent=2)
        print(f"  Glossário exportado → {path}")

# ─────────────────────────────────────────────────────────────────────────────
# DATACLASS — Solicitação de tradução
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class SolicitacaoTraducao:
    texto: str
    idioma_origem: str = "auto"          # "auto" = detectar automaticamente
    idioma_destino: str = "pt-BR"
    dominio: str = "geral"               # geral | técnico | jurídico | médico | literário | audiovisual
    tom: str = "formal"                  # formal | informal | neutro
    modo: str = "direto"                 # direto | plan-and-solve
    instrucoes_extras: str = ""

# ─────────────────────────────────────────────────────────────────────────────
# AGENTE TRADUTOR
# ─────────────────────────────────────────────────────────────────────────────
class AgenteTradutorProfissional:
    """
    Agente de tradução profissional com skill completo.
    Powered by DeepSeek via OpenAI-compatible API.
    """

    def __init__(self, api_key: str = API_KEY, verbose: bool = False):
        self.client = OpenAI(api_key=api_key, base_url=BASE_URL)
        self.verbose = verbose
        self.glossario = GlossarioSessao()
        self.historico: list[dict] = []
        self._sessao_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _montar_prompt_usuario(self, sol: SolicitacaoTraducao) -> str:
        """Monta o prompt de usuário com todas as instruções da solicitação."""
        partes = []

        # Cabeçalho da solicitação
        origem = sol.idioma_origem if sol.idioma_origem != "auto" else "detectar automaticamente"
        partes.append(
            f"**Solicitação de tradução**\n"
            f"Par idiomático: {origem} → {sol.idioma_destino}\n"
            f"Domínio: {sol.dominio} | Tom: {sol.tom} | Modo: {sol.modo}"
        )

        # Glossário de sessão (se existir)
        glossario_txt = self.glossario.como_texto()
        if glossario_txt:
            partes.append(glossario_txt)

        # Instruções extras do usuário
        if sol.instrucoes_extras:
            partes.append(f"**Instruções adicionais**: {sol.instrucoes_extras}")

        # Texto a traduzir
        if sol.modo == "plan-and-solve":
            partes.append(
                "Execute as 4 fases do protocolo (Análise → Tradução → Localização → Revisão QA).\n"
                "Sinalize cada fase com um cabeçalho.\n\n"
                f"**Texto a traduzir:**\n{sol.texto}"
            )
        else:
            partes.append(f"**Texto a traduzir:**\n{sol.texto}")

        return "\n\n".join(partes)

    def traduzir(self, sol: SolicitacaoTraducao) -> str:
        """Executa a tradução e retorna o texto traduzido."""
        prompt = self._montar_prompt_usuario(sol)

        if self.verbose:
            print(f"\n[AGENTE] Iniciando tradução — domínio={sol.dominio} modo={sol.modo}")
            print(f"[AGENTE] Texto ({len(sol.texto)} chars):\n  {sol.texto[:100]}{'...' if len(sol.texto)>100 else ''}")

        # Mantém histórico de conversa para contexto
        self.historico.append({"role": "user", "content": prompt})

        resposta = self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_TRADUTOR},
                *self.historico,
            ],
            max_tokens=4096,
            temperature=0.3,   # baixo para precisão terminológica
            stream=False,
        )

        traducao = resposta.choices[0].message.content.strip()
        self.historico.append({"role": "assistant", "content": traducao})

        if self.verbose:
            tokens = resposta.usage
            print(f"[AGENTE] Concluído — {tokens.prompt_tokens} in / {tokens.completion_tokens} out tokens")

        return traducao

    def adicionar_ao_glossario(self, termo: str, traducao: str,
                                origem: str, destino: str,
                                dominio: str = "geral", contexto: str = ""):
        """Adiciona termo ao glossário de sessão manualmente."""
        self.glossario.adicionar(termo, traducao, origem, destino, dominio, contexto)
        print(f"  ✓ Glossário: '{termo}' → '{traducao}' adicionado.")

    def revisar(self, texto_traduzido: str, idioma: str = "pt-BR") -> str:
        """Solicita revisão QA de um texto já traduzido."""
        prompt = (
            f"Revise este texto em {idioma} para gramática, pontuação, "
            f"coerência de estilo e consistência terminológica. "
            f"Retorne apenas o texto revisado, sem explicações.\n\n"
            f"{texto_traduzido}"
        )
        self.historico.append({"role": "user", "content": prompt})
        r = self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_TRADUTOR},
                *self.historico,
            ],
            max_tokens=4096,
            temperature=0.2,
        )
        revisado = r.choices[0].message.content.strip()
        self.historico.append({"role": "assistant", "content": revisado})
        return revisado

    def exportar_sessao(self):
        """Exporta histórico e glossário da sessão."""
        path_hist = f"sessao_{self._sessao_id}.json"
        with open(path_hist, "w", encoding="utf-8") as f:
            json.dump(self.historico, f, ensure_ascii=False, indent=2)
        print(f"  Histórico exportado → {path_hist}")
        if self.glossario.entradas:
            self.glossario.exportar(f"glossario_{self._sessao_id}.json")

# ─────────────────────────────────────────────────────────────────────────────
# MODO INTERATIVO — CLI conversacional
# ─────────────────────────────────────────────────────────────────────────────
IDIOMAS = {
    "1": ("pt-BR", "Português (Brasil)"),
    "2": ("pt-PT", "Português (Portugal)"),
    "3": ("en",    "Inglês"),
    "4": ("es",    "Espanhol"),
    "5": ("fr",    "Francês"),
    "6": ("de",    "Alemão"),
    "7": ("it",    "Italiano"),
    "8": ("ja",    "Japonês"),
    "9": ("zh",    "Chinês Mandarim"),
    "0": ("outro", "Outro (digitar)"),
}

DOMINIOS = {
    "1": "geral",
    "2": "técnico",
    "3": "jurídico",
    "4": "médico",
    "5": "literário",
    "6": "audiovisual",
    "7": "tecnologia",
}

def selecionar_idioma(prompt_txt: str) -> str:
    print(f"\n  {prompt_txt}")
    for k, (cod, nome) in IDIOMAS.items():
        print(f"    {k}: {nome}")
    escolha = input("  Opção: ").strip()
    if escolha == "0":
        return input("  Digite o idioma: ").strip()
    return IDIOMAS.get(escolha, ("pt-BR", ""))[0]

def modo_interativo():
    SEP = "═" * 60

    print(f"\n{SEP}")
    print("  AGENTE TRADUTOR PROFISSIONAL")
    print("  Powered by DeepSeek | CNGSM 2026")
    print(SEP)
    print("  Comandos: 'sair' | 'glossario' | 'revisar' | 'exportar'")
    print(SEP)

    agente = AgenteTradutorProfissional(verbose=False)

    while True:
        print(f"\n{'─'*60}")
        print("  [1] Nova tradução")
        print("  [2] Adicionar termo ao glossário")
        print("  [3] Revisar texto já traduzido")
        print("  [4] Exportar sessão")
        print("  [0] Sair")
        cmd = input("\n  Opção: ").strip()

        # ── Nova tradução
        if cmd == "1":
            print("\n  ── NOVA TRADUÇÃO")

            print("\n  Digite o texto (linha em branco para terminar):")
            linhas = []
            while True:
                l = input()
                if not l:
                    break
                linhas.append(l)
            texto = "\n".join(linhas).strip()
            if not texto:
                print("  Texto vazio. Abortando.")
                continue

            destino = selecionar_idioma("Idioma de DESTINO:")

            print("\n  Domínio:")
            for k, v in DOMINIOS.items():
                print(f"    {k}: {v}")
            dom_escolha = input("  Opção [1=geral]: ").strip() or "1"
            dominio = DOMINIOS.get(dom_escolha, "geral")

            modo = "direto"
            if len(texto) > 300:
                r = input("\n  Texto longo detectado. Usar modo Plan-and-Solve? [s/N]: ").strip().lower()
                if r == "s":
                    modo = "plan-and-solve"

            extras = input("  Instruções extras (Enter para pular): ").strip()

            sol = SolicitacaoTraducao(
                texto=texto,
                idioma_destino=destino,
                dominio=dominio,
                modo=modo,
                instrucoes_extras=extras,
            )

            print(f"\n  Traduzindo... ", end="", flush=True)
            resultado = agente.traduzir(sol)
            print("✓\n")
            print(SEP)
            print(resultado)
            print(SEP)

        # ── Adicionar glossário
        elif cmd == "2":
            print("\n  ── ADICIONAR AO GLOSSÁRIO")
            termo      = input("  Termo original: ").strip()
            traducao   = input("  Tradução: ").strip()
            origem     = input("  Idioma origem (ex: en): ").strip() or "en"
            destino    = input("  Idioma destino (ex: pt-BR): ").strip() or "pt-BR"
            dominio    = input("  Domínio (geral/técnico/etc): ").strip() or "geral"
            contexto   = input("  Contexto (opcional): ").strip()
            agente.adicionar_ao_glossario(termo, traducao, origem, destino, dominio, contexto)

        # ── Revisar texto
        elif cmd == "3":
            print("\n  ── REVISÃO QA")
            print("  Cole o texto traduzido (linha em branco para terminar):")
            linhas = []
            while True:
                l = input()
                if not l:
                    break
                linhas.append(l)
            texto = "\n".join(linhas).strip()
            idioma = input("  Idioma do texto (ex: pt-BR): ").strip() or "pt-BR"

            print("\n  Revisando... ", end="", flush=True)
            revisado = agente.revisar(texto, idioma)
            print("✓\n")
            print(SEP)
            print(revisado)
            print(SEP)

        # ── Exportar
        elif cmd == "4":
            agente.exportar_sessao()

        # ── Sair
        elif cmd == "0" or cmd.lower() == "sair":
            exportar = input("\n  Exportar sessão antes de sair? [s/N]: ").strip().lower()
            if exportar == "s":
                agente.exportar_sessao()
            print("\n  Encerrando. Até logo.\n")
            break

        else:
            print("  Opção inválida.")

# ─────────────────────────────────────────────────────────────────────────────
# MODO DIRETO — linha de comando
# ─────────────────────────────────────────────────────────────────────────────
def modo_direto(args):
    agente = AgenteTradutorProfissional(verbose=args.verbose)

    # Lê texto da entrada
    if args.arquivo:
        with open(args.arquivo, encoding="utf-8") as f:
            texto = f.read()
    elif args.texto:
        texto = args.texto
    else:
        print("Erro: forneça --texto ou --arquivo")
        sys.exit(1)

    modo = "plan-and-solve" if args.planejar else "direto"

    sol = SolicitacaoTraducao(
        texto=texto,
        idioma_origem=args.origem or "auto",
        idioma_destino=args.destino or "pt-BR",
        dominio=args.dominio or "geral",
        tom=args.tom or "formal",
        modo=modo,
        instrucoes_extras=args.instrucoes or "",
    )

    resultado = agente.traduzir(sol)
    print(resultado)

    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(resultado)
        print(f"\n✓ Tradução salva em: {args.saida}")

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agente Tradutor Profissional — DeepSeek",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Exemplos:
          python tradutor_agente.py
          python tradutor_agente.py --texto "Hello, world!" --destino pt-BR
          python tradutor_agente.py --arquivo contrato.txt --dominio juridico --saida contrato_pt.txt
          python tradutor_agente.py --texto "Refactor nested loops" --dominio tecnico --planejar
        """)
    )
    parser.add_argument("--texto",     help="Texto a traduzir")
    parser.add_argument("--arquivo",   help="Arquivo de texto a traduzir")
    parser.add_argument("--origem",    help="Idioma de origem (padrão: auto)")
    parser.add_argument("--destino",   help="Idioma de destino (padrão: pt-BR)")
    parser.add_argument("--dominio",   help="Domínio: geral|técnico|jurídico|médico|literário (padrão: geral)")
    parser.add_argument("--tom",       help="Tom: formal|informal|neutro (padrão: formal)")
    parser.add_argument("--saida",     help="Arquivo de saída para a tradução")
    parser.add_argument("--instrucoes",help="Instruções extras para o agente")
    parser.add_argument("--planejar",  action="store_true", help="Usar modo Plan-and-Solve")
    parser.add_argument("--verbose",   action="store_true", help="Exibir logs de execução")
    parser.add_argument("--key",       help="API key (sobrescreve variável de ambiente)")

    args = parser.parse_args()

    # API key via argumento
    if args.key:
        os.environ["DEEPSEEK_API_KEY"] = args.key

    # Sem argumentos → modo interativo
    if not args.texto and not args.arquivo:
        modo_interativo()
    else:
        modo_direto(args)
