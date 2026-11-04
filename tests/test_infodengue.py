import unittest
from datetime import date

from app.infodengue import InfoDengueErro, buscar_situacao, normalizar
from tests.base import BaseTestCase


def semana(se, casos, nivel=1):
    # formato devolvido pela API alertcity do InfoDengue
    return {"data_iniSE": 1760227200000, "SE": se, "casos_est": casos + 0.6, "casos": casos,
            "p_inc100k": casos * 2.123, "nivel": nivel, "Rt": 0.9}


RESPOSTA = [semana(202601 + i, i, 1 if i < 10 else 2) for i in range(14)][::-1]  # vem fora de ordem


def falso_ok(geocode, ano):
    return RESPOSTA


def falso_fora_do_ar(geocode, ano):
    raise InfoDengueErro("O InfoDengue está indisponível no momento.", 502)


class NormalizarTest(unittest.TestCase):
    def test_ultimas_12_semanas_em_ordem(self):
        linhas = normalizar(RESPOSTA)
        self.assertEqual(len(linhas), 12)
        self.assertEqual([l["se"] for l in linhas], list(range(202603, 202615)))
        ultima = linhas[-1]
        self.assertEqual((ultima["semana"], ultima["ano"], ultima["casos"]), (14, 2026, 13))
        self.assertEqual((ultima["casos_estimados"], ultima["incidencia_100mil"]), (14, 27.6))
        self.assertEqual((ultima["nivel"], ultima["nivel_nome"]), (2, "amarelo"))

    def test_aceita_nomes_alternativos_e_ignora_lixo(self):
        linhas = normalizar([{"se": 202540, "casos": 3, "inc": 1.5, "nivel": 4}, {"sem": "se"}, "x"])
        self.assertEqual(len(linhas), 1)
        self.assertEqual((linhas[0]["incidencia_100mil"], linhas[0]["nivel_nome"]), (1.5, "vermelho"))

    def test_resposta_inesperada(self):
        with self.assertRaises(InfoDengueErro):
            normalizar({"error_message": "GEO-Code sent is empty."})

    def test_geocode_invalido(self):
        with self.assertRaises(InfoDengueErro) as ctx:
            buscar_situacao("123", falso_ok)
        self.assertEqual(ctx.exception.status, 400)

    def test_consulta_pede_ano_atual(self):
        anos = []
        buscar_situacao("3518206", lambda g, ano: anos.append((g, ano)) or [], hoje=date(2026, 1, 5), usar_cache=False)
        self.assertEqual(anos, [(3518206, 2026)])


class DengueRotaTest(BaseTestCase):
    def test_rota_com_tendencia_e_nome(self):
        self.app.config["INFODENGUE_CONSULTOR"] = falso_ok
        d = self.client.get("/api/dengue/3518206").get_json()
        self.assertEqual(d["municipio"], "Guararapes")
        self.assertEqual(d["atual"]["casos"], 13)
        self.assertEqual(d["tendencia"]["direcao"], "alta")
        self.assertIn("InfoDengue", d["fonte"])

    def test_rota_propaga_falha_da_api_externa(self):
        self.app.config["INFODENGUE_CONSULTOR"] = falso_fora_do_ar
        r = self.client.get("/api/dengue/3518206")
        self.assertEqual(r.status_code, 502)
        self.assertIn("indisponível", r.get_json()["erro"])
