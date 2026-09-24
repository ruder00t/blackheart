(function () {
  "use strict";

  // --- official CVSS v3.1 metric weights ---
  var W = {
    AV: { N: 0.85, A: 0.62, L: 0.55, P: 0.20 },
    AC: { L: 0.77, H: 0.44 },
    UI: { N: 0.85, R: 0.62 },
    C: { H: 0.56, L: 0.22, N: 0.00 },
    I: { H: 0.56, L: 0.22, N: 0.00 },
    A: { H: 0.56, L: 0.22, N: 0.00 },
    PR: {
      U: { N: 0.85, L: 0.62, H: 0.27 },
      C: { N: 0.85, L: 0.68, H: 0.50 }
    },
    E: { X: 1, H: 1, F: 0.97, P: 0.94, U: 0.91 },
    RL: { X: 1, U: 1, W: 0.97, T: 0.96, O: 0.95 },
    RC: { X: 1, C: 1, R: 0.96, U: 0.92 }
  };

  var ORDER = ["AV", "AC", "PR", "UI", "S", "C", "I", "A", "E", "RL", "RC"];
  var TEMPORAL = ["E", "RL", "RC"];

  // current selection (defaults match the .on buttons in the template)
  var sel = { AV: "N", AC: "L", PR: "N", UI: "N", S: "U", C: "H", I: "H", A: "H",
              E: "X", RL: "X", RC: "X" };

  function roundup(x) {
    var i = Math.round(x * 100000);
    return (i % 10000 === 0) ? i / 100000 : (Math.floor(i / 10000) + 1) / 10.0;
  }

  function severity(s) {
    if (s <= 0) return "None";
    if (s < 4.0) return "Low";
    if (s < 7.0) return "Medium";
    if (s < 9.0) return "High";
    return "Critical";
  }

  function compute() {
    var s = sel.S;
    var pr = W.PR[s][sel.PR];
    var iss = 1 - ((1 - W.C[sel.C]) * (1 - W.I[sel.I]) * (1 - W.A[sel.A]));
    var impact = (s === "U")
      ? 6.42 * iss
      : 7.52 * (iss - 0.029) - 3.25 * Math.pow(iss - 0.02, 15);
    var expl = 8.22 * W.AV[sel.AV] * W.AC[sel.AC] * pr * W.UI[sel.UI];

    var base;
    if (impact <= 0) base = 0.0;
    else if (s === "U") base = roundup(Math.min(impact + expl, 10));
    else base = roundup(Math.min(1.08 * (impact + expl), 10));

    var temporal = roundup(base * W.E[sel.E] * W.RL[sel.RL] * W.RC[sel.RC]);
    var hasTemporal = sel.E !== "X" || sel.RL !== "X" || sel.RC !== "X";
    return { base: base, temporal: temporal, hasTemporal: hasTemporal };
  }

  function vector() {
    var v = "CVSS:3.1";
    ["AV", "AC", "PR", "UI", "S", "C", "I", "A"].forEach(function (m) {
      v += "/" + m + ":" + sel[m];
    });
    TEMPORAL.forEach(function (m) { if (sel[m] !== "X") v += "/" + m + ":" + sel[m]; });
    return v;
  }

  function sevClass(name) { return "sev-" + name.toLowerCase(); }

  function render() {
    var r = compute();
    var score = r.hasTemporal ? r.temporal : r.base;
    var sev = severity(score);

    var elScore = document.getElementById("cvssScore");
    var elSev = document.getElementById("cvssSev");
    elScore.textContent = score.toFixed(1);
    elSev.textContent = sev;
    elScore.className = "cvss-score " + sevClass(sev);
    elSev.className = "cvss-sev " + sevClass(sev);

    document.getElementById("cvssBase").textContent = r.base.toFixed(1);
    document.getElementById("cvssTemp").textContent = r.hasTemporal ? r.temporal.toFixed(1) : "\u2013";

    var vec = vector();
    var elVec = document.getElementById("cvssVec");
    elVec.textContent = vec;
    elVec.dataset.raw = vec;
    ensureCopy(elVec, vec);
  }

  // lightweight copy button (independent of app.js $VAR handling)
  function ensureCopy(el, raw) {
    var b = el.querySelector(".copy");
    if (!b) {
      b = document.createElement("button");
      b.className = "copy";
      b.textContent = "copy";
      el.appendChild(b);
    }
    b.onclick = function () {
      navigator.clipboard.writeText(raw).then(function () {
        b.textContent = "copied"; b.classList.add("ok");
        var t = document.getElementById("toast");
        if (t) { t.classList.add("show"); setTimeout(function () { t.classList.remove("show"); }, 1000); }
        setTimeout(function () { b.textContent = "copy"; b.classList.remove("ok"); }, 1200);
      });
    };
  }

  function setButton(metric, val) {
    var wrap = document.querySelector('.cvss-metric[data-m="' + metric + '"]');
    if (!wrap || !(val in (metricValues(metric) || {}))) return;
    sel[metric] = val;
    wrap.querySelectorAll("button").forEach(function (btn) {
      btn.classList.toggle("on", btn.dataset.val === val);
    });
  }

  function metricValues(m) {
    if (m === "S") return { U: 1, C: 1 };
    if (m === "PR") return W.PR.U;
    return W[m];
  }

  function wire() {
    document.querySelectorAll(".cvss-metric").forEach(function (wrap) {
      var m = wrap.dataset.m;
      wrap.querySelectorAll("button").forEach(function (btn) {
        btn.addEventListener("click", function () {
          sel[m] = btn.dataset.val;
          wrap.querySelectorAll("button").forEach(function (b) { b.classList.remove("on"); });
          btn.classList.add("on");
          render();
        });
      });
    });

    var parse = document.getElementById("cvssParse");
    parse.addEventListener("input", function () {
      var str = parse.value.trim().toUpperCase();
      if (!str) return;
      var parts = str.split("/");
      var found = false;
      parts.forEach(function (p) {
        var kv = p.split(":");
        if (kv.length !== 2) return;
        var m = kv[0], v = kv[1];
        if (ORDER.indexOf(m) === -1) return;
        var valid = metricValues(m);
        if (valid && v in valid) { setButton(m, v); found = true; }
      });
      if (found) render();
    });
  }

  document.addEventListener("DOMContentLoaded", function () { wire(); render(); });
})();
