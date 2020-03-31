FROM python:3.7-slim-buster

RUN useradd --create-home rssbriefing

WORKDIR /home/rssbriefing

COPY . .

RUN apt-get update -y && \
    apt-get install -y gcc python3-dev libpq-dev && \
    python -m pip install --no-cache-dir -r requirements.txt &&

RUN chmod +x entrypoint.sh
RUN chown -R rssbriefing:rssbriefing ./
USER rssbriefing

ENV FLASK_APP "application.py"

EXPOSE 5000

CMD ["./entrypoint.sh"]

