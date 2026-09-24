/* Blackheart terminal pop-out: ensure the tmux session + ttyd are up, then
   point the iframe at ttyd. Shows a clear message if tmux/ttyd are missing. */
(function () {
  "use strict";
  var frame = document.getElementById("termFrame");
  var msg = document.getElementById("termMsg");
  var msgText = document.getElementById("termMsgText");

  function fail(html) {
    frame.style.display = "none";
    msg.style.display = "flex";
    msgText.innerHTML = html;
  }

  fetch("/api/term/ensure", { method: "POST" })
    .then(function (r) { return r.json(); })
    .then(function (d) {
      if (!d.ok) {
        if (d.missing && d.missing.length) {
          fail("Missing runtime dependenc" + (d.missing.length > 1 ? "ies" : "y") +
            ": <code>" + d.missing.join("</code> <code>") + "</code>.<br><br>" +
            "Install with <code>./install.sh</code> or your package manager, then reload.");
        } else {
          fail("Could not start the terminal.");
        }
        return;
      }
      if (!d.ttyd) {
        fail("ttyd is not running. Reload to retry.");
        return;
      }
      frame.src = d.ttyd_url || window.TTYD_URL;
    })
    .catch(function () { fail("Terminal backend unreachable."); });
})();
