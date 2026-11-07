import os
import unittest

from app import create_app
from app.db import adaptar_sql
from tests.base import BaseTestCase


class AdaptarSqlTest(unittest.TestCase):
    def test_postgres_converte_parametros_nomeados(self):
        sql = "INSERT INTO t (a, b) VALUES (:a, :b) RETURNING *"
        self.assertEqual(adaptar_sql(sql, "postgres"),
                         "INSERT INTO t (a, b) VALUES (%(a)s, %(b)s) RETURNING *")

    def test_postgres_repetido_e_cast(self):
        sql = "WHERE x LIKE :q OR y LIKE :q AND z = 1::int"
        self.assertEqual(adaptar_sql(sql, "postgres"),
                         "WHERE x LIKE %(q)s OR y LIKE %(q)s AND z = 1::int")

    def test_sqlite_nao_altera(self):
        sql = "SELECT * FROM t WHERE id = :id"
        self.assertEqual(adaptar_sql(sql, "sqlite"), sql)


class SchemasTest(unittest.TestCase):
    def test_schemas_tem_as_mesmas_tabelas(self):
        base = os.path.join(os.path.dirname(__file__), "..", "app")
        def tabelas(nome):
            with open(os.path.join(base, nome), encoding="utf-8") as f:
                texto = f.read()
            return sorted(l.split()[5] for l in texto.splitlines() if l.startswith("CREATE TABLE"))
        self.assertEqual(tabelas("schema.sql"), tabelas("schema_postgres.sql"))
        self.assertEqual(tabelas("schema.sql"), ["avaliacoes", "focos"])


class SaudeTest(BaseTestCase):
    def test_saude_padrao_nao_toca_no_banco(self):
        corpo = self.client.get("/api/saude").get_json()
        self.assertEqual(corpo["status"], "ok")
        self.assertNotIn("banco", corpo)

    def test_saude_com_banco(self):
        self.assertEqual(self.client.get("/api/saude?db=1").get_json()["banco"], "sqlite")


@unittest.skipUnless(os.environ.get("TEST_DATABASE_URL"),
                     "defina TEST_DATABASE_URL (use uma branch de teste do Neon) para rodar")
class PostgresIntegracaoTest(unittest.TestCase):
    """Roda contra um PostgreSQL real. Remove só os registros que ele mesmo criou."""

    def setUp(self):
        self.app = create_app({"TESTING": True, "DATABASE_URL": os.environ["TEST_DATABASE_URL"],
                               "AGENTE_CODIGO": "integ"})
        self.agente = {"X-Codigo-Agente": "integ"}
        self.client = self.app.test_client()
        self.ids = []

    def tearDown(self):
        for id_ in self.ids:
            self.client.delete(f"/api/focos/{id_}", headers=self.agente)

    def test_fluxo_completo(self):
        self.assertEqual(self.client.get("/api/saude?db=1").get_json()["banco"], "postgres")
        r = self.client.post("/api/focos", json={"tipo": "outros", "logradouro": "ZZ Rua Teste Integração",
                                                "bairro": "Bairro Teste"})
        self.assertEqual(r.status_code, 201)
        id_ = r.get_json()["id"]
        self.ids.append(id_)
        self.assertEqual(self.client.get(f"/api/focos/{id_}").status_code, 200)
        achados = self.client.get("/api/focos?q=bairro TESTE").get_json()  # busca sem diferenciar maiúsculas
        self.assertIn(id_, [f["id"] for f in achados])
        r = self.client.patch(f"/api/focos/{id_}/status", json={"status": "eliminado"}, headers=self.agente)
        self.assertEqual(r.get_json()["status"], "eliminado")
        self.assertEqual(self.client.get("/api/estatisticas").status_code, 200)
        av = self.client.post("/api/avaliacoes", json={"nota": 5, "perfil": "morador"})
        self.assertEqual(av.status_code, 201)
        self.assertEqual(self.client.delete(f"/api/focos/{id_}", headers=self.agente).status_code, 204)
        self.ids.remove(id_)
