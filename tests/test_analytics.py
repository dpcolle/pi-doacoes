import unittest

from app.analytics import resumir_doacoes, resumir_feedbacks
from tests.base import BaseTestCase

DOACOES = [
    {"categoria": "alimento", "quantidade": 10, "cidade": "Birigui", "criado_em": "2026-09-03 10:00:00"},
    {"categoria": "alimento", "quantidade": 20, "cidade": "Birigui", "criado_em": "2026-09-10 10:00:00"},
    {"categoria": "higiene", "quantidade": 3, "cidade": "Araçatuba", "criado_em": "2026-10-01 10:00:00"},
]


class AnalyticsTest(unittest.TestCase):
    def test_resumo_doacoes(self):
        r = resumir_doacoes(DOACOES)
        self.assertEqual(r["total_registros"], 3)
        self.assertEqual(r["total_itens"], 33)
        self.assertEqual(r["media_quantidade"], 11.0)
        self.assertEqual(r["mediana_quantidade"], 10)
        self.assertEqual(r["por_categoria"], {"alimento": 30, "higiene": 3})
        self.assertEqual(r["top_cidades"][0], {"cidade": "Birigui", "doacoes": 2})
        self.assertEqual([m["mes"] for m in r["serie_mensal"]], ["2026-09", "2026-10"])

    def test_resumo_vazio_nao_quebra(self):
        r = resumir_doacoes([])
        self.assertEqual((r["total_itens"], r["media_quantidade"]), (0, 0))

    def test_resumo_feedbacks(self):
        r = resumir_feedbacks([{"nota": 5}, {"nota": 4}, {"nota": 2}, {"nota": 5}])
        self.assertEqual(r["nota_media"], 4.0)
        self.assertEqual(r["satisfeitos_pct"], 75.0)
        self.assertEqual(r["distribuicao"]["5"], 2)

    def test_feedbacks_vazio(self):
        self.assertIsNone(resumir_feedbacks([])["nota_media"])


class EstatisticasRotaTest(BaseTestCase):
    def test_endpoint_e_feedback(self):
        self.nova_doacao(quantidade=7)
        r = self.client.post("/api/feedbacks", json={"nota": 5, "perfil": "voluntario"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.get_json()["versao"], self.app.config["VERSAO"])
        est = self.client.get("/api/estatisticas").get_json()
        self.assertEqual(est["doacoes"]["total_itens"], 7)
        self.assertEqual(est["feedbacks"]["nota_media"], 5)

    def test_feedback_invalido(self):
        r = self.client.post("/api/feedbacks", json={"nota": 9, "perfil": "x"})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(set(r.get_json()["detalhes"]), {"nota", "perfil"})

    def test_paginas_v2_e_acessibilidade(self):
        for caminho in ("/painel", "/feedback"):
            html = self.client.get(caminho).get_data(as_text=True)
            self.assertIn("Pular para o conteúdo principal", html)
            self.assertIn('aria-label="Ferramentas de acessibilidade"', html)
            self.assertIn('lang="pt-BR"', html)
