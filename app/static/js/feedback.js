"use strict";
const formFb = document.getElementById("form-feedback");
formFb.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  limparErros(formFb);
  const dados = Object.fromEntries(new FormData(formFb));
  try {
    await api("/api/feedbacks", { method: "POST", body: JSON.stringify(dados) });
    formFb.reset();
    avisar("Obrigado! Sua avaliação foi registrada.");
  } catch (e) {
    mostrarErros(formFb, e.detalhes || {});
    avisar(e.message, "erro");
  }
});
