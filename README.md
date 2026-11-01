# Doações Comunitárias — Projeto Integrador (Univesp)

Sistema web para uma organização comunitária registrar doações recebidas, consultar o
estoque, medir indicadores e coletar a avaliação de quem usa. **O domínio é um exemplo:**
troque "doação" pela entidade do seu problema real (ver `docs/ADAPTAR_AO_SEU_PROJETO.md`).

## Requisitos técnicos atendidos
| Requisito | Onde está |
|---|---|
| Framework web | Flask (`app/`) |
| Banco de dados | SQLite (`app/schema.sql`, `app/db.py`) — consultas parametrizadas |
| JavaScript | `app/static/js/` (consumo da API, validação, gráfico SVG, acessibilidade) |
| Nuvem | `Dockerfile`, `Procfile`, `render.yaml`, rota `/api/saude` |
| Uso de API | **Consome** ViaCEP (`app/cep.py`) e **expõe** API REST própria (`app/routes_api.py`) |
| Acessibilidade | HTML semântico, *skip link*, rótulos, `aria-live`, foco visível, alto contraste, zoom de texto, tabela alternativa ao gráfico |
| Controle de versão | Git; tags `v1.0.0` (solução inicial) e `v2.0.0` (final); `CHANGELOG.md` |
| Testes | 28 testes `unittest` (`tests/`) + CI no GitHub Actions |
| Análise de dados (opcional) | `app/analytics.py` + painel `/painel` |

## Rodar localmente
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app wsgi run --debug        # http://127.0.0.1:5000
python -m unittest discover -s tests -t . -v
```

## Publicar na nuvem
1. `git remote add origin <seu-repositório-no-GitHub>` e `git push --tags origin main`.
2. No Render.com: *New → Blueprint* e selecione o repositório (usa `render.yaml`).
3. No plano gratuito o banco é temporário; para dados persistentes use disco pago ou migre para PostgreSQL.

## API
`GET/POST /api/doacoes` · `GET/PUT/DELETE /api/doacoes/<id>` · `GET /api/cep/<cep>` ·
`GET/POST /api/feedbacks` · `GET /api/estatisticas` · `GET /api/saude`
