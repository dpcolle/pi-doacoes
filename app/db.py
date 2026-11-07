"""Acesso ao banco de dados.

- Sem DATABASE_URL: SQLite local (desenvolvimento e testes).
- Com DATABASE_URL (postgresql://...): PostgreSQL, por exemplo o Neon (produção).

O SQL do projeto é escrito uma única vez, com parâmetros nomeados (:nome),
e traduzido para o PostgreSQL (%(nome)s) quando necessário.
"""
import re
import sqlite3

from flask import current_app, g

_PARAM_NOMEADO = re.compile(r"(?<![:\w]):([A-Za-z_]\w*)")


def adaptar_sql(sql, dialeto):
    if dialeto == "postgres":
        return _PARAM_NOMEADO.sub(r"%(\1)s", sql)
    return sql


class Conexao:
    """Interface mínima igual para SQLite e PostgreSQL."""

    def __init__(self, bruta, dialeto):
        self.bruta = bruta
        self.dialeto = dialeto

    def execute(self, sql, params=None):
        sql = adaptar_sql(sql, self.dialeto)
        if self.dialeto == "postgres":
            return self.bruta.execute(sql, params or None)
        return self.bruta.execute(sql, params or ())

    def executar_script(self, script):
        if self.dialeto == "sqlite":
            self.bruta.executescript(script)
        else:
            for comando in script.split(";"):
                if comando.strip():
                    self.bruta.execute(comando)
            self.bruta.commit()

    def commit(self):
        self.bruta.commit()

    def close(self):
        self.bruta.close()


def get_db():
    if "db" not in g:
        url = current_app.config.get("DATABASE_URL")
        if url:
            import psycopg  # importado só quando o PostgreSQL é usado
            from psycopg.rows import dict_row

            bruta = psycopg.connect(url, row_factory=dict_row, connect_timeout=15)
            g.db = Conexao(bruta, "postgres")
        else:
            bruta = sqlite3.connect(current_app.config["DATABASE"])
            bruta.row_factory = sqlite3.Row
            bruta.execute("PRAGMA foreign_keys = ON")
            g.db = Conexao(bruta, "sqlite")
    return g.db


def close_db(_erro=None):
    conexao = g.pop("db", None)
    if conexao is not None:
        conexao.close()


def init_db():
    banco = get_db()
    arquivo = "schema_postgres.sql" if banco.dialeto == "postgres" else "schema.sql"
    with current_app.open_resource(arquivo) as f:
        banco.executar_script(f.read().decode("utf-8"))
    migrar(banco)


def migrar(banco):
    """Atualiza bancos criados por versões anteriores (o CREATE TABLE IF NOT EXISTS não altera tabelas)."""
    if banco.dialeto == "postgres":
        banco.execute("ALTER TABLE focos ADD COLUMN IF NOT EXISTS whatsapp TEXT")
    else:
        colunas = [linha["name"] for linha in banco.execute("PRAGMA table_info(focos)").fetchall()]
        if "whatsapp" not in colunas:
            banco.execute("ALTER TABLE focos ADD COLUMN whatsapp TEXT")
    banco.commit()
