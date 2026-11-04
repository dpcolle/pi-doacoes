import unittest

from app.analytics import resumir_avaliacoes, resumir_focos, tendencia_casos
from tests.base import BaseTestCase

FOCOS = [
    {"tipo": "pneu", "bairro": "Centro", "status": "aberto",
     "criado_em": "2026-09-03 10:00:00", "atualizado_em": "2026-09-03 10:00:00"},
    {"tipo": "pneu", "bairro": "Centro", "status": "vistoriado",
     "criado_em": "2026-09-10 10:00:00", "atualizado_em": "2026-09-11 10:00:00"},
    {"tipo": "calha", "bairro": "Vila Nova", "status": "eliminado",
     "criado_em": "2026-10-01 10:00:00", "atualizado_em": "2026-10-04 10:00:00"},
    {"tipo": "terreno", "bairro": "Vila Nova", "status": "eliminado",
     "criado_em": "2026-10-02 10:00:00", "atualizado_em": "2026-10-03 10:00:00"},
]


class AnalyticsTest(unittest.TestCase):
    def test_resumo_focos(self):
        r = resumir_focos(FOCOS)
        self.assertEqual((r["total"], r["abertos"], r["vistoriados"], r["eliminados"]), (4, 1, 1, 2))
        self.assertEqual(r["eliminados_pct"], 50.0)
        self.assertEqual(r["dias_ate_eliminar"], 2.0)  # média de 3 e 1 dias
        self.assertEqual(list(r["por_tipo"])[0], "pneu")
        self.assertEqual(r["bairros_pendentes"], [{"bairro": "Centro", "focos": 2}])  # eliminados não contam
        self.assertEqual([m["mes"] for m in r["serie_mensal"]], ["2026-09", "2026-10"])

    def test_resumo_vazio_nao_quebra(self):
        r = resumir_focos([])
        self.assertEqual((r["total"], r["eliminados_pct"], r["dias_ate_eliminar"]), (0, None, None))

    def test_resumo_avaliacoes_por_versao(self):
        r = resumir_avaliacoes([{"nota": 3, "versao": "1.0.0"}, {"nota": 4, "versao": "1.0.0"},
                                {"nota": 5, "versao": "2.0.0"}, {"nota": 5, "versao": "2.0.0"}])
        self.assertEqual(r["nota_media"], 4.25)
        self.assertEqual(r["satisfeitos_pct"], 75.0)
        self.assertEqual(r["media_por_versao"], {"1.0.0": 3.5, "2.0.0": 5})

    def test_avaliacoes_vazio(self):
        self.assertIsNone(resumir_avaliacoes([])["nota_media"])

    def test_tendencia(self):
        semanas = [{"casos": c} for c in (1, 1, 1, 1, 2, 2, 3, 3)]
        self.assertEqual(tendencia_casos(semanas),
                         {"ultimas": 10, "anteriores": 4, "variacao_pct": 150.0, "direcao": "alta"})
        self.assertIsNone(tendencia_casos(semanas[:5]))
        zero = tendencia_casos([{"casos": 0}] * 4 + [{"casos": None}] * 4)
        self.assertEqual((zero["direcao"], zero["variacao_pct"]), ("estável", None))


class EstatisticasRotaTest(BaseTestCase):
    def test_endpoint_e_avaliacao(self):
        self.novo_foco()
        r = self.client.post("/api/avaliacoes", json={"nota": 5, "perfil": "agente"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.get_json()["versao"], self.app.config["VERSAO"])
        est = self.client.get("/api/estatisticas").get_json()
        self.assertEqual(est["focos"]["abertos"], 1)
        self.assertEqual(est["avaliacoes"]["nota_media"], 5)

    def test_avaliacao_invalida(self):
        r = self.client.post("/api/avaliacoes", json={"nota": 9, "perfil": "x"})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(set(r.get_json()["detalhes"]), {"nota", "perfil"})
