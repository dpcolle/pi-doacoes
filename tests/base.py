import os
import tempfile
import unittest

from app import create_app


class BaseTestCase(unittest.TestCase):
    """Cria um app com banco SQLite temporário e isolado para cada teste."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app(
            {"TESTING": True, "DATABASE": os.path.join(self.tmp.name, "teste.sqlite"),
             "DATABASE_URL": None}  # nunca usar o banco de produção nos testes
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def novo_foco(self, **extra):
        dados = {"tipo": "pneu", "logradouro": "Rua das Flores", "numero": "120", "bairro": "Centro"}
        dados.update(extra)
        return self.client.post("/api/focos", json=dados)
