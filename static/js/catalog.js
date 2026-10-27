/* =============================================================================
   BRAWL HUB — Busca do catálogo de Brawlers (Fase 5)
   Filtra os cards já renderizados, sem nova consulta à API.
   ========================================================================== */
(function () {
  "use strict";

  var search = document.getElementById("cat-search");
  var grid = document.getElementById("catalog-grid");
  if (!search || !grid) return;

  var cards = Array.prototype.slice.call(grid.querySelectorAll(".brawler-card"));
  var count = document.getElementById("cat-count");
  var empty = document.getElementById("cat-empty");
  var total = cards.length;

  // Pré-carrega o nome para filtrar sem reler o DOM
  cards.forEach(function (c) { c._name = c.dataset.name || ""; });

  function apply() {
    var q = (search.value || "").trim().toLowerCase();
    var shown = 0;

    cards.forEach(function (c) {
      var ok = !q || c._name.indexOf(q) !== -1;
      c.style.display = ok ? "" : "none";
      if (ok) shown++;
    });

    if (count) {
      count.textContent = q
        ? "Mostrando " + shown + " de " + total + " Brawlers"
        : "Mostrando " + total + " de " + total + " Brawlers";
    }
    if (empty) empty.hidden = shown !== 0;
  }

  search.addEventListener("input", apply);
  apply();
})();
