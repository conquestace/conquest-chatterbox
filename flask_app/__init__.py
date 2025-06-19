from flask import Flask, jsonify, render_template
from .routes.tts import tts_bp
from .routes.vc import vc_bp
from .routes.editing import editing_bp

# Optional imports for mounting the Gradio demo. The gradio demo is an ASGI
# application, so if it's available we later wrap the Flask app with FastAPI
# and Starlette's WSGIMiddleware to serve everything from a single ASGI app.

try:  # Optional Gradio integration
    from gradio import mount_gradio_app
    from main_gradio import demo as gradio_demo
except Exception:  # pragma: no cover - gradio optional
    mount_gradio_app = None
    gradio_demo = None


def create_app():
    """Create and return the web application.

    If the optional Gradio dependencies are installed, this function returns a
    FastAPI application that serves both the Flask routes and the Gradio demo.
    Otherwise, a plain Flask application is returned.
    """

    flask_app = Flask(__name__)
    flask_app.register_blueprint(tts_bp, url_prefix="/api")
    flask_app.register_blueprint(vc_bp, url_prefix="/api")
    flask_app.register_blueprint(editing_bp, url_prefix="/api/edit")

    @flask_app.get("/")
    def index():
        """Render a simple landing page."""

        return render_template("index.html")

    @flask_app.get("/api")
    def api_root():
        """Return basic API information."""

        return jsonify(
            {"message": "Chatterbox API", "endpoints": ["/api/tts", "/api/vc", "/api/edit"]}
        )

    # If gradio is installed, wrap the Flask app with FastAPI so we can mount the
    # gradio demo under the /gradio endpoint. Otherwise just return the Flask app
    # directly.
    if mount_gradio_app and gradio_demo:  # pragma: no cover - optional
        from fastapi import FastAPI
        from starlette.middleware.wsgi import WSGIMiddleware

        fastapi_app = FastAPI()
        # Mount the Flask application at the root.
        fastapi_app.mount("/", WSGIMiddleware(flask_app))
        # Mount the gradio demo at /gradio.
        mount_gradio_app(fastapi_app, gradio_demo, path="/gradio")
        return fastapi_app

    return flask_app
