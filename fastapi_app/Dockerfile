FROM python:3.12

ENV PYTHONUNBUFFERED=1

WORKDIR /fastapi_app

RUN pip install --upgrade pip 'poetry==1.8.3'
RUN poetry config virtualenvs.create false --local
COPY ../fastapi_app/poetry.lock fastapi_app/pyproject.toml ./
RUN poetry install
