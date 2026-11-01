from tests.base import BaseTestCase


class ApiDoacoesTest(BaseTestCase):
    def test_saude(self):
        r = self.client.get("/api/saude")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["status"], "ok")

    def test_criar_e_detalhar(self):
        r = self.nova_doacao()
        self.assertEqual(r.status_code, 201)
        criado = r.get_json()
        self.assertEqual(r.headers["Location"], f"/api/doacoes/{criado['id']}")
        r2 = self.client.get(f"/api/doacoes/{criado['id']}")
        self.assertEqual(r2.get_json()["item"], "Arroz 5kg")

    def test_criar_invalido_retorna_400_com_detalhes(self):
        r = self.client.post("/api/doacoes", json={"item": "x"})
        self.assertEqual(r.status_code, 400)
        self.assertIn("item", r.get_json()["detalhes"])

    def test_corpo_que_nao_e_json(self):
        r = self.client.post("/api/doacoes", data="texto", content_type="text/plain")
        self.assertEqual(r.status_code, 400)

    def test_listar_com_filtros(self):
        self.nova_doacao(item="Arroz")
        self.nova_doacao(item="Sabonete", categoria="higiene", doador="Maria")
        todos = self.client.get("/api/doacoes").get_json()
        self.assertEqual(len(todos), 2)
        so_higiene = self.client.get("/api/doacoes?categoria=higiene").get_json()
        self.assertEqual([d["item"] for d in so_higiene], ["Sabonete"])
        por_doador = self.client.get("/api/doacoes?q=maria").get_json()
        self.assertEqual(len(por_doador), 1)

    def test_atualizar(self):
        id_ = self.nova_doacao().get_json()["id"]
        r = self.client.put(f"/api/doacoes/{id_}",
                            json={"item": "Arroz 5kg", "categoria": "alimento", "quantidade": 99})
        self.assertEqual(r.get_json()["quantidade"], 99)

    def test_remover(self):
        id_ = self.nova_doacao().get_json()["id"]
        self.assertEqual(self.client.delete(f"/api/doacoes/{id_}").status_code, 204)
        self.assertEqual(self.client.get(f"/api/doacoes/{id_}").status_code, 404)

    def test_inexistente_retorna_404(self):
        self.assertEqual(self.client.get("/api/doacoes/999").status_code, 404)
        self.assertEqual(self.client.delete("/api/doacoes/999").status_code, 404)

    def test_sql_injection_nao_funciona(self):
        self.nova_doacao()
        r = self.client.get("/api/doacoes", query_string={"q": "'; DROP TABLE doacoes; --"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(self.client.get("/api/doacoes").get_json()), 1)

    def test_pagina_inicial(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn('lang="pt-BR"', r.get_data(as_text=True))
