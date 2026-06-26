import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

load_dotenv()

from backend.routes import api_bp
from backend.serve import frontend_bp

app = Flask(__name__, static_folder="frontend/static", template_folder="frontend/templates")
CORS(app)

app.register_blueprint(api_bp, url_prefix="/api")
app.register_blueprint(frontend_bp)

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    print(f"\n  NTT DATA AI Presentation Generator")
    print(f"  Running on http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
