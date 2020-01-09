"""
        Data structure for feed items which are considered for the Briefing.
"""


class FeedItem(object):

    def __init__(self, idx_id, feed_id, feed_title, title, description, link, created, guid):
        self.idx_id = idx_id
        self.feed_id = feed_id
        self.feed_title = feed_title
        self.title = title
        self.description = description
        self.link = link
        self.created = created
        self.guid = guid
        self.reference = None
        self.score = 0
