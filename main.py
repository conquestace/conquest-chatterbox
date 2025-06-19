"""Entrypoint for running the Flask web server.

This module exposes a ``webapp`` function which returns the Flask ``app``
instance. Having a callable named ``webapp`` is useful when deploying the
project on platforms that expect a factory function (e.g. gunicorn or certain
cloud providers).  The script can still be executed directly for local
development.
"""

from flask_app import create_app

app = create_app()


def webapp():
    """Return the Flask application instance."""

    return app


if __name__ == "__main__":
    app.run(debug=True)
