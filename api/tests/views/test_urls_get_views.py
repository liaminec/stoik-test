# pylint: disable=unused-argument
from contextlib import closing

from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import text

from flaskr.db import get_db, close_db


def test_get(app: Flask, client: FlaskClient) -> None:
    close_db()
    with closing(get_db()) as conn:
        conn.execute(
            text(
                """
                INSERT INTO urls (url, short_path, clicks, created_at)
                VALUES ('https://www.google.com', 'A1b2C3d', 3, NOW())
                """
            )
        )
        conn.commit()
        response = client.get("/urls/A1b2C3d")
        assert response.status_code == 302
    close_db()
    with closing(get_db()) as conn:
        clicks = conn.execute(
            text(
                """
                SELECT clicks
                FROM urls
                WHERE short_path = 'A1b2C3d'
                """
            )
        ).scalar_one()
    assert clicks == 4


def test_get_not_found(app: Flask, client: FlaskClient) -> None:
    close_db()
    with closing(get_db()) as conn:
        conn.execute(
            text(
                """
                INSERT INTO urls (url, short_path, clicks, created_at)
                VALUES ('https://www.google.com', 'A1b2C3d', 3, '2025-01-01')
                """
            )
        )
        conn.commit()
        response = client.get("/urls/E1f2G3h", follow_redirects=True)
    assert response.status_code == 404
    assert response.json["message"] == "Not found"


def test_get_outdated(app: Flask, client: FlaskClient) -> None:
    close_db()
    with closing(get_db()) as conn:
        conn.execute(
            text(
                """
                INSERT INTO urls (url, short_path, clicks, created_at)
                VALUES ('https://www.google.com', 'A1b2C3d', 3, '2024-01-01')
                """
            )
        )
        conn.commit()
        response = client.get("/urls/A1b2C3d", follow_redirects=True)
        assert response.status_code == 404
    close_db()
    with closing(get_db()) as conn:
        clicks = conn.execute(
            text(
                """
                SELECT clicks
                FROM urls
                WHERE short_path = 'A1b2C3d'
                """
            )
        ).scalar_one()
    assert clicks == 3
