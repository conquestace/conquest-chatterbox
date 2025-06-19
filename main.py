"""Entrypoint for running the Flask web server.

This module exposes a ``webapp`` function which returns the Flask ``app``
instance. Having a callable named ``webapp`` is useful when deploying the
project on platforms that expect a factory function (e.g. gunicorn or certain
cloud providers).  The script can still be executed directly for local
development.
"""

from flask_app import create_app

try:
    import uvicorn  # type: ignore
except Exception:  # pragma: no cover - uvicorn optional
    uvicorn = None


app = create_app()


def webapp():
    """Return the Flask application instance."""

    return app


if __name__ == "__main__":
    # If the application object has a ``router`` attribute we are dealing with a
    # FastAPI/Starlette app (used when Gradio is enabled). In that case run with
    # ``uvicorn``. Otherwise fall back to Flask's built-in development server.
    if hasattr(app, "router") and uvicorn is not None:
        uvicorn.run(app, host="0.0.0.0", port=5000)
    else:
        app.run(debug=True)
