/* Command library: add programs, add commands under them with placeholder
   buttons, live-substitute the shared vars, persist to data/library.json. */
(function () {
  "use strict";
  var TN = window.TN;
  var state = window.LIBRARY || { programs: [] };
  var VARKEYS = window.VARKEYS || [];
  var list = document.getElementById("libList");
  if (!list) return;

  function save() {
    fetch("/api/library", {
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
    list.innerHTML = "";
    if (!state.programs.length) {
      var e = document.createElement("div");
      e.className = "card";
      e.innerHTML = '<p class="empty">No programs yet. Add one above.</p>';
      list.appendChild(e);
      return;
    }
    state.programs.forEach(function (prog, pi) {
      var card = document.createElement("div");
      card.className = "card prog";

      var head = document.createElement("div");
      head.className = "proghead";
      var h = document.createElement("h3");
      h.textContent = prog.name;
      head.appendChild(h);
      var rm = document.createElement("button");
      rm.className = "xbtn"; rm.textContent = "remove";
      rm.addEventListener("click", function () { state.programs.splice(pi, 1); save(); render(); });
      head.appendChild(rm);
      card.appendChild(head);

      (prog.commands || []).forEach(function (cmd, ci) {
        var el = document.createElement("div");
        el.className = "cmd";
        el.innerHTML = TN.fillHtml(cmd);
        var del = document.createElement("button");
        del.className = "del"; del.textContent = "del";
        del.addEventListener("click", function () { prog.commands.splice(ci, 1); save(); render(); });
        el.appendChild(del);
        TN.attachCopy(el, TN.fillRaw(cmd));
        card.appendChild(el);
      });

      var inp = document.createElement("input");
      inp.type = "text";
      inp.placeholder = "command — use the buttons for placeholders";
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
        prog.commands = prog.commands || [];
        prog.commands.push(v);
        save(); render();
      });
      inp.addEventListener("keydown", function (ev) { if (ev.key === "Enter") add.click(); });
      wrap.appendChild(prompt); wrap.appendChild(inp); wrap.appendChild(add);
      card.appendChild(wrap);

      list.appendChild(card);
    });
  }

  document.getElementById("libAddProg").addEventListener("click", function () {
    var i = document.getElementById("libProg");
    var n = i.value.trim();
    if (!n) return;
    state.programs.push({ name: n, commands: [] });
    i.value = "";
    save(); render();
  });
  document.getElementById("libProg").addEventListener("keydown", function (ev) {
    if (ev.key === "Enter") document.getElementById("libAddProg").click();
  });
  document.addEventListener("tn:vars", render);

  render();
})();
