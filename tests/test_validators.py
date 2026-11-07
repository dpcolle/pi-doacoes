import unittest

from app.validators import validar_avaliacao, validar_foco, validar_status


class ValidarFocoTest(unittest.TestCase):
    def test_dados_validos_sao_normalizados(self):
        dados, erros = validar_foco({"tipo": " PNEU ", "logradouro": "  Rua A ", "bairro": "Centro",
                                     "cep": "16700-000", "uf": "sp", "descricao": ""})
        self.assertEqual(erros, {})
        self.assertEqual((dados["tipo"], dados["logradouro"], dados["cep"], dados["uf"]),
                         ("pneu", "Rua A", "16700000", "SP"))
        self.assertIsNone(dados["descricao"])

    def test_campos_obrigatorios(self):
        _, erros = validar_foco({})
        self.assertEqual(set(erros), {"tipo", "logradouro", "bairro"})

    def test_limites_de_tamanho(self):
        _, erros = validar_foco({"tipo": "pneu", "logradouro": "R" * 121, "bairro": "B",
                                 "numero": "1" * 51, "descricao": "x" * 301})
        self.assertEqual(set(erros), {"logradouro", "bairro", "numero", "descricao"})

    def test_cep_e_uf_invalidos(self):
        _, erros = validar_foco({"tipo": "calha", "logradouro": "Rua A", "bairro": "Centro",
                                 "cep": "123", "uf": "SPX"})
        self.assertEqual(set(erros), {"cep", "uf"})

    def test_corpo_nao_json(self):
        self.assertIn("corpo", validar_foco(None)[1])
        self.assertIn("corpo", validar_status("eliminado")[1])

    def test_status(self):
        self.assertEqual(validar_status({"status": "Eliminado"}), ("eliminado", {}))
        self.assertIn("status", validar_status({"status": "fechado"})[1])


class ValidarAvaliacaoTest(unittest.TestCase):
    def test_valida(self):
        dados, erros = validar_avaliacao({"nota": "4", "perfil": "AGENTE", "comentario": " ok "})
        self.assertEqual(erros, {})
        self.assertEqual(dados, {"nota": 4, "perfil": "agente", "comentario": "ok"})

    def test_invalida(self):
        for nota in (0, 6, True, "x", None):
            with self.subTest(nota=nota):
                _, erros = validar_avaliacao({"nota": nota, "perfil": "doador"})
                self.assertEqual(set(erros), {"nota", "perfil"})


if __name__ == "__main__":
    unittest.main()
