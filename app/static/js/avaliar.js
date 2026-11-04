"use strict";
const formAv = document.getElementById("form-avaliacao");
formAv.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  limparErros(formAv);
  const dados = Object.fromEntries(new FormData(formAv));
  try {
    await api("/api/avaliacoes", { method: "POST", body: JSON.stringify(dados) });
    formAv.reset();
    avisar("Obrigado! Sua avaliação foi registrada.");
  } catch (e) {
    mostrarErros(formAv, e.detalhes || {});
    avisar(e.message, "erro");
  }
});
