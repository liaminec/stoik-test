from contextlib import closing

from flask import current_app, Response, redirect
from flask_pydantic import validate
from pydantic import ValidationError
from sqlalchemy import text, Connection, TextClause
from sqlalchemy.exc import IntegrityError, NoResultFound

from flaskr.db import get_db
from urls import urls_bp
from urls.models import UrlCreate, ShortPath
from urls.utils import short_path_generator


def _create(dbconn: Connection, insert_query: TextClause, url: str) -> tuple[bool, str]:
    short_path = short_path_generator()
    try:
        ShortPath(short_path=short_path)
    except ValidationError as valerr:
        return False, str(valerr)
    try:
        dbconn.execute(insert_query, {"short_path": short_path, "url": url})
    except IntegrityError as integ_err:
        return False, str(integ_err)
    dbconn.commit()
    return True, short_path


@urls_bp.route("/", methods=["POST"])
@validate()
def create(body: UrlCreate):
    logger = current_app.logger

    url = body.url
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
            existing_result = conn.execute(check_query, {"url": url}).scalar_one()
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

    create_success = False
    output = ""
    fail_counter = 0
    with closing(get_db()) as conn:
        while not create_success and fail_counter <= 3:
            create_success, output = _create(conn, insert_query, url)
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


@urls_bp.route("/<string:short_path>", methods=["GET"])
def path(short_path: str):
    logger = current_app.logger

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
            url, clicks = conn.execute(
                select_query, {"short_path": short_path}
            ).scalar_one()
    except NoResultFound as nores:
        logger.warning(
            "No url could be found for short path %(short_path)s, reason: %(err)s"
            % {"short_path": short_path, "err": str(nores)}
        )
        return {"message": "Not found"}, 404
    clicks += 1
    update_query = text(
        """
        UPDATE urls
        SET clicks = :clicks
        WHERE short_path = :short_path
        """
    )
    with closing(get_db()) as conn:
        conn.execute(update_query, {"clicks": clicks, "short_path": short_path})
        conn.commit()
    return redirect(url, code=302)
