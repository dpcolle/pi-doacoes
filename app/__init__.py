"""Sistema de Gestão de Doações Comunitárias - Projeto Integrador Univesp."""
import os

from flask import Flask

from . import db

__version__ = "1.0.0"


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.environ.get(
            "DATABASE_PATH", os.path.join(app.instance_path, "doacoes.sqlite")
        ),
        VERSAO=__version__,
    )
    app.json.ensure_ascii = False
    if config:
        app.config.update(config)

    os.makedirs(os.path.dirname(os.path.abspath(app.config["DATABASE"])), exist_ok=True)
    app.teardown_appcontext(db.close_db)
    with app.app_context():
        db.init_db()

    from .routes_api import bp as api_bp
    from .routes_web import bp as web_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)
    return app
