CREATE TABLE IF NOT EXISTS doacoes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    item       TEXT    NOT NULL,
    categoria  TEXT    NOT NULL CHECK (categoria IN ('alimento','higiene','vestuario','outros')),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    doador     TEXT,
    cep        TEXT,
    cidade     TEXT,
    uf         TEXT,
    criado_em  TEXT    NOT NULL DEFAULT (datetime('now'))
);
