FROM python:3.13.2-alpine

WORKDIR /app

RUN addgroup -S linktiles && adduser -S linktiles -G linktiles
USER linktiles

COPY --chown=linktiles:linktiles requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

COPY --chown=linktiles:linktiles app /app/app

ENV GUNICORN_WORKERS=2

ENTRYPOINT ["sh", "-c", "python -m gunicorn -w ${GUNICORN_WORKERS} -b 0.0.0.0:${LT_SERVER_PORT:-5001} app:linktiles"]
