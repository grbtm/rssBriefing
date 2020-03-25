FROM python:3.7.4-slim

ENV FLASK_APP "application.py"
ENV FLASK_ENV "development"
ENV FLASK_DEBUG True
ENV APP_SETTINGS "config.DevelopmentConfig"
ENV BETA_CODE "test"

WORKDIR /

COPY . .

RUN apt-get update -y && \
    apt-get install -y gcc python3-dev libpq-dev && \
    python -m pip install --no-cache-dir -r requirements.txt && \
    flask db upgrade

EXPOSE 5000

ENTRYPOINT ["python"]

CMD ["application.py"]

