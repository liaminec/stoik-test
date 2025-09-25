from contextlib import closing
from typing import Generator, Any

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import text

from flaskr import create_app
from flaskr.db import get_db, close_db


@pytest.fixture(name="app", scope="session")
def app_fixture() -> Generator[Flask, Any, None]:
    app = create_app()
    app.config.update({"TESTING": True})

    yield app


@pytest.fixture()
def client(app) -> FlaskClient:
    return app.test_client()


@pytest.fixture(autouse=True)
def invalidated_conn(app: Flask) -> Generator[None, Any, None]:
    with app.app_context():
        yield


@pytest.fixture(autouse=True)
def clear_db(app: Flask) -> Generator[None, Any, None]:
    with app.app_context():
        close_db()
        with closing(get_db()) as conn:
            conn.execute(text("DELETE FROM urls"))
            conn.commit()
        yield
        close_db()
        with closing(get_db()) as conn:
            conn.execute(text("DELETE FROM urls"))
            conn.commit()
