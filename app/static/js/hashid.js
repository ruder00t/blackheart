/* Blackheart hash identifier — detect likely hash types from format/length and
 * emit the exact hashcat mode + John format, with the engagement PASSLIST filled.
 * Heuristic (like hashid/hash-identifier); hex-length hashes are ambiguous by
 * design, so several candidates are shown ranked most-likely first. Offline. */
(function () {
  "use strict";
  var input = document.getElementById("hidIn"), out = document.getElementById("hidOut");
  if (!input) return;

  function passlist() {
    try { return (window.VARS && window.VARS.PASSLIST) || "/usr/share/wordlists/rockyou.txt"; }
    catch (e) { return "/usr/share/wordlists/rockyou.txt"; }
  }

  // each rule: {re, list:[{name, m(hashcat mode)|null, john}]}
  var RULES = [
    { re: /^[a-f0-9]{32}$/i, list: [
      { name: "MD5", m: "0", john: "raw-md5" },
      { name: "NTLM", m: "1000", john: "nt" },
      { name: "MD4", m: "900", john: "raw-md4" },
      { name: "LM (half)", m: "3000", john: "lm" },
      { name: "double MD5", m: "2600", john: null },
    ] },
    { re: /^[a-f0-9]{40}$/i, list: [
      { name: "SHA-1", m: "100", john: "raw-sha1" },
      { name: "RIPEMD-160", m: "6000", john: "ripemd-160" },
      { name: "SHA-1(base64) / other 160-bit", m: "100", john: null },
    ] },
    { re: /^\*[A-F0-9]{40}$/i, list: [
      { name: "MySQL 4.1/5.x", m: "300", john: "mysql-sha1" },
    ] },
    { re: /^[a-f0-9]{16}$/i, list: [
      { name: "MySQL 3.23", m: "200", john: "mysql" },
      { name: "DES(Unix) / crypt(16)", m: "1500", john: "descrypt" },
    ] },
    { re: /^[a-f0-9]{56}$/i, list: [{ name: "SHA-224", m: "1300", john: "raw-sha224" }] },
    { re: /^[a-f0-9]{64}$/i, list: [
      { name: "SHA-256", m: "1400", john: "raw-sha256" },
      { name: "SHA3-256", m: "17400", john: null },
      { name: "Keccak-256", m: "17800", john: null },
      { name: "BLAKE2s / GOST", m: "1400", john: null },
    ] },
    { re: /^[a-f0-9]{96}$/i, list: [{ name: "SHA-384", m: "10800", john: "raw-sha384" }] },
    { re: /^[a-f0-9]{128}$/i, list: [
      { name: "SHA-512", m: "1700", john: "raw-sha512" },
      { name: "Whirlpool", m: "6100", john: "whirlpool" },
      { name: "SHA3-512 / Keccak-512", m: "17600", john: null },
    ] },
    { re: /^\$2[abxy]\$\d\d\$[./A-Za-z0-9]{53}$/, list: [{ name: "bcrypt", m: "3200", john: "bcrypt" }] },
    { re: /^\$1\$[^$]{1,8}\$/, list: [{ name: "md5crypt (Cisco IOS type 5, FreeBSD)", m: "500", john: "md5crypt" }] },
    { re: /^\$5\$/, list: [{ name: "sha256crypt", m: "7400", john: "sha256crypt" }] },
    { re: /^\$6\$/, list: [{ name: "sha512crypt", m: "1800", john: "sha512crypt" }] },
    { re: /^\$(P|H)\$/, list: [{ name: "phpass (WordPress / phpBB3 / Joomla)", m: "400", john: "phpass" }] },
    { re: /^\$apr1\$/, list: [{ name: "Apache apr1 md5", m: "1600", john: "md5crypt" }] },
    { re: /^\{SSHA\}/, list: [{ name: "LDAP salted SHA-1 (SSHA)", m: "111", john: "salted-sha1" }] },
    { re: /^\{SHA\}/, list: [{ name: "LDAP SHA-1 (base64)", m: "101", john: "nsldap" }] },
    { re: /^\$8\$/, list: [{ name: "Cisco IOS type 8 (pbkdf2-sha256)", m: "9200", john: "cisco8" }] },
    { re: /^\$9\$/, list: [{ name: "Cisco IOS type 9 (scrypt)", m: "9300", john: "cisco9" }] },
    { re: /^pbkdf2_sha256\$/, list: [{ name: "Django (PBKDF2-SHA256)", m: "10000", john: "django" }] },
    { re: /^\$argon2(id|i|d)\$/, list: [{ name: "Argon2", m: null, john: "argon2" }] },
    { re: /^\$krb5tgs\$23\$/, list: [{ name: "Kerberos 5 TGS-REP (RC4) — Kerberoast", m: "13100", john: "krb5tgs" }] },
    { re: /^\$krb5tgs\$(17|18)\$/, list: [{ name: "Kerberos 5 TGS-REP (AES)", m: "19700", john: "krb5tgs" }] },
    { re: /^\$krb5asrep\$23\$/, list: [{ name: "Kerberos 5 AS-REP (RC4) — AS-REProast", m: "18200", john: "krb5asrep" }] },
    { re: /^\$krb5pa\$23\$/, list: [{ name: "Kerberos 5 AS-REQ Pre-Auth (RC4)", m: "7500", john: "krb5pa-md5" }] },
    { re: /^[^:]+::[^:]*:[a-f0-9]{16}:[a-f0-9]{32}:/i, list: [{ name: "NetNTLMv1", m: "5500", john: "netntlm" }] },
    { re: /^[^:]+::[^:]*:[a-f0-9]{16}:[a-f0-9]{32,}:[a-f0-9]+/i, list: [{ name: "NetNTLMv2", m: "5600", john: "netntlmv2" }] },
    { re: /^[a-f0-9]{32}:[a-f0-9]{32}$/i, list: [{ name: "NTLM PwDump (LM:NT)", m: "1000", john: "nt" }] },
    { re: /^[a-f0-9]{32}:[^:]+$/i, list: [{ name: "md5(salt) / md5($pass.$salt)", m: "10", john: "dynamic" }] },
    { re: /^\$sha1\$\d+\$/, list: [{ name: "Atlassian / PBKDF2-SHA1 variants", m: "12001", john: null }] },
    { re: /^SCRYPT:/i, list: [{ name: "scrypt", m: "8900", john: null }] },
    { re: /^eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\./, list: [{ name: "JWT (JSON Web Token)", m: "16500", john: null }] },
    { re: /^0x0100[a-f0-9]+$/i, list: [{ name: "MSSQL 2005+", m: "132", john: "mssql05" }] },
    { re: /^[a-f0-9]{130}$/i, list: [{ name: "Oracle 11g (SHA-1, H:)", m: "112", john: "oracle11" }] },
  ];

  function esc(s) { return String(s).replace(/[&<>]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]; }); }

  function render() {
    var h = input.value.trim();
    if (!h) { out.innerHTML = ""; return; }
    var matches = [];
    RULES.forEach(function (r) { if (r.re.test(h)) matches.push.apply(matches, r.list); });
    if (!matches.length) {
      out.innerHTML = '<p class="hint" style="margin:0">No confident match. Try CyberChef&rsquo;s <b>Analyse hash</b> (Open above), or check length/prefix.</p>';
      return;
    }
    var wl = passlist();
    var html = matches.map(function (c, i) {
      var mode = c.m != null
        ? '<div class="cmd plain" data-tpl="hashcat -m ' + esc(c.m) + ' hash.txt ' + esc(wl) + '" style="margin-bottom:6px"></div>'
        : '<p class="hint" style="margin:2px 0 6px">no hashcat mode (unsupported / mode varies)</p>';
      var jn = c.john
        ? '<div class="cmd plain" data-tpl="john --format=' + esc(c.john) + ' hash.txt --wordlist=' + esc(wl) + '" style="margin-bottom:0"></div>'
        : '';
      var badge = (i === 0) ? ' <span class="tag" style="color:#5fb3a1;border-color:#2f5a4f">most likely</span>' : '';
      return '<div class="card" style="margin:0 0 10px;background:var(--panel-2)">' +
             '<h3 style="margin:0 0 8px">' + esc(c.name) +
             (c.m != null ? ' <span class="tag">-m ' + esc(c.m) + '</span>' : '') + badge + '</h3>' +
             mode + jn + '</div>';
    }).join("");
    out.innerHTML = html;
    if (window.TN && TN.renderTpls) TN.renderTpls(out);  // wire copy buttons
  }

  input.addEventListener("input", render);
})();
