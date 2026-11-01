"use strict";
const NOMES_CAT = { alimento: "Alimento", higiene: "Higiene", vestuario: "Vestuário", outros: "Outros" };
const NS = "http://www.w3.org/2000/svg";

function el(nome, attrs = {}, texto) {
  const e = document.createElementNS(NS, nome);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (texto !== undefined) e.textContent = texto;
  return e;
}

/** Gráfico de barras horizontal em SVG puro, com rótulos de valor (não depende só de cor). */
function desenharGrafico(dados) {
  const alvo = document.getElementById("grafico");
  const entradas = Object.entries(dados);
  if (!entradas.length) { alvo.textContent = "Ainda não há doações para exibir."; return; }
  const max = Math.max(...entradas.map(([, v]) => v));
  const altura = 36, largura = 640, margemEsq = 110;
  const svg = el("svg", { viewBox: `0 0 ${largura} ${entradas.length * altura + 10}`, role: "img",
    "aria-label": "Gráfico de barras: " + entradas.map(([c, v]) => `${NOMES_CAT[c]} ${v}`).join(", "),
    style: "width:100%;max-width:640px;height:auto" });
  entradas.forEach(([cat, valor], i) => {
    const y = i * altura + 5;
    const w = Math.max(2, ((largura - margemEsq - 60) * valor) / max);
    svg.append(
      el("text", { x: 0, y: y + 20, fill: "currentColor", "font-size": 15 }, NOMES_CAT[cat]),
      el("rect", { x: margemEsq, y, width: w, height: 26, fill: "var(--primaria)" }),
      el("text", { x: margemEsq + w + 6, y: y + 20, fill: "currentColor", "font-size": 15, "font-weight": 700 }, valor)
    );
  });
  alvo.replaceChildren(svg);
}

function preencherTabela(dados) {
  const corpo = document.getElementById("tab-categorias");
  corpo.replaceChildren(...Object.entries(dados).map(([c, v]) => {
    const tr = document.createElement("tr");
    for (const t of [NOMES_CAT[c], v]) { const td = document.createElement("td"); td.textContent = t; tr.append(td); }
    return tr;
  }));
}

async function iniciar() {
  try {
    const { doacoes: d, feedbacks: f } = await api("/api/estatisticas");
    document.getElementById("k-registros").textContent = d.total_registros;
    document.getElementById("k-itens").textContent = d.total_itens;
    document.getElementById("k-media").textContent = String(d.media_quantidade).replace(".", ",");
    document.getElementById("k-satisf").textContent = f.satisfeitos_pct === null ? "–" : f.satisfeitos_pct + "%";
    desenharGrafico(d.por_categoria);
    preencherTabela(d.por_categoria);
    const lista = document.getElementById("lista-cidades");
    lista.replaceChildren(...d.top_cidades.map((c) => {
      const li = document.createElement("li");
      li.textContent = `${c.cidade}: ${c.doacoes} doação(ões)`;
      return li;
    }));
    if (!d.top_cidades.length) lista.textContent = "Informe o CEP nas doações para ver as cidades.";
    document.getElementById("resumo-notas").textContent = f.total
      ? `${f.total} avaliação(ões); nota média ${String(f.nota_media).replace(".", ",")} de 5.`
      : "Ainda não há avaliações.";
  } catch (e) {
    avisar(e.message, "erro");
  }
}
iniciar();
