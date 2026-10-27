/* =============================================================================
   BRAWL HUB — Dashboard do jogador
   Gráfico de distribuição, filtros de Brawlers e filtros do histórico.
   Todos os filtros operam sobre dados já carregados (sem nova consulta à API).
   ========================================================================== */
(function () {
  "use strict";

  var fmt = function (n) { return Number(n).toLocaleString("pt-BR"); };

  /* ------------------------------------------------ Gráfico (Chart.js) --- */
  function renderChart() {
    var canvas = document.getElementById("dist-chart");
    var dataEl = document.getElementById("dist-data");
    if (!canvas || !dataEl || typeof Chart === "undefined") return;

    var rows;
    try { rows = JSON.parse(dataEl.textContent); } catch (e) { return; }
    if (!Array.isArray(rows) || !rows.length) return;

    var labels = rows.map(function (r) { return r.name; });
    var values = rows.map(function (r) { return r.trophies; });

    new Chart(canvas, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "Troféus",
          data: values,
          backgroundColor: "rgba(255, 206, 40, 0.85)",
          hoverBackgroundColor: "#ffe36b",
          borderColor: "#b07d00",
          borderWidth: 2,
          borderRadius: 8,
          borderSkipped: false
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function (ctx) { return " " + fmt(ctx.parsed.x) + " troféus"; }
            }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: {
              color: "#93a4d4",
              callback: function (v) { return fmt(v); }
            },
            grid: { color: "rgba(255,255,255,0.06)" }
          },
          y: {
            ticks: { color: "#d5deff", font: { weight: "700" } },
            grid: { display: false }
          }
        }
      }
    });
  }

  /* ------------------------------------------------- Filtros Brawlers --- */
  function brawlerFilters() {
    var grid = document.getElementById("brawler-grid");
    if (!grid) return;

    var search = document.getElementById("bf-name");
    var power = document.getElementById("bf-power");
    var sort = document.getElementById("bf-sort");
    var count = document.getElementById("bf-count");
    var more = document.getElementById("bf-more");
    var cards = Array.prototype.slice.call(grid.querySelectorAll(".brawler-card"));
    if (!cards.length) return;

    var total = cards.length;
    var PAGE = 12;      // quantos cards mostrar por vez
    var limit = PAGE;   // limite atual (ampliado pelo "Ver mais")

    // Pré-carrega os valores para ordenar sem reler o DOM toda vez
    cards.forEach(function (c) {
      c._d = {
        name: c.dataset.name || "",
        trophies: +c.dataset.trophies || 0,
        highest: +c.dataset.highest || 0,
        power: +c.dataset.power || 0,
        rank: +c.dataset.rank || 0
      };
    });

    function apply() {
      var q = (search.value || "").trim().toLowerCase();
      var lv = power.value;
      var sortBy = sort.value;

      function passes(c) {
        var okQ = !q || c._d.name.indexOf(q) !== -1;
        var okP = !lv || c._d.power === +lv;
        return okQ && okP;
      }

      // Ordenação (define a ordem visual)
      var sorted = cards.slice().sort(function (a, b) {
        switch (sortBy) {
          case "name": return a._d.name.localeCompare(b._d.name);
          case "highest": return b._d.highest - a._d.highest;
          case "power": return b._d.power - a._d.power;
          case "rank": return b._d.rank - a._d.rank;
          default: return b._d.trophies - a._d.trophies;
        }
      });
      sorted.forEach(function (c) { grid.appendChild(c); });

      // Filtragem + limite progressivo (mostra os primeiros `limit` que passam)
      var matchSeen = 0;
      sorted.forEach(function (c) {
        var ok = passes(c);
        var within = ok && matchSeen < limit;
        if (ok) matchSeen++;
        c.style.display = within ? "" : "none";
      });

      var totalMatched = matchSeen;
      var currentlyShown = Math.min(limit, totalMatched);

      if (count) {
        var txt = "Mostrando " + currentlyShown + " de " + totalMatched + " Brawlers";
        if (totalMatched !== total) txt += " (" + total + " no total)";
        count.textContent = txt;
      }

      // Botão "Ver mais"
      if (more && more.parentElement) {
        var remaining = totalMatched - currentlyShown;
        more.parentElement.style.display = remaining > 0 ? "" : "none";
        more.textContent = "Ver mais (" + remaining + ")";
        more.disabled = remaining <= 0;
      }

      // Estado vazio
      var empty = grid.querySelector(".empty-filter");
      if (totalMatched === 0) {
        if (!empty) {
          empty = document.createElement("p");
          empty.className = "empty-filter";
          empty.textContent = "Nenhum Brawler corresponde aos filtros.";
          grid.appendChild(empty);
        }
        empty.style.display = "";
      } else if (empty) {
        empty.style.display = "none";
      }
    }

    // Mudar filtro/ordenação volta ao primeiro bloco
    function resetAndApply() { limit = PAGE; apply(); }

    [search, power, sort].forEach(function (el) {
      if (!el) return;
      el.addEventListener("input", resetAndApply);
      el.addEventListener("change", resetAndApply);
    });

    // "Ver mais" apenas amplia o limite, mantendo filtros e ordem atuais
    if (more) {
      more.addEventListener("click", function () {
        limit += PAGE;
        apply();
      });
    }

    apply();
  }

  /* ------------------------------------- Filtros + paginação do histórico - */
  function battleFilters() {
    var list = document.getElementById("battle-list");
    if (!list) return;

    var mode = document.getElementById("mf-mode");
    var result = document.getElementById("mf-result");
    var pager = document.getElementById("battle-pager");
    var status = document.getElementById("battle-status");
    var rows = Array.prototype.slice.call(list.querySelectorAll(".battle-row"));

    var PER_PAGE = 5; // partidas por página
    var page = 1;

    function matchedRows() {
      var m = mode.value, r = result.value;
      return rows.filter(function (row) {
        var okM = !m || row.dataset.mode === m;
        var okR = !r || row.dataset.result === r;
        return okM && okR;
      });
    }

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
        });
        pager.appendChild(b);
      }

      mkBtn("‹ Anterior", page - 1, { disabled: page <= 1 });
      for (var i = 1; i <= pages; i++) {
        mkBtn(String(i), i, { active: i === page });
      }
      mkBtn("Próxima ›", page + 1, { disabled: page >= pages });
    }

    function render() {
      var matched = matchedRows();
      var pages = Math.max(1, Math.ceil(matched.length / PER_PAGE));
      if (page > pages) page = pages;
      if (page < 1) page = 1;

      var start = (page - 1) * PER_PAGE;
      var slice = matched.slice(start, start + PER_PAGE);

      // Esconde tudo e mostra apenas a fatia da página atual
      rows.forEach(function (row) { row.style.display = "none"; });
      slice.forEach(function (row) { row.style.display = ""; });

      // Estado vazio
      var empty = list.querySelector(".empty-filter");
      if (matched.length === 0) {
        if (!empty) {
          empty = document.createElement("p");
          empty.className = "empty-filter";
          empty.textContent = "Nenhuma partida com esses filtros.";
          list.appendChild(empty);
        }
        empty.style.display = "";
      } else if (empty) {
        empty.style.display = "none";
      }

      // Texto de status
      if (status) {
        status.textContent = matched.length
          ? "Página " + page + " de " + pages + " · " + matched.length + " partidas"
          : "0 partidas";
      }

      buildPager(pages);
    }

    // Mudar filtro volta para a primeira página
    [mode, result].forEach(function (el) {
      if (!el) return;
      el.addEventListener("change", function () { page = 1; render(); });
    });

    render();
  }

  /* -------------------------------------------------- Formatar datas ----- */
  function formatTimes() {
    var nodes = document.querySelectorAll("[data-btime]");
    Array.prototype.forEach.call(nodes, function (n) {
      var raw = n.getAttribute("data-btime");
      if (!raw) return;
      // "20261026T213039.000Z" -> ISO parseável
      var iso = raw.replace(/^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})/,
        "$1-$2-$3T$4:$5:$6");
      var d = new Date(iso);
      if (isNaN(d)) { n.textContent = raw; return; }
      var pad = function (x) { return String(x).padStart(2, "0"); };
      n.textContent = pad(d.getDate()) + "/" + pad(d.getMonth() + 1) +
        " " + pad(d.getHours()) + ":" + pad(d.getMinutes());
    });
  }

  /* ---------------------------------------------------------- Init ------- */
  function init() {
    renderChart();
    brawlerFilters();
    battleFilters();
    formatTimes();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
