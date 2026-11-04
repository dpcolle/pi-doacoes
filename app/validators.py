"""Validação de dados de entrada (nunca confiar no cliente)."""

TIPOS = ("pneu", "caixa_dagua", "vaso_planta", "lixo_entulho", "piscina", "calha", "terreno", "outros")
STATUS = ("aberto", "vistoriado", "eliminado")
PERFIS = ("morador", "agente", "coordenador")


def _texto(valor):
    return str(valor).strip() if valor is not None else ""


def validar_foco(dados):
    """Retorna (dados_limpos, erros). Se erros não for vazio, rejeitar."""
    if not isinstance(dados, dict):
        return None, {"corpo": "Envie um objeto JSON válido."}

    erros = {}
    tipo = _texto(dados.get("tipo")).lower()
    if tipo not in TIPOS:
        erros["tipo"] = "Escolha o tipo de criadouro."

    descricao = _texto(dados.get("descricao"))
    if len(descricao) > 300:
        erros["descricao"] = "Use até 300 caracteres."

    logradouro = _texto(dados.get("logradouro"))
    if not 3 <= len(logradouro) <= 120:
        erros["logradouro"] = "Informe a rua (3 a 120 caracteres)."

    numero = _texto(dados.get("numero"))
    if len(numero) > 10:
        erros["numero"] = "Use até 10 caracteres (ou deixe em branco)."

    bairro = _texto(dados.get("bairro"))
    if not 2 <= len(bairro) <= 80:
        erros["bairro"] = "Informe o bairro (2 a 80 caracteres)."

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
        "tipo": tipo,
        "descricao": descricao or None,
        "logradouro": logradouro,
        "numero": numero or None,
        "bairro": bairro,
        "cep": cep or None,
        "cidade": cidade or None,
        "uf": uf or None,
    }, {}


def validar_status(dados):
    if not isinstance(dados, dict):
        return None, {"corpo": "Envie um objeto JSON válido."}
    status = _texto(dados.get("status")).lower()
    if status not in STATUS:
        return None, {"status": "Escolha: " + ", ".join(STATUS) + "."}
    return status, {}


def validar_avaliacao(dados):
    if not isinstance(dados, dict):
        return None, {"corpo": "Envie um objeto JSON válido."}
    erros = {}
    try:
        nota = int(dados.get("nota"))
        if isinstance(dados.get("nota"), bool) or not 1 <= nota <= 5:
            raise ValueError
    except (TypeError, ValueError):
        nota = None
        erros["nota"] = "Escolha uma nota de 1 a 5."
    perfil = _texto(dados.get("perfil")).lower()
    if perfil not in PERFIS:
        erros["perfil"] = "Escolha: " + ", ".join(PERFIS) + "."
    comentario = _texto(dados.get("comentario"))
    if len(comentario) > 500:
        erros["comentario"] = "Use até 500 caracteres."
    if erros:
        return None, erros
    return {"nota": nota, "perfil": perfil, "comentario": comentario or None}, {}
