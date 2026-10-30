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
  var rarityButtons = Array.prototype.slice.call(document.querySelectorAll(".rarity-filter"));
  var selectedRarity = "Todos";
  var total = cards.length;

  // Pré-carrega o nome para filtrar sem reler o DOM
  cards.forEach(function (c) { c._name = c.dataset.name || ""; });

  function apply() {
    var q = (search.value || "").trim().toLowerCase();
    var shown = 0;

    cards.forEach(function (c) {
      var okName = !q || c._name.indexOf(q) !== -1;
      var okRarity = selectedRarity === "Todos" || c.dataset.rarity === selectedRarity;
      var ok = okName && okRarity;
      c.style.display = ok ? "" : "none";
      if (ok) shown++;
    });

    if (count) {
      count.textContent = "Mostrando " + shown + " de " + total + " Brawlers";
    }
    if (empty) empty.hidden = shown !== 0;
  }

  search.addEventListener("input", apply);
  rarityButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      selectedRarity = button.dataset.rarity || "Todos";
      rarityButtons.forEach(function (item) {
        item.classList.toggle("is-active", item === button);
      });
      apply();
    });
  });
  apply();
})();
