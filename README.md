# rssBriefing a.k.a. RoboBriefing &#x1f916;

RoboBriefing &#x1f916; (recently "re-branded" from previously: rssBriefing) is a RSS/Atom fuelled fully automated daily news briefing app,
powered by Natural Language Processing models ([gensim's LDA](https://radimrehurek.com/gensim/models/ldamodel.html), [Facebook's BART](https://github.com/pytorch/fairseq/tree/master/examples/bart)).

Beta testing has started: https://rssbriefing.live

## Briefing generation pipeline with [LDA](https://radimrehurek.com/gensim/models/ldamodel.html) and [BART](https://github.com/pytorch/fairseq/tree/master/examples/bart)
![Briefing generation outline](https://rssbriefing.live/static/the_figure.png)


## Current setup
RoboBriefing currently consists of
- a Flask app with a basic RSS reader, where users can create profiles and follow RSS/Atom feeds
  (The RSS reader functionality will be removed in the future, it's database ORM is currently used to manage feeds and users.
  The Docker deployment therefore creates a seed user and a standard set of feeds when initializing the database)
- the briefing generation models (topic modeling, scraping, summarization) which are using the RSS feeds from the seed user
- a Briefing page which fetches the latest briefing from DB and displays it in the Flask app (no need to be logged in to view)
- a Django email backend (since flask-mail is not maintained anymore) to send out the briefing to users


## Requirements
Consider that the default summarization model [`bart-large-cnn`](https://github.com/pytorch/fairseq/tree/master/examples/bart),
which is downloaded via the `transformers` library, is about 3.5GB as a tar.gz file.

## TO DO
- add standard bash scripts to run the full briefing generation pipeline:
    - `python -m rssbriefing.scripts.update_all_feeds`
    - `python -m rssbriefing.briefing_model.briefing`
    - `python -m rssbriefing.scripts.send_briefing_emails`


## How to run with a Dockerfile

Clone the repo and `cd` into the directory:
```
git clone https://github.com/grbtm/rssBriefing.git
cd rssBriefing
```

Build a Docker image from the Dockerfile:
```
docker build -t rssbriefing .
```

To customize your container create an `.env` file in the repository root directory before calling `docker run`:
```
# set CUDA devide id (>=0) to use GPU
CUDA_DEVICE_ID=0

# setting secret keys
export SECRET_FLASK_KEY='set_your_secret_key'

# add URL to your database
export DATABASE_URL=""

# set Flask environment: development or production (default)
export FLASK_ENV="development"

# choose App configs: config.DevelopmentConfig or config.ProductionConfig
export APP_SETTINGS=""

# choose custom values for seed user
export SEED_USER = ""
export SEED_PASSWORD = ""
export SEED_EMAIL = ""

# set credentials for email backend
export EMAIL_HOST=""
export EMAIL_PORT=""
export EMAIL_HOST_USER=""
export EMAIL_HOST_PASSWORD=""
```

Run the app in a Docker container, by default a temporary sqlite db will be initiated inside the container with
a database migration and a seed user with a standard set of news feeds will be populated:
```
docker run -e DB_UPGRADE=1 -e DB_SEED=1 -p 5000:5000 rssbriefing
```

Alternatively: to run with GPU, assuming that you have set up
[Docker instructions to access an NVIDIA GPU](https://docs.docker.com/config/containers/resource_constraints/#gpu):
```
docker run --gpus -e DB_UPGRADE=1 -e DB_SEED=1 -p 5000:5000 rssbriefing
```

Kick off the briefing generation modules in the Docker container (find out name of running container with `docker ps`),
by running one command after the other to fetch the latest feed posts and run the briefing model (with arg `-u 1`
for the seed user):
```
docker exec -it <name of your container> python -m rssbriefing.scripts.update_all_feeds
docker exec -it <name of your container> python -m rssbriefing.briefing_model.briefing -u 1
```

Finally open in browser and view the briefing:
```
0.0.0.0:5000/
```


## How to run with pyenv virtualenv
Note: pyenv instructions are not up to date, the Dockerfile based instructions are

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
