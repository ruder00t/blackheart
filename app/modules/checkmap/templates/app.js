// State persists in localStorage, namespaced per run so multiple checklist
// files opened from the same file:// origin never collide.
(function () {
  var NS = window.__RUN_NS__ || "run";
  var KEY = "pcl:" + NS;
  var state = {};
  try { state = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) {}

  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}
    updateProgress();
  }

  // tri-state: undefined -> checked -> crossed -> undefined
  function applyState(step) {
    var id = step.dataset.id, s = state[id];
    var cb = step.querySelector(".cb");
    cb.classList.remove("checked", "crossed");
    step.classList.remove("crossed");
    cb.textContent = "";
    if (s === "checked") { cb.classList.add("checked"); cb.textContent = "✓"; }
    else if (s === "crossed") { cb.classList.add("crossed"); step.classList.add("crossed"); cb.textContent = "✕"; }
  }

  function cycle(step) {
    var id = step.dataset.id, s = state[id];
    if (!s) state[id] = "checked";
    else if (s === "checked") state[id] = "crossed";
    else delete state[id];
    applyState(step); save();
  }

  function updateProgress() {
    var steps = document.querySelectorAll(".step");
    var done = 0;
    steps.forEach(function (st) {
      var s = state[st.dataset.id];
      if (s === "checked" || s === "crossed") done++;
    });
    var el = document.getElementById("progress");
    if (el) el.textContent = done + " / " + steps.length + " handled";
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".step").forEach(function (step) {
      applyState(step);
      step.querySelector(".cb").addEventListener("click", function (e) { e.stopPropagation(); cycle(step); });
      var txt = step.querySelector(".step-text");
      if (txt) txt.addEventListener("click", function () { cycle(step); });
    });

    document.querySelectorAll(".cmd-toggle").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var box = btn.nextElementSibling;
        box.classList.toggle("open");
        btn.textContent = box.classList.contains("open")
          ? "▾ hide commands" : "▸ show commands";
      });
    });

    document.querySelectorAll(".cmd button").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var text = btn.previousElementSibling.textContent;
        copy(text, btn);
      });
    });

    var ex = document.getElementById("expandAll");
    if (ex) ex.addEventListener("click", function () {
      document.querySelectorAll("details").forEach(function (d) { d.open = true; });
    });
    var col = document.getElementById("collapseAll");
    if (col) col.addEventListener("click", function () {
      document.querySelectorAll("details.svc, details.section").forEach(function (d) { d.open = false; });
    });
    var rs = document.getElementById("reset");
    if (rs) rs.addEventListener("click", function () {
      if (!confirm("Clear all checkbox state for this checklist?")) return;
      state = {}; save();
      document.querySelectorAll(".step").forEach(applyState);
    });

    updateProgress();
  });

  // clipboard with file:// fallback
  function copy(text, btn) {
    function ok() { var o = btn.textContent; btn.textContent = "copied"; btn.classList.add("copied");
      setTimeout(function () { btn.textContent = o; btn.classList.remove("copied"); }, 1200); }
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(ok, function () { legacy(text, ok); });
    } else { legacy(text, ok); }
  }
  function legacy(text, ok) {
    var ta = document.createElement("textarea");
    ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta); ta.select();
    try { document.execCommand("copy"); ok(); } catch (e) {}
    document.body.removeChild(ta);
  }
})();
