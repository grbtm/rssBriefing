from donkey_package.models import User, Feed


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_user_by_username(username):
    found = User.query.filter_by(username=username).first()

    return found


def get_feedlist_for_dropdown(user_id):
    feeds = Feed.query.filter(Feed.users.any(User.id == user_id)).all()

    return feeds
