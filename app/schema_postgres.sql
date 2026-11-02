CREATE TABLE IF NOT EXISTS doacoes (
    id         SERIAL PRIMARY KEY,
    item       TEXT    NOT NULL,
    categoria  TEXT    NOT NULL CHECK (categoria IN ('alimento','higiene','vestuario','outros')),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    doador     TEXT,
    cep        TEXT,
    cidade     TEXT,
    uf         TEXT,
    criado_em  TEXT    NOT NULL DEFAULT to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS')
);

CREATE TABLE IF NOT EXISTS feedbacks (
    id         SERIAL PRIMARY KEY,
    nota       INTEGER NOT NULL CHECK (nota BETWEEN 1 AND 5),
    perfil     TEXT    NOT NULL CHECK (perfil IN ('doador','voluntario','coordenador')),
    comentario TEXT,
    versao     TEXT    NOT NULL,
    criado_em  TEXT    NOT NULL DEFAULT to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS')
);
