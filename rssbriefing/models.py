from datetime import datetime
from time import time
import jwt
import click

from flask.cli import with_appcontext
from flask import current_app as app
from werkzeug.security import generate_password_hash
from rssbriefing import db


seed_feeds = [
    {"title": "BBC News - Home", "href": "http://feeds.bbci.co.uk/news/rss.xml"},
    {"title": "NYT > Top Stories", "href": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"},
    {"title": "NYT > World News", "href": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"},
    {"title": "NYT > Business > Economy", "href": "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml"},
    {"title": "Reuters: Top News", "href": "http://feeds.reuters.com/reuters/topNews"},
    {"title": "Reuters: Business News", "href": "http://feeds.reuters.com/reuters/businessNews"},
    {"title": "International homepage", "href": "https://www.ft.com/?format=rss"},
    {"title": "Fortune", "href": "https://fortune.com/feed"},
    {"title": "Top News and Analysis (pro)", "href": "http://www.cnbc.com/id/19746125/device/rss/rss.xml"},
    {"title": "U.S. News", "href": "https://www.cnbc.com/id/15837362/device/rss/rss.html"},
    {"title": "WSJ.com: World News", "href": "https://feeds.a.dj.com/rss/RSSWorldNews.xml"},
    {"title": "Economy", "href": "https://rss.politico.com/economy.xml"},
    {"title": "Al Jazeera English", "href": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"title": "CNN.com - RSS Channel - Politics", "href": "http://rss.cnn.com/rss/cnn_allpolitics.rss"},
    {"title": "International", "href": "https://www.economist.com/international/rss.xml"},
    {"title": "Business", "href": "https://www.economist.com/business/rss.xml"},
    {"title": "Bloomberg Politics", "href": "https://feeds.bloomberg.com/politics/news.rss"},
    {"title": "Bloomberg.com", "href": "https://feeds.bloomberg.com/business/news.rss"},
    {"title": "World & Nation", "href": "https://www.latimes.com/world-nation/rss2.0.xml"},
    {"title": "World", "href": "http://feeds.washingtonpost.com/rss/world"},
    {"title": "DER SPIEGEL - International", "href": "https://www.spiegel.de/international/index.rss"},
    {"title": "CBC | World News", "href": "https://rss.cbc.ca/lineup/world.xml"},
    {"title": "The Independent - World", "href": "https://www.independent.co.uk/news/world/rss"},
    {"title": "World News - Breaking News, Top Stories", "href": "https://www.huffpost.com/section/world-news/feed"},
    {"title": "Deutsche Welle", "href": "https://rss.dw.com/atom/rss-en-all"},
    {"title": "The Globe and Mail - World", "href": "https://theglobeandmail.com/rss/section/world/"}

]


user_feed = db.Table('user_feed',
                     db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                     db.Column('feed_id', db.Integer, db.ForeignKey('feed.id'), primary_key=True)
                     )


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    feeds = db.relationship('Feed', secondary=user_feed, lazy='subquery', backref=db.backref('users', lazy=True))
    briefing_items = db.relationship('Briefing', lazy=True, backref=db.backref('user', lazy='joined'))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return Users.query.get(id)


class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), index=True, unique=True)
    description = db.Column(db.String())
    link = db.Column(db.String())
    href = db.Column(db.String())
    items = db.relationship('Item', lazy=True, backref=db.backref('feed', lazy='joined'))
    briefing_items = db.relationship('Briefing', lazy=True, backref=db.backref('feed', lazy='joined'))

    def __repr__(self):
        return '<Feed {}>'.format(self.title)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), index=True, nullable=False)
    description = db.Column(db.String())
    link = db.Column(db.String(), nullable=False)
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    guid = db.Column(db.String())
    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'), nullable=False)

    def __repr__(self):
        return '<Feed {}, Item {}>'.format(self.feed_id, self.title)


class Briefing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), index=True, nullable=False)
    description = db.Column(db.String())
    summary = db.Column(db.String())
    link = db.Column(db.String(), nullable=False)
    reference = db.Column(db.String())
    score = db.Column(db.Float())
    created = db.Column(db.DateTime)
    briefing_created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    guid = db.Column(db.String())

    feed_title = db.Column(db.String(), db.ForeignKey('feed.title'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return '<Briefing item title {}, feed title {}, user {}>'.format(self.title, self.feed_title, self.user_id)


@click.command('seed-db')
@with_appcontext
def seed_db_command():
    """ Initialize database with seed values of a minimum set of RSS/Atom feeds needed for briefing generation. """

    new_user = Users(username=app.config["SEED_USER"],
                     email=app.config["SEED_EMAIL"],
                     password_hash=generate_password_hash(app.config["SEED_PASSWORD"]))
    db.session.add(new_user)
    db.session.commit()

    seed_user = Users.query.get(1)

    for feed in seed_feeds:
        feed_entry = Feed(title=feed["title"], href=feed["href"])
        seed_user.feeds.append(feed_entry)

    db.session.commit()
    click.echo('Initialized the database with seed user and feeds.')
