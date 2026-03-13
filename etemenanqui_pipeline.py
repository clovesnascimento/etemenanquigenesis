"""
Pipeline de Avaliação Métrica — Projeto Etemenanqui
=====================================================
Três camadas de diagnóstico independentes:
  L1 — Teto Teórico      : Entropia de Shannon
  L2 — Eficiência Arq.   : Compressão gzip
  L3 — Custo Real         : Tokens BPE via tiktoken

Uso:
    pip install tiktoken --break-system-packages
    python etemenanqui_pipeline.py

Substitua CORPUS_A e CORPUS_B pelos textos reais quando disponíveis.
"""

import gzip
import math
import json
from collections import Counter
from dataclasses import dataclass, field, asdict
from typing import Optional

# ── Dependência opcional ───────────────────────────────────────────────────────
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    print("[AVISO] tiktoken não instalado. Camada 3 desabilitada.")
    print("        Execute: pip install tiktoken --break-system-packages\n")


# ══════════════════════════════════════════════════════════════════════════════
# CORPORA DE TESTE
# Substitua pelos textos reais do experimento.
# Os dois textos devem expressar o mesmo conteúdo semântico.
# ══════════════════════════════════════════════════════════════════════════════

CORPUS_A_LABEL = "Inglês (baseline)"
CORPUS_A = """
The tower of Babel was a monument to human ambition. Every brick carried the weight
of collective desire. The builders spoke one language, shared one vision, reached
toward the sky with unified purpose. The gods, alarmed by this convergence of will,
scattered the words. Suddenly the same mouth produced different sounds. The same
gesture meant opposite things. Communication collapsed into noise. The tower stopped
growing. Not because the stones ran out, but because the meaning between the stones
dissolved. Language is not the bricks. Language is the mortar.
""".strip()

CORPUS_B_LABEL = "Etemenanqui (placeholder)"
CORPUS_B = """
Twr Bbl — mnmt hmn ambt. Brc krr wgt cltv dsr. Bldr spk 1 lng, shr 1 vsn,
rch skw unf prp. Gds, alrm cnvg wl, sct wrd. Sdnl sm mth prd dff snd.
Sm gst mnt opp thn. Cmm clps nz. Twr stp grw. Nt brc stn rn, bt mnng
btwn stn dslv. Lng nt brc. Lng mtr.
""".strip()

# ══════════════════════════════════════════════════════════════════════════════
# ESTRUTURAS DE DADOS
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class MetricasTexto:
    label: str
    char_count: int = 0
    word_count: int = 0
    # L1
    shannon_entropy_char: float = 0.0
    shannon_entropy_word: float = 0.0
    bits_per_char: float = 0.0
    # L2
    gzip_bytes_original: int = 0
    gzip_bytes_compressed: int = 0
    gzip_ratio: float = 0.0
    # L3
    bpe_token_count: Optional[int] = None
    bpe_chars_per_token: Optional[float] = None

@dataclass
class GapDiagnostico:
    metrica: str
    valor_a: float
    valor_b: float
    ratio_b_over_a: float          # <1 = B mais eficiente; >1 = B mais caro
    interpretacao: str = ""


# ══════════════════════════════════════════════════════════════════════════════
# CAMADA 1 — ENTROPIA DE SHANNON
# ══════════════════════════════════════════════════════════════════════════════

def entropia_shannon(tokens: list[str]) -> float:
    """H = -Σ p(x) · log₂ p(x)"""
    n = len(tokens)
    if n == 0:
        return 0.0
    contagem = Counter(tokens)
    return -sum((c / n) * math.log2(c / n) for c in contagem.values())


def calcular_camada1(texto: str, m: MetricasTexto) -> None:
    chars = list(texto)
    words = texto.split()
    m.char_count = len(chars)
    m.word_count = len(words)
    m.shannon_entropy_char = entropia_shannon(chars)
    m.shannon_entropy_word = entropia_shannon(words)

    # Bits necessários por caractere se usarmos código de entropia ótimo
    m.bits_per_char = m.shannon_entropy_char


# ══════════════════════════════════════════════════════════════════════════════
# CAMADA 2 — GZIP
# ══════════════════════════════════════════════════════════════════════════════

def calcular_camada2(texto: str, m: MetricasTexto) -> None:
    encoded = texto.encode("utf-8")
    compressed = gzip.compress(encoded, compresslevel=9)
    m.gzip_bytes_original = len(encoded)
    m.gzip_bytes_compressed = len(compressed)
    m.gzip_ratio = len(compressed) / len(encoded)


# ══════════════════════════════════════════════════════════════════════════════
# CAMADA 3 — BPE / tiktoken
# ══════════════════════════════════════════════════════════════════════════════

def calcular_camada3(texto: str, m: MetricasTexto, encoding_name: str = "cl100k_base") -> None:
    if not TIKTOKEN_AVAILABLE:
        return
    enc = tiktoken.get_encoding(encoding_name)
    tokens = enc.encode(texto)
    m.bpe_token_count = len(tokens)
    m.bpe_chars_per_token = m.char_count / len(tokens) if tokens else 0.0


# ══════════════════════════════════════════════════════════════════════════════
# DIAGNÓSTICO DE GAPS
# ══════════════════════════════════════════════════════════════════════════════

