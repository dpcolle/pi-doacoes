# Alerta Dengue Comunitário — Projeto Integrador (Univesp)

**Sistema publicado:** https://doacoes-comunitarias.onrender.com

> No plano gratuito, o primeiro acesso depois de um tempo sem uso pode levar cerca de 1 minuto.

## Integrantes

| Nome | RA | Polo |
|---|---|---|
| Diego Ettore Colle | 2005387 | Guararapes SP |

Sistema web para a comunidade **registrar possíveis criadouros do *Aedes aegypti*** (sem informar
dados pessoais) e para a equipe de combate às endemias **acompanhar a vistoria** de cada local
(aberto → vistoriado → eliminado). O painel mostra a **situação da dengue no município** com dados
oficiais do InfoDengue e os indicadores dos registros da comunidade.

## Telas

| Página | Para quem | O que faz |
|---|---|---|
| `/` Registrar criadouro | Moradores e agentes | Registro com CEP automático; lista com filtro; o agente muda a situação |
| `/painel` | Coordenação e comunidade | Nível de alerta e casos semanais do município (InfoDengue); locais registrados, eliminados, tempo até eliminar, tipos e bairros pendentes; satisfação por versão |
| `/prevencao` | Comunidade | Prevenção, sintomas, sinais de alarme e vacina, com fontes oficiais |
| `/avaliar` | Todos | Avaliação do sistema (nota, perfil e sugestão), ligada à versão |

## Requisitos técnicos atendidos

| Requisito | Onde está |
|---|---|
| Framework web | Flask (`app/`) |
| Banco de dados | PostgreSQL no Neon (produção) e SQLite (local e testes): `app/db.py`, `app/schema*.sql`; consultas parametrizadas |
| JavaScript | `app/static/js/` (consumo da API, validação, gráficos SVG, acessibilidade) |
| Nuvem | Aplicação no Render e banco no Neon; `Dockerfile`, `Procfile`, `render.yaml`, rota `/api/saude` |
| Uso de API | **Consome** ViaCEP (`app/cep.py`) e InfoDengue (`app/infodengue.py`); **expõe** API REST própria (`app/routes_api.py`) |
| Acessibilidade | HTML semântico, *skip link*, rótulos, `aria-live`, foco visível, alto contraste, zoom de texto, tabelas alternativas aos gráficos, VLibras |
| Controle de versão | Git e GitHub; tags de versão; `CHANGELOG.md` |
| Testes | 49 testes `unittest` (`tests/`) e CI no GitHub Actions |
| Análise de dados | `app/analytics.py`: taxa de eliminação, tempo médio até eliminar, ranking de tipos e bairros, tendência de casos (4 semanas × 4 anteriores), satisfação por versão |
| Privacidade (LGPD) | O registro não pede nome, telefone nem e-mail |

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

### Municípios do painel

Por padrão: Murutinga do Sul (3532108), Guararapes (3518206) e Penápolis (3537305).
Para trocar, defina a variável `MUNICIPIOS` no formato `Nome:codigoIBGE;Nome:codigoIBGE`.

## Publicar na nuvem

1. Envie o código ao GitHub (`git push`).
2. No Render: **New > Web Service**, conecte o repositório e use
   `pip install -r requirements.txt` (build) e `gunicorn wsgi:app` (start).
3. Em **Environment Variables**, defina `DATABASE_URL` (string de conexão do Neon) e `PYTHON_VERSION` = `3.12.3`.
4. Em **Advanced**, use `/api/saude` como *Health Check Path*.

A string de conexão contém a senha do banco: nunca a coloque no código nem no GitHub.

## API

`GET/POST /api/focos` (filtros `status`, `tipo`, `q`) · `GET/PUT/DELETE /api/focos/<id>` ·
`PATCH /api/focos/<id>/status` · `GET /api/cep/<cep>` · `GET /api/municipios` ·
`GET /api/dengue/<codigoIBGE>` · `GET/POST /api/avaliacoes` · `GET /api/estatisticas` ·
`GET /api/saude` (`?db=1` testa o banco)

## Fontes de dados

- [InfoDengue](https://info.dengue.mat.br) (Fiocruz/FGV): casos e nível de alerta por município e semana epidemiológica.
- [ViaCEP](https://viacep.com.br): endereço a partir do CEP.
