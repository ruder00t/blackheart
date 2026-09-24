/* Tool library: name + link pairs, copyable link, persisted. No variables. */
(function () {
  "use strict";
  var TN = window.TN;
  var state = window.TOOLS || { tools: [] };
  var list = document.getElementById("tlList");
  if (!list) return;
  function esc(s) { return String(s).replace(/[&<>]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]; }); }

  function save() {
    fetch("/api/tool-library", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state),
    }).then(function (r) { return r.json(); })
      .then(function () { TN.toast("Saved"); })
      .catch(function () { TN.toast("Save failed"); });
  }

  function render() {
    list.innerHTML = "";
    var card = document.createElement("div");
    card.className = "card";
    var h = document.createElement("h3"); h.textContent = "Tools"; card.appendChild(h);
    if (!state.tools.length) {
      var e = document.createElement("p"); e.className = "empty";
      e.textContent = "No tools yet. Add one above."; card.appendChild(e);
    }
    state.tools.forEach(function (t, i) {
      var el = document.createElement("div");
      el.className = "cmd";
      el.innerHTML = '<span class="lbl">' + esc(t.name) + '</span>' + esc(t.path);
      var del = document.createElement("button");
      del.className = "del"; del.textContent = "del";
      del.addEventListener("click", function () { state.tools.splice(i, 1); save(); render(); });
      el.appendChild(del);
      TN.attachCopy(el, t.path);
      card.appendChild(el);
    });
    list.appendChild(card);
  }

  document.getElementById("tlAdd").addEventListener("click", function () {
    var n = document.getElementById("tlName"), p = document.getElementById("tlPath");
    var nn = n.value.trim(), pp = p.value.trim();
    if (!nn || !pp) return;
    state.tools.push({ name: nn, path: pp });
    n.value = ""; p.value = "";
    save(); render();
  });
  document.getElementById("tlPath").addEventListener("keydown", function (ev) {
    if (ev.key === "Enter") document.getElementById("tlAdd").click();
  });
  render();
})();
