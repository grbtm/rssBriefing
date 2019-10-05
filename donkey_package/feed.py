import feedparser

from donkey_package.db import get_db


def parse_feed(href):
    feed_dict = feedparser.parse(href)
    return feed_dict


def get_feed_id(feed_dict):
    title = feed_dict.feed.title

    db = get_db()
    db_id = db.execute(
        'SELECT id from feed WHERE title = ?', (title,)
    ).fetchone()[0]
    return db_id


def update_feed_db(feed_dict):
    # Get latest feed items
    entries = feed_dict.entries

    # Set up db connection
    db = get_db()

    # Insert new entries to db
    for entry in entries:
        feed_id = get_feed_id(feed_dict)
        title = entry.title
        description = entry.description if entry.description else 'No description'
        link = entry.link

        db.execute(
            'INSERT INTO item (feed_id, title, description, link)'
            ' VALUES (?, ?, ?, ?)',
            (feed_id, title, description, link)
        )

    db.commit()
