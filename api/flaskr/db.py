import os

import click
from flask import g, current_app, Flask
from sqlalchemy import create_engine, Connection, Row, text


def get_db() -> Connection:
    if "db" in g:
        return g.db
    engine = create_engine(os.getenv("DB_URL"))
    db_conn = engine.connect()
    g.db = db_conn
    g.db.row_factory = Row
    return g.db


def close_db(e=None) -> None:  # pylint: disable=unused-argument
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("flaskr/schema.sql") as f:
        db.execute(text(f.read().decode("utf8")))
        db.commit()


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Database initialized.")


def init_app(app: Flask):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
