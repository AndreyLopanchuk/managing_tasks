FROM python:3.12

ENV PYTHONUNBUFFERED=1

WORKDIR /aiohttp_server

RUN pip install --upgrade pip 'poetry==1.8.3'
RUN poetry config virtualenvs.create false --local
COPY ../aiohttp_server/poetry.lock aiohttp_server/pyproject.toml ./
RUN poetry install
