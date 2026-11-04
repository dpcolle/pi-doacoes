# Histórico de versões

## 1.0.0 - Solução inicial: Alerta Dengue Comunitário
Primeira versão aplicada à comunidade (protótipo para coleta de feedback).
- Registro de possíveis criadouros do *Aedes aegypti* sem dados pessoais (LGPD), com CEP automático (ViaCEP).
- Acompanhamento pelo agente de endemias: situação aberto → vistoriado → eliminado.
- Painel: nível de alerta e casos semanais do município pela API do InfoDengue, com tendência de 4 semanas;
  indicadores dos registros (eliminados, tempo até eliminar, tipos e bairros pendentes).
- Página de prevenção, sintomas, sinais de alarme e vacina, com fontes oficiais.
- Avaliação do sistema por perfil (morador, agente, coordenação), com média por versão.
- Acessibilidade: VLibras, alto contraste, zoom, tabelas alternativas aos gráficos.
- 49 testes automatizados.

## 0.2.0 e 0.1.0 - Base técnica (sistema de exemplo)
Sistema de exemplo de doações usado para montar a base técnica: Flask, banco SQLite/PostgreSQL,
API REST, ViaCEP, painel, acessibilidade, nuvem e CI. Substituído pela versão 1.0.0 acima.
