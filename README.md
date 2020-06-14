# rssBriefing a.k.a. RoboBriefing &#x1f916;

RoboBriefing &#x1f916; (recently "re-branded" from previously: rssBriefing) is a RSS/Atom fuelled fully automated daily news briefing app,
powered by Natural Language Processing models ([gensim's LDA](https://radimrehurek.com/gensim/models/ldamodel.html), [Facebook's BART](https://github.com/pytorch/fairseq/tree/master/examples/bart)).

Beta testing has started: https://rssbriefing.live

## TO DO
- improve handling of `python -m spacy download en` to download spaCy English language library 'en_core_web_sm'
- due to [transformers](https://github.com/huggingface/transformers) Issue [#4504](https://github.com/huggingface/transformers/issues/4504) -> current necessity to install `transformers` from source
- add standard bash scripts to run the full briefing generation pipeline:
    - `python -m rssbriefing.scripts.update_all_feeds`
    - `python -m rssbriefing.briefing_model.briefing`
    - `python -m rssbriefing.scripts.send_briefing_emails`


## How to run with pyenv virtualenv
Having [`pyenv`](https://github.com/pyenv/pyenv) installed, clone the repo and `cd` into the directory:
```
git clone https://github.com/grbtm/rssBriefing.git
cd rssBriefing
```
Then create a virtual environment with `pyenv` specifying python version 3.7.4 (if necessary first install:
`pyenv install 3.7.4`), activate it and install requirements:
```
pyenv virtualenv 3.7.4 <environment_name>
pyenv activate  <environment_name>
pip install -r requirements.txt
```
Please follow current `TODO` instructions to manually download the spaCy English language model and
install [transformers](https://github.com/huggingface/transformers) from source:
```
python -m spacy download en
cd ..
git clone https://github.com/huggingface/transformers
cd transformers
pip install .
```
Run the flask app in development mode:
```
cd rssBriefing
flask run
```
When done:
```
pyenv deactivate
```

## How to run with Docker
[Docker instructions haven't been updated yet with the notes in `TODO`]

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
