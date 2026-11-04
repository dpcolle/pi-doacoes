-- Registros de possíveis criadouros do Aedes aegypti informados pela comunidade.
-- Não guarda nome, telefone nem e-mail de quem registra (LGPD: dados mínimos).
CREATE TABLE IF NOT EXISTS focos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo          TEXT    NOT NULL CHECK (tipo IN ('pneu','caixa_dagua','vaso_planta','lixo_entulho','piscina','calha','terreno','outros')),
    descricao     TEXT,
    logradouro    TEXT    NOT NULL,
    numero        TEXT,
    bairro        TEXT    NOT NULL,
    cep           TEXT,
    cidade        TEXT,
    uf            TEXT,
    status        TEXT    NOT NULL DEFAULT 'aberto' CHECK (status IN ('aberto','vistoriado','eliminado')),
    criado_em     TEXT    NOT NULL DEFAULT (datetime('now')),
    atualizado_em TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS avaliacoes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    nota       INTEGER NOT NULL CHECK (nota BETWEEN 1 AND 5),
    perfil     TEXT    NOT NULL CHECK (perfil IN ('morador','agente','coordenador')),
    comentario TEXT,
    versao     TEXT    NOT NULL,
    criado_em  TEXT    NOT NULL DEFAULT (datetime('now'))
);
