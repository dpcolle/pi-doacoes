"""API REST própria do sistema (JSON)."""
from flask import Blueprint, current_app, jsonify, request

from .db import get_db
from .validators import validar_doacao

bp = Blueprint("api", __name__, url_prefix="/api")


def _erro(mensagem, status, detalhes=None):
    corpo = {"erro": mensagem}
    if detalhes:
        corpo["detalhes"] = detalhes
    return jsonify(corpo), status


def _buscar(doacao_id):
    return get_db().execute("SELECT * FROM doacoes WHERE id = ?", (doacao_id,)).fetchone()


@bp.get("/saude")
def saude():
    """Usado por serviços de nuvem para verificar se a aplicação está no ar."""
    get_db().execute("SELECT 1")
    return jsonify({"status": "ok", "versao": current_app.config["VERSAO"]})


@bp.get("/doacoes")
def listar():
    sql, params = "SELECT * FROM doacoes WHERE 1=1", []
    categoria = request.args.get("categoria", "").strip().lower()
    busca = request.args.get("q", "").strip()
    if categoria:
        sql += " AND categoria = ?"
        params.append(categoria)
    if busca:
        sql += " AND (item LIKE ? OR doador LIKE ?)"
        params += [f"%{busca}%", f"%{busca}%"]
    sql += " ORDER BY id DESC"
    linhas = get_db().execute(sql, params).fetchall()
    return jsonify([dict(l) for l in linhas])


@bp.post("/doacoes")
def criar():
    dados, erros = validar_doacao(request.get_json(silent=True))
    if erros:
        return _erro("Dados inválidos.", 400, erros)
    banco = get_db()
    cur = banco.execute(
        "INSERT INTO doacoes (item, categoria, quantidade, doador, cep, cidade, uf) "
        "VALUES (:item, :categoria, :quantidade, :doador, :cep, :cidade, :uf)",
        dados,
    )
    banco.commit()
    resposta = jsonify(dict(_buscar(cur.lastrowid)))
    resposta.status_code = 201
    resposta.headers["Location"] = f"/api/doacoes/{cur.lastrowid}"
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
    banco.execute("DELETE FROM doacoes WHERE id = ?", (doacao_id,))
    banco.commit()
    return "", 204
