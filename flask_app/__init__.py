from flask import Flask, jsonify
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
        """Simple landing page for the API."""

        return jsonify({"message": "Chatterbox API", "endpoints": ["/api/tts", "/api/vc", "/api/edit"]})

    return app
