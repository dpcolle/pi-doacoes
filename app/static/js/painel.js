"use strict";
const NOMES_TIPO = Object.fromEntries(JSON.parse(document.getElementById("tipos-json").textContent));
const NIVEIS = { 1: "Verde (baixo)", 2: "Amarelo (atenção)", 3: "Laranja (transmissão sustentada)", 4: "Vermelho (alta incidência)" };
const NS = "http://www.w3.org/2000/svg";
const num = (v) => (v === null || v === undefined ? "–" : String(v).replace(".", ","));

function el(nome, attrs = {}, texto) {
  const e = document.createElementNS(NS, nome);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (texto !== undefined) e.textContent = texto;
  return e;
}

/** Barras horizontais com rótulo de valor (a informação não depende só da cor). */
function barrasHorizontais(alvo, entradas, vazio) {
  if (!entradas.length) { alvo.textContent = vazio; return; }
  const max = Math.max(...entradas.map(([, v]) => v), 1);
  const altura = 36, largura = 640, margemEsq = 150;
  const svg = el("svg", { viewBox: `0 0 ${largura} ${entradas.length * altura + 10}`, role: "img",
    "aria-label": "Gráfico de barras: " + entradas.map(([n, v]) => `${n} ${v}`).join(", "),
    style: "width:100%;max-width:640px;height:auto" });
  entradas.forEach(([nome, valor], i) => {
    const y = i * altura + 5;
    const w = Math.max(2, ((largura - margemEsq - 60) * valor) / max);
    svg.append(
      el("text", { x: 0, y: y + 20, fill: "currentColor", "font-size": 15 }, nome),
      el("rect", { x: margemEsq, y, width: w, height: 26, fill: "var(--primaria)" }),
      el("text", { x: margemEsq + w + 6, y: y + 20, fill: "currentColor", "font-size": 15, "font-weight": 700 }, valor)
    );
  });
  alvo.replaceChildren(svg);
}

/** Colunas por semana epidemiológica com o número de casos acima de cada coluna. */
function colunasSemanas(alvo, semanas) {
  if (!semanas.length) { alvo.textContent = "Sem dados do InfoDengue para este município."; return; }
  const largura = 640, altura = 220, base = 190, topo = 24;
  const passo = largura / semanas.length;
  const max = Math.max(...semanas.map((s) => s.casos || 0), 1);
  const svg = el("svg", { viewBox: `0 0 ${largura} ${altura}`, role: "img",
    "aria-label": "Casos notificados por semana: " + semanas.map((s) => `semana ${s.semana}: ${s.casos ?? 0}`).join(", "),
    style: "width:100%;max-width:640px;height:auto" });
  svg.append(el("line", { x1: 0, x2: largura, y1: base, y2: base, stroke: "currentColor", "stroke-width": 1 }));
  semanas.forEach((s, i) => {
    const h = ((base - topo) * (s.casos || 0)) / max;
    const x = i * passo + passo * 0.15, w = passo * 0.7;
    svg.append(
      el("rect", { x, y: base - h, width: w, height: Math.max(h, 1), fill: "var(--primaria)" }),
      el("text", { x: x + w / 2, y: base - h - 6, "text-anchor": "middle", fill: "currentColor", "font-size": 13, "font-weight": 700 }, s.casos ?? 0),
      el("text", { x: x + w / 2, y: base + 18, "text-anchor": "middle", fill: "currentColor", "font-size": 12 }, "SE " + s.semana)
    );
  });
  alvo.replaceChildren(svg);
}

function linhaTabela(valores) {
  const tr = document.createElement("tr");
  for (const v of valores) { const td = document.createElement("td"); td.textContent = v; tr.append(td); }
  return tr;
}

/* ---- Situação do município (API do InfoDengue, consultada pelo servidor) ---- */
const seletor = document.getElementById("municipio");

async function carregarMunicipio() {
  const geocode = seletor.value;
  try { localStorage.setItem("pi-municipio", geocode); } catch (_) { /* modo privado */ }
  document.getElementById("grafico-casos").textContent = "Carregando dados do InfoDengue…";
  try {
    const d = await api("/api/dengue/" + geocode);
    const a = d.atual;
    document.getElementById("k-nivel").textContent = a ? NIVEIS[a.nivel] || "Sem dados" : "–";
    document.getElementById("k-casos").textContent = a ? num(a.casos) : "–";
    document.getElementById("k-inc").textContent = a ? num(a.incidencia_100mil) : "–";
    const t = d.tendencia;
    document.getElementById("tendencia").textContent = t
      ? `Últimas 4 semanas: ${t.ultimas} casos notificados, contra ${t.anteriores} nas 4 anteriores (${t.direcao}` +
        (t.variacao_pct === null ? ")." : `, ${t.variacao_pct > 0 ? "+" : ""}${num(t.variacao_pct)}%).`)
      : "";
    colunasSemanas(document.getElementById("grafico-casos"), d.semanas);
    document.getElementById("tab-casos").replaceChildren(...d.semanas.map((s) =>
      linhaTabela([`${s.semana}/${s.ano}`, num(s.casos), num(s.casos_estimados), NIVEIS[s.nivel] || "–"])));
  } catch (e) {
    document.getElementById("grafico-casos").textContent = e.message;
    avisar(e.message, "erro");
  }
}

async function iniciarMunicipios() {
  const lista = await api("/api/municipios");
  let salvo = null;
  try { salvo = localStorage.getItem("pi-municipio"); } catch (_) { /* modo privado */ }
  seletor.replaceChildren(...lista.map((m) => new Option(m.nome, m.geocode, false, m.geocode === salvo)));
  seletor.addEventListener("change", carregarMunicipio);
  if (lista.length) carregarMunicipio();
}

/* ---- Registros e avaliações (banco de dados do sistema) ---- */
async function carregarEstatisticas() {
  const { focos: f, avaliacoes: a } = await api("/api/estatisticas");
  document.getElementById("k-total").textContent = f.total;
  document.getElementById("k-abertos").textContent = f.abertos;
  document.getElementById("k-elim").textContent = f.eliminados_pct === null ? "–" : `${f.eliminados} (${num(f.eliminados_pct)}%)`;
  document.getElementById("k-dias").textContent = num(f.dias_ate_eliminar);
  const tipos = Object.entries(f.por_tipo).map(([t, n]) => [NOMES_TIPO[t] || t, n]);
  barrasHorizontais(document.getElementById("grafico-tipos"), tipos, "Ainda não há registros.");
  document.getElementById("tab-tipos").replaceChildren(...tipos.map(linhaTabela));
  const lista = document.getElementById("lista-bairros");
  lista.replaceChildren(...f.bairros_pendentes.map((b) => {
    const li = document.createElement("li");
    li.textContent = `${b.bairro}: ${b.focos} local(is)`;
    return li;
  }));
  if (!f.bairros_pendentes.length) lista.textContent = "Nenhum local pendente.";
  const versoes = Object.entries(a.media_por_versao).map(([v, m]) => `versão ${v}: ${num(m)}`).join("; ");
  document.getElementById("resumo-notas").textContent = a.total
    ? `${a.total} avaliação(ões); nota média ${num(a.nota_media)} de 5; ${num(a.satisfeitos_pct)}% deram nota 4 ou 5. Por versão: ${versoes}.`
    : "Ainda não há avaliações.";
}

iniciarMunicipios().catch((e) => avisar(e.message, "erro"));
carregarEstatisticas().catch((e) => avisar(e.message, "erro"));
