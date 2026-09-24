/* Script library: named multi-line bodies, live var substitution, copy whole. */
(function () {
  "use strict";
  var TN = window.TN;
  var state = window.SCRIPTS || { scripts: [] };
  var VARKEYS = window.VARKEYS || [];
  var list = document.getElementById("slList");
  if (!list) return;

  function save() {
    fetch("/api/script-library", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state),
    }).then(function (r) { return r.json(); })
      .then(function () { TN.toast("Saved"); })
      .catch(function () { TN.toast("Save failed"); });
  }

  function insertToken(el, tok) {
    var s = el.selectionStart, e = el.selectionEnd;
    if (s == null) { s = e = el.value.length; }
    el.value = el.value.slice(0, s) + tok + el.value.slice(e);
    el.focus();
    var p = s + tok.length; el.setSelectionRange(p, p);
  }
  function tokrow(target) {
    var d = document.createElement("div"); d.className = "tokrow";
    VARKEYS.forEach(function (k) {
      var b = document.createElement("button");
      b.className = "tok"; b.type = "button"; b.textContent = "$" + k;
      b.addEventListener("click", function () { insertToken(target, "$" + k); });
      d.appendChild(b);
    });
    return d;
  }

  function render() {
    list.innerHTML = "";
    if (!state.scripts.length) {
      var e = document.createElement("div"); e.className = "card";
      e.innerHTML = '<p class="empty">No scripts yet. Add one above.</p>';
      list.appendChild(e); return;
    }
    state.scripts.forEach(function (sc, i) {
      var card = document.createElement("div"); card.className = "card prog";
      var head = document.createElement("div"); head.className = "proghead";
      var h = document.createElement("h3"); h.textContent = sc.name; head.appendChild(h);
      var rm = document.createElement("button"); rm.className = "xbtn"; rm.textContent = "remove";
      rm.addEventListener("click", function () { state.scripts.splice(i, 1); save(); render(); });
      head.appendChild(rm); card.appendChild(head);

      var block = document.createElement("div");
      block.className = "cmd script";
      block.innerHTML = "<pre>" + TN.fillHtml(sc.body) + "</pre>";
      TN.attachCopy(block, TN.fillRaw(sc.body));
      card.appendChild(block);
      list.appendChild(card);
    });
  }

  document.getElementById("slToks").appendChild(tokrow(document.getElementById("slBody")));
  document.getElementById("slAdd").addEventListener("click", function () {
    var n = document.getElementById("slName"), b = document.getElementById("slBody");
    var nn = n.value.trim(), bb = b.value;
    if (!nn || !bb.trim()) return;
    state.scripts.push({ name: nn, body: bb });
    n.value = ""; b.value = "";
    save(); render();
  });
  document.addEventListener("tn:vars", render);
  render();
})();
