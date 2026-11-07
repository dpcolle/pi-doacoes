"use strict";
/* v2: divulgar o site nas redes sociais (sugestão da avaliação dos moradores). */
(function () {
  const url = window.location.origin + "/";
  const texto = "Viu água parada? Registre o local e ajude a combater a dengue no nosso bairro:";
  document.getElementById("share-whatsapp").href = "https://wa.me/?text=" + encodeURIComponent(texto + " " + url);
  document.getElementById("share-facebook").href =
    "https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(url);

  // Celular: abre o menu de compartilhamento do próprio aparelho (Instagram, Telegram etc.)
  const botao = document.getElementById("compartilhar");
  if (navigator.share) {
    botao.hidden = false;
    botao.addEventListener("click", () => {
      navigator.share({ title: "Alerta Dengue Comunitário", text: texto, url }).catch(() => { /* cancelado */ });
    });
  }

  document.getElementById("copiar-link").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(url);
      avisar("Link copiado: " + url);
    } catch (_) {
      avisar("Não foi possível copiar. O endereço é " + url, "erro");
    }
  });
})();
