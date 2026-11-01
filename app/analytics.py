"""Análise de dados: estatística descritiva sobre doações e feedbacks.

Funções puras (recebem listas de dicionários), por isso fáceis de testar.
"""
from collections import Counter
from statistics import mean, median


def resumir_doacoes(doacoes):
    quantidades = [d["quantidade"] for d in doacoes]
    por_categoria = Counter()
    for d in doacoes:
        por_categoria[d["categoria"]] += d["quantidade"]
    cidades = Counter(d["cidade"] for d in doacoes if d.get("cidade"))
    meses = Counter(d["criado_em"][:7] for d in doacoes)
    return {
        "total_registros": len(doacoes),
        "total_itens": sum(quantidades),
        "media_quantidade": round(mean(quantidades), 1) if quantidades else 0,
        "mediana_quantidade": median(quantidades) if quantidades else 0,
        "por_categoria": dict(por_categoria),
        "top_cidades": [{"cidade": c, "doacoes": n} for c, n in cidades.most_common(5)],
        "serie_mensal": [{"mes": m, "doacoes": meses[m]} for m in sorted(meses)],
    }


def resumir_feedbacks(feedbacks):
    notas = [f["nota"] for f in feedbacks]
    distribuicao = {str(n): notas.count(n) for n in range(1, 6)}
    satisfeitos = sum(1 for n in notas if n >= 4)
    return {
        "total": len(notas),
        "nota_media": round(mean(notas), 2) if notas else None,
        "distribuicao": distribuicao,
        "satisfeitos_pct": round(100 * satisfeitos / len(notas), 1) if notas else None,
    }
