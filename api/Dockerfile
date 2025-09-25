FROM python:3.10
ARG PROJECT_NAME="stoik-test"
ENV PYTHONBUFFERED=1

USER root

ENV PATH="/root/.local/bin:/root/.poetry/bin:$PATH"
RUN pip install poetry

WORKDIR /home/app/
COPY . .
RUN poetry config virtualenvs.create false
RUN poetry install --no-root
