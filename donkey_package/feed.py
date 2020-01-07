import calendar
from datetime import datetime

import feedparser
import html2text

from donkey_package import db
from donkey_package.models import Item, Feed


def parse_feed(href):
    feed_dict = feedparser.parse(href)
    return feed_dict


def well_formed(feed_dict):
    # consider a feed malformed if
    #   1. feedparser bozo attribute declares an error (value: 1) and
    #   2. no entry list loaded

    if feed_dict.bozo and len(feed_dict.entries) is 0:
        result = False
    else:
        result = True
    return result


def get_latest_feed_dict(feed_id):

    feed = Feed.query.filter_by(id=feed_id).first()
    feed_href = feed.href

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

        elif attribute == 'description':    # HTML parsing of description

            text_maker = html2text.HTML2Text()
            text_maker.ignore_links = False
            text_maker.ignore_images = True

            value = text_maker.handle(entry[attribute])

        else:

            value = entry[attribute]

    else:

        if attribute == 'published_parsed':

            value = datetime.now()

        else:

            value = 'No {}'.format(attribute)

    return value


def update_feed_db(feed_id, feed_dict):

    # Get latest feed items
    entries = feed_dict.entries

    # Insert new entries to db
    for entry in entries:

        title = parse_entry_attribute(entry, 'title')
        description = parse_entry_attribute(entry, 'description')
        link = parse_entry_attribute(entry, 'link')
        created = parse_entry_attribute(entry, 'published_parsed')

        found = Item.query.filter_by(feed_id=feed_id, title=title, description=description, link=link).first()

        if not found:

            new_item = Item(title=title, description=description, link=link, created=created, feed_id=feed_id)
            db.session.add(new_item)

    db.session.commit()
