import calendar
from datetime import datetime

import feedparser

from donkey_package.db import get_db


def parse_feed(href):
    feed_dict = feedparser.parse(href)
    return feed_dict


def well_formed(feed_dict):
    # consider a feed malformed if 1. feedparser bozo attribute declares an error (value: 1) and 2. no entry list loaded
    if feed_dict.bozo and len(feed_dict.entries) is 0:
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


def get_latest_feed_dict(feed_id):
    db = get_db()
    feed_href = db.execute(
        'SELECT href from feed WHERE id = ?', (feed_id,)
    ).fetchone()[0]
    return parse_feed(feed_href)


def datetime_from_time_struct(time_struct_time):
    # convert struct time to unix timestamp
    ts = calendar.timegm(time_struct_time)
    # then create datetime object in UTC
    dt = datetime.utcfromtimestamp(ts)
    return dt


def parse_entry_attribute(entry, attribute):
    if entry.get(attribute) and entry[attribute]:  # ensure that attribute exists and is not empty string
        if attribute == 'published_parsed':  # special handling of date information
            value = datetime_from_time_struct(entry[attribute])
        else:
            value = entry[attribute]
    else:
        if attribute == 'published_parsed':
            value = datetime.now()
        else:
            value = 'No {}'.format(attribute)
    return value


def update_feed_db(feed_dict):
    # Get latest feed items
    entries = feed_dict.entries

    # Set up db connection
    db = get_db()

    # Insert new entries to db
    for entry in entries:
        feed_id = get_feed_id(feed_dict)

        title = parse_entry_attribute(entry, 'title')
        description = parse_entry_attribute(entry, 'description')
        link = parse_entry_attribute(entry, 'link')
        created = parse_entry_attribute(entry, 'published_parsed')

        found = db.execute(
            'SELECT * FROM item'
            '   WHERE (feed_id = ? AND title = ? AND description = ? AND link = ?)',
            (feed_id, title, description, link)
        ).fetchone()

        if not found:
            db.execute(
                'INSERT INTO item (feed_id, title, description, link, created)'
                ' VALUES (?, ?, ?, ?, ?)',
                (feed_id, title, description, link, created)
            )

    db.commit()
