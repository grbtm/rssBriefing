import socket
from tqdm import tqdm

from rssbriefing import create_app
from rssbriefing.feed import get_latest_feed_dict, update_feed_db
from rssbriefing.models import Feed

# Set timeout in seconds for new socket objects, needed for feedparser connections
socket.setdefaulttimeout(10)


def main():
    # Set up app context to be able to access extensions such as SQLAlchemy when this module is run independently
    app = create_app()
    app.app_context().push()

    # Get all feeds
    feeds = Feed.query.all()

    app.logger.info(f'Updating a total of {len(feeds)} feeds...')

    for feed in tqdm(feeds):
        app.logger.info(f'Getting the latest posts from feed: {feed.title}')
        feed_dict = get_latest_feed_dict(feed_id=feed.id)

        app.logger.info(f'Writing the latest posts of feed: {feed.title} to db...')
        update_feed_db(feed_id=feed.id, feed_dict=feed_dict)
        app.logger.info('Done.')

    app.logger.info('Done with all feeds.')


if __name__ == '__main__':
    main()
