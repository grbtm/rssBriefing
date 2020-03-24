FROM python:3.7.4-slim

WORKDIR /

COPY . .

RUN apt-get update -y && \
    apt-get install -y gcc python3-dev libpq-dev && \
    python -m pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python"]

CMD ["application.py"]

