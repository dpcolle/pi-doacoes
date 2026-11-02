"""API REST própria do sistema (JSON)."""
from flask import Blueprint, current_app, jsonify, request

from . import analytics
from .cep import CepErro, buscar_cep
from .db import get_db
from .validators import validar_doacao, validar_feedback

bp = Blueprint("api", __name__, url_prefix="/api")


def _erro(mensagem, status, detalhes=None):
    corpo = {"erro": mensagem}
    if detalhes:
        corpo["detalhes"] = detalhes
    return jsonify(corpo), status


def _buscar(doacao_id):
    return get_db().execute("SELECT * FROM doacoes WHERE id = :id", {"id": doacao_id}).fetchone()


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


@bp.get("/doacoes")
def listar():
    sql, params = "SELECT * FROM doacoes WHERE 1=1", {}
    categoria = request.args.get("categoria", "").strip().lower()
    busca = request.args.get("q", "").strip().lower()
    if categoria:
        sql += " AND categoria = :categoria"
        params["categoria"] = categoria
    if busca:
        # LOWER(...) torna a busca sem diferenciar maiúsculas tanto no SQLite quanto no PostgreSQL
        sql += " AND (LOWER(item) LIKE :busca OR LOWER(doador) LIKE :busca)"
        params["busca"] = f"%{busca}%"
    sql += " ORDER BY id DESC"
    linhas = get_db().execute(sql, params).fetchall()
    return jsonify([dict(l) for l in linhas])


@bp.post("/doacoes")
def criar():
    dados, erros = validar_doacao(request.get_json(silent=True))
    if erros:
        return _erro("Dados inválidos.", 400, erros)
    banco = get_db()
    linha = banco.execute(
        "INSERT INTO doacoes (item, categoria, quantidade, doador, cep, cidade, uf) "
        "VALUES (:item, :categoria, :quantidade, :doador, :cep, :cidade, :uf) RETURNING *",
        dados,
    ).fetchone()
    banco.commit()
    resposta = jsonify(dict(linha))
    resposta.status_code = 201
    resposta.headers["Location"] = f"/api/doacoes/{linha['id']}"
    return resposta


@bp.get("/doacoes/<int:doacao_id>")
def detalhar(doacao_id):
    linha = _buscar(doacao_id)
    if linha is None:
        return _erro("Doação não encontrada.", 404)
    return jsonify(dict(linha))


@bp.put("/doacoes/<int:doacao_id>")
def atualizar(doacao_id):
    if _buscar(doacao_id) is None:
        return _erro("Doação não encontrada.", 404)
    dados, erros = validar_doacao(request.get_json(silent=True))
    if erros:
        return _erro("Dados inválidos.", 400, erros)
    banco = get_db()
    banco.execute(
        "UPDATE doacoes SET item=:item, categoria=:categoria, quantidade=:quantidade, "
        "doador=:doador, cep=:cep, cidade=:cidade, uf=:uf WHERE id=:id",
        {**dados, "id": doacao_id},
    )
    banco.commit()
    return jsonify(dict(_buscar(doacao_id)))


@bp.delete("/doacoes/<int:doacao_id>")
def remover(doacao_id):
    if _buscar(doacao_id) is None:
        return _erro("Doação não encontrada.", 404)
    banco = get_db()
    banco.execute("DELETE FROM doacoes WHERE id = :id", {"id": doacao_id})
    banco.commit()
    return "", 204


# ---- v2: API externa (ViaCEP) -------------------------------------------------
@bp.get("/cep/<cep>")
def consultar_cep(cep):
    try:
        return jsonify(buscar_cep(cep, current_app.config.get("CEP_CONSULTOR")))
    except CepErro as e:
        return _erro(e.mensagem, e.status)


# ---- v2: feedback da comunidade ----------------------------------------------
@bp.post("/feedbacks")
def criar_feedback():
    dados, erros = validar_feedback(request.get_json(silent=True))
    if erros:
        return _erro("Dados inválidos.", 400, erros)
    banco = get_db()
    linha = banco.execute(
        "INSERT INTO feedbacks (nota, perfil, comentario, versao) "
        "VALUES (:nota, :perfil, :comentario, :versao) RETURNING *",
        {**dados, "versao": current_app.config["VERSAO"]},
    ).fetchone()
    banco.commit()
    return jsonify(dict(linha)), 201


@bp.get("/feedbacks")
def listar_feedbacks():
    linhas = get_db().execute("SELECT * FROM feedbacks ORDER BY id DESC").fetchall()
    return jsonify([dict(l) for l in linhas])


# ---- v2: análise de dados -----------------------------------------------------
@bp.get("/estatisticas")
def estatisticas():
    banco = get_db()
    doacoes = [dict(l) for l in banco.execute("SELECT * FROM doacoes").fetchall()]
    feedbacks = [dict(l) for l in banco.execute("SELECT * FROM feedbacks").fetchall()]
    return jsonify({
        "doacoes": analytics.resumir_doacoes(doacoes),
        "feedbacks": analytics.resumir_feedbacks(feedbacks),
    })
