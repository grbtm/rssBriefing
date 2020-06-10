import argparse
import sys
from textwrap import TextWrapper

from flask import render_template

from rssbriefing import create_app
from rssbriefing.briefing_utils import get_standard_briefing
from rssbriefing.db_utils import get_user_by_id, get_all_users
from rssbriefing.email import send_single_mail


def parse_args():
    parser = argparse.ArgumentParser()

    command_group = parser.add_mutually_exclusive_group(required=True)

    command_group.add_argument('-u', '--user_ids',
                               nargs='+',
                               action='store',  # the default value
                               help="State user_ids to whom briefing should be sent.")
    command_group.add_argument('-A', '--All',
                               action='store_true',
                               help="Send briefing to all users. Arguments '-u' and '-A' are mutually exclusive.")

    return parser.parse_args()


def main():
    # Set up app context to be able to access extensions such as SQLAlchemy when this module is run independently
    app = create_app()
    app.app_context().push()

    try:

        args = parse_args()

        if args.All:

            users = get_all_users()

        else:

            users = [get_user_by_id(user_id) for user_id in args.user_ids]

        app.logger.info(f'Fetching the latest briefing...')

        briefing_items, latest_briefing_date = get_standard_briefing()

        app.logger.info(
            f'Latest briefing was generated on {latest_briefing_date} and contains {len(briefing_items)} items.')

        if briefing_items:
            # Wrap each summary into a paragraph of max width 70 chars
            wrapper = TextWrapper()
            for item in briefing_items:
                item.summary = wrapper.fill(item.summary)

            for user in users:
                app.logger.info(f'Sending briefing for user {user}...')
                send_single_mail(subject="Today's RoboBriefing",
                                 from_email=app.config['ADMINS'][0],
                                 recipient_list=[user.email],
                                 text_body=render_template('briefing/briefing_email.txt',
                                                           user=user, items=briefing_items,
                                                           briefing_date=latest_briefing_date))
    except:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())


if __name__ == '__main__':
    main()
