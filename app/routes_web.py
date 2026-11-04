"""Páginas HTML."""
from flask import Blueprint, render_template

bp = Blueprint("web", __name__)


@bp.get("/")
def index():
    return render_template("index.html")


@bp.get("/painel")
def painel():
    return render_template("painel.html")


@bp.get("/prevencao")
def prevencao():
    return render_template("prevencao.html")


@bp.get("/avaliar")
def avaliar():
    return render_template("avaliar.html")
