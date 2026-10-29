/* =============================================================================
   BRAWL HUB — Interações da interface
   Menu mobile, validação da tag de jogador e avisos flutuantes.
   Histórico local das pesquisas recentes.
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

  /* ----------------------------------------- Histórico de pesquisas ------- */
  var HISTORY_KEY = "brawlhub.searchHistory";
  var HISTORY_LIMIT = 5;

  function readHistory() {
    try {
      var value = JSON.parse(window.localStorage.getItem(HISTORY_KEY) || "[]");
      return Array.isArray(value) ? value.filter(function (item) {
        return item && typeof item.tag === "string";
      }).slice(0, HISTORY_LIMIT) : [];
    } catch (e) {
      return [];
    }
  }

  function writeHistory(items) {
    try {
      window.localStorage.setItem(HISTORY_KEY, JSON.stringify(items.slice(0, HISTORY_LIMIT)));
    } catch (e) { /* armazenamento pode estar bloqueado pelo navegador */ }
  }

  function saveHistoryTag(tag, name) {
    var items = readHistory().filter(function (item) { return item.tag !== tag; });
    items.unshift({ tag: tag, name: name || null });
    writeHistory(items);
  }

  function syncProfileHistory() {
    var profile = document.querySelector("[data-player-tag]");
    if (!profile) return;
    var tag = normalizeTag(profile.getAttribute("data-player-tag"));
    var name = profile.getAttribute("data-player-name") || "";
    if (!isValidTag(tag) || !name) return;
    var items = readHistory();
    var found = false;
    items = items.map(function (item) {
      if (item.tag !== tag) return item;
      found = true;
      return { tag: item.tag, name: name };
    });
    if (found) writeHistory(items);
  }

  syncProfileHistory();

  var form = document.getElementById("busca");
  var input = document.getElementById("tag-input");
  var hint = document.getElementById("search-hint");
  var historyBox = document.getElementById("search-history");

  function closeHistory() {
    if (!historyBox || !input) return;
    historyBox.hidden = true;
    historyBox.classList.remove("is-open");
    input.setAttribute("aria-expanded", "false");
  }

  function openHistory() {
    if (!historyBox || !input) return;
    var items = readHistory();
    historyBox.innerHTML = "";
    if (!items.length) { closeHistory(); return; }

    items.forEach(function (item, index) {
      var row = document.createElement("div");
      row.className = "search-history__item";
      row.setAttribute("role", "option");

      var choose = document.createElement("button");
      choose.type = "button";
      choose.className = "search-history__choose";
      choose.innerHTML = "<strong></strong><span></span>";
      choose.querySelector("strong").textContent = item.name || "Jogador pesquisado";
      choose.querySelector("span").textContent = item.tag;
      choose.addEventListener("click", function () {
        input.value = item.tag;
        closeHistory();
        input.focus();
      });

      var remove = document.createElement("button");
      remove.type = "button";
      remove.className = "search-history__remove";
      remove.setAttribute("aria-label", "Remover " + item.tag + " do histórico");
      remove.textContent = "×";
      remove.addEventListener("click", function () {
        var current = readHistory();
        current.splice(index, 1);
        writeHistory(current);
        openHistory();
      });

      row.appendChild(choose);
      row.appendChild(remove);
      historyBox.appendChild(row);
    });
    historyBox.hidden = false;
    historyBox.classList.remove("is-open");
    void historyBox.offsetWidth;
    historyBox.classList.add("is-open");
    input.setAttribute("aria-expanded", "true");
  }

  if (input && historyBox) {
    input.addEventListener("focus", openHistory);
    input.addEventListener("click", openHistory);
    document.addEventListener("click", function (e) {
      if (!historyBox.contains(e.target) && e.target !== input) closeHistory();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeHistory();
    });
  }

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

      saveHistoryTag(tag, null);
      setHint("ok", "Tag reconhecida! Abrindo o painel de <strong>" + tag + "</strong>…");
      // A navegação real será feita pelo backend; aqui garantimos o fluxo.
      window.location.href = "/perfil/" + encodeURIComponent(tag.slice(1)) + "/";
    });
  }

})();
