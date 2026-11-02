# Doações Comunitárias — Projeto Integrador (Univesp)

**Sistema publicado:** https://doacoes-comunitarias.onrender.com

> No plano gratuito, o primeiro acesso depois de um tempo sem uso pode levar cerca de 1 minuto.

## Integrantes

| Nome | RA | Polo |
|---|---|---|
| Diego Ettore Colle | 2005387 | Guararapes SP |

Sistema web para uma organização comunitária registrar doações recebidas, consultar o
estoque, medir indicadores e coletar a avaliação de quem usa. **O domínio é um exemplo:**
troque "doação" pela entidade do seu problema real (ver `docs/ADAPTAR_AO_SEU_PROJETO.md`).

## Requisitos técnicos atendidos

| Requisito | Onde está |
|---|---|
| Framework web | Flask (`app/`) |
| Banco de dados | PostgreSQL no Neon (produção) e SQLite (local e testes): `app/db.py`, `app/schema*.sql`; consultas parametrizadas |
| JavaScript | `app/static/js/` (consumo da API, validação, gráfico SVG, acessibilidade) |
| Nuvem | Aplicação no Render e banco no Neon; `Dockerfile`, `Procfile`, `render.yaml`, rota `/api/saude` |
| Uso de API | **Consome** a ViaCEP (`app/cep.py`) e **expõe** API REST própria (`app/routes_api.py`) |
| Acessibilidade | HTML semântico, *skip link*, rótulos, `aria-live`, foco visível, alto contraste, zoom de texto, tabela alternativa ao gráfico |
| Controle de versão | Git e GitHub; tags `v1.0.0` e `v2.0.0`; `CHANGELOG.md` |
| Testes | 35 testes `unittest` (`tests/`) e CI no GitHub Actions |
| Análise de dados (opcional) | `app/analytics.py` e painel `/painel` |

## Rodar localmente

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
flask --app wsgi run --debug        # http://127.0.0.1:5000
python -m unittest discover -s tests -t . -v
```

Linux ou macOS: troque a segunda linha por `source .venv/bin/activate`.

Sem a variável `DATABASE_URL`, o sistema usa SQLite local. Para usar o Neon, veja `docs/NEON.md`.

## Publicar na nuvem

1. Envie o código ao GitHub (`git push`).
2. No Render: **New > Web Service**, conecte o repositório e use
   `pip install -r requirements.txt` (build) e `gunicorn wsgi:app` (start).
3. Em **Environment Variables**, defina `DATABASE_URL` (string de conexão do Neon) e `PYTHON_VERSION` = `3.12.3`.
4. Em **Advanced**, use `/api/saude` como *Health Check Path*.

A string de conexão contém a senha do banco: nunca a coloque no código nem no GitHub.

## API

`GET/POST /api/doacoes` · `GET/PUT/DELETE /api/doacoes/<id>` · `GET /api/cep/<cep>` ·
`GET/POST /api/feedbacks` · `GET /api/estatisticas` · `GET /api/saude` (`?db=1` testa o banco)
