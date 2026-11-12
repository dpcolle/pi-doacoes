"""Consulta de CEP nas APIs públicas ViaCEP (https://viacep.com.br) e BrasilAPI.

A ViaCEP é a fonte principal. Se ela não responder a partir do servidor (o que
acontece em alguns provedores de nuvem), o sistema tenta a BrasilAPI. Se as duas
falharem, o navegador do usuário consulta a ViaCEP diretamente (ver focos.js).
"""
import json
import urllib.error
import urllib.request

AGENTE = "AlertaDengueComunitario/2.0 (+https://github.com/dpcolle/pi-doacoes)"
MSG_INDISPONIVEL = "Serviço de CEP indisponível no momento. Preencha cidade e UF manualmente."


class CepErro(Exception):
    def __init__(self, mensagem, status):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status


def normalizar(cep):
    return "".join(c for c in str(cep) if c.isdigit())


def _get_json(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": AGENTE, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (URLs fixas)
        return json.loads(resp.read().decode("utf-8"))


def _viacep(cep, timeout):
    return _get_json(f"https://viacep.com.br/ws/{cep}/json/", timeout)


def _brasilapi(cep, timeout):
    """Converte a resposta da BrasilAPI para o formato da ViaCEP."""
    try:
        d = _get_json(f"https://brasilapi.com.br/api/cep/v1/{cep}", timeout)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"erro": True}
        raise
    return {"logradouro": d.get("street") or "", "bairro": d.get("neighborhood") or "",
            "localidade": d.get("city") or "", "uf": d.get("state") or ""}


def _consultar_apis(cep, timeout=5, provedores=(_viacep, _brasilapi)):
    for provedor in provedores:
        try:
            dados = provedor(cep, timeout)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            continue
        if isinstance(dados, dict):
            return dados
    raise CepErro(MSG_INDISPONIVEL, 502)


def buscar_cep(cep, consultor=None):
    """Retorna cidade/UF de um CEP. `consultor` permite trocar a API em testes."""
    limpo = normalizar(cep)
    if len(limpo) != 8:
        raise CepErro("O CEP deve ter 8 dígitos.", 400)
    dados = (consultor or _consultar_apis)(limpo)
    if not isinstance(dados, dict) or dados.get("erro"):
        raise CepErro("CEP não encontrado.", 404)
    return {
        "cep": limpo,
        "logradouro": dados.get("logradouro", ""),
        "bairro": dados.get("bairro", ""),
        "cidade": dados.get("localidade", ""),
        "uf": dados.get("uf", ""),
    }
