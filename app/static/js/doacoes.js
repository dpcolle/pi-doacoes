"use strict";

const NOMES = { alimento: "Alimento", higiene: "Higiene", vestuario: "Vestuário", outros: "Outros" };
const form = document.getElementById("form-doacao");
const corpo = document.getElementById("corpo-tabela");

function celula(texto) {
  const td = document.createElement("td");
  td.textContent = texto; // textContent evita XSS
  return td;
}

function linha(d) {
  const tr = document.createElement("tr");
  tr.append(
    celula(d.item), celula(NOMES[d.categoria]), celula(d.quantidade),
    celula(d.doador || "—"),
    celula([d.cidade, d.uf].filter(Boolean).join("/") || "—"),
    celula(formatarData(d.criado_em))
  );
  const acoes = document.createElement("td");
  const botao = document.createElement("button");
  botao.type = "button";
  botao.className = "perigo";
  botao.textContent = "Excluir";
  botao.setAttribute("aria-label", "Excluir doação: " + d.item);
  botao.addEventListener("click", () => excluir(d));
  acoes.append(botao);
  tr.append(acoes);
  return tr;
}

async function carregar() {
  const params = new URLSearchParams();
  const q = document.getElementById("filtro-q").value.trim();
  const cat = document.getElementById("filtro-cat").value;
  if (q) params.set("q", q);
  if (cat) params.set("categoria", cat);
  try {
    const dados = await api("/api/doacoes?" + params);
    corpo.replaceChildren(...dados.map(linha));
    if (!dados.length) {
      const tr = document.createElement("tr");
      const td = celula("Nenhuma doação encontrada.");
      td.colSpan = 7;
      tr.append(td);
      corpo.append(tr);
    }
  } catch (e) {
    avisar(e.message, "erro");
  }
}

async function excluir(d) {
  if (!window.confirm(`Excluir a doação "${d.item}"?`)) return;
  try {
    await api("/api/doacoes/" + d.id, { method: "DELETE" });
    avisar("Doação excluída.");
    carregar();
  } catch (e) {
    avisar(e.message, "erro");
  }
}

/* ---- Consulta de CEP ---------------------------------------------------------
 * A consulta roda assim que o CEP tem 8 dígitos (ao digitar ou colar), ao sair do
 * campo e, se ainda não tiver rodado, antes de registrar a doação. Assim, apertar
 * Enter logo depois de digitar o CEP também preenche cidade e UF.
 */
const campoCep = form.elements.cep;
const botaoRegistrar = form.querySelector('button[type="submit"]');
let cepPreenchido = "";   // CEP cuja consulta preencheu cidade/UF
let consultaAtual = null; // { cep, promessa } da consulta em andamento

function soDigitos(valor) {
  return valor.replace(/\D/g, "");
}

function erroCep(mensagem) {
  document.getElementById("erro-cep").textContent = mensagem;
  campoCep.setAttribute("aria-invalid", "true");
}

/** Consulta o CEP uma vez por valor. Resolve true quando cidade/UF foram preenchidas. */
function consultarCep() {
  const cep = soDigitos(campoCep.value);
  if (cep.length !== 8) return Promise.resolve(false);
  if (cep === cepPreenchido) return Promise.resolve(true);
  if (consultaAtual && consultaAtual.cep === cep) return consultaAtual.promessa;

  const promessa = (async () => {
    try {
      const dados = await api("/api/cep/" + cep);
      if (soDigitos(campoCep.value) !== cep) return false; // o CEP mudou durante a consulta
      form.elements.cidade.value = dados.cidade;
      form.elements.uf.value = dados.uf;
      cepPreenchido = cep;
      avisar(`CEP encontrado: ${dados.cidade}/${dados.uf}.`);
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
  const cep = soDigitos(campoCep.value);
  document.getElementById("erro-cep").textContent = "";
  campoCep.removeAttribute("aria-invalid");
  // CEP alterado: apaga a cidade/UF que vieram do CEP anterior
  if (cepPreenchido && cep !== cepPreenchido) {
    form.elements.cidade.value = "";
    form.elements.uf.value = "";
    cepPreenchido = "";
  }
  if (cep.length === 8) consultarCep();
});
campoCep.addEventListener("blur", consultarCep);

/* ---- Registro da doação ------------------------------------------------------ */
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
    if (cep.length === 8 && cep !== cepPreenchido) {
      const encontrado = await consultarCep();
      if (!encontrado && !form.elements.cidade.value.trim()) {
        // CEP não encontrado ou serviço fora do ar: não registra sem cidade.
        // O usuário corrige o CEP ou preenche cidade/UF manualmente e registra de novo.
        campoCep.focus();
        return;
      }
    }
    const dados = Object.fromEntries(new FormData(form));
    await api("/api/doacoes", { method: "POST", body: JSON.stringify(dados) });
    form.reset();
    cepPreenchido = "";
    avisar("Doação registrada com sucesso.");
    document.getElementById("item").focus();
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

carregar();
