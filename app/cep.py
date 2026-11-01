"""Integração com a API pública ViaCEP (https://viacep.com.br)."""
import json
import urllib.error
import urllib.request


class CepErro(Exception):
    def __init__(self, mensagem, status):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status


def normalizar(cep):
    return "".join(c for c in str(cep) if c.isdigit())


def _consultar_viacep(cep, timeout=5):
    url = f"https://viacep.com.br/ws/{cep}/json/"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310 (URL fixa)
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError):
        raise CepErro("Serviço de CEP indisponível no momento. Preencha cidade e UF manualmente.", 502)


def buscar_cep(cep, consultor=None):
    """Retorna cidade/UF de um CEP. `consultor` permite trocar a API em testes."""
    limpo = normalizar(cep)
    if len(limpo) != 8:
        raise CepErro("O CEP deve ter 8 dígitos.", 400)
    dados = (consultor or _consultar_viacep)(limpo)
    if not isinstance(dados, dict) or dados.get("erro"):
        raise CepErro("CEP não encontrado.", 404)
    return {
        "cep": limpo,
        "logradouro": dados.get("logradouro", ""),
        "bairro": dados.get("bairro", ""),
        "cidade": dados.get("localidade", ""),
        "uf": dados.get("uf", ""),
    }
