import unittest

from app.cep import CepErro, buscar_cep, normalizar
from tests.base import BaseTestCase

FALSO_OK = lambda cep: {"cep": "16200-000", "logradouro": "Rua A", "bairro": "Centro",
                        "localidade": "Birigui", "uf": "SP"}
FALSO_NAO_EXISTE = lambda cep: {"erro": True}


def FALSO_FORA_DO_AR(cep):
    raise CepErro("Serviço de CEP indisponível no momento.", 502)


class CepServicoTest(unittest.TestCase):
    def test_normalizar(self):
        self.assertEqual(normalizar("16.200-000"), "16200000")

    def test_busca_ok(self):
        r = buscar_cep("16200-000", FALSO_OK)
        self.assertEqual((r["cidade"], r["uf"]), ("Birigui", "SP"))

    def test_cep_curto(self):
        with self.assertRaises(CepErro) as ctx:
            buscar_cep("123", FALSO_OK)
        self.assertEqual(ctx.exception.status, 400)

    def test_cep_inexistente(self):
        with self.assertRaises(CepErro) as ctx:
            buscar_cep("00000000", FALSO_NAO_EXISTE)
        self.assertEqual(ctx.exception.status, 404)


class CepRotaTest(BaseTestCase):
    def test_rota_usa_consultor_injetado(self):
        self.app.config["CEP_CONSULTOR"] = FALSO_OK
        r = self.client.get("/api/cep/16200000")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["cidade"], "Birigui")

    def test_rota_propaga_falha_da_api_externa(self):
        self.app.config["CEP_CONSULTOR"] = FALSO_FORA_DO_AR
        self.assertEqual(self.client.get("/api/cep/16200000").status_code, 502)
