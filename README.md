# rssBriefing

rssBriefing is a RSS/Atom fuelled daily briefing app built with Flask, Bootstrap and Natural Language Processing models
from gensim.

Beta testing has started: https://rssbriefing.eu-central-1.elasticbeanstalk.com/


## How to run with Docker

Clone the repo and `cd` into the directory:
```
git clone https://github.com/grbtm/rssBriefing.git
cd rssBriefing
```

Build a Docker image from the Dockerfile:
```
docker build -t rssbriefing .
```

Run the app in a Docker container, by default a sqlite db will be initiated with
a database migration
```
docker run -e DB_UPGRADE=1 -p 5000:5000 rssbriefing
```
to customize your container create an `.env` file in the repository root directory before calling `docker run`:
```
# setting secret keys
export SECRET_FLASK_KEY='set_your_secret_key'

# add URL to your database
export DATABASE_URL=""

# set Flask environment: development or production (default)
export FLASK_ENV="development"

# choose App configs: config.DevelopmentConfig or config.ProductionConfig
export APP_SETTINGS=""

# set a code for the registration process
export BETA_CODE="test"
```
