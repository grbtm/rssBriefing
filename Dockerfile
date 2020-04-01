# Use slim version of python 3.7 based on stable Debian Buster
FROM python:3.7-slim-buster

# Create non-root user
RUN useradd --create-home rssbriefing

# Set home as working directory
WORKDIR /home/rssbriefing

# Copy all files from current workdir to workdir in container
COPY . .

# Run installations
RUN apt-get update -y && \
    apt-get install -y gcc python3-dev libpq-dev && \
    python -m pip install --no-cache-dir -r requirements.txt && \
    python -m pip install --no-cache-dir gunicorn

# Use the created user when running the image and adapt ownership
RUN chmod +x entrypoint.sh
RUN chown -R rssbriefing:rssbriefing ./
USER rssbriefing

# Set Flask app variable before calling the app
ENV FLASK_APP "application.py"

# Expose Flask's default port
EXPOSE 5000

# Run app from shell script with option to trigger db upgrade if env var is given
CMD ["./entrypoint.sh"]

