from logging.config import dictConfig

from flasgger import Swagger
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
    Swagger(app)
    db.init_app(app)
    import urls.views  # pylint: disable=unused-import,import-outside-toplevel

    app.register_blueprint(urls_bp, url_prefix="/urls")
    return app
