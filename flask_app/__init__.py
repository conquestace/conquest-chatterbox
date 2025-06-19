from flask import Flask
from .routes.tts import tts_bp
from .routes.vc import vc_bp
from .routes.editing import editing_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(tts_bp, url_prefix="/api")
    app.register_blueprint(vc_bp, url_prefix="/api")
    app.register_blueprint(editing_bp, url_prefix="/api/edit")
    return app
