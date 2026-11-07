-- Registros de possíveis criadouros do Aedes aegypti informados pela comunidade.
-- Não guarda nome nem e-mail. O WhatsApp é opcional, só com autorização, nunca sai
-- na lista pública e é apagado depois do aviso final (LGPD: consentimento e necessidade).
CREATE TABLE IF NOT EXISTS focos (
    id            SERIAL PRIMARY KEY,
    tipo          TEXT    NOT NULL CHECK (tipo IN ('pneu','caixa_dagua','vaso_planta','lixo_entulho','piscina','calha','terreno','outros')),
    descricao     TEXT,
    logradouro    TEXT    NOT NULL,
    numero        TEXT,
    bairro        TEXT    NOT NULL,
    cep           TEXT,
    cidade        TEXT,
    uf            TEXT,
    whatsapp      TEXT,
    status        TEXT    NOT NULL DEFAULT 'aberto' CHECK (status IN ('aberto','vistoriado','eliminado')),
    criado_em     TEXT    NOT NULL DEFAULT to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS'),
    atualizado_em TEXT    NOT NULL DEFAULT to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS')
);

CREATE TABLE IF NOT EXISTS avaliacoes (
    id         SERIAL PRIMARY KEY,
    nota       INTEGER NOT NULL CHECK (nota BETWEEN 1 AND 5),
    perfil     TEXT    NOT NULL CHECK (perfil IN ('morador','agente','coordenador')),
    comentario TEXT,
    versao     TEXT    NOT NULL,
    criado_em  TEXT    NOT NULL DEFAULT to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS')
);
