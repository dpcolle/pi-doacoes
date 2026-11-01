# Adaptar o sistema ao problema real do seu grupo

O tema "doações" é um exemplo funcional. Para trocar de domínio:

1. `app/schema.sql`: renomeie a tabela `doacoes` e as colunas.
2. `app/validators.py`: ajuste `validar_doacao` e `CATEGORIAS`.
3. `app/routes_api.py`: renomeie rotas e SQL (`/api/doacoes`).
4. `app/analytics.py`: troque os indicadores pelos que importam à comunidade.
5. Templates e `app/static/js/doacoes.js`: textos, campos e colunas.
6. `tests/`: atualize os testes junto (rode a suíte a cada passo).

A API de CEP pode ser substituída por outra API pública relevante (clima, IBGE, etc.), mantendo o padrão de `app/cep.py`: função que consulta + parâmetro injetável para testes.
