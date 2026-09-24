/* Reverse shells: filter the shell list by OS, substitute LHOST/LPORT, encode. */
(function () {
  "use strict";
  var TN = window.TN, SHELLS = window.SHELLS || [];
  var rsHost = document.getElementById("rsHost"),
      rsPort = document.getElementById("rsPort"),
      rsType = document.getElementById("rsType"),
      rsEnc = document.getElementById("rsEnc"),
      rsOut = document.getElementById("rsOut"),
      osWrap = document.getElementById("rsOS");
  if (!rsOut) return;

  var os = "linux";

  function esc(s) {
    return String(s).replace(/[&<>]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c];
    });
  }
  function escapeReg(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
  function b64utf8(s) { return btoa(unescape(encodeURIComponent(s))); }
  function b64utf16le(s) {
    var o = "";
    for (var i = 0; i < s.length; i++) {
      var c = s.charCodeAt(i);
      o += String.fromCharCode(c & 0xff, (c >> 8) & 0xff);
    }
    return btoa(o);
  }
  function encode(cmd, enc, name) {
    if (enc === "raw") return cmd;
    if (enc === "url") return encodeURIComponent(cmd);
    if (/powershell|powercat/i.test(name)) return "powershell -nop -enc " + b64utf16le(cmd);
    return "echo " + b64utf8(cmd) + " | base64 -d | bash";
  }

  function filtered() {
    return SHELLS.filter(function (s) { return os === "all" || s.os.indexOf(os) >= 0; });
  }
  function fillSelect() {
    var cur = rsType.value, list = filtered();
    rsType.innerHTML = "";
    list.forEach(function (s) {
      var o = document.createElement("option");
      o.value = s.name; o.textContent = s.name;
      rsType.appendChild(o);
    });
    if (list.some(function (s) { return s.name === cur; })) rsType.value = cur;
  }
  function current() {
    return SHELLS.filter(function (s) { return s.name === rsType.value; })[0];
  }

  function render() {
    var h = rsHost.value.trim() || "$LHOST", p = rsPort.value.trim() || "$LPORT";
    var s = current();
    rsOut.innerHTML = "";
    if (!s) return;
    var cmd = s.cmd.split("{h}").join(h).split("{p}").join(p).trim();
    var enc = rsEnc.value;
    var raw = encode(cmd, enc, s.name);
    var el = document.createElement("div");
    el.className = "cmd";
    var body = (enc === "raw")
      ? esc(raw).replace(new RegExp("(" + escapeReg(h) + "|" + escapeReg(p) + ")", "g"), '<span class="v">$1</span>')
      : esc(raw);
    el.innerHTML = '<span class="lbl">' + esc(s.name) + (enc !== "raw" ? " — " + enc : "") + "</span>" + body;
    TN.attachCopy(el, raw);
    rsOut.appendChild(el);
  }

  osWrap.querySelectorAll("button").forEach(function (b) {
    b.addEventListener("click", function () {
      os = this.dataset.os;
      osWrap.querySelectorAll("button").forEach(function (x) { x.classList.remove("on"); });
      this.classList.add("on");
      fillSelect(); render();
    });
  });
  rsHost.addEventListener("input", function () { TN.setVar("LHOST", this.value.trim()); });
  rsPort.addEventListener("input", function () { TN.setVar("LPORT", this.value.trim()); });
  rsType.addEventListener("change", render);
  rsEnc.addEventListener("change", render);
  document.addEventListener("tn:vars", function () {
    if (document.activeElement !== rsHost) rsHost.value = TN.vars.LHOST || "";
    if (document.activeElement !== rsPort) rsPort.value = TN.vars.LPORT || "";
    render();
  });

  rsHost.value = TN.vars.LHOST || "";
  rsPort.value = TN.vars.LPORT || "";
  fillSelect();
  render();
})();
