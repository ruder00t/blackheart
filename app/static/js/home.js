/* Home extras: New project / Reset to defaults / Import-all backup.
   Reuses TN.setVar + TN.saveVars so live substitution and vars.json stay in sync. */
(function () {
  "use strict";
  var TN = window.TN;
  var defaults = window.VAR_DEFAULTS || {};
  var targetKeys = window.VAR_TARGETKEYS || [];

  function setField(key, val) {
    var inp = document.querySelector('input[data-var="' + key + '"]');
    if (inp) inp.value = val;
    if (TN && TN.setVar) TN.setVar(key, val);
  }

  var np = document.getElementById("newProject");
  if (np) np.addEventListener("click", function () {
    if (!confirm("Clear target-specific variables (RHOST, RPORT, DOMAIN, USER, PASS)? Your LHOST/ports/wordlists stay.")) return;
    targetKeys.forEach(function (k) { setField(k, ""); });
    if (TN && TN.saveVars) TN.saveVars();
  });

  var rd = document.getElementById("resetDefaults");
  if (rd) rd.addEventListener("click", function () {
    if (!confirm("Reset ALL variables to their default values?")) return;
    Object.keys(defaults).forEach(function (k) { setField(k, defaults[k]); });
    if (TN && TN.saveVars) TN.saveVars();
  });

  var ib = document.getElementById("importAllBtn");
  var inp = document.getElementById("importAll");
  if (ib && inp) {
    ib.addEventListener("click", function () { inp.click(); });
    inp.addEventListener("change", function (ev) {
      var f = ev.target.files && ev.target.files[0];
      if (!f) return;
      var r = new FileReader();
      r.onload = function () {
        var payload;
        try { payload = JSON.parse(r.result); }
        catch (e) { TN.toast("Invalid backup file"); return; }
        if (!confirm("Import this backup? It overwrites your current saved settings (variables, libraries, additions, etc.).")) return;
        fetch("/api/backup/import", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }).then(function (r) { return r.json(); })
          .then(function (d) {
            if (d && d.ok) { TN.toast("Imported — reloading"); setTimeout(function () { location.reload(); }, 600); }
            else { TN.toast("Import failed"); }
          }).catch(function () { TN.toast("Import failed"); });
      };
      r.readAsText(f);
      ev.target.value = "";
    });
  }
})();
