import os

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from urls import urls_bp


@pytest.fixture(name="app")
def app_fixture():
    app = Flask(__name__)
    db = SQLAlchemy()
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URL")
    db.init_app(app)
    app.register_blueprint(urls_bp)
    app.config.update({"TESTING": True})

    yield app

    conn = db.engine.connect()
    conn.execute("DELETE FROM urls")
    conn.commit()
    conn.close()


@pytest.fixture()
def client(app):
    return app.test_client()
