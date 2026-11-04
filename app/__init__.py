"""Alerta Dengue Comunitário - Projeto Integrador Univesp."""
import os

from flask import Flask

from . import db

__version__ = "1.0.0"

# Municípios do grupo (código IBGE). Pode ser trocado pela variável MUNICIPIOS,
# no formato "Nome:codigo;Nome:codigo".
MUNICIPIOS_PADRAO = "Murutinga do Sul:3532108;Guararapes:3518206;Penápolis:3537305"


def _ler_municipios(texto):
    lista = []
    for parte in texto.split(";"):
        nome, _, codigo = parte.partition(":")
        if nome.strip() and codigo.strip().isdigit():
            lista.append({"nome": nome.strip(), "geocode": codigo.strip()})
    return lista


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.environ.get(
            "DATABASE_PATH", os.path.join(app.instance_path, "dengue.sqlite")
        ),
        DATABASE_URL=os.environ.get("DATABASE_URL"),  # PostgreSQL (Neon); vazio = SQLite
        VERSAO=__version__,
        MUNICIPIOS=_ler_municipios(os.environ.get("MUNICIPIOS", MUNICIPIOS_PADRAO)),
    )
    app.json.ensure_ascii = False
    app.json.sort_keys = False  # mantém a ordem dos rankings (ex.: tipos mais registrados primeiro)
    if config:
        app.config.update(config)

    if not app.config["DATABASE_URL"]:
        os.makedirs(os.path.dirname(os.path.abspath(app.config["DATABASE"])), exist_ok=True)
    app.teardown_appcontext(db.close_db)
    with app.app_context():
        db.init_db()

    from .routes_api import bp as api_bp
    from .routes_web import bp as web_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)
    return app
