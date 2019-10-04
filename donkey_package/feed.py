import feedparser


def parse_feed(href):
    feed_dict = feedparser.parse(href)
    return feed_dict
