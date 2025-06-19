from flask import Flask, jsonify, render_template
from .routes.tts import tts_bp
from .routes.vc import vc_bp
from .routes.editing import editing_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(tts_bp, url_prefix="/api")
    app.register_blueprint(vc_bp, url_prefix="/api")
    app.register_blueprint(editing_bp, url_prefix="/api/edit")

    @app.get("/")
    def index():
        """Render a simple landing page."""

        return render_template("index.html")

    @app.get("/api")
    def api_root():
        """Return basic API information."""

        return jsonify({"message": "Chatterbox API", "endpoints": ["/api/tts", "/api/vc", "/api/edit"]})

    return app
