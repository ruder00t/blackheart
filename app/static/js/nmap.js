/* Blackheart nmap builder — assemble an nmap command from the controls.
 * Target is $RHOST (substituted for display via TN.renderTpls' copy fill). */
(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  var out = $("nmOutCmd"), hint = $("nmHint");
  if (!out) return;

  var portMode = $("nmPortMode"), portsCustom = $("nmPorts");
  portMode.addEventListener("change", function () {
    portsCustom.disabled = portMode.value !== "custom";
    if (portMode.value === "custom") portsCustom.focus();
    render();
  });

  // -A implies -sV -sC -O; grey those out when -A is on
  function syncA() {
    var a = $("nmA").checked;
    ["nmSV", "nmSC", "nmO"].forEach(function (id) { $(id).disabled = a; });
  }

  function render() {
    var parts = ["nmap"];
    var warn = [];

    // scan type + timing + rate
    if ($("nmScan").value) parts.push($("nmScan").value);
    if ($("nmTiming").value) parts.push($("nmTiming").value);
    if ($("nmRate").value) parts.push($("nmRate").value);

    // detection
    if ($("nmA").checked) parts.push("-A");
    else {
      if ($("nmSV").checked) parts.push("-sV");
      if ($("nmSC").checked) parts.push("-sC");
      if ($("nmO").checked) parts.push("-O");
    }
    if ($("nmPn").checked) parts.push("-Pn");
    if ($("nmN").checked) parts.push("-n");
    if ($("nmv").checked) parts.push("-v");
    if ($("nmReason").checked) parts.push("--reason");
    if ($("nmOpen").checked) parts.push("--open");

    // scripts
    var sc = $("nmScript").value.trim();
    if (sc) parts.push("--script " + sc);

    // ports (skip for ping sweep)
    var pingOnly = $("nmScan").value === "-sn";
    if (!pingOnly) {
      var pm = portMode.value;
      if (pm === "custom") {
        var p = portsCustom.value.trim();
        if (p) parts.push("-p " + p); else warn.push("custom ports selected but empty");
      } else if (pm) parts.push(pm);
    }

    // output
    if ($("nmOut").value) parts.push($("nmOut").value);

    parts.push("$RHOST");

    // sanity hints
    if ($("nmScan").value.indexOf("-sU") > -1) warn.push("UDP scans are slow — consider --top-ports 100");
    if ($("nmScan").value === "-sS" || $("nmScan").value.indexOf("-sS") > -1) warn.push("-sS/-sU need root (sudo)");
    if (pingOnly) warn.push("ping sweep ignores port/detection options");

    var cmd = parts.join(" ");
    out.innerHTML = '<div class="cmd" data-tpl="' + cmd.replace(/"/g, "&quot;") + '"></div>';
    if (window.TN && TN.renderTpls) TN.renderTpls(out);
    hint.textContent = warn.length ? "note: " + warn.join(" · ") : "";
  }

  // wire every control
  ["nmScan", "nmTiming", "nmRate", "nmPortMode", "nmPorts", "nmScript", "nmOut"].forEach(function (id) {
    $(id).addEventListener("input", render); $(id).addEventListener("change", render);
  });
  ["nmSV", "nmSC", "nmO", "nmA", "nmPn", "nmN", "nmv", "nmReason", "nmOpen"].forEach(function (id) {
    $(id).addEventListener("change", function () { syncA(); render(); });
  });

  syncA();
  render();
})();
