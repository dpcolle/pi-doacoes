# Histórico de versões

## 1.0.0 - Solução inicial (protótipo)
- Cadastro, listagem, filtro e exclusão de doações (API REST + interface web).
- Banco de dados SQLite, validação no servidor, testes automatizados.

## 2.0.0 - Solução final
- Integração com a API ViaCEP (cidade/UF automáticos) com tratamento de falha.
- Coleta de feedback da comunidade (`/feedback`) vinculada à versão do sistema.
- Análise de dados e painel de indicadores (`/painel`) com gráfico e tabela alternativa.
- Acessibilidade: ajuste de texto, alto contraste, skip link, rótulos e aria-live.
- Nuvem: Dockerfile, Procfile, render.yaml, rota de saúde; CI com GitHub Actions.
- 28 testes automatizados.
