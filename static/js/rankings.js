/* =============================================================================
   BRAWL HUB — Rankings (Fase 6)
   Paginação no cliente (10 por página) + clique nas linhas navega para o
   destino (perfil do jogador ou página do clube). Sem chamadas extra à API.
   ========================================================================== */
(function () {
  "use strict";

  var list = document.getElementById("rank-list");
  if (!list) return;

  var pager = document.getElementById("rank-pager");
  var status = document.getElementById("rank-status");
  var rows = Array.prototype.slice.call(list.querySelectorAll(".rank-row"));

  var PER_PAGE = 10;
  var page = 1;
  var total = rows.length;

  function buildPager(pages) {
    if (!pager) return;
    pager.innerHTML = "";
    if (pages <= 1) { pager.style.display = "none"; return; }
    pager.style.display = "";

    function mkBtn(label, target, opts) {
      opts = opts || {};
      var b = document.createElement("button");
      b.type = "button";
      b.className = "pager-btn" + (opts.active ? " pager-btn--active" : "");
      b.textContent = label;
      b.disabled = !!opts.disabled;
      b.addEventListener("click", function () {
        page = target;
        render();
        // Volta pro topo da lista ao trocar de página
        list.scrollIntoView({ behavior: "smooth", block: "start" });
      });
      pager.appendChild(b);
    }

    mkBtn("‹ Anterior", page - 1, { disabled: page <= 1 });

    // Janela de páginas ao redor da atual (evita 8 botões para 200 linhas)
    var start = Math.max(1, page - 2);
    var end = Math.min(pages, page + 2);
    if (start > 1) mkBtn("1", 1);
    if (start > 2) mkBtn("…", page, { disabled: true });
    for (var i = start; i <= end; i++) mkBtn(String(i), i, { active: i === page });
    if (end < pages - 1) mkBtn("…", page, { disabled: true });
    if (end < pages) mkBtn(String(pages), pages);

    mkBtn("Próxima ›", page + 1, { disabled: page >= pages });
  }

  function render() {
    var pages = Math.max(1, Math.ceil(total / PER_PAGE));
    if (page > pages) page = pages;
    if (page < 1) page = 1;

    var start = (page - 1) * PER_PAGE;
    var slice = rows.slice(start, start + PER_PAGE);

    rows.forEach(function (r) { r.style.display = "none"; });
    slice.forEach(function (r) { r.style.display = ""; });

    if (status) {
      status.textContent = total
        ? "Página " + page + " de " + pages + " · " + total + " posições"
        : "Sem dados";
    }
    buildPager(pages);
  }

  // Clique na linha navega para o destino definido no template (data-href)
  rows.forEach(function (row) {
    row.addEventListener("click", function () {
      var href = row.dataset.href;
      if (href) window.location.href = href;
    });
    // Teclado: a linha se comporta como link
    row.setAttribute("tabindex", "0");
    row.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        row.click();
      }
    });
  });

  render();
})();
