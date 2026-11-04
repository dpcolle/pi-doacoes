"""Integração com a API pública do InfoDengue (https://info.dengue.mat.br).

O InfoDengue (Fiocruz/FGV) publica, por semana epidemiológica e por município,
os casos notificados de dengue, a estimativa de casos e o nível de alerta (1 a 4).
"""
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

URL = "https://info.dengue.mat.br/api/alertcity"
NIVEIS = {1: "verde", 2: "amarelo", 3: "laranja", 4: "vermelho"}
_CACHE = {}          # geocode -> (instante, resultado); os dados mudam no máximo uma vez por semana
_VALIDADE = 3600     # segundos


class InfoDengueErro(Exception):
    def __init__(self, mensagem, status):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status


def _consultar_api(geocode, ano, timeout=10):
    """Busca as semanas do ano anterior e do atual (cobre a virada de ano)."""
    params = urllib.parse.urlencode({
        "geocode": geocode, "disease": "dengue", "format": "json",
        "ew_start": 1, "ew_end": 53, "ey_start": ano - 1, "ey_end": ano,
    })
    try:
        with urllib.request.urlopen(f"{URL}?{params}", timeout=timeout) as resp:  # noqa: S310 (URL fixa)
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError):
        raise InfoDengueErro("O InfoDengue está indisponível no momento. Tente mais tarde.", 502)


def _primeiro(registro, *chaves):
    for chave in chaves:
        if registro.get(chave) is not None:
            return registro[chave]
    return None


def _numero(valor, casas=None):
    try:
        n = float(valor)
    except (TypeError, ValueError):
        return None
    return round(n, casas) if casas is not None else int(round(n))


def normalizar(registros, semanas=12):
    """Converte a resposta da API em uma lista simples das últimas `semanas`, em ordem cronológica."""
    if not isinstance(registros, list):
        raise InfoDengueErro("Resposta inesperada do InfoDengue.", 502)
    linhas = []
    for r in registros:
        if not isinstance(r, dict):
            continue
        se = _numero(_primeiro(r, "SE", "se"))
        if not se:
            continue
        nivel = _numero(_primeiro(r, "nivel"))
        linhas.append({
            "se": se,                                   # ex.: 202644 = semana 44 de 2026
            "semana": se % 100,
            "ano": se // 100,
            "casos": _numero(_primeiro(r, "casos")),
            "casos_estimados": _numero(_primeiro(r, "casos_est")),
            "incidencia_100mil": _numero(_primeiro(r, "p_inc100k", "inc"), 1),
            "nivel": nivel,
            "nivel_nome": NIVEIS.get(nivel, "sem dados"),
        })
    linhas.sort(key=lambda l: l["se"])
    return linhas[-semanas:]


def buscar_situacao(geocode, consultor=None, hoje=None, usar_cache=True):
    """Retorna as últimas semanas do município. `consultor` permite trocar a API em testes."""
    geocode = str(geocode)
    if not (geocode.isdigit() and len(geocode) == 7):
        raise InfoDengueErro("Código IBGE inválido (7 dígitos).", 400)
    agora = time.time()
    if usar_cache and geocode in _CACHE and agora - _CACHE[geocode][0] < _VALIDADE:
        return _CACHE[geocode][1]
    ano = (hoje or date.today()).year
    semanas = normalizar((consultor or _consultar_api)(int(geocode), ano))
    resultado = {"geocode": geocode, "semanas": semanas, "atual": semanas[-1] if semanas else None}
    if usar_cache:
        _CACHE[geocode] = (agora, resultado)
    return resultado
