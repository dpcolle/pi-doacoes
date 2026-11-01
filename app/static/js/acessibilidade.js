"use strict";
/* Ferramentas de acessibilidade: tamanho do texto e alto contraste (preferência lembrada). */
(function () {
  const raiz = document.documentElement;
  const botaoContraste = document.getElementById("aa-contraste");
  let tamanho = 100;

  function ler(chave) { try { return localStorage.getItem(chave); } catch (_) { return null; } }
  function gravar(chave, valor) { try { localStorage.setItem(chave, valor); } catch (_) { /* modo privado */ } }

  function aplicarTamanho() { raiz.style.setProperty("--tamanho", tamanho + "%"); gravar("pi-tamanho", tamanho); }
  function aplicarContraste(ativo) {
    document.body.classList.toggle("alto-contraste", ativo);
    botaoContraste.setAttribute("aria-pressed", String(ativo));
    gravar("pi-contraste", ativo ? "1" : "0");
  }

  tamanho = Math.min(150, Math.max(80, parseInt(ler("pi-tamanho"), 10) || 100));
  aplicarTamanho();
  aplicarContraste(ler("pi-contraste") === "1");

  document.getElementById("aa-mais").addEventListener("click", () => { tamanho = Math.min(150, tamanho + 10); aplicarTamanho(); });
  document.getElementById("aa-menos").addEventListener("click", () => { tamanho = Math.max(80, tamanho - 10); aplicarTamanho(); });
  botaoContraste.addEventListener("click", () => aplicarContraste(botaoContraste.getAttribute("aria-pressed") !== "true"));
})();
