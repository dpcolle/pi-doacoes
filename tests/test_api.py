from tests.base import BaseTestCase


class ApiFocosTest(BaseTestCase):
    def test_saude(self):
        r = self.client.get("/api/saude")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["status"], "ok")

    def test_criar_e_detalhar(self):
        r = self.novo_foco()
        self.assertEqual(r.status_code, 201)
        criado = r.get_json()
        self.assertEqual(r.headers["Location"], f"/api/focos/{criado['id']}")
        self.assertEqual(criado["status"], "aberto")  # todo registro começa aguardando vistoria
        r2 = self.client.get(f"/api/focos/{criado['id']}")
        self.assertEqual(r2.get_json()["bairro"], "Centro")

    def test_criar_invalido_retorna_400_com_detalhes(self):
        r = self.client.post("/api/focos", json={"tipo": "x"})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(set(r.get_json()["detalhes"]), {"tipo", "logradouro", "bairro"})

    def test_corpo_que_nao_e_json(self):
        r = self.client.post("/api/focos", data="texto", content_type="text/plain")
        self.assertEqual(r.status_code, 400)

    def test_listar_com_filtros(self):
        self.novo_foco()
        id2 = self.novo_foco(tipo="calha", bairro="Jardim América").get_json()["id"]
        self.client.patch(f"/api/focos/{id2}/status", json={"status": "eliminado"})
        self.assertEqual(len(self.client.get("/api/focos").get_json()), 2)
        abertos = self.client.get("/api/focos?status=aberto").get_json()
        self.assertEqual([f["bairro"] for f in abertos], ["Centro"])
        por_bairro = self.client.get("/api/focos?q=jardim").get_json()
        self.assertEqual([f["id"] for f in por_bairro], [id2])
        so_calha = self.client.get("/api/focos?tipo=calha").get_json()
        self.assertEqual(len(so_calha), 1)

    def test_mudar_status(self):
        id_ = self.novo_foco().get_json()["id"]
        r = self.client.patch(f"/api/focos/{id_}/status", json={"status": "vistoriado"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["status"], "vistoriado")

    def test_status_invalido(self):
        id_ = self.novo_foco().get_json()["id"]
        r = self.client.patch(f"/api/focos/{id_}/status", json={"status": "resolvido?"})
        self.assertEqual(r.status_code, 400)
        self.assertIn("status", r.get_json()["detalhes"])

    def test_atualizar(self):
        id_ = self.novo_foco().get_json()["id"]
        r = self.client.put(f"/api/focos/{id_}",
                            json={"tipo": "piscina", "logradouro": "Rua das Flores", "bairro": "Vila Nova"})
        self.assertEqual((r.get_json()["tipo"], r.get_json()["bairro"]), ("piscina", "Vila Nova"))

    def test_remover(self):
        id_ = self.novo_foco().get_json()["id"]
        self.assertEqual(self.client.delete(f"/api/focos/{id_}").status_code, 204)
        self.assertEqual(self.client.get(f"/api/focos/{id_}").status_code, 404)

    def test_inexistente_retorna_404(self):
        self.assertEqual(self.client.get("/api/focos/999").status_code, 404)
        self.assertEqual(self.client.delete("/api/focos/999").status_code, 404)
        self.assertEqual(self.client.patch("/api/focos/999/status", json={"status": "aberto"}).status_code, 404)

    def test_sql_injection_nao_funciona(self):
        self.novo_foco()
        r = self.client.get("/api/focos", query_string={"q": "'; DROP TABLE focos; --", "status": "x' OR '1'='1"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json(), [])
        self.assertEqual(len(self.client.get("/api/focos").get_json()), 1)

    def test_nao_guarda_dados_pessoais(self):
        criado = self.novo_foco(nome="Fulano", telefone="18999999999").get_json()
        self.assertNotIn("nome", criado)
        self.assertNotIn("telefone", criado)


class PaginasTest(BaseTestCase):
    def test_paginas_e_acessibilidade(self):
        for caminho in ("/", "/painel", "/prevencao", "/avaliar"):
            with self.subTest(caminho=caminho):
                r = self.client.get(caminho)
                self.assertEqual(r.status_code, 200)
                html = r.get_data(as_text=True)
                self.assertIn('lang="pt-BR"', html)
                self.assertIn("Pular para o conteúdo principal", html)
                self.assertIn('aria-label="Ferramentas de acessibilidade"', html)
                self.assertIn("vlibras", html)

    def test_municipios_configurados(self):
        lista = self.client.get("/api/municipios").get_json()
        self.assertIn({"nome": "Guararapes", "geocode": "3518206"}, lista)
