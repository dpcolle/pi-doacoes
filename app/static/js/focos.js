"use strict";

const TIPOS = Object.fromEntries(JSON.parse(document.getElementById("tipos-json").textContent));
const SITUACOES = { aberto: "Aberto", vistoriado: "Vistoriado", eliminado: "Eliminado" };
const form = document.getElementById("form-foco");
const corpo = document.getElementById("corpo-tabela");

function celula(texto) {
  const td = document.createElement("td");
  td.textContent = texto; // textContent evita XSS
  return td;
}

/* ---- Modo agente (v2) -----------------------------------------------------------
 * Só quem tem o código (variável AGENTE_CODIGO no servidor) muda a situação, exclui
 * e avisa o morador. Os demais veem a situação como texto.
 */
const formAgente = document.getElementById("form-agente");
const agenteAtivo = document.getElementById("agente-ativo");
let modoAgente = false;

function aplicarModoAgente(ativo) {
  modoAgente = ativo;
  formAgente.hidden = ativo;
  agenteAtivo.hidden = !ativo;
  carregar();
}

formAgente.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const campo = document.getElementById("codigo-agente");
  const erro = document.getElementById("erro-codigo-agente");
  erro.textContent = "";
  campo.removeAttribute("aria-invalid");
  try {
    await api("/api/agente/entrar", { method: "POST", codigo: campo.value });
    guardarCodigoAgente(campo.value);
    campo.value = "";
    aplicarModoAgente(true);
    avisar("Modo agente ativo.");
    document.getElementById("sair-agente").focus();
  } catch (e) {
    erro.textContent = e.message;
    campo.setAttribute("aria-invalid", "true");
    campo.focus();
  }
});

document.getElementById("sair-agente").addEventListener("click", () => {
  guardarCodigoAgente("");
  aplicarModoAgente(false);
  avisar("Você saiu do modo agente.");
  document.getElementById("codigo-agente").focus();
});

/** Público: a situação como texto. Agente: seletor que salva na hora. */
function celulaSituacao(f) {
  const td = document.createElement("td");
  if (!modoAgente) {
    const span = document.createElement("span");
    span.className = "situacao-texto situacao-" + f.status;
    span.textContent = SITUACOES[f.status];
    td.append(span);
    return td;
  }
  const sel = document.createElement("select");
  sel.setAttribute("aria-label", `Situação do registro em ${f.logradouro}, ${f.bairro}`);
  sel.className = "situacao situacao-" + f.status;
  for (const [valor, nome] of Object.entries(SITUACOES)) {
    sel.append(new Option(nome, valor, false, valor === f.status));
  }
  sel.addEventListener("change", async () => {
    try {
      await api(`/api/focos/${f.id}/status`, { method: "PATCH", body: JSON.stringify({ status: sel.value }) });
      f.status = sel.value;
      sel.className = "situacao situacao-" + sel.value;
      avisar(`Situação alterada para ${SITUACOES[sel.value]}.` + (f.tem_contato ? " Avise o morador pelo WhatsApp." : ""));
    } catch (e) {
      sel.value = f.status;
      avisar(e.message, "erro");
    }
  });
  td.append(sel);
  return td;
}

/** Abre o WhatsApp com a mensagem pronta. No aviso final (eliminado), apaga o número. */
async function avisarMorador(f, botao, endereco) {
  const janela = window.open("about:blank", "_blank"); // aberta no clique, para não ser bloqueada
  try {
    const { link, status } = await api(`/api/focos/${f.id}/contato`);
    if (janela) janela.location.href = link; else window.location.href = link;
    if (status === "eliminado") {
      await api(`/api/focos/${f.id}/contato`, { method: "DELETE" });
      f.tem_contato = false;
      botao.remove();
      avisar(`WhatsApp aberto para o registro em ${endereco}. Como foi o aviso final, o número foi apagado do sistema.`);
    } else {
      avisar(`WhatsApp aberto para o registro em ${endereco}. O número fica guardado até o aviso de eliminação.`);
    }
  } catch (e) {
    if (janela) janela.close();
    avisar(e.message, "erro");
  }
}

function linha(f) {
  const tr = document.createElement("tr");
  const endereco = [f.logradouro, f.numero].filter(Boolean).join(", ");
  const local = [f.cidade, f.uf].filter(Boolean).join("/");
  const tdTipo = celula(TIPOS[f.tipo] || f.tipo);
  if (f.descricao) {
    const p = document.createElement("small");
    p.className = "descricao";
    p.textContent = f.descricao;
    tdTipo.append(p);
  }
  tr.append(tdTipo, celula(endereco), celula(local ? `${f.bairro} (${local})` : f.bairro),
            celula(formatarData(f.criado_em)), celulaSituacao(f));
  if (!modoAgente) return tr;
  const acoes = document.createElement("td");
  acoes.className = "acoes";
  if (f.tem_contato) {
    const zap = document.createElement("button");
    zap.type = "button";
    zap.textContent = "Avisar no WhatsApp";
    zap.setAttribute("aria-label", `Avisar no WhatsApp o morador do registro em ${endereco}`);
    zap.addEventListener("click", () => avisarMorador(f, zap, endereco));
    acoes.append(zap);
  }
  const botao = document.createElement("button");
  botao.type = "button";
  botao.className = "perigo";
  botao.textContent = "Excluir";
  botao.setAttribute("aria-label", `Excluir registro em ${endereco}`);
  botao.addEventListener("click", () => excluir(f, endereco));
  acoes.append(botao);
  tr.append(acoes);
  return tr;
}

