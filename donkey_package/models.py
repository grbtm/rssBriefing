from datetime import datetime

from donkey_package import db

user_feed = db.Table('user_feed',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                     db.Column('feed_id', db.Integer, db.ForeignKey('feed.id'), primary_key=True)
                     )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    feeds = db.relationship('Feed', secondary=user_feed, lazy='subquery',
                            backref=db.backref('users', lazy=True))

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), index=True, unique=True)
    description = db.Column(db.String())
    link = db.Column(db.String())
    href = db.Column(db.String())

    def __repr__(self):
        return '<Feed {}>'.format(self.title)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), index=True)
    description = db.Column(db.String())
    link = db.Column(db.String())
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    guid = db.Column(db.String())
    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'), nullable=False)
