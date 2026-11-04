"""Análise de dados: estatística descritiva sobre focos, avaliações e casos de dengue.

Funções puras (recebem listas de dicionários), por isso fáceis de testar.
"""
from collections import Counter
from statistics import mean


def _dias_entre(inicio, fim):
    from datetime import datetime
    formato = "%Y-%m-%d %H:%M:%S"
    try:
        return (datetime.strptime(fim, formato) - datetime.strptime(inicio, formato)).total_seconds() / 86400
    except (TypeError, ValueError):
        return None


def resumir_focos(focos):
    por_status = Counter(f["status"] for f in focos)
    por_tipo = Counter(f["tipo"] for f in focos)
    bairros_abertos = Counter(f["bairro"] for f in focos if f["status"] != "eliminado")
    meses = Counter(f["criado_em"][:7] for f in focos)
    resolvidos = [f for f in focos if f["status"] == "eliminado"]
    prazos = [d for d in (_dias_entre(f["criado_em"], f.get("atualizado_em")) for f in resolvidos) if d is not None]
    return {
        "total": len(focos),
        "abertos": por_status.get("aberto", 0),
        "vistoriados": por_status.get("vistoriado", 0),
        "eliminados": por_status.get("eliminado", 0),
        "eliminados_pct": round(100 * len(resolvidos) / len(focos), 1) if focos else None,
        "dias_ate_eliminar": round(mean(prazos), 1) if prazos else None,
        "por_tipo": dict(por_tipo.most_common()),
        "bairros_pendentes": [{"bairro": b, "focos": n} for b, n in bairros_abertos.most_common(5)],
        "serie_mensal": [{"mes": m, "focos": meses[m]} for m in sorted(meses)],
    }


def resumir_avaliacoes(avaliacoes):
    notas = [a["nota"] for a in avaliacoes]
    satisfeitos = sum(1 for n in notas if n >= 4)
    por_versao = {}
    for a in avaliacoes:
        por_versao.setdefault(a.get("versao", "?"), []).append(a["nota"])
    return {
        "total": len(notas),
        "nota_media": round(mean(notas), 2) if notas else None,
        "distribuicao": {str(n): notas.count(n) for n in range(1, 6)},
        "satisfeitos_pct": round(100 * satisfeitos / len(notas), 1) if notas else None,
        # comparação v1 x v2 para o relatório final
        "media_por_versao": {v: round(mean(n), 2) for v, n in sorted(por_versao.items())},
    }


def tendencia_casos(semanas, janela=4):
    """Compara a soma de casos das últimas `janela` semanas com a das `janela` anteriores."""
    casos = [s["casos"] or 0 for s in semanas]
    if len(casos) < 2 * janela:
        return None
    recente, anterior = sum(casos[-janela:]), sum(casos[-2 * janela:-janela])
    variacao = None if anterior == 0 else round(100 * (recente - anterior) / anterior, 1)
    direcao = "alta" if recente > anterior else "queda" if recente < anterior else "estável"
    return {"ultimas": recente, "anteriores": anterior, "variacao_pct": variacao, "direcao": direcao}
