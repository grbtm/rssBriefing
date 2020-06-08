from rssbriefing import db
from rssbriefing.models import Briefing


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


def get_standard_briefing():
    # Get the date of the most recent briefing for example user
    latest_briefing_date = get_latest_briefing_date(user=1)

    if latest_briefing_date:
        # Get all items of most recent briefing
        items = get_briefing_items(user=1, briefing_date=latest_briefing_date)

        if all([item.guid for item in items]):
            items = sorted(items, key=lambda item: int(item.guid), reverse=False)

        # Convert briefing date to custom string format for display
        latest_briefing_date = latest_briefing_date.strftime("%B %d, %Y at %I:%M %p")
    else:
        return None, None

    return items, latest_briefing_date
