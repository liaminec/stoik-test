# stoik-test


This project is a ground base for a URL shortening API.

The API is fairly simple, post a url, and it will return a short path to make it a shortened URL.

## 1. Project Structure

````
|
|_api/
|  |_flaskr/ // app and DB init
|  |  |_db.py  // DB init and app association commands
|  |  |_schemas.sql  // DB creation SQL script
|  |_urls/  // routes related to URLs shortening
|  |_tests/  // unit tests
|  |_app.py  // app main script
|  |_.pre-commit-config.yaml
|_pylintrc  // pylint config
````

The API was made using Flask for the web part.

The database used is PostgreSQL, and we're using SQLAlchemy as a DB toolkit to allow the API to communicate with the DB.

The dependencies are managed using poetry, there is pre-commit to ensure some degree of code quality and the app is
dockerized to make the launch easy.


## 1. Launching the project

Prerequisites: Docker and Docker Compose V2

To launch the app

```
docker-compose --profile local build
docker-compose --profile local up
```

Coming soon: Swagger (waiting for Docker to be fixed)

To launch the tests

```
docker-compose --profile test build
docker-compose --profile test up
```


## 2. Swagger

A swagger was generated using the flaggser package,
to see it go to
``localhost:5000/apidocs``
