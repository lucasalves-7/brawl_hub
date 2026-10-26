/* =============================================================================
   BRAWL HUB — Interações da interface
   Menu mobile, validação da tag de jogador e avisos flutuantes.
   ========================================================================== */
(function () {
  "use strict";

  /* ------------------------------------------------------ Avisos (toast) -- */
  var toastEl = document.getElementById("toast");
  var toastText = document.getElementById("toast-text");
  var toastTimer = null;

  function showToast(message) {
    if (!toastEl || !toastText) return;
    toastText.textContent = message;
    toastEl.hidden = false;
    // Reinicia a animação de entrada
    toastEl.classList.remove("is-visible");
    // força reflow para o efeito disparar de novo
    void toastEl.offsetWidth;
    toastEl.classList.add("is-visible");

    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      toastEl.classList.remove("is-visible");
      setTimeout(function () { toastEl.hidden = true; }, 250);
    }, 2800);
  }

  /* --------------------------------------- Links de seções ainda não prontas */
  document.addEventListener("click", function (e) {
    var link = e.target.closest("[data-soon]");
    if (!link) return;
    e.preventDefault();
    showToast("A seção “" + link.getAttribute("data-soon") + "” chega em uma próxima fase.");
  });

  /* ------------------------------------------------------- Menu mobile ---- */
  var toggle = document.getElementById("menu-toggle");
  var nav = document.getElementById("nav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("nav--open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");
    });

    // Fecha o menu ao clicar em um link ou fora dele
    document.addEventListener("click", function (e) {
      if (!nav.classList.contains("nav--open")) return;
      if (nav.contains(e.target) || toggle.contains(e.target)) return;
      nav.classList.remove("nav--open");
      toggle.setAttribute("aria-expanded", "false");
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("nav--open")) {
        nav.classList.remove("nav--open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  /* ------------------------------------------- Validação da tag do jogador */
  // Conjunto de caracteres aceito pela tag de Brawl Stars.
  var TAG_CHARS = "0289PYLQGRJCUV";

  function normalizeTag(raw) {
    var t = String(raw || "").trim().toUpperCase();
    if (t.charAt(0) !== "#") t = "#" + t;
    return t;
  }

  function isValidTag(tag) {
    var body = tag.slice(1); // remove o "#"
    if (body.length < 3 || body.length > 14) return false;
    for (var i = 0; i < body.length; i++) {
      if (TAG_CHARS.indexOf(body.charAt(i)) === -1) return false;
    }
    return true;
  }

  var form = document.getElementById("busca");
  var input = document.getElementById("tag-input");
  var hint = document.getElementById("search-hint");

  function setHint(state, html) {
    if (!hint) return;
    hint.setAttribute("data-state", state);
    var span = hint.querySelector("span");
    if (span) span.innerHTML = html;
  }

  var HINT_DEFAULT =
    'A tag começa com <strong>#</strong> e aparece no seu perfil do jogo.';

  if (form && input) {
    input.addEventListener("input", function () {
      // Limpa o erro assim que o usuário começa a corrigir
      if (hint && hint.getAttribute("data-state") === "error") {
        setHint("idle", HINT_DEFAULT);
      }
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var tag = normalizeTag(input.value);

      if (!isValidTag(tag)) {
        setHint(
          "error",
          "Tag inválida. Use apenas <strong>0–9</strong>, <strong>P Y L Q G R J C U V</strong> — de <strong>3</strong> a <strong>14</strong> caracteres."
        );
        input.focus();
        return;
      }

      setHint("ok", "Tag reconhecida! Abrindo o painel de <strong>" + tag + "</strong>…");
      // A navegação real será feita pelo backend; aqui garantimos o fluxo.
      window.location.href = "/perfil/" + encodeURIComponent(tag.slice(1)) + "/";
    });
  }

  /* ------------------------------------------------ Preencher tag-exemplo -- */
  var fillBtn = document.getElementById("fill-example");
  if (fillBtn) {
    fillBtn.addEventListener("click", function () {
      // O backend escolhe um jogador real (líder global) para o exemplo.
      window.location.href = "/exemplo/";
    });
  }
})();
