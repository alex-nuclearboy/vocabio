# syntax=docker/dockerfile:1

FROM python:3.13-slim-trixie AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app


FROM base AS builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1

RUN python -m pip install --no-cache-dir "poetry==2.4.1"

COPY pyproject.toml poetry.lock ./

RUN poetry sync \
    --only main \
    --no-root \
    --no-ansi

COPY . .

RUN DJANGO_SECRET_KEY=build-only-secret-key \
    DJANGO_DEBUG=True \
    DATABASE_URL=postgresql://vocabio:vocabio@localhost:5432/vocabio \
    .venv/bin/python manage.py collectstatic --noinput


FROM base AS runtime

ENV HOME=/home/vocabio \
    PATH="/app/.venv/bin:$PATH"

RUN groupadd --gid 10001 vocabio \
    && useradd \
        --uid 10001 \
        --gid 10001 \
        --create-home \
        --home-dir /home/vocabio \
        vocabio

COPY --from=builder --chown=vocabio:vocabio /app /app

USER vocabio

EXPOSE 8000

CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8000} config.wsgi:application"]
