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

form.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  limparErros(form);
  const dados = Object.fromEntries(new FormData(form));
  try {
    await api("/api/doacoes", { method: "POST", body: JSON.stringify(dados) });
    form.reset();
    avisar("Doação registrada com sucesso.");
    document.getElementById("item").focus();
    carregar();
  } catch (e) {
    mostrarErros(form, e.detalhes || {});
    avisar(e.message, "erro");
  }
});

document.getElementById("form-filtro").addEventListener("submit", (ev) => {
  ev.preventDefault();
  carregar();
});

document.getElementById("cep").addEventListener("blur", async (ev) => {
  const cep = ev.target.value.replace(/\D/g, "");
  if (cep.length !== 8) return;
  try {
    const dados = await api("/api/cep/" + cep);
    form.elements.cidade.value = dados.cidade;
    form.elements.uf.value = dados.uf;
    avisar(`CEP encontrado: ${dados.cidade}/${dados.uf}.`);
  } catch (e) {
    avisar(e.message, "erro");
  }
});

carregar();
