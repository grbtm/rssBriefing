from donkey_package.models import User


def get_user_from_db(username):
    found = User.query.filter_by(username=username).first()
    return found
