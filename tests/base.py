import os
import tempfile
import unittest

from app import create_app


class BaseTestCase(unittest.TestCase):
    """Cria um app com banco SQLite temporário e isolado para cada teste."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app(
            {"TESTING": True, "DATABASE": os.path.join(self.tmp.name, "teste.sqlite")}
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def nova_doacao(self, **extra):
        dados = {"item": "Arroz 5kg", "categoria": "alimento", "quantidade": 10}
        dados.update(extra)
        return self.client.post("/api/doacoes", json=dados)
