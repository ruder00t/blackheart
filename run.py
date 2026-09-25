"""Start Blackheart on 127.0.0.1:8090 (localhost only, offline)."""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8090, debug=False)
