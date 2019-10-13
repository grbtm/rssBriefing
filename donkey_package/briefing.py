from flask import Blueprint, g, render_template

from donkey_package.auth import login_required
from donkey_package.db import get_db

bp = Blueprint('briefing', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()
    items = db.execute(
        'SELECT i.title, i.description, i.link'
        ' FROM item i '
        ' JOIN feed f on i.feed_id = f.id'
        ' JOIN user u on u.id = f.user_id'
        ' WHERE u.id = ?'
        ' LIMIT 10', (g.user['id'],)
    ).fetchall()
    feeds = db.execute(
        'SELECT feed.id, title'
        ' FROM feed'
        ' JOIN user on user.id = feed.user_id'
        ' WHERE user.id = ?', (g.user['id'],)
    ).fetchall()
    return render_template('briefing/index.html', items=items, feeds=feeds)
