/* Additions manager: append entries to any tab's overlay, choose top/bottom,
   live var substitution + copy, persist to data/additions.json, import/export. */
(function () {
  "use strict";
  var TN = window.TN;
  var state = window.ADD_STATE || {};
  var TARGETS = window.ADD_TARGETS || [];
  var VARKEYS = window.VARKEYS || [];

  var list = document.getElementById("addList");
  var sel = document.getElementById("addTarget");
  var text = document.getElementById("addText");
  var toks = document.getElementById("addToks");
  var posSeg = document.getElementById("addPos");
  if (!list) return;

  var pos = "bottom";
  var labelById = {};
  TARGETS.forEach(function (t) { labelById[t.id] = t.label; });

  function save() {
    return fetch("/api/additions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state),
    })
      .then(function (r) { return r.json(); })
      .then(function (d) { if (d && d.additions) state = d.additions; TN.toast("Saved"); })
      .catch(function () { TN.toast("Save failed"); });
  }

  function insertToken(input, tok) {
    var s = input.selectionStart, e = input.selectionEnd;
    if (s == null) { s = e = input.value.length; }
    input.value = input.value.slice(0, s) + tok + input.value.slice(e);
    input.focus();
    var p = s + tok.length;
    input.setSelectionRange(p, p);
  }

  VARKEYS.forEach(function (k) {
    var b = document.createElement("button");
    b.className = "tok"; b.type = "button"; b.textContent = "$" + k;
    b.addEventListener("click", function () { insertToken(text, "$" + k); });
    toks.appendChild(b);
  });

  posSeg.querySelectorAll("button[data-pos]").forEach(function (b) {
    b.addEventListener("click", function () {
      posSeg.querySelectorAll("button").forEach(function (x) { x.classList.remove("on"); });
      b.classList.add("on");
      pos = b.dataset.pos;
    });
  });

  function uid() { return "a" + Date.now().toString(36) + Math.random().toString(36).slice(2, 6); }

  function render() {
    list.innerHTML = "";
    var ids = Object.keys(state);
    if (!ids.length) {
      var e = document.createElement("div");
      e.className = "card";
      e.innerHTML = '<p class="empty">No additions yet. Add one above; it will appear on its target tab.</p>';
      list.appendChild(e);
      return;
    }
    ids.forEach(function (mid) {
      var items = state[mid] || [];
      if (!items.length) return;
      var card = document.createElement("div");
      card.className = "card prog";
      var head = document.createElement("div");
      head.className = "proghead";
      var h = document.createElement("h3");
      h.textContent = labelById[mid] || mid;
      head.appendChild(h);
      card.appendChild(head);

      items.forEach(function (it, i) {
        var el = document.createElement("div");
        el.className = "cmd";
        el.innerHTML = TN.fillHtml(it.text);
        var badge = document.createElement("span");
        badge.className = "poslbl";
        badge.textContent = it.pos === "top" ? "top" : "bottom";
        el.appendChild(badge);
        var del = document.createElement("button");
        del.className = "del"; del.textContent = "del";
        del.addEventListener("click", function () {
          items.splice(i, 1);
          if (!items.length) delete state[mid];
          save(); render();
        });
        el.appendChild(del);
        TN.attachCopy(el, TN.fillRaw(it.text));
        card.appendChild(el);
      });
      list.appendChild(card);
    });
  }

  document.getElementById("addBtn").addEventListener("click", function () {
    var mid = sel.value;
    var v = text.value.trim();
    if (!mid || !v) return;
    if (!Array.isArray(state[mid])) state[mid] = [];
    var entry = { id: uid(), text: v, pos: pos };
    if (pos === "top") state[mid].unshift(entry);
    else state[mid].push(entry);
    text.value = "";
    save(); render();
  });
  text.addEventListener("keydown", function (ev) {
    if (ev.key === "Enter") document.getElementById("addBtn").click();
  });

  // import / export
  document.getElementById("addImportBtn").addEventListener("click", function () {
    document.getElementById("addImport").click();
  });
  document.getElementById("addImport").addEventListener("change", function (ev) {
    var f = ev.target.files && ev.target.files[0];
    if (!f) return;
    var r = new FileReader();
    r.onload = function () {
      var data;
      try { data = JSON.parse(r.result); }
      catch (e) { TN.toast("Invalid JSON"); return; }
      if (!data || typeof data !== "object") { TN.toast("Invalid file"); return; }
      if (!confirm("Replace all current additions with the imported file?")) return;
      state = data;
      save().then(render);
    };
    r.readAsText(f);
    ev.target.value = "";
  });

  document.addEventListener("tn:vars", render);
  render();
})();
