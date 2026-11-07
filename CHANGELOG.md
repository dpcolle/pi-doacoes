# Histórico de versões

## 2.0.0 - Solução final: melhorias a partir da avaliação da comunidade
Mudanças pedidas por quem usou a versão 1.0 (avaliações de 07/11/2026 na tela "Avaliar o sistema"):
- **Compartilhar nas redes sociais** (sugestão de morador): botões para enviar no WhatsApp,
  publicar no Facebook, menu de compartilhar do celular e copiar o link, em todas as páginas.
- **Aviso ao morador pelo WhatsApp** (sugestão de morador): número opcional, só com autorização
  expressa; nunca aparece na lista pública; o agente abre o WhatsApp com a mensagem pronta e o número
  é apagado depois do aviso de eliminação (LGPD: consentimento, finalidade e necessidade).
- **Área do agente protegida por código** (variável `AGENTE_CODIGO`): só o agente muda a situação,
  exclui registros e vê o botão de aviso. Antes qualquer visitante podia alterar.
- **Número ou ponto de referência** aceita até 50 caracteres (antes 10), para referências como
  "ao lado do ecoponto".
- Migração automática do banco da versão 1.0 (coluna `whatsapp`).
- 62 testes automatizados.

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
