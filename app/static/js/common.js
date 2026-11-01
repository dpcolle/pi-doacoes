"use strict";

/** Chamada à API própria; lança Error com .detalhes quando a API devolve erro. */
async function api(caminho, opcoes = {}) {
  const resposta = await fetch(caminho, {
    headers: { "Content-Type": "application/json" },
    ...opcoes,
  });
  if (resposta.status === 204) return null;
  const corpo = await resposta.json().catch(() => ({}));
  if (!resposta.ok) {
    const erro = new Error(corpo.erro || "Erro inesperado. Tente novamente.");
    erro.detalhes = corpo.detalhes || {};
    erro.status = resposta.status;
    throw erro;
  }
  return corpo;
}

/** Mensagem lida por leitores de tela (região aria-live). */
function avisar(mensagem, tipo = "ok") {
  const el = document.getElementById("status");
  el.textContent = mensagem;
  el.dataset.tipo = tipo;
}

function limparErros(form) {
  form.querySelectorAll(".erro").forEach((e) => (e.textContent = ""));
  form.querySelectorAll("[aria-invalid]").forEach((e) => e.removeAttribute("aria-invalid"));
}

function mostrarErros(form, detalhes) {
  let primeiro = null;
  for (const [campo, msg] of Object.entries(detalhes)) {
    const entrada = form.elements[campo];
    const alvo = document.getElementById("erro-" + campo);
    if (alvo) alvo.textContent = msg;
    if (entrada) {
      entrada.setAttribute("aria-invalid", "true");
      primeiro = primeiro || entrada;
    }
  }
  if (primeiro) primeiro.focus();
}

function formatarData(iso) {
  const d = new Date(iso.replace(" ", "T") + "Z");
  return d.toLocaleDateString("pt-BR");
}
