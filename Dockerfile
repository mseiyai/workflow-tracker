FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --create-home --shell /usr/sbin/nologin app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --requirement requirements.txt

COPY --chown=app:app backend/ backend/
COPY --chown=app:app migrations/ migrations/
COPY --chown=app:app data/ data/
COPY --chown=app:app alembic.ini ./
COPY --chown=app:app --chmod=755 docker/api-entrypoint.sh /usr/local/bin/api-entrypoint.sh

USER app

EXPOSE 8000

ENTRYPOINT ["api-entrypoint.sh"]
CMD ["fastapi", "run", "backend/app.py", "--host", "0.0.0.0", "--port", "8000"]
