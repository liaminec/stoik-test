# pylint: disable=unused-argument, duplicate-code
from contextlib import closing
from datetime import datetime

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import text
from sqlalchemy.exc import NoResultFound

from flaskr.db import get_db, close_db


def test_create(app: Flask, client: FlaskClient) -> None:
    response = client.post("/urls/", json={"url": "https://google.com"})
    assert response.status_code == 201
    short_path = response.json.get("short_path")
    assert len(short_path) == 7
    assert short_path.isalnum()
    close_db()
    with closing(get_db()) as conn:
        url, clicks = conn.execute(
            text(
                """
                SELECT url, clicks
                FROM urls
                WHERE short_path = :short_path
                """
            ),
            {"short_path": short_path},
        ).one()
    assert url == "https://google.com"
    assert clicks == 0


def test_create_malformed_url(app: Flask, client: FlaskClient) -> None:
    close_db()
    response = client.post("/urls/", json={"url": "google"})
    assert response.status_code == 400
    with pytest.raises(NoResultFound):
        close_db()
        with closing(get_db()) as conn:
            conn.execute(
                text(
                    """
                    SELECT url, short_path, created_at, clicks
                    FROM urls
                    WHERE url = :url
                    """
                ),
                {"url": "google"},
            ).one()


def test_create_url_exists(app: Flask, client: FlaskClient) -> None:
    close_db()
    with closing(get_db()) as conn:
        conn.execute(
            text(
                """
                INSERT INTO urls (url, short_path, created_at, clicks)
                VALUES ('https://google.com', 'A1b2C3d', NOW(), 3)
                """
            )
        )
        conn.commit()
        response = client.post("/urls/", json={"url": "https://google.com"})
    assert response.status_code == 200
    short_path = response.json.get("short_path")
    assert short_path == "A1b2C3d"


def test_create_url_exists_but_outdated(app: Flask, client: FlaskClient) -> None:
    close_db()
    with closing(get_db()) as conn:
        conn.execute(
            text(
                """
                INSERT INTO urls (url, short_path, created_at, clicks)
                VALUES ('https://google', 'A1b2C3d', '2024-01-01', 3)
                """
            )
        )
        conn.commit()
        response = client.post("/urls/", json={"url": "https://google.com"})
        assert response.status_code == 201
        short_path = response.json.get("short_path")
        assert len(short_path) == 7
        assert short_path.isalnum()
        assert short_path != "A1b2C3d"
    close_db()
    with closing(get_db()) as conn:
        url, short_path, created_at, clicks = conn.execute(
            text(
                """
                SELECT url, short_path, created_at, clicks
                FROM urls
                WHERE short_path = :short_path
                AND (NOW()::date - created_at::date) < 90
                """
            ),
            {"short_path": short_path},
        ).one()
    assert url == "https://google.com"
    assert clicks == 0
    assert created_at > datetime(2024, 1, 1)
