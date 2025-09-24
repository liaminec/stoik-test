from contextlib import closing

from flask import current_app, Response, redirect
from flask_pydantic import validate
from pydantic import ValidationError
from sqlalchemy import text, Connection
from sqlalchemy.exc import IntegrityError, NoResultFound

from flaskr.db import get_db
from urls import urls_bp
from urls.models import UrlCreate, ShortPath
from urls.utils import short_path_generator

logger = current_app.logger


@urls_bp.post("/")
@validate()
def create(data: UrlCreate):
    url = data.link
    check_query = text(
        """
        SELECT short_path
        FROM urls
        WHERE url = :url
        AND (NOW()::date - created_at::date) < 90
        """
    )
    existing_result = ""
    with closing(get_db()) as conn:
        try:
            existing_result = conn.engine.execute(
                check_query, {"url": url}
            ).scalar_one()
        except NoResultFound:
            logger.info("No short path exists for the url %s", url)
    if existing_result:
        return Response({"short_path": existing_result}, status=200)
    insert_query = text(
        """
        INSERT INTO urls (short_path, url)
        VALUES (:short_path, :url)
        """
    )

    def _create(dbconn: Connection) -> tuple[bool, str]:
        short_path = short_path_generator()
        try:
            ShortPath(short_path=short_path)
        except ValidationError as valerr:
            return False, str(valerr)
        try:
            dbconn.engine.execute(insert_query, {"short_path": short_path, "url": url})
        except IntegrityError as integ_err:
            return False, str(integ_err)
        return True, short_path

    create_success = False
    output = ""
    fail_counter = 0
    with closing(get_db()) as conn:
        while not create_success and fail_counter <= 3:
            create_success, output = _create(conn)
            logger.warning("Could not generate short URL, cause: %s", output)
            fail_counter += 1
    if not create_success:
        logger.error("Short URL for %s could not be generated", url)
        return Response(
            {"message": "The short URL could not be generated, please try again later"},
            status=400,
        )
    logger.info("Short URL for %s successfully generated", url)
    return Response({"short_path": output}, status=201)


@urls_bp.get("/<str: short_path>")
def path(short_path: str):
    select_query = text(
        """
        SELECT url, clicks
        FROM urls
        WHERE short_path = :short_path
        AND (NOW()::date - created_at::date) < 90
        """
    )
    try:
        with closing(get_db()) as conn:
            url, clicks = conn.engine.execute(
                select_query, {"short_path": short_path}
            ).scalar_one()
    except NoResultFound as nores:
        logger.warning(
            "No url could be found for short path %(short_path)s, reason: %(err)s"
            % {"short_path": short_path, "err": str(nores)}
        )
        return Response({"message": "Not found"}, status=404)
    clicks += 1
    update_query = text(
        """
        UPDATE urls
        SET clicks = :clicks
        WHERE short_path = :short_path
        """
    )
    with closing(get_db()) as conn:
        conn.engine.execute(update_query, {"clicks": clicks, "short_path": short_path})
    return redirect(url, code=302)
