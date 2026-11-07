"""API REST própria do sistema (JSON)."""
import hmac
from urllib.parse import quote

from flask import Blueprint, current_app, jsonify, request

from . import analytics
from .cep import CepErro, buscar_cep
from .db import get_db
from .infodengue import InfoDengueErro, buscar_situacao
from .validators import validar_avaliacao, validar_foco, validar_status

bp = Blueprint("api", __name__, url_prefix="/api")

_AGORA = {"sqlite": "datetime('now')",
          "postgres": "to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS')"}


def _erro(mensagem, status, detalhes=None):
    corpo = {"erro": mensagem}
    if detalhes:
        corpo["detalhes"] = detalhes
    return jsonify(corpo), status


def _buscar(foco_id):
    return get_db().execute("SELECT * FROM focos WHERE id = :id", {"id": foco_id}).fetchone()


def _publico(linha):
    """Registro como a API mostra a qualquer pessoa: o WhatsApp nunca sai, só se existe."""
    dados = dict(linha)
    dados["tem_contato"] = bool(dados.pop("whatsapp", None))
    return dados


def _exige_agente():
    """Ações de agente de endemias exigem o código definido em AGENTE_CODIGO."""
    codigo = current_app.config.get("AGENTE_CODIGO")
    if not codigo:
        return _erro("Área do agente não configurada. Defina a variável AGENTE_CODIGO no servidor.", 503)
    enviado = request.headers.get("X-Codigo-Agente", "")
    if not hmac.compare_digest(enviado.encode(), codigo.encode()):
        return _erro("Código do agente inválido.", 401)
    return None


@bp.post("/agente/entrar")
def agente_entrar():
    negado = _exige_agente()
    return negado or ("", 204)


@bp.get("/saude")
def saude():
    """Verificação de saúde para a nuvem.

    Por padrão NÃO consulta o banco: o serviço de hospedagem chama esta rota o tempo
    todo e manteria o banco do Neon acordado, consumindo a cota gratuita.
    Use /api/saude?db=1 para testar também a conexão com o banco.
    """
    resposta = {"status": "ok", "versao": current_app.config["VERSAO"]}
    if request.args.get("db") == "1":
        banco = get_db()
        banco.execute("SELECT 1").fetchone()
        resposta["banco"] = banco.dialeto
    return jsonify(resposta)


# ---- Focos (possíveis criadouros) ---------------------------------------------
@bp.get("/focos")
def listar():
    sql, params = "SELECT * FROM focos WHERE 1=1", {}
    for campo in ("status", "tipo"):
        valor = request.args.get(campo, "").strip().lower()
        if valor:
            sql += f" AND {campo} = :{campo}"  # nome da coluna vem da lista fixa acima
            params[campo] = valor
    busca = request.args.get("q", "").strip().lower()
    if busca:
        # LOWER(...) torna a busca sem diferenciar maiúsculas tanto no SQLite quanto no PostgreSQL
        sql += " AND (LOWER(bairro) LIKE :busca OR LOWER(logradouro) LIKE :busca)"
        params["busca"] = f"%{busca}%"
    sql += " ORDER BY id DESC"
    linhas = get_db().execute(sql, params).fetchall()
    return jsonify([_publico(l) for l in linhas])


@bp.post("/focos")
def criar():
    dados, erros = validar_foco(request.get_json(silent=True))
    if erros:
        return _erro("Dados inválidos.", 400, erros)
    banco = get_db()
    linha = banco.execute(
        "INSERT INTO focos (tipo, descricao, logradouro, numero, bairro, cep, cidade, uf, whatsapp) "
        "VALUES (:tipo, :descricao, :logradouro, :numero, :bairro, :cep, :cidade, :uf, :whatsapp) RETURNING *",
        dados,
    ).fetchone()
    banco.commit()
    resposta = jsonify(_publico(linha))
    resposta.status_code = 201
    resposta.headers["Location"] = f"/api/focos/{linha['id']}"
    return resposta


@bp.get("/focos/<int:foco_id>")
def detalhar(foco_id):
    linha = _buscar(foco_id)
    if linha is None:
        return _erro("Registro não encontrado.", 404)
    return jsonify(_publico(linha))


@bp.put("/focos/<int:foco_id>")
def atualizar(foco_id):
    negado = _exige_agente()
    if negado:
        return negado
    if _buscar(foco_id) is None:
        return _erro("Registro não encontrado.", 404)
    dados, erros = validar_foco(request.get_json(silent=True))
    if erros:
        return _erro("Dados inválidos.", 400, erros)
    banco = get_db()
    banco.execute(
        "UPDATE focos SET tipo=:tipo, descricao=:descricao, logradouro=:logradouro, numero=:numero, "
        f"bairro=:bairro, cep=:cep, cidade=:cidade, uf=:uf, atualizado_em={_AGORA[banco.dialeto]} "
        "WHERE id=:id",
        {**dados, "id": foco_id},
    )
    banco.commit()
    return jsonify(_publico(_buscar(foco_id)))


