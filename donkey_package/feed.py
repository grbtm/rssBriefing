import calendar
from datetime import datetime

import feedparser

from donkey_package.db import get_db


def parse_feed(href):
    feed_dict = feedparser.parse(href)
    return feed_dict


def well_formed(feed_dict):
    if feed_dict.bozo:
        result = False
    else:
        result = True
    return result


def get_feed_id(feed_dict):
    title = feed_dict.feed.title

    db = get_db()
    db_id = db.execute(
        'SELECT id from feed WHERE title = ?', (title,)
    ).fetchone()[0]
    return db_id


def datetime_from_time_struct(time_struct_time):
    # convert struct time to unix timestamp
    ts = calendar.timegm(time_struct_time)
    # then create datetime object in UTC
    dt = datetime.utcfromtimestamp(ts)
    return dt


def update_feed_db(feed_dict):
    # Get latest feed items
    entries = feed_dict.entries

    # Set up db connection
    db = get_db()

    # Insert new entries to db
    for entry in entries:
        feed_id = get_feed_id(feed_dict)
        if entry.get('title') and entry.title:  # ensure that attribute exists and is not empty string
            title = entry.title
        if entry.get('description') and entry.description:
            description = entry.description
        link = entry.link
        if entry.get('published_parsed'):
            created = datetime_from_time_struct(entry.published_parsed)
        else:
            created = datetime.now()

        db.execute(
            'INSERT INTO item (feed_id, title, description, link, created)'
            ' VALUES (?, ?, ?, ?, ?)',
            (feed_id, title, description, link, created)
        )

    db.commit()
