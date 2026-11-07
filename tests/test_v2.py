"""Versão 2.0: melhorias pedidas pela comunidade na avaliação da versão 1.0."""
import os
import sqlite3
import tempfile
import unittest
from urllib.parse import unquote

from app import create_app
from app.validators import normalizar_whatsapp, validar_foco
from tests.base import BaseTestCase


class NumeroTest(unittest.TestCase):
    def test_ponto_de_referencia_com_ate_50_caracteres(self):
        base = {"tipo": "pneu", "logradouro": "Rua A", "bairro": "Centro"}
        dados, erros = validar_foco({**base, "numero": "Em frente à Escola Estadual, perto do ecoponto"})
        self.assertEqual(erros, {})
        self.assertIn("ecoponto", dados["numero"])
        self.assertIn("numero", validar_foco({**base, "numero": "x" * 51})[1])


class WhatsappValidacaoTest(unittest.TestCase):
    def test_normalizar(self):
        self.assertEqual(normalizar_whatsapp("(18) 99999-1234"), "5518999991234")
        self.assertEqual(normalizar_whatsapp("+55 18 3606-1234"), "551836061234")
        self.assertIsNone(normalizar_whatsapp("  "))
        for ruim in ("123", "018999991234", "1899999123456"):
            with self.subTest(valor=ruim):
                self.assertIs(normalizar_whatsapp(ruim), False)

    def test_exige_autorizacao(self):
        base = {"tipo": "pneu", "logradouro": "Rua A", "bairro": "Centro", "whatsapp": "18999991234"}
        self.assertIn("aceite_contato", validar_foco(base)[1])
        dados, erros = validar_foco({**base, "aceite_contato": "on"})
        self.assertEqual((erros, dados["whatsapp"]), ({}, "5518999991234"))

    def test_sem_whatsapp_nao_exige_autorizacao(self):
        self.assertEqual(validar_foco({"tipo": "pneu", "logradouro": "Rua A", "bairro": "Centro"})[1], {})


class PrivacidadeEAgenteTest(BaseTestCase):
    def foco_com_whatsapp(self):
        return self.novo_foco(whatsapp="(18) 99999-1234", aceite_contato="on").get_json()["id"]

    def test_whatsapp_nunca_aparece_na_api_publica(self):
        id_ = self.foco_com_whatsapp()
        for r in (self.client.get("/api/focos").get_json()[0], self.client.get(f"/api/focos/{id_}").get_json()):
            self.assertNotIn("whatsapp", r)
            self.assertTrue(r["tem_contato"])
            self.assertNotIn("99999", str(r))

    def test_acoes_de_agente_exigem_codigo(self):
        id_ = self.novo_foco().get_json()["id"]
        for metodo, caminho, corpo in (("patch", f"/api/focos/{id_}/status", {"status": "eliminado"}),
                                       ("delete", f"/api/focos/{id_}", None),
                                       ("get", f"/api/focos/{id_}/contato", None)):
            with self.subTest(caminho=caminho):
                r = getattr(self.client, metodo)(caminho, json=corpo, headers={"X-Codigo-Agente": "errado"})
                self.assertEqual(r.status_code, 401)
        self.assertEqual(self.client.get(f"/api/focos/{id_}").get_json()["status"], "aberto")

    def test_entrar_como_agente(self):
        self.assertEqual(self.client.post("/api/agente/entrar", headers=self.AGENTE).status_code, 204)
        self.assertEqual(self.client.post("/api/agente/entrar").status_code, 401)

    def test_sem_codigo_configurado_a_area_fica_fechada(self):
        self.app.config["AGENTE_CODIGO"] = None
        self.assertEqual(self.client.post("/api/agente/entrar", headers=self.AGENTE).status_code, 503)

    def test_link_do_whatsapp_com_mensagem_da_situacao(self):
        id_ = self.foco_com_whatsapp()
        self.client.patch(f"/api/focos/{id_}/status", json={"status": "eliminado"}, headers=self.AGENTE)
        link = self.client.get(f"/api/focos/{id_}/contato", headers=self.AGENTE).get_json()["link"]
        self.assertTrue(link.startswith("https://wa.me/5518999991234?text="))
        self.assertIn("foi eliminado", unquote(link))
        self.assertIn("Rua das Flores, 120, Centro", unquote(link))

    def test_numero_apagado_depois_do_aviso(self):
        id_ = self.foco_com_whatsapp()
        self.assertEqual(self.client.delete(f"/api/focos/{id_}/contato", headers=self.AGENTE).status_code, 204)
        self.assertFalse(self.client.get(f"/api/focos/{id_}").get_json()["tem_contato"])
        self.assertEqual(self.client.get(f"/api/focos/{id_}/contato", headers=self.AGENTE).status_code, 404)

    def test_editar_registro_nao_apaga_o_whatsapp(self):
        id_ = self.foco_com_whatsapp()
        self.client.put(f"/api/focos/{id_}", json={"tipo": "calha", "logradouro": "Rua B", "bairro": "Centro"},
                        headers=self.AGENTE)
        self.assertTrue(self.client.get(f"/api/focos/{id_}").get_json()["tem_contato"])

    def test_pagina_tem_compartilhar_e_campo_whatsapp(self):
        html = self.client.get("/").get_data(as_text=True)
        for trecho in ('id="share-whatsapp"', 'id="share-facebook"', 'id="copiar-link"',
                       'name="whatsapp"', 'name="aceite_contato"', 'maxlength="50"', 'id="form-agente"'):
            self.assertIn(trecho, html)
        self.assertIn('id="share-whatsapp"', self.client.get("/prevencao").get_data(as_text=True))


class MigracaoTest(unittest.TestCase):
    def test_banco_da_versao_1_ganha_a_coluna_whatsapp(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "v1.sqlite")
            antigo = sqlite3.connect(caminho)
            antigo.execute("CREATE TABLE focos (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT NOT NULL, "
                           "descricao TEXT, logradouro TEXT NOT NULL, numero TEXT, bairro TEXT NOT NULL, cep TEXT, "
                           "cidade TEXT, uf TEXT, status TEXT NOT NULL DEFAULT 'aberto', "
                           "criado_em TEXT NOT NULL DEFAULT (datetime('now')), "
                           "atualizado_em TEXT NOT NULL DEFAULT (datetime('now')))")
            antigo.execute("INSERT INTO focos (tipo, logradouro, bairro) VALUES ('pneu', 'Rua Velha', 'Centro')")
            antigo.commit()
            antigo.close()
            app = create_app({"TESTING": True, "DATABASE": caminho, "DATABASE_URL": None})
            cliente = app.test_client()
            self.assertEqual(cliente.get("/api/focos").get_json()[0]["logradouro"], "Rua Velha")
            r = cliente.post("/api/focos", json={"tipo": "pneu", "logradouro": "Rua Nova", "bairro": "Centro",
                                                 "whatsapp": "18999991234", "aceite_contato": True})
            self.assertEqual(r.status_code, 201)
