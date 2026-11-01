import unittest

from app.validators import validar_doacao


class ValidarDoacaoTest(unittest.TestCase):
    def test_dados_validos_sao_normalizados(self):
        dados, erros = validar_doacao(
            {"item": "  Feijão ", "categoria": "ALIMENTO", "quantidade": "3",
             "cep": "16200-000", "uf": "sp"}
        )
        self.assertEqual(erros, {})
        self.assertEqual(dados["item"], "Feijão")
        self.assertEqual(dados["categoria"], "alimento")
        self.assertEqual(dados["quantidade"], 3)
        self.assertEqual(dados["cep"], "16200000")
        self.assertEqual(dados["uf"], "SP")

    def test_campos_obrigatorios(self):
        _, erros = validar_doacao({})
        self.assertEqual(set(erros), {"item", "categoria", "quantidade"})

    def test_quantidade_invalida(self):
        for ruim in (0, -1, "abc", None, True, 100001, 2.5e9):
            with self.subTest(valor=ruim):
                _, erros = validar_doacao({"item": "Sabão", "categoria": "higiene", "quantidade": ruim})
                self.assertIn("quantidade", erros)

    def test_cep_e_uf_invalidos(self):
        _, erros = validar_doacao({"item": "Sabão", "categoria": "higiene", "quantidade": 1,
                                   "cep": "123", "uf": "SPX"})
        self.assertEqual(set(erros), {"cep", "uf"})

    def test_corpo_nao_json(self):
        _, erros = validar_doacao(None)
        self.assertIn("corpo", erros)


if __name__ == "__main__":
    unittest.main()
