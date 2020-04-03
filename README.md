# rssBriefing

rssBriefing is a RSS/Atom fuelled daily briefing app built with Flask, Bootstrap and Natural Language Processing models
from gensim.

Beta testing has started: https://rssbriefing.eu-central-1.elasticbeanstalk.com/


## How to run

```
git clone https://github.com/grbtm/rssBriefing.git
cd rssBriefing
docker build -t rssbriefing .
docker run -e DB_UPGRADE=1 -p 5000:5000 rssbriefing
```
