from contextlib import closing

from flask import current_app, Response, redirect, request
from pydantic import ValidationError
from sqlalchemy import text, Connection
from sqlalchemy.exc import IntegrityError, NoResultFound, MultipleResultsFound

from flaskr.db import get_db
from urls import urls_bp
from urls.models import UrlCreate, ShortPath
from urls.utils import short_path_generator


@urls_bp.route("/", methods=["POST"])
def create():
    """
    Endpoint creating a short path and linking it to a given url.
    ---
    parameters:
        - name: body
          in: body
          description: URL which will be shortened
          schema:
            type: object
            properties:
              url:
                type: string
                example: 'https://www.google.com'
    responses:
      201:
        description: The short path was created.
        schema:
            type: object
            properties:
                short_path:
                    type: string
                    example: 'A1b2C3d'
    """
    logger = current_app.logger
    body = request.get_json()
    try:
        url_create = UrlCreate(**body)
    except ValidationError as verr:
        return verr.json(), 400
    url = url_create.url

    def _create(dbconn: Connection) -> tuple[bool, str]:
        short_path = short_path_generator()
        try:
            ShortPath(short_path=short_path)
        except ValidationError as valerr:
            return False, valerr.json()
        try:
            dbconn.execute(insert_query, {"short_path": short_path, "url": url})
        except IntegrityError as integ_err:
            return False, str(integ_err)
        dbconn.commit()
        return True, short_path

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
        except MultipleResultsFound as mulres:
            logger.error(
                "Multiple valid results were found for %(url)s, reason: %(err)s"
                % {"url": url, "err": str(mulres)}
            )
            return {
                "message": "Cannot generate a short path for this URL currently"
            }, 400
        if existing_result:
            return {"short_path": existing_result}, 200
        insert_query = text(
            """
            INSERT INTO urls (short_path, url)
            VALUES (:short_path, :url)
            """
        )

        create_success = False
        output = ""
        fail_counter = 0
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
    return {"short_path": output}, 201


@urls_bp.route("/<string:short_path>", methods=["GET"])
def path(short_path: str):
    """
    Endpoint that redirects to a url linked to a given short path.
    ---
    parameters:
        - name: short_path
          in: path
          description: The short path that will redirect to its associated url
          schema:
            type: string
            example: 'A1b2C3d'
    responses:
      302:
        description: Redirection to the URL
    """
    logger = current_app.logger

    select_query = text(
        """
        SELECT url, clicks
        FROM urls
        WHERE short_path = :short_path
          AND (NOW()::date - created_at::date) < 90
        """
    )
    with closing(get_db()) as conn:
        try:
            url, clicks = conn.execute(select_query, {"short_path": short_path}).one()
        except NoResultFound as nores:
            logger.error(
                "No url could be found for short path %(short_path)s, reason: %(err)s"
                % {"short_path": short_path, "err": str(nores)}
            )
            return {"message": "Not found"}, 404
        except MultipleResultsFound as mulres:
            logger.error(
                "Multiple valid results were found for %(short_path)s, reason: %(err)s"
                % {"short_path": short_path, "err": str(mulres)}
            )
            return {"message": "There was an issue with the link"}, 400
        clicks += 1
        update_query = text(
            """
            UPDATE urls
            SET clicks = :clicks
            WHERE short_path = :short_path
            """
        )
        conn.execute(update_query, {"clicks": clicks, "short_path": short_path})
        conn.commit()
    return redirect(url, code=302)
