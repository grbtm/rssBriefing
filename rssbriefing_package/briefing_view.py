from flask import Blueprint, g, render_template

from rssbriefing_package import db
from rssbriefing_package.auth import login_required
from rssbriefing_package.db_utils import get_feedlist_for_dropdown
from rssbriefing_package.models import Briefing

bp = Blueprint('briefing', __name__)


def get_latest_briefing_date(user):
    datetime_obj = db.session.query(
        db.func.max(Briefing.briefing_created)). \
        filter(Briefing.user_id == user). \
        scalar()

    return datetime_obj


def get_briefing_items(user, briefing_date):
    items = Briefing.query. \
        filter(Briefing.user_id == user). \
        filter(Briefing.briefing_created == briefing_date). \
        all()

    return items


def get_feedlist_for_logged_in_user():
    if g.user:
        feedlist = get_feedlist_for_dropdown(g.user.id)
    else:
        feedlist = None

    return feedlist


@bp.route('/')
@login_required
def index():
    # Get the date of the most recent briefing
    latest_briefing_date = get_latest_briefing_date(user=g.user.id)

    # Get all items of most recent briefing
    items = get_briefing_items(user=g.user.id, briefing_date=latest_briefing_date)

    # If briefing available: Convert briefing date to custom string format for display
    if latest_briefing_date:
        latest_briefing_date = latest_briefing_date.strftime("%B %d, %Y at %I:%M %p")

    # Get all feeds of user for the dropdown in the header navbar
    feeds = get_feedlist_for_dropdown(g.user.id)

    return render_template('briefing/index.html',
                           items=items,
                           feeds=feeds,
                           briefing_date=latest_briefing_date)


@bp.route('/start')
def landing_page():
    # Get the date of the most recent briefing
    latest_briefing_date = get_latest_briefing_date(user=1)

    # Convert briefing date to custom string format for display
    latest_briefing_date = latest_briefing_date.strftime("%B %d, %Y at %I:%M %p") if latest_briefing_date else None

    # For logged in user: Get all feeds of user for the dropdown in the header navbar
    feeds = get_feedlist_for_logged_in_user()

    return render_template('landing_page/start.html',
                           feeds=feeds,
                           briefing_date=latest_briefing_date)


@bp.route('/example')
def example_briefing():
    # Get the date of the most recent briefing for example user
    latest_briefing_date = get_latest_briefing_date(user=1)

    if latest_briefing_date:
        # Get all items of most recent briefing
        items = get_briefing_items(user=1, briefing_date=latest_briefing_date)

        # Convert briefing date to custom string format for display
        latest_briefing_date = latest_briefing_date.strftime("%B %d, %Y at %I:%M %p")

        # For logged in user: Get all feeds of user for the dropdown in the header navbar
        feeds = get_feedlist_for_logged_in_user()
    else:
        items, latest_briefing_date, feeds = None, None, None

    return render_template('landing_page/example_briefing.html',
                           items=items,
                           feeds=feeds,
                           briefing_date=latest_briefing_date)


@bp.route('/how_it_works')
def how_it_works():
    # For logged in user: Get all feeds of user for the dropdown in the header navbar
    feeds = get_feedlist_for_logged_in_user()

    return render_template('landing_page/how_it_works.html',
                           feeds=feeds)
