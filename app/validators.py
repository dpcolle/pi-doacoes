"""Validação de dados de entrada (nunca confiar no cliente)."""

CATEGORIAS = ("alimento", "higiene", "vestuario", "outros")


def _texto(valor):
    return str(valor).strip() if valor is not None else ""


def validar_doacao(dados):
    """Retorna (dados_limpos, erros). Se erros não for vazio, rejeitar."""
    if not isinstance(dados, dict):
        return None, {"corpo": "Envie um objeto JSON válido."}

    erros = {}
    item = _texto(dados.get("item"))
    if not 2 <= len(item) <= 80:
        erros["item"] = "Informe o item com 2 a 80 caracteres."

    categoria = _texto(dados.get("categoria")).lower()
    if categoria not in CATEGORIAS:
        erros["categoria"] = "Escolha: " + ", ".join(CATEGORIAS) + "."

    bruto = dados.get("quantidade")
    quantidade = None
    if isinstance(bruto, bool):
        erros["quantidade"] = "Informe um número inteiro."
    else:
        try:
            quantidade = int(bruto)
            if not 1 <= quantidade <= 100000:
                raise ValueError
        except (TypeError, ValueError):
            erros["quantidade"] = "Informe um número inteiro entre 1 e 100000."

    doador = _texto(dados.get("doador"))
    if len(doador) > 80:
        erros["doador"] = "Use até 80 caracteres."

    cep = "".join(c for c in _texto(dados.get("cep")) if c.isdigit())
    if cep and len(cep) != 8:
        erros["cep"] = "O CEP deve ter 8 dígitos."

    cidade = _texto(dados.get("cidade"))[:80]
    uf = _texto(dados.get("uf")).upper()
    if uf and (len(uf) != 2 or not uf.isalpha()):
        erros["uf"] = "Use a sigla com 2 letras."

    if erros:
        return None, erros
    return {
        "item": item,
        "categoria": categoria,
        "quantidade": quantidade,
        "doador": doador or None,
        "cep": cep or None,
        "cidade": cidade or None,
        "uf": uf or None,
    }, {}
