from logging.config import dictConfig

from flask import Flask
from flaskr import db
from urls import urls_bp

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)


def create_app() -> Flask:
    app = Flask("app")
    db.init_app(app)
    app.register_blueprint(urls_bp)
    return app
