# rssBriefing a.k.a. RoboBriefing &#x1f916;

rssBriefing (recently "re-branded" RoboBriefing &#x1f916;) is a RSS/Atom fuelled fully automated daily briefing app,
powered by Natural Language Processing models ([gensim's LDA](https://radimrehurek.com/gensim/models/ldamodel.html), [Facebook's BART](https://github.com/pytorch/fairseq/tree/master/examples/bart).

Beta testing has started: https://rssbriefing.live

## TO DO (open bugs)
- handling of `python -m spacy download en` to obtain 'en_core_web_sm'
- `AttributeError 'dict' object has no attribute 'batch_encode_plus'` -> necessity to install transformers from source


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

Run the app in a Docker container, by default a temporary sqlite db will be initiated inside the container with
a database migration:
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

Finally open in browser:
```
0.0.0.0:5000/
```
