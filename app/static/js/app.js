/* Blackheart core: shared variable store, live command substitution, copy,
   toast, and the home Save action. Exposes window.TN for module scripts. */
window.TN = (function () {
  "use strict";
  var vars = window.VARS || {};

  function esc(s) {
    return String(s).replace(/[&<>]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c];
    });
  }

  // fill for display: highlight known values, keep $VAR for blanks
  function fillHtml(tpl) {
    return esc(tpl).replace(/\$([A-Z_]+)/g, function (m, k) {
      return vars[k]
        ? '<span class="v">' + esc(vars[k]) + "</span>"
        : '<span class="ph">' + m + "</span>";
    });
  }
  // fill for copy: plain text, keep $VAR for blanks
  function fillRaw(tpl) {
    return tpl.replace(/\$([A-Z_]+)/g, function (m, k) { return vars[k] || m; });
  }

  function attachCopy(el, raw) {
    var b = document.createElement("button");
    b.className = "copy";
    b.textContent = "copy";
    b.addEventListener("click", function () {
      navigator.clipboard.writeText(raw).then(function () {
        b.textContent = "copied"; b.classList.add("ok"); toast();
        setTimeout(function () { b.textContent = "copy"; b.classList.remove("ok"); }, 1200);
      });
    });
    el.appendChild(b);
    attachSend(el, raw);   // additive: "send to terminal" next to copy
  }

  // ----- send to terminal (split button: send + caret picker) -----
  // click       = stage at prompt (no Enter, safer for destructive cmds)
  // shift-click  = run now (append Enter)
  // caret        = 2x2 picker -> send to a NON-default pane (shift = run)
  function attachSend(el, raw) {
    var wrap = document.createElement("span");
    wrap.className = "sendwrap";

    var s = document.createElement("button");
    s.className = "send";
    s.textContent = "send";
    s.title = "Send to active pane · click = stage · shift-click = run";
    s.addEventListener("click", function (e) {
      Term.send(raw, Term.getActive(), e.shiftKey);
      s.textContent = e.shiftKey ? "ran" : "sent";
      s.classList.add("ok");
      setTimeout(function () { s.textContent = "send"; s.classList.remove("ok"); }, 1200);
    });

    var c = document.createElement("button");
    c.className = "send-caret";
    c.innerHTML = "&#9662;";           // ▾
    c.title = "Send to a specific pane (2x2 picker)";
    c.addEventListener("click", function (e) {
      e.stopPropagation();
      Term.openPicker(raw, c);
    });

    wrap.appendChild(s);
    wrap.appendChild(c);
    el.appendChild(wrap);
  }

  function renderTpls(root) {
    (root || document).querySelectorAll(".cmd[data-tpl]").forEach(function (el) {
      var lbl = el.querySelector(".lbl");
      var lblHtml = lbl ? lbl.outerHTML : "";
      var raw = fillRaw(el.dataset.tpl);
      el.innerHTML = lblHtml + fillHtml(el.dataset.tpl);
      attachCopy(el, raw);
    });
  }

  // ----- Additions overlay: inject user notes onto their target tab -----
  function buildAddCard(where, items) {
    var card = document.createElement("div");
    card.className = "card additions-card";
    card.dataset.addWhere = where;
    var h = document.createElement("h3");
    h.textContent = "Additions";
    card.appendChild(h);
    var hint = document.createElement("p");
    hint.className = "hint";
    hint.textContent = "Your own entries for this tab (" + where + "). Manage them on the Additions tab.";
    card.appendChild(hint);
    items.forEach(function (it) {
      var el = document.createElement("div");
      el.className = "cmd";
      el.innerHTML = fillHtml(it.text);
      attachCopy(el, fillRaw(it.text));
      card.appendChild(el);
    });
    return card;
  }

  function renderAdditions() {
    var all = window.ADDITIONS || {};
    var active = window.ACTIVE;
    if (!active) return;
    var pane = document.querySelector(".pane");
    if (!pane) return;

    // clear any previously injected cards (so re-render on var change is clean)
    pane.querySelectorAll(".additions-card").forEach(function (c) { c.remove(); });

    var items = all[active] || [];
    if (!items.length) return;

    var top = items.filter(function (i) { return i.pos === "top"; });
    var bottom = items.filter(function (i) { return i.pos !== "top"; });

    if (top.length) {
      var head = pane.querySelector(".pane-head");
      var topCard = buildAddCard("top", top);
      if (head && head.nextSibling) pane.insertBefore(topCard, head.nextSibling);
      else pane.appendChild(topCard);
    }
    if (bottom.length) {
      pane.appendChild(buildAddCard("bottom", bottom));
    }
  }

  var toastEl, toastT;
  function toast(msg) {
    if (!toastEl) toastEl = document.getElementById("toast");
    if (!toastEl) return;
    toastEl.textContent = msg || "Copied";
    toastEl.classList.add("show");
    clearTimeout(toastT);
    toastT = setTimeout(function () { toastEl.classList.remove("show"); }, 1400);
  }

  function syncFields(k) {
    document.querySelectorAll('input[data-var="' + k + '"]').forEach(function (inp) {
      if (document.activeElement !== inp) inp.value = vars[k] || "";
    });
  }

  function setVar(k, v) {
    vars[k] = v;
    syncFields(k);
    renderTpls();
    document.dispatchEvent(new CustomEvent("tn:vars"));
  }

  function saveVars() {
    return fetch("/api/vars", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(vars),
    })
      .then(function (r) { return r.json(); })
      .then(function () { toast("Variables saved"); })
      .catch(function () { toast("Save failed"); });
  }

  function wireHome() {
    var grid = document.getElementById("varGrid");
    if (grid) {
      grid.querySelectorAll("input[data-var]").forEach(function (inp) {
        inp.addEventListener("input", function () {
          setVar(this.dataset.var, this.value.trim());
        });
      });
    }
    var save = document.getElementById("saveVars");
    if (save) save.addEventListener("click", saveVars);
    var logo = document.getElementById("logoSave");   // logo saves from any page
    if (logo) logo.addEventListener("click", saveVars);
  }

  function wireChips() {
    document.querySelectorAll(".chip input").forEach(function (cb) {
      function sync() { cb.closest(".chip").classList.toggle("on", cb.checked); }
      cb.addEventListener("change", sync);
      sync();
    });
  }

  // keep the sidebar scroll position across page loads (nav is the scroll box)
  function wireSideScroll() {
    var navEl = document.querySelector(".side nav");
    if (!navEl) return;
    var KEY = "bh:side:scroll";
    try {
      var y = sessionStorage.getItem(KEY);
      if (y !== null) navEl.scrollTop = parseInt(y, 10) || 0;
    } catch (e) {}
    // make sure the active item is in view; only override if it's off-screen
    var act = navEl.querySelector(".navitem.active");
    if (act) {
      var top = act.offsetTop, bot = top + act.offsetHeight;
      if (top < navEl.scrollTop || bot > navEl.scrollTop + navEl.clientHeight) {
        act.scrollIntoView({ block: "center" });
      }
    }
    var t;
    navEl.addEventListener("scroll", function () {
      clearTimeout(t);
      t = setTimeout(function () {
        try { sessionStorage.setItem(KEY, navEl.scrollTop); } catch (e) {}
      }, 80);
    });
  }

  function wireNav() {
    document.querySelectorAll(".navgroup").forEach(function (g) {
      var head = g.querySelector(".navhead");
      if (!head) return;
      // startup: every group closed except Engagement (saved state ignored)
      var collapsed = g.dataset.cat !== "Engagement";
      if (g.querySelector(".navitem.active")) collapsed = false;  // keep active tab visible
      g.classList.toggle("collapsed", collapsed);
      head.addEventListener("click", function () {
        g.classList.toggle("collapsed");
      });
    });
  }

  function wireTabs() {
    document.querySelectorAll(".tabseg").forEach(function (seg) {
      var key = seg.dataset.panels;
      var panels = document.querySelector('.tabpanels[data-panels="' + key + '"]');
      if (!panels) return;
      seg.querySelectorAll("button[data-tab]").forEach(function (b) {
        b.addEventListener("click", function () {
          seg.querySelectorAll("button").forEach(function (x) { x.classList.remove("on"); });
          b.classList.add("on");
          panels.querySelectorAll(".tabpanel").forEach(function (p) {
            p.hidden = p.dataset.tab !== b.dataset.tab;
          });
        });
      });
    });
  }

  // ----- global search -----
  function wireSearch() {
    var btn = document.getElementById("searchBtn");
    var overlay = document.getElementById("searchOverlay");
    var input = document.getElementById("searchInput");
    var results = document.getElementById("searchResults");
    if (!btn || !overlay || !input || !results) return;
    var data = null, sel = -1, rows = [];

    function esc(s) { return String(s).replace(/[&<>]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]; }); }
    function hl(s, q) {
      if (!q) return esc(s);
      var i = s.toLowerCase().indexOf(q.toLowerCase());
      if (i < 0) return esc(s);
      return esc(s.slice(0, i)) + "<mark>" + esc(s.slice(i, i + q.length)) + "</mark>" + esc(s.slice(i + q.length));
    }
    function open() {
      overlay.hidden = false; input.value = ""; input.focus();
      render("");
      if (!data) {
        fetch("/api/search-index").then(function (r) { return r.json(); })
          .then(function (d) { data = d; render(input.value); })
          .catch(function () { results.innerHTML = '<div class="searchEmpty">Search index unavailable.</div>'; });
      }
    }
    function close() { overlay.hidden = true; }
    function render(q) {
      if (!data) { results.innerHTML = '<div class="searchEmpty">Loading…</div>'; return; }
      q = (q || "").trim();
      var list = q ? data.filter(function (e) { return (e.t + " " + e.c).toLowerCase().indexOf(q.toLowerCase()) > -1; }) : data.slice(0, 40);
      list = list.slice(0, 60);
      sel = list.length ? 0 : -1;
      rows = list;
      if (!list.length) { results.innerHTML = '<div class="searchEmpty">No matches.</div>'; return; }
      results.innerHTML = list.map(function (e, i) {
        return '<a class="sr' + (i === 0 ? ' sel' : '') + '" href="' + e.url + '" data-i="' + i + '">' +
          '<span class="cmd-t">' + hl(e.c, q) + '</span>' +
          '<span class="sr-tab">' + esc(e.tab) + '</span></a>';
      }).join("");
      Array.prototype.forEach.call(results.querySelectorAll(".sr"), function (a) {
        a.addEventListener("mouseenter", function () { setSel(+a.dataset.i); });
      });
    }
    function setSel(i) {
      var els = results.querySelectorAll(".sr");
      if (!els.length) return;
      sel = (i + els.length) % els.length;
      els.forEach(function (e, j) { e.classList.toggle("sel", j === sel); });
      els[sel].scrollIntoView({ block: "nearest" });
    }
    function go() { if (sel >= 0 && rows[sel]) window.location.href = rows[sel].url; }

    btn.addEventListener("click", open);
    overlay.addEventListener("click", function (e) { if (e.target === overlay) close(); });
    input.addEventListener("input", function () { render(input.value); });
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); setSel(sel + 1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); setSel(sel - 1); }
      else if (e.key === "Enter") { e.preventDefault(); go(); }
      else if (e.key === "Escape") { close(); }
    });
    document.addEventListener("keydown", function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); overlay.hidden ? open() : close(); }
    });
  }

  // ----- integrated terminal controller (tiles, send, overlay, picker) -----
  // Tile colour is read from the panes themselves (server capture-pane):
  //   only-a-prompt / cleared -> BLUE, output above the prompt -> GREEN.
  // Ctrl+L inside the terminal clears the pane, so it goes BLUE on next poll —
  // no browser keystroke capture needed. Sending sets the tile GREEN at once.
  var Term = (function () {
    var ACTIVE_KEY = "bh:term:active";
    var active = 0, tileEls = [], pollTimer = null;

    function quad(q) { return ["TL", "TR", "BL", "BR"][q] || ("#" + q); }

    function loadActive() {
      try {
        var v = parseInt(localStorage.getItem(ACTIVE_KEY), 10);
        if (v >= 0 && v <= 3) active = v;
      } catch (e) {}
    }
    function getActive() { return active; }
    function setActive(q) {
      active = q;
      try { localStorage.setItem(ACTIVE_KEY, String(q)); } catch (e) {}
      renderActive();
    }
    function renderActive() {
      tileEls.forEach(function (el, i) { if (el) el.classList.toggle("active", i === active); });
    }
    function setTile(q, state) {
      var el = tileEls[q];
      if (!el) return;
      el.classList.remove("blue", "green");
      el.classList.add(state === "green" ? "green" : "blue");
    }
    function applyTiles(states) {
      if (!states) return;
      states.forEach(function (st, i) { setTile(i, st); });
    }

    function send(raw, q, run) {
      fetch("/api/term/send", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: raw, pane: q, run: !!run }),
      }).then(function (r) { return r.json(); }).then(function (d) {
        if (d.ok) {
          setTile(q, "green");                       // optimistic; poll confirms
          toast((run ? "Sent + run \u2192 " : "Staged \u2192 ") + quad(q));
          setTimeout(pollStatus, 400);
        } else if (d.missing && d.missing.length) {
          toast("Missing: " + d.missing.join(", "));
        } else { toast("Send failed"); }
      }).catch(function () { toast("Send failed"); });
    }

    function pollStatus() {
      fetch("/api/term/status").then(function (r) { return r.json(); })
        .then(function (d) { if (d && d.ok) applyTiles(d.tiles); })
        .catch(function () {});
    }
    function startPoll() {
      pollStatus();
      if (pollTimer) clearInterval(pollTimer);
      pollTimer = setInterval(pollStatus, 2000);
    }

    // ----- 2x2 picker (send to a non-default pane) -----
    var pendingRaw = null;
    function openPicker(raw, anchor) {
      var pop = document.getElementById("pickerPop");
      if (!pop) return;
      pendingRaw = raw;
      pop.hidden = false;
      var r = anchor.getBoundingClientRect();
      var w = pop.offsetWidth, h = pop.offsetHeight;
      var left = Math.min(r.left, window.innerWidth - w - 8);
      var top = r.bottom + 6;
      if (top + h > window.innerHeight) top = r.top - h - 6;
      pop.style.left = Math.max(8, left) + "px";
      pop.style.top = Math.max(8, top) + "px";
    }
    function closePicker() {
      var pop = document.getElementById("pickerPop");
      if (pop) pop.hidden = true;
      pendingRaw = null;
    }

    // ----- in-page overlay -----
    function ensureAndLoad(frame, msgBox, msgText) {
      fetch("/api/term/ensure", { method: "POST" })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (!d.ok) {
            if (msgBox) {
              msgBox.hidden = false;
              msgText.innerHTML = (d.missing && d.missing.length)
                ? ("Missing runtime dependenc" + (d.missing.length > 1 ? "ies" : "y") +
                   ": <code>" + d.missing.join("</code> <code>") +
                   "</code>. Install via <code>./install.sh</code>, then reopen.")
                : "Could not start the terminal.";
            }
            return;
          }
          if (msgBox) msgBox.hidden = true;
          if (d.ttyd && frame && !frame.src) frame.src = d.ttyd_url;
          else if (!d.ttyd && msgBox) { msgBox.hidden = false; msgText.textContent = "ttyd is not running."; }
          startPoll();
        })
        .catch(function () {
          if (msgBox) { msgBox.hidden = false; msgText.textContent = "Terminal backend unreachable."; }
        });
    }

    function init() {
      loadActive();
      var wrap = document.getElementById("paneTiles");
      if (wrap) {
        tileEls = [null, null, null, null];
        wrap.querySelectorAll(".tile").forEach(function (el) {
          var q = parseInt(el.dataset.q, 10);
          tileEls[q] = el;
          el.addEventListener("click", function () { setActive(q); });
        });
        renderActive();
      }

      var toggle = document.getElementById("termToggle");
      var ov = document.getElementById("termOverlay");
      var frame = document.getElementById("termOverlayFrame");
      var msgBox = document.getElementById("termOverlayMsg");
      var msgText = document.getElementById("termOverlayMsgText");
      var close = document.getElementById("termClose");
      if (toggle && ov) {
        toggle.addEventListener("click", function () {
          var show = ov.hidden;
          ov.hidden = !show;
          toggle.classList.toggle("on", show);
          if (show) ensureAndLoad(frame, msgBox, msgText);
        });
      }
      if (close && ov) close.addEventListener("click", function () {
        ov.hidden = true; if (toggle) toggle.classList.remove("on");
      });

      var pop = document.getElementById("pickerPop");
      if (pop) {
        pop.querySelectorAll(".pickerGrid button").forEach(function (b) {
          b.addEventListener("click", function (e) {
            var q = parseInt(b.dataset.q, 10);
            if (pendingRaw != null) send(pendingRaw, q, e.shiftKey);
            closePicker();
          });
        });
      }
      document.addEventListener("click", function (e) {
        var pop = document.getElementById("pickerPop");
        if (pop && !pop.hidden && !pop.contains(e.target)) closePicker();
      });
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") closePicker();
      });

      startPoll();
    }

    return { init: init, getActive: getActive, setActive: setActive,
             send: send, openPicker: openPicker };
  })();

  document.addEventListener("DOMContentLoaded", function () {
    renderTpls(document);
    renderAdditions();
    wireHome();
    wireChips();
    wireNav();
    wireSideScroll();
    wireTabs();
    wireSearch();
    Term.init();
  });
  // additions carry $VARs too — re-render them when variables change
  document.addEventListener("tn:vars", renderAdditions);

  return {
    vars: vars, fillHtml: fillHtml, fillRaw: fillRaw,
    renderTpls: renderTpls, attachCopy: attachCopy, toast: toast, setVar: setVar,
    saveVars: saveVars,
  };
})();
