/* Brawl Hub — expansão compacta dos equipamentos da ficha */
(function () {
  "use strict";

  var wrap = document.getElementById("gears-list-wrap");
  var list = document.getElementById("gears-list");
  var toggle = document.getElementById("gears-toggle");
  if (!wrap || !list || !toggle || list.children.length <= 2) return;

  function compactHeight() {
    var second = list.children[1];
    return second.offsetTop + second.offsetHeight;
  }

  function setHeight() {
    wrap.style.maxHeight = wrap.classList.contains("is-collapsed")
      ? compactHeight() + "px"
      : list.scrollHeight + "px";
  }

  function update(expanded) {
    wrap.classList.toggle("is-collapsed", !expanded);
    wrap.classList.toggle("is-expanded", expanded);
    toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
    toggle.querySelector("span").textContent = expanded
      ? "Mostrar menos"
      : "Ver todos os equipamentos";
    setHeight();
  }

  update(false);
  toggle.addEventListener("click", function () {
    update(!wrap.classList.contains("is-expanded"));
  });

  window.addEventListener("resize", function () {
    if (!wrap.classList.contains("is-expanded")) setHeight();
  });
})();