async function carregar() {
  const params = new URLSearchParams();
  const q = document.getElementById("filtro-q").value.trim();
  const status = document.getElementById("filtro-status").value;
  if (q) params.set("q", q);
  if (status) params.set("status", status);
  try {
    document.getElementById("col-acoes").hidden = !modoAgente;
    const dados = await api("/api/focos?" + params);
    corpo.replaceChildren(...dados.map(linha));
    if (!dados.length) {
      const tr = document.createElement("tr");
      const td = celula("Nenhum registro encontrado.");
      td.colSpan = modoAgente ? 6 : 5;
      tr.append(td);
      corpo.append(tr);
    }
  } catch (e) {
    avisar(e.message, "erro");
  }
}

async function excluir(f, endereco) {
  if (!window.confirm(`Excluir o registro em "${endereco}"?`)) return;
  try {
    await api("/api/focos/" + f.id, { method: "DELETE" });
    avisar("Registro excluído.");
    carregar();
  } catch (e) {
    avisar(e.message, "erro");
  }
}

/* ---- Consulta de CEP (API ViaCEP pelo servidor) --------------------------------
 * Roda quando o CEP chega a 8 dígitos, ao sair do campo e antes de registrar.
 * Preenche rua e bairro só se estiverem vazios: em cidades pequenas o CEP é geral
 * e a ViaCEP devolve só a cidade.
 */
const campoCep = form.elements.cep;
const botaoRegistrar = form.querySelector('button[type="submit"]');
let cepPreenchido = "";
let consultaAtual = null;

const soDigitos = (valor) => valor.replace(/\D/g, "");

function erroCep(mensagem) {
  document.getElementById("erro-cep").textContent = mensagem;
  campoCep.setAttribute("aria-invalid", "true");
}

function consultarCep() {
  const cep = soDigitos(campoCep.value);
  if (cep.length !== 8) return Promise.resolve(false);
  if (cep === cepPreenchido) return Promise.resolve(true);
  if (consultaAtual && consultaAtual.cep === cep) return consultaAtual.promessa;

  const promessa = (async () => {
    try {
      const d = await api("/api/cep/" + cep);
      if (soDigitos(campoCep.value) !== cep) return false;
      const el = form.elements;
      if (d.logradouro && !el.logradouro.value.trim()) el.logradouro.value = d.logradouro;
      if (d.bairro && !el.bairro.value.trim()) el.bairro.value = d.bairro;
      el.cidade.value = d.cidade;
      el.uf.value = d.uf;
      cepPreenchido = cep;
      avisar(`CEP encontrado: ${d.cidade}/${d.uf}.` + (d.logradouro ? "" : " Informe a rua e o bairro."));
      return true;
    } catch (e) {
      erroCep(e.message);
      avisar(e.message, "erro");
      return false;
    } finally {
      if (consultaAtual && consultaAtual.cep === cep) consultaAtual = null;
    }
  })();
  consultaAtual = { cep, promessa };
  return promessa;
}

campoCep.addEventListener("input", () => {
  document.getElementById("erro-cep").textContent = "";
  campoCep.removeAttribute("aria-invalid");
  if (soDigitos(campoCep.value).length === 8) consultarCep();
});
campoCep.addEventListener("blur", consultarCep);

/* ---- Registro ---------------------------------------------------------------- */
let enviando = false;

form.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  if (enviando) return; // evita registro duplicado com Enter ou clique repetido
  enviando = true;
  botaoRegistrar.disabled = true;
  form.setAttribute("aria-busy", "true");
  try {
    limparErros(form);
    const cep = soDigitos(campoCep.value);
    if (cep.length === 8 && cep !== cepPreenchido) await consultarCep();
    const dados = Object.fromEntries(new FormData(form));
    await api("/api/focos", { method: "POST", body: JSON.stringify(dados) });
    form.reset();
    cepPreenchido = "";
    avisar("Obrigado! O local foi registrado para a equipe de combate às endemias. Compartilhe o site com seus vizinhos.");
    document.getElementById("tipo").focus();
    carregar();
  } catch (e) {
    mostrarErros(form, e.detalhes || {});
    avisar(e.message, "erro");
  } finally {
    enviando = false;
    botaoRegistrar.disabled = false;
    form.removeAttribute("aria-busy");
  }
});

document.getElementById("form-filtro").addEventListener("submit", (ev) => {
  ev.preventDefault();
  carregar();
});

if (codigoAgente()) {
  api("/api/agente/entrar", { method: "POST" })
    .then(() => aplicarModoAgente(true))
    .catch(() => { guardarCodigoAgente(""); carregar(); });
} else {
  carregar();
}