@bp.patch("/focos/<int:foco_id>/status")
def mudar_status(foco_id):
    """Usado pelo agente de endemias: aberto -> vistoriado -> eliminado."""
    negado = _exige_agente()
    if negado:
        return negado
    if _buscar(foco_id) is None:
        return _erro("Registro não encontrado.", 404)
    status, erros = validar_status(request.get_json(silent=True))
    if erros:
        return _erro("Dados inválidos.", 400, erros)
    banco = get_db()
    banco.execute(
        f"UPDATE focos SET status=:status, atualizado_em={_AGORA[banco.dialeto]} WHERE id=:id",
        {"status": status, "id": foco_id},
    )
    banco.commit()
    return jsonify(_publico(_buscar(foco_id)))


@bp.delete("/focos/<int:foco_id>")
def remover(foco_id):
    negado = _exige_agente()
    if negado:
        return negado
    if _buscar(foco_id) is None:
        return _erro("Registro não encontrado.", 404)
    banco = get_db()
    banco.execute("DELETE FROM focos WHERE id = :id", {"id": foco_id})
    banco.commit()
    return "", 204


# ---- v2: aviso ao morador pelo WhatsApp ---------------------------------------
_MENSAGENS = {
    "aberto": "o local que você registrou em {local} foi recebido e aguarda vistoria",
    "vistoriado": "o local que você registrou em {local} foi vistoriado",
    "eliminado": "o criadouro que você registrou em {local} foi eliminado",
}


@bp.get("/focos/<int:foco_id>/contato")
def contato(foco_id):
    """Só para o agente: devolve o link do WhatsApp com a mensagem pronta."""
    negado = _exige_agente()
    if negado:
        return negado
    linha = _buscar(foco_id)
    if linha is None:
        return _erro("Registro não encontrado.", 404)
    if not linha["whatsapp"]:
        return _erro("Este registro não tem WhatsApp para aviso.", 404)
    local = ", ".join(p for p in (linha["logradouro"], linha["numero"], linha["bairro"]) if p)
    texto = ("Olá! Aqui é a equipe de combate à dengue. Informamos que "
             + _MENSAGENS[linha["status"]].format(local=local)
             + ". Obrigado por ajudar a proteger o bairro!")
    return jsonify({"link": f"https://wa.me/{linha['whatsapp']}?text={quote(texto)}", "status": linha["status"]})


@bp.delete("/focos/<int:foco_id>/contato")
def apagar_contato(foco_id):
    """Apaga o WhatsApp depois do aviso final: o dado não é guardado além do necessário."""
    negado = _exige_agente()
    if negado:
        return negado
    if _buscar(foco_id) is None:
        return _erro("Registro não encontrado.", 404)
    banco = get_db()
    banco.execute("UPDATE focos SET whatsapp = NULL WHERE id = :id", {"id": foco_id})
    banco.commit()
    return "", 204


# ---- APIs externas -----------------------------------------------------------
@bp.get("/cep/<cep>")
def consultar_cep(cep):
    try:
        return jsonify(buscar_cep(cep, current_app.config.get("CEP_CONSULTOR")))
    except CepErro as e:
        return _erro(e.mensagem, e.status)


@bp.get("/municipios")
def municipios():
    return jsonify(current_app.config["MUNICIPIOS"])


@bp.get("/dengue/<geocode>")
def situacao_dengue(geocode):
    consultor = current_app.config.get("INFODENGUE_CONSULTOR")
    try:
        dados = buscar_situacao(geocode, consultor, usar_cache=consultor is None)
    except InfoDengueErro as e:
        return _erro(e.mensagem, e.status)
    nomes = {m["geocode"]: m["nome"] for m in current_app.config["MUNICIPIOS"]}
    return jsonify({**dados, "municipio": nomes.get(dados["geocode"]),
                    "tendencia": analytics.tendencia_casos(dados["semanas"]),
                    "fonte": "InfoDengue (Fiocruz/FGV), dados do SINAN"})


# ---- Avaliação da comunidade -------------------------------------------------
@bp.post("/avaliacoes")
def criar_avaliacao():
    dados, erros = validar_avaliacao(request.get_json(silent=True))
    if erros:
        return _erro("Dados inválidos.", 400, erros)
    banco = get_db()
    linha = banco.execute(
        "INSERT INTO avaliacoes (nota, perfil, comentario, versao) "
        "VALUES (:nota, :perfil, :comentario, :versao) RETURNING *",
        {**dados, "versao": current_app.config["VERSAO"]},
    ).fetchone()
    banco.commit()
    return jsonify(dict(linha)), 201


@bp.get("/avaliacoes")
def listar_avaliacoes():
    linhas = get_db().execute("SELECT * FROM avaliacoes ORDER BY id DESC").fetchall()
    return jsonify([dict(l) for l in linhas])


# ---- Análise de dados --------------------------------------------------------
@bp.get("/estatisticas")
def estatisticas():
    banco = get_db()
    focos = [dict(l) for l in banco.execute("SELECT * FROM focos").fetchall()]
    avaliacoes = [dict(l) for l in banco.execute("SELECT * FROM avaliacoes").fetchall()]
    return jsonify({
        "focos": analytics.resumir_focos(focos),
        "avaliacoes": analytics.resumir_avaliacoes(avaliacoes),
    })