MAPA_INTERPRETACAO = {
    # (H_A > H_B, gzip_A > gzip_B, bpe_A > bpe_B)  →  diagnóstico
    (False, False, False): "Etemenanqui mais denso e mais caro — redesenho necessário.",
    (True,  False, False): "Entropia menor, mas sem estrutura explorável. Raízes aleatórias.",
    (True,  True,  False): "Regularidade interna presente, mas invisível ao tokenizador inglês.",
    (True,  True,  True ): "ÓTIMO — Economia real e teórica alinhadas.",
    (False, True,  True ): "Paradoxo: comprime bem mas entropia alta. Verificar corpus.",
    (False, False, True ): "BPE eficiente por coincidência com inglês. Sem ganho real de design.",
    (True,  False, True ): "Tokens eficientes, gzip ruim. Morfologia irregular.",
    (False, True,  False): "gzip bom, BPE caro. Padrões repetíveis mas morfemas novos demais.",
}

def diagnosticar_gaps(a: MetricasTexto, b: MetricasTexto) -> list[GapDiagnostico]:
    gaps = []

    def gap(metrica, val_a, val_b):
        ratio = val_b / val_a if val_a else float("inf")
        return GapDiagnostico(metrica=metrica, valor_a=val_a, valor_b=val_b, ratio_b_over_a=ratio)

    g_entropy = gap("Shannon (char)", a.shannon_entropy_char, b.shannon_entropy_char)
    g_gzip    = gap("gzip ratio",     a.gzip_ratio,           b.gzip_ratio)
    gaps.extend([g_entropy, g_gzip])

    if a.bpe_token_count and b.bpe_token_count:
        g_bpe = gap("BPE tokens", a.bpe_token_count, b.bpe_token_count)
        gaps.append(g_bpe)

    # Interpretação composta
    h_melhor    = b.shannon_entropy_char < a.shannon_entropy_char
    gzip_melhor = b.gzip_ratio < a.gzip_ratio
    bpe_melhor  = (b.bpe_token_count or 1) < (a.bpe_token_count or 1)

    chave = (h_melhor, gzip_melhor, bpe_melhor)
    interpretacao = MAPA_INTERPRETACAO.get(chave, "Padrão não mapeado — analisar manualmente.")

    for g in gaps:
        g.interpretacao = interpretacao

    return gaps


# ══════════════════════════════════════════════════════════════════════════════
# RELATÓRIO
# ══════════════════════════════════════════════════════════════════════════════

def formatar_relatorio(a: MetricasTexto, b: MetricasTexto, gaps: list[GapDiagnostico]) -> str:
    linhas = []
    SEP = "═" * 64

    def secao(titulo):
        linhas.append(f"\n{SEP}")
        linhas.append(f"  {titulo}")
        linhas.append(SEP)

    def linha_comparacao(label, va, vb, fmt=".4f", menor_melhor=True):
        diff = vb - va
        sinal = "▼" if (diff < 0) == menor_melhor else "▲"
        linhas.append(
            f"  {label:<28} {va:{fmt}}  →  {vb:{fmt}}  {sinal} {abs(diff):{fmt}}"
        )

    secao("CAMADA 1 — ENTROPIA DE SHANNON")
    linhas.append(f"  {'':28} {a.label:<16} {b.label}")
    linha_comparacao("Entropia (char)", a.shannon_entropy_char, b.shannon_entropy_char)
    linha_comparacao("Entropia (word)", a.shannon_entropy_word, b.shannon_entropy_word)
    linha_comparacao("Bits/char",       a.bits_per_char,        b.bits_per_char)
    linhas.append(f"  {'Chars':28} {a.char_count:<16} {b.char_count}")
    linhas.append(f"  {'Words':28} {a.word_count:<16} {b.word_count}")

    secao("CAMADA 2 — COMPRESSÃO GZIP")
    linha_comparacao("Bytes originais",   a.gzip_bytes_original,   b.gzip_bytes_original, fmt=".0f")
    linha_comparacao("Bytes comprimidos", a.gzip_bytes_compressed, b.gzip_bytes_compressed, fmt=".0f")
    linha_comparacao("Razão gzip",        a.gzip_ratio,            b.gzip_ratio)

    secao("CAMADA 3 — TOKENS BPE (cl100k_base)")
    if a.bpe_token_count is not None:
        linha_comparacao("Tokens BPE",        float(a.bpe_token_count), float(b.bpe_token_count), fmt=".0f")
        linha_comparacao("Chars/token",       a.bpe_chars_per_token,    b.bpe_chars_per_token)
    else:
        linhas.append("  [tiktoken não disponível]")

    secao("DIAGNÓSTICO DE GAPS")
    for g in gaps:
        indicator = "▼ GANHO" if g.ratio_b_over_a < 1 else "▲ CUSTO"
        linhas.append(
            f"  {g.metrica:<28} ratio={g.ratio_b_over_a:.3f}  {indicator}"
        )

    linhas.append(f"\n  INTERPRETAÇÃO COMPOSTA:")
    linhas.append(f"  {gaps[0].interpretacao if gaps else 'N/A'}")
    linhas.append(f"\n{SEP}\n")

    return "\n".join(linhas)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def avaliar(texto: str, label: str) -> MetricasTexto:
    m = MetricasTexto(label=label)
    calcular_camada1(texto, m)
    calcular_camada2(texto, m)
    calcular_camada3(texto, m)
    return m


def main():
    print("\nIniciando pipeline de avaliação Etemenanqui...\n")

    ma = avaliar(CORPUS_A, CORPUS_A_LABEL)
    mb = avaliar(CORPUS_B, CORPUS_B_LABEL)
    gaps = diagnosticar_gaps(ma, mb)

    relatorio = formatar_relatorio(ma, mb, gaps)
    print(relatorio)

    # Exporta JSON para análise posterior
    resultado = {
        "corpus_a": asdict(ma),
        "corpus_b": asdict(mb),
        "gaps": [asdict(g) for g in gaps],
    }
    with open("etemenanqui_resultado.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print("Resultado exportado para: etemenanqui_resultado.json")


if __name__ == "__main__":
    main()
