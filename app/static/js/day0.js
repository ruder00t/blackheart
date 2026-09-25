/* Day0: per-OS setup notes/commands. Add entries under the active OS tab,
   live-substitute shared vars, copy button per entry, persist to data/day0.json. */
(function () {
  "use strict";
  var TN = window.TN;
  var state = window.DAY0 || {};
  var OSES = window.DAY0_OSES || [];
  var VARKEYS = window.VARKEYS || [];
  var panels = document.getElementById("d0Panels");
  var tabs = document.getElementById("d0Tabs");
  if (!panels || !tabs) return;

  var current = (OSES[0] && OSES[0][0]) || "parrot";
  OSES.forEach(function (o) { if (!Array.isArray(state[o[0]])) state[o[0]] = []; });

  function save() {
    fetch("/api/day0", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state),
    })
      .then(function (r) { return r.json(); })
      .then(function () { TN.toast("Saved"); })
      .catch(function () { TN.toast("Save failed"); });
  }

  function insertToken(input, tok) {
    var s = input.selectionStart, e = input.selectionEnd;
    if (s == null) { s = e = input.value.length; }
    input.value = input.value.slice(0, s) + tok + input.value.slice(e);
    input.focus();
    var pos = s + tok.length;
    input.setSelectionRange(pos, pos);
  }

  function tokrow(input) {
    var d = document.createElement("div");
    d.className = "tokrow";
    VARKEYS.forEach(function (k) {
      var b = document.createElement("button");
      b.className = "tok"; b.type = "button"; b.textContent = "$" + k;
      b.addEventListener("click", function () { insertToken(input, "$" + k); });
      d.appendChild(b);
    });
    return d;
  }

  function render() {
    panels.innerHTML = "";
    var items = state[current] || [];
    var card = document.createElement("div");
    card.className = "card";

    var h = document.createElement("h3");
    var label = current;
    OSES.forEach(function (o) { if (o[0] === current) label = o[1]; });
    h.textContent = label + " — setup";
    card.appendChild(h);

    if (!items.length) {
      var e = document.createElement("p");
      e.className = "empty";
      e.textContent = "No entries yet. Paste a command or note below.";
      card.appendChild(e);
    }

    items.forEach(function (txt, i) {
      var el = document.createElement("div");
      el.className = "cmd";
      el.innerHTML = TN.fillHtml(txt);
      var del = document.createElement("button");
      del.className = "del"; del.textContent = "del";
      del.addEventListener("click", function () { items.splice(i, 1); save(); render(); });
      el.appendChild(del);
      TN.attachCopy(el, TN.fillRaw(txt));
      card.appendChild(el);
    });

    var inp = document.createElement("input");
    inp.type = "text";
    inp.placeholder = "command or note — use the buttons for placeholders";
    card.appendChild(tokrow(inp));

    var wrap = document.createElement("div");
    wrap.className = "cmdinput";
    var prompt = document.createElement("span");
    prompt.className = "prompt"; prompt.textContent = ">";
    var add = document.createElement("button");
    add.className = "btn"; add.textContent = "Add";
    add.addEventListener("click", function () {
      var v = inp.value.trim();
      if (!v) return;
      items.push(v);
      save(); render();
    });
    inp.addEventListener("keydown", function (ev) { if (ev.key === "Enter") add.click(); });
    wrap.appendChild(prompt); wrap.appendChild(inp); wrap.appendChild(add);
    card.appendChild(wrap);

    panels.appendChild(card);
  }

  tabs.querySelectorAll("button[data-os]").forEach(function (b) {
    b.addEventListener("click", function () {
      tabs.querySelectorAll("button").forEach(function (x) { x.classList.remove("on"); });
      b.classList.add("on");
      current = b.dataset.os;
      render();
    });
  });

  document.addEventListener("tn:vars", render);
  render();
})();
