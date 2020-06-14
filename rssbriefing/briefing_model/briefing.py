"""

Briefing generation module

"""
import argparse
import sys
from datetime import datetime

import pytz

from rssbriefing import create_app
from rssbriefing import db
from rssbriefing.briefing_model.configs import DISCARD_FEEDS, DISCARD_LIVE_POSTS
from rssbriefing.briefing_model.ranking import get_candidates, rank_candidates
from rssbriefing.briefing_model.summarization import enrich_with_summary
from rssbriefing.briefing_model.topic_modeling import compute_topics
from rssbriefing.db_utils import get_user_by_id, get_all_users


def save_to_db(briefing_items):
    current_utc_datetime = datetime.now(pytz.utc)

    for item in briefing_items:
        # Enrich the selected briefing items with current datetime for the 'briefing_created' attribute
        item.briefing_created = current_utc_datetime

        db.session.add(item)

    # Commit to db only after looping over all selected Briefing items
    db.session.commit()


def filter_posts(posts):
    posts = [post for post in posts if post.feed_title not in DISCARD_FEEDS]
    posts = [post for post in posts if all([url_extract not in post.link for url_extract in DISCARD_LIVE_POSTS])]

    return posts


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--similarity_threshold',
                        type=float,
                        help="Supply similarity threshold as necessary condition for briefing items.")

    command_group = parser.add_mutually_exclusive_group(required=True)

    command_group.add_argument('-u', '--user_ids',
                               nargs='+',
                               action='store',  # the default value
                               help="State user_ids for whom briefing should be generated.")
    command_group.add_argument('-A', '--All',
                               action='store_true',
                               help="Generate briefing for all users. Arguments '-u' and '-A' are mutually exclusive.")

    return parser.parse_args()


def generate_briefing():
    # Set up app context to be able to access extensions such as SQLAlchemy when this module is run independently
    app = create_app()
    app.app_context().push()

    try:

        args = parse_args()

        if args.All:

            users = get_all_users()

        else:

            users = [get_user_by_id(user_id) for user_id in args.user_ids]

        # Compute the current trending topics
        topic_model = compute_topics(app)

        app.logger.info(f'Generating briefing for users {users}...')

        for user in users:
            app.logger.info(f'Generating briefing for user {user}...')

            candidates = get_candidates(app, user.id)

            candidates = filter_posts(candidates)

            selected = rank_candidates(app, candidates, topic_model, args.similarity_threshold)

            selected = enrich_with_summary(app, selected)

            app.logger.info(f'The chosen briefing items are:')
            for post in selected:
                app.logger.info('----------------------------------------------------')
                app.logger.info(f'Post title: \n{post.title}')
                app.logger.info('----------------------------------------------------')
                app.logger.info(f'Post description: \n{post.description}')
                app.logger.info(f'Post summary: \n{post.summary}')
                app.logger.info(
                    f'Post topic id {post.reference}, ranked {post.guid}: \n {topic_model.print_topic(int(post.reference), topn=10)}')
                app.logger.info(f'topic probability: \n{post.score}')

            app.logger.info(f'Writing {len(selected)} briefing items for user {user} to DB...')
            save_to_db(selected)
            app.logger.info('DB write done.')

    except:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())


if __name__ == '__main__':
    generate_briefing()
