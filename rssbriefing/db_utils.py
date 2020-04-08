from rssbriefing.models import Users, Feed


def get_user_by_id(user_id):
    return Users.query.get(user_id)


def get_user_by_username(username):
    found = Users.query.filter_by(username=username).first()

    return found


def get_feedlist_for_dropdown(user_id):
    feeds = Feed.query.filter(Feed.users.any(Users.id == user_id)).all()

    return feeds


def get_all_users():
    return Users.query.all()
