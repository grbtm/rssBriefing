from datetime import datetime

from rssbriefing_package import db

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
