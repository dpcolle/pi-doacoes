"use strict";

/** Código do agente de endemias, guardado só nesta aba do navegador. */
function codigoAgente() {
  try { return sessionStorage.getItem("pi-agente") || ""; } catch (_) { return ""; }
}

function guardarCodigoAgente(codigo) {
  try {
    if (codigo) sessionStorage.setItem("pi-agente", codigo);
    else sessionStorage.removeItem("pi-agente");
  } catch (_) { /* modo privado: vale só até recarregar */ }
}

/** Chamada à API própria; lança Error com .detalhes quando a API devolve erro. */
async function api(caminho, opcoes = {}) {
  const cabecalhos = { "Content-Type": "application/json" };
  const codigo = opcoes.codigo !== undefined ? opcoes.codigo : codigoAgente();
  if (codigo) cabecalhos["X-Codigo-Agente"] = codigo;
  const { codigo: _ignorado, ...resto } = opcoes;
  const resposta = await fetch(caminho, { headers: cabecalhos, ...resto });
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
